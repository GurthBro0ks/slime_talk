import Foundation
// Pure monotonic safety gate. No microphone or network code lives here.
struct PTTGate {
    enum State: String { case IDLE, REQUESTING, AUTHORIZED_PREPARING, TRANSMITTING, BUSY, WAIT_FOR_RELEASE, DISCONNECTED }
    var state: State = .DISCONNECTED
    var held = false
    var capture = false
    var epoch: Int?
    var deadline: Double = 0
    var lastSpeech: Double = 0
    var generation = 0
    mutating func connected() { if !held { state = .IDLE } }
    mutating func press() -> Bool { guard !held, state == .IDLE || state == .BUSY else { return false }; held = true; generation += 1; state = .REQUESTING; return true }
    mutating func grant(_ value: Int, requestedAt: Double, now: Double) -> Bool { guard held, state == .REQUESTING, now < requestedAt + 2 else { return false }; epoch = value; deadline = requestedAt + 2; state = .AUTHORIZED_PREPARING; return true }
    mutating func renew(requestedAt: Double, now: Double) -> Bool { guard epoch != nil, now < deadline, now < requestedAt + 2 else { return false }; deadline = requestedAt + 2; return true }
    mutating func captureStarted(now: Double) { capture = true; lastSpeech = now }
    mutating func started(now: Double) { state = .TRANSMITTING }
    mutating func stop(disconnected: Bool = false) { generation += 1; epoch = nil; capture = false; state = held ? .WAIT_FOR_RELEASE : (disconnected ? .DISCONNECTED : .IDLE) }
    mutating func release(connected: Bool) { held = false; stop(disconnected: !connected) }
    func mayCapture(now: Double, appleActive: Bool) -> Bool { held && epoch != nil && now < deadline && appleActive && (state == .AUTHORIZED_PREPARING || state == .TRANSMITTING) }
    func expiry(now: Double) -> String? { if epoch != nil && now >= deadline { return "authorization_loss" }; if capture && now - lastSpeech >= 3 { return "silence_expiry" }; return nil }
}
