import SwiftUI
import PushToTalk
import AVFoundation

// Prerequisite probe only. No channel, audio session, capture, or network is started.
// Replace this screen with the authorized PTT experiment after signing is verified.
@main
struct SlimeTalkApp: App {
    var body: some Scene {
        WindowGroup {
            VStack(spacing: 16) {
                Text("slime_talk feasibility").font(.title2)
                Text("Signing probe").font(.headline)
                Text("PTT is not implemented in this build.")
                Text("Microphone and network remain inactive.")
            }
            .multilineTextAlignment(.center)
            .padding()
        }
    }
}
