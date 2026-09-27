plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
android {
 namespace="ai.slimy.slimetalk.feasibility"
 compileSdk=35
 defaultConfig { applicationId="ai.slimy.slimetalk.feasibility"; minSdk=30; targetSdk=35; versionCode=System.getenv("GITHUB_RUN_NUMBER")?.toInt() ?: 1; versionName="0.1.0" }
 compileOptions { sourceCompatibility=JavaVersion.VERSION_17; targetCompatibility=JavaVersion.VERSION_17 }
 kotlinOptions { jvmTarget="17" }
}
dependencies {
 implementation("io.livekit:livekit-android:2.29.0")
 implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")
 implementation("com.squareup.okhttp3:okhttp:4.12.0")
 testImplementation("junit:junit:4.13.2")
}
