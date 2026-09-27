import SwiftUI
import PushToTalk
import AVFoundation
import Security
import LiveKit

private let channelID = UUID(uuidString: "838d72ab-e627-4e79-90a4-884f9e3d7bad")!
private func now() -> Double { ProcessInfo.processInfo.systemUptime }
private func evidence(_ event: String, _ value: String = "") { print("PTT t=\(Date().timeIntervalSince1970) mono=\(now()) event=\(event) \(value)") }
private enum Vault {
    static func get(_ name: String) -> String { let q: [String: Any] = [kSecClass as String:kSecClassGenericPassword,kSecAttrService as String:"slime-talk-feasibility",kSecAttrAccount as String:name,kSecReturnData as String:true]; var v: CFTypeRef?; guard SecItemCopyMatching(q as CFDictionary,&v) == errSecSuccess, let d = v as? Data else { return "" }; return String(data:d,encoding:.utf8) ?? "" }
    static func set(_ name: String, _ value: String) { let q: [String: Any] = [kSecClass as String:kSecClassGenericPassword,kSecAttrService as String:"slime-talk-feasibility",kSecAttrAccount as String:name]; SecItemDelete(q as CFDictionary); var n=q; n[kSecValueData as String]=Data(value.utf8); n[kSecAttrAccessible as String]=kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly; SecItemAdd(n as CFDictionary,nil) }
}
// Observes samples only; never stores PCM or calls a recording API.
final class PCMObserver: AudioRenderer, @unchecked Sendable {
    let local: Bool; let callback: @Sendable (Bool) -> Void
    private let lock = NSLock(); private var voiced: Double = 0; private var first = true
    init(local: Bool, callback: @escaping @Sendable (Bool) -> Void) { self.local=local; self.callback=callback }
    func render(pcmBuffer b: AVAudioPCMBuffer) {
        lock.lock(); defer { lock.unlock() }
        if first { first=false; evidence(local ? "capture_first_pcm" : "remote_first_pcm") }
        guard local, let samples=b.floatChannelData?[0], b.frameLength>0 else { return }
        let n=Int(b.frameLength); var power: Float=0; var crossings=0
        for i in 0..<n { power += samples[i]*samples[i]; if i>0 && (samples[i]>0) != (samples[i-1]>0) { crossings += 1 } }
        let rms=sqrt(power/Float(n)); let z=Float(crossings)/Float(n)
        voiced = rms>0.008 && z>0.005 && z<0.45 ? voiced+Double(n)/b.format.sampleRate : 0
        callback(voiced >= 0.06)
    }
}
final class EngineEvidence: AudioEngineObserver, @unchecked Sendable {
    var next: (any AudioEngineObserver)?
    func engineWillStart(_ engine: AVAudioEngine, isPlayoutEnabled: Bool, isRecordingEnabled: Bool) -> Int { evidence("engine_will_start","input=\(isRecordingEnabled) output=\(isPlayoutEnabled)"); return next?.engineWillStart(engine,isPlayoutEnabled:isPlayoutEnabled,isRecordingEnabled:isRecordingEnabled) ?? 0 }
    func engineDidStop(_ engine: AVAudioEngine, isPlayoutEnabled: Bool, isRecordingEnabled: Bool) -> Int { evidence("engine_did_stop","input=\(isRecordingEnabled) output=\(isPlayoutEnabled)"); return next?.engineDidStop(engine,isPlayoutEnabled:isPlayoutEnabled,isRecordingEnabled:isRecordingEnabled) ?? 0 }
}
@MainActor final class PTTModel: NSObject, ObservableObject, PTChannelManagerDelegate, PTChannelRestorationDelegate, RoomDelegate {
    @Published var state="DISCONNECTED"
    @Published var message="Enter the approved controller HTTPS URL and iPhone pairing key."
    @Published var endpoint=Vault.get("endpoint")
    @Published var pairingKey=Vault.get("pairing")
    var manager: PTChannelManager?
    lazy var room=Room(delegate:self)
    var gate=PTTGate(); var appleActive=false; var uiHeld=false; var forcedEnd=false; var joined=false
    var session=""; var pushToken=""; var connected=false; var connecting=false
    var track: LocalAudioTrack?; var publication: LocalTrackPublication?
    var timer: Task<Void,Never>?; var polling: Task<Void,Never>?
    var captureObserved=false; var starting=false; var shutdown: Task<Void,Never>?
    var remoteOwner: String?; var lastSpeechLog: Double=0
    lazy var localPCM=PCMObserver(local:true) { [weak self] speech in Task { @MainActor in
        guard let self, self.gate.mayCapture(now:now(),appleActive:self.appleActive) else { return }
        self.captureObserved=true; if self.publication != nil { self.gate.state = .TRANSMITTING; self.show() }; if speech { self.gate.lastSpeech=now(); if now()-self.lastSpeechLog>0.25 { self.lastSpeechLog=now(); evidence("last_qualifying_speech") } }
    } }
    let remotePCM=PCMObserver(local:false) { _ in }
    func show() { state=gate.state.rawValue }
    func bootstrap() async {
        guard manager == nil else { return }
        do {
            LiveKitSDK.disableLogging()
            AudioManager.shared.audioSession.isAutomaticConfigurationEnabled=false
            try AudioManager.shared.setEngineAvailability(.none)
            AudioManager.shared.set(engineObservers:[EngineEvidence(),AudioManager.shared.audioSession])
            try AVAudioSession.sharedInstance().setCategory(.playAndRecord,mode:.voiceChat,options:[.defaultToSpeaker,.allowBluetooth])
            manager=try await PTChannelManager.channelManager(delegate:self,restorationDelegate:self)
            joined=manager?.activeChannelUUID == channelID
            if joined && !endpoint.isEmpty { await connect() }
        } catch { message="Apple PTT setup failed"; halt("apple_setup_failure",disconnected:true) }
        timer=Task { [weak self] in while !Task.isCancelled { try? await Task.sleep(nanoseconds:50_000_000); guard let self else { return }; if let reason=self.gate.expiry(now:now()) { self.halt(reason) } } }
    }
    func api(_ path: String, _ body: [String:Any] = [:], authenticated: Bool = true) async throws -> [String:Any] {
        guard let root=URL(string:endpoint), root.scheme=="https", root.user==nil, root.password==nil, root.query==nil, let url=URL(string:path,relativeTo:root) else { throw URLError(.badURL) }
        var r=URLRequest(url:url); r.httpMethod="POST"; r.timeoutInterval=1.5; r.setValue("application/json",forHTTPHeaderField:"Content-Type")
        if authenticated { r.setValue("Bearer "+session,forHTTPHeaderField:"Authorization") }; r.httpBody=try JSONSerialization.data(withJSONObject:body)
        let (data,response)=try await URLSession.shared.data(for:r)
        guard (response as? HTTPURLResponse)?.statusCode==200, let json=try JSONSerialization.jsonObject(with:data) as? [String:Any] else { throw URLError(.userAuthenticationRequired) }; return json
    }
    func join() { AVAudioSession.sharedInstance().requestRecordPermission { [weak self] allowed in Task { @MainActor in guard let self else { return }; guard allowed else { self.message="Microphone permission required";return }; Vault.set("endpoint",self.endpoint); Vault.set("pairing",self.pairingKey); self.manager?.requestJoinChannel(channelUUID:channelID,descriptor:PTChannelDescriptor(name:"slime talk feasibility",image:nil)) } } }
    func connect() async {
        guard !connecting else { return }; connecting=true; defer { connecting=false }
        do {
            halt("connect_reset",disconnected:true); await shutdown?.value
            await room.disconnect()
            let login=try await api("/login",["device":"iphone","key":pairingKey],authenticated:false)
            guard let s=login["session"] as? String,let url=login["url"] as? String,let token=login["token"] as? String else { throw URLError(.badServerResponse) }; session=s
            try await room.connect(url:url,token:token)
            connected=true;gate.connected();show();message="Joined — ready for physical testing";evidence("media_connected")
            if !pushToken.isEmpty { _=try await api("/push",["token":pushToken]) }
            startPolling()
        } catch { message="Connection unavailable"; halt("connection_failure",disconnected:true) }
    }
    func startPolling() {
        polling?.cancel();polling=Task { [weak self] in while !Task.isCancelled {
            guard let self else { return }
            do {
                let begin=now()
                if let epoch=self.gate.epoch {
                    _=try await self.api("/renew",["epoch":epoch])
                    if self.gate.epoch==epoch && !self.gate.renew(requestedAt:begin,now:now()) { self.halt("authorization_loss") }
                }
                let status=try await self.api("/status")
                let owner=status["owner"] as? String
                if owner != self.remoteOwner {
                    self.remoteOwner=owner
                    if owner != "iphone" && owner != nil { self.manager?.setActiveRemoteParticipant(PTParticipant(name:"Pixel test device",image:nil),channelUUID:channelID,completionHandler:nil) }
                    else { self.manager?.setActiveRemoteParticipant(nil,channelUUID:channelID,completionHandler:nil) }
                }
                if let epoch=self.gate.epoch, status["epoch"] as? Int != epoch || owner != "iphone" { self.halt("authorization_loss") }
            } catch { self.halt("controller_connection_loss",disconnected:true); return }
            try? await Task.sleep(nanoseconds:500_000_000)
        } }
    }
    func down() { guard !uiHeld else { return };uiHeld=true;evidence("physical_press");manager?.requestBeginTransmitting(channelUUID:channelID) }
    func up() { uiHeld=false;gate.held=false;halt("release");gate.release(connected:connected);show();manager?.stopTransmitting(channelUUID:channelID) }
    func request() async {
        guard connected, gate.press() else { manager?.stopTransmitting(channelUUID:channelID);return };show();evidence("ptt_request")
        let generation=gate.generation, sent=now()
        do {
            let answer=try await api("/request",["requestId":UUID().uuidString.lowercased()])
            guard answer["granted"] as? Bool == true,let epoch=answer["epoch"] as? Int else { gate.state = .BUSY;show();evidence("deny");forcedEnd=true;manager?.stopTransmitting(channelUUID:channelID);return }
            guard gate.generation==generation,gate.grant(epoch,requestedAt:sent,now:now()) else { _=try? await api("/release",["epoch":epoch]);return }
            evidence("grant","epoch=\(epoch)");show();await startIfReady()
        } catch { halt("authorization_failure") }
    }
    func startIfReady() async {
        guard !starting,gate.mayCapture(now:now(),appleActive:appleActive),track==nil else { return };starting=true;defer { starting=false }
        let generation=gate.generation
        do {
            let newTrack=await LocalAudioTrack.createTrack()
            guard generation==gate.generation,gate.mayCapture(now:now(),appleActive:appleActive) else { try? await newTrack.stop();return }
            track=newTrack;captureObserved=false;gate.captureStarted(now:now());newTrack.add(audioRenderer:localPCM)
            try AudioManager.shared.setEngineAvailability(.default)
            evidence("capture_start_requested")
            let pub=try await room.localParticipant.publish(audioTrack:newTrack)
            guard generation==gate.generation,gate.mayCapture(now:now(),appleActive:appleActive) else { try? await newTrack.stop();try? await room.localParticipant.unpublish(publication:pub);return }
            publication=pub;if captureObserved { gate.started(now:now()) };show();evidence("publication_ready")
        } catch { halt("publish_failure") }
    }
    func halt(_ reason: String, disconnected: Bool = false) {
        let epoch=gate.epoch;let oldTrack=track;let oldPub=publication;let oldSession=session
        gate.stop(disconnected:disconnected);track=nil;publication=nil;if disconnected { connected=false };show();evidence(reason)
        do { try AudioManager.shared.setEngineAvailability(AudioEngineAvailability(isInputAvailable:false,isOutputAvailable:appleActive)); evidence("capture_input_disabled","input=\(AudioManager.shared.engineAvailability.isInputAvailable) engine=\(AudioManager.shared.isEngineRunning)") }
        catch { message="STOP: microphone shutdown could not be confirmed";try? AudioManager.shared.setEngineAvailability(.none) }
        if epoch != nil { forcedEnd=true;manager?.stopTransmitting(channelUUID:channelID) }
        shutdown=Task {
            do { try await oldTrack?.stop(); evidence("capture_stop_completed"); if let pub=oldPub { try await room.localParticipant.unpublish(publication:pub) }; evidence("publication_stop_completed") }
            catch { await room.disconnect();message="STOP: track shutdown failed" }
            if let epoch,session==oldSession { _=try? await api("/release",["epoch":epoch]);evidence("ownership_release_requested","epoch=\(epoch)") }
        }
    }
    func channelDescriptor(restoredChannelUUID: UUID) -> PTChannelDescriptor { PTChannelDescriptor(name:"slime talk feasibility",image:nil) }
    func channelManager(_ channelManager: PTChannelManager, didJoinChannel channelUUID: UUID, reason: PTChannelJoinReason) { joined=true;evidence("apple_join");Task { await connect() } }
    func channelManager(_ channelManager: PTChannelManager, didLeaveChannel channelUUID: UUID, reason: PTChannelLeaveReason) { joined=false;halt("channel_left",disconnected:true);polling?.cancel();Task { await room.disconnect() } }
    func channelManager(_ channelManager: PTChannelManager, channelUUID: UUID, didBeginTransmittingFrom source: PTChannelTransmitRequestSource) { evidence("apple_did_begin");if !uiHeld && (gate.state == .WAIT_FOR_RELEASE || gate.state == .BUSY) { gate.release(connected:connected) };Task { await request() } }
    func channelManager(_ channelManager: PTChannelManager, channelUUID: UUID, didEndTransmittingFrom source: PTChannelTransmitRequestSource) { evidence("apple_did_end");if forcedEnd { forcedEnd=false;return };gate.held=false;halt("system_release");gate.release(connected:connected);show() }
    func channelManager(_ channelManager: PTChannelManager, didActivate audioSession: AVAudioSession) { appleActive=true;evidence("apple_audio_activated");do { try AudioManager.shared.setEngineAvailability(AudioEngineAvailability(isInputAvailable:false,isOutputAvailable:true));evidence("receive_engine","running=\(AudioManager.shared.isEngineRunning)");Task { await startIfReady() } }catch{halt("audio_activation_failure")} }
    func channelManager(_ channelManager: PTChannelManager, didDeactivate audioSession: AVAudioSession) { appleActive=false;evidence("apple_audio_deactivated");halt("apple_audio_loss");try? AudioManager.shared.setEngineAvailability(.none) }
    func channelManager(_ channelManager: PTChannelManager, receivedEphemeralPushToken pushToken: Data) { self.pushToken=pushToken.map{String(format:"%02x",$0)}.joined();Task { if !session.isEmpty { _=try? await api("/push",["token":self.pushToken]);evidence("apns_registered") } } }
    func incomingPushResult(channelManager: PTChannelManager, channelUUID: UUID, pushPayload: [String:Any]) -> PTPushResult { evidence("apple_ptt_push");Task { if !connected { await connect() } };return .activeRemoteParticipant(PTParticipant(name:"Pixel test device",image:nil)) }
    func channelManager(_ channelManager: PTChannelManager, failedToJoinChannel channelUUID: UUID, error: Error) { halt("apple_join_failure",disconnected:true) }
    func channelManager(_ channelManager: PTChannelManager, failedToBeginTransmittingInChannel channelUUID: UUID, error: Error) { halt("apple_begin_failure") }
    nonisolated func room(_ room: Room, participant: RemoteParticipant, didSubscribeTrack publication: RemoteTrackPublication) { Task { @MainActor in evidence("remote_subscription");(publication.track as? RemoteAudioTrack)?.add(audioRenderer:self.remotePCM) } }
    nonisolated func room(_ room: Room, didStartReconnectWithMode reconnectMode: ReconnectMode) { Task { @MainActor in self.halt("media_connection_loss",disconnected:true) } }
    nonisolated func room(_ room: Room, didCompleteReconnectWithMode reconnectMode: ReconnectMode) { Task { @MainActor in self.connected=true;self.gate.connected();self.show();evidence("media_reconnected_no_reacquire") } }
    nonisolated func room(_ room: Room, didDisconnectWithError error: LiveKitError?) { Task { @MainActor in guard !self.connecting else { return }; self.halt("media_disconnected",disconnected:true) } }
}
struct HoldControl: UIViewRepresentable {
    let down: ()->Void; let up: ()->Void
    func makeUIView(context: Context) -> UIButton { let b=UIButton(type:.system); b.setTitle("HOLD TO TALK",for:.normal);b.backgroundColor = .systemGreen;b.layer.cornerRadius=16;b.addTarget(context.coordinator,action:#selector(Coordinator.down),for:.touchDown);b.addTarget(context.coordinator,action:#selector(Coordinator.up),for:[.touchUpInside,.touchUpOutside,.touchCancel,.touchDragExit]);return b }
    func updateUIView(_ uiView: UIButton,context: Context) {}
    func makeCoordinator()->Coordinator { Coordinator(down,up) }
    final class Coordinator: NSObject { let d:()->Void;let u:()->Void;init(_ d:@escaping()->Void,_ u:@escaping()->Void){self.d=d;self.u=u};@objc func down(){d()};@objc func up(){u()} }
}
@main struct SlimeTalkApp: App {
    @StateObject var model=PTTModel()
    var body: some Scene { WindowGroup { VStack(spacing:20) {
        Text("slime talk — feasibility").font(.title2)
        Text(model.state).font(.headline);Text(model.message)
        if !model.connected { TextField("Controller HTTPS URL",text:$model.endpoint).textInputAutocapitalization(.never).autocorrectionDisabled();SecureField("iPhone pairing key",text:$model.pairingKey);Button("Join / reconnect") { if model.joined { Task { await model.connect() } } else { model.join() } } }
        HoldControl(down:{model.down()},up:{model.up()}).frame(height:150)
        Button("Leave") { model.manager?.leaveChannel(channelUUID:channelID) }
    }.padding().task { await model.bootstrap() } } }
}
