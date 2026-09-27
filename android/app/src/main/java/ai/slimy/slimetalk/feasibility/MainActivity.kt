package ai.slimy.slimetalk.feasibility
import android.Manifest
import android.app.Activity
import android.os.*
import android.content.pm.PackageManager
import android.content.ClipboardManager
import android.content.ClipData
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.util.Base64
import android.util.Log
import android.view.MotionEvent
import android.widget.*
import io.livekit.android.*
import io.livekit.android.events.RoomEvent
import io.livekit.android.room.Room
import io.livekit.android.room.track.*
import kotlinx.coroutines.*
import io.livekit.android.events.collect
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import livekit.org.webrtc.AudioTrackSink
import livekit.org.webrtc.audio.JavaAudioDeviceModule
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.KeyStore
import java.util.UUID
import java.util.concurrent.TimeUnit
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import kotlin.math.sqrt

class MainActivity:Activity(){
 private val scope=CoroutineScope(SupervisorJob()+Dispatchers.Main.immediate)
 private val gate=PTTGate();private lateinit var status:TextView;private lateinit var endpoint:EditText;private lateinit var key:EditText
 private val trace=ArrayDeque<String>();private lateinit var traceView:TextView
 private var room:Room?=null;private var local:LocalAudioTrack?=null;private var session="";private var connected=false;private var poll:Job?=null;private var publishing=false
 private var publicationReady=false;private var captureObserved=false
 private val http=OkHttpClient.Builder().followRedirects(false).followSslRedirects(false).callTimeout(1500,TimeUnit.MILLISECONDS).build()
 private fun now()=SystemClock.elapsedRealtime()
 private fun event(name:String,detail:String=""){val line="time=${System.currentTimeMillis()} mono=${now()} event=$name $detail";Log.i("SLIME_PTT",line);runOnUiThread{trace.addLast(line);while(trace.size>5000)trace.removeFirst();if(::traceView.isInitialized)traceView.text=trace.takeLast(12).joinToString("\n")}}
 private fun show(){status.text=gate.state.name}
 private fun storeKey():SecretKey {val s=KeyStore.getInstance("AndroidKeyStore").apply{load(null)};if(!s.containsAlias("slime-pairing")){val g=KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,"AndroidKeyStore");g.init(KeyGenParameterSpec.Builder("slime-pairing",KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT).setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());g.generateKey()};return s.getKey("slime-pairing",null)as SecretKey}
 private fun savePairing(){val c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.ENCRYPT_MODE,storeKey());val encrypted=c.doFinal(key.text.toString().toByteArray());getPreferences(MODE_PRIVATE).edit().putString("endpoint",endpoint.text.toString()).putString("key",Base64.encodeToString(c.iv+encrypted,Base64.NO_WRAP)).apply()}
 private fun loadPairing():String=try{val d=Base64.decode(getPreferences(MODE_PRIVATE).getString("key","")!!,Base64.NO_WRAP);val c=Cipher.getInstance("AES/GCM/NoPadding");c.init(Cipher.DECRYPT_MODE,storeKey(),GCMParameterSpec(128,d.copyOfRange(0,12)));String(c.doFinal(d.copyOfRange(12,d.size)))}catch(_:Exception){""}
 override fun onCreate(b:Bundle?){super.onCreate(b);LiveKit.loggingLevel=io.livekit.android.util.LoggingLevel.OFF;val box=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(28,40,28,20)};status=TextView(this);endpoint=EditText(this).apply{hint="Approved controller HTTPS URL";setText(getPreferences(MODE_PRIVATE).getString("endpoint",""))};key=EditText(this).apply{hint="Pixel pairing key";inputType=129;setText(loadPairing())};box.addView(status);box.addView(endpoint);box.addView(key)
 box.addView(Button(this).apply{text="Join / reconnect";setOnClickListener{if(checkSelfPermission(Manifest.permission.RECORD_AUDIO)!=PackageManager.PERMISSION_GRANTED)requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO),1)else scope.launch{join()}}})
 box.addView(Button(this).apply{text="HOLD TO TALK";minimumHeight=300;setOnTouchListener{_,e->when(e.actionMasked){MotionEvent.ACTION_DOWN->{press();true};MotionEvent.ACTION_UP,MotionEvent.ACTION_CANCEL->{release();true};MotionEvent.ACTION_MOVE->{if(e.x<0||e.y<0||e.x>width||e.y>height)release();true};else->true}}})
 traceView=TextView(this).apply{textSize=9f};box.addView(ScrollView(this).apply{addView(traceView)},LinearLayout.LayoutParams(-1,240));box.addView(Button(this).apply{text="Copy QA trace";setOnClickListener{(getSystemService(CLIPBOARD_SERVICE)as ClipboardManager).setPrimaryClip(ClipData.newPlainText("PTT QA trace",trace.joinToString("\n")))}})
 setContentView(box);show();scope.launch{while(isActive){delay(50);gate.expiry(now())?.let{halt(it)}}}
 }
 private suspend fun api(path:String,body:JSONObject=JSONObject(),auth:Boolean=true):JSONObject {
 val base=endpoint.text.toString().trim();require(base.startsWith("https://")&&!base.contains('@')&&!base.contains('?'))
 val request=Request.Builder().url(base.trimEnd('/')+path).post(body.toString().toRequestBody("application/json".toMediaType()));if(auth)request.header("Authorization","Bearer $session")
 return withContext(Dispatchers.IO){http.newCall(request.build()).execute().use{require(it.isSuccessful);JSONObject(it.body!!.string())}}
 }
 private suspend fun join(){
 halt("connect_reset",true);poll?.cancel();room?.disconnect();room?.release()
 try{savePairing();val login=api("/login",JSONObject().put("device","pixel").put("key",key.text.toString()),false);session=login.getString("session")
 val r=LiveKit.create(applicationContext,overrides=LiveKitOverrides(audioOptions=AudioOptions(disableAudioPrewarming=true,javaAudioDeviceModuleCustomizer={builder->builder.setAudioRecordStateCallback(object:JavaAudioDeviceModule.AudioRecordStateCallback{
 override fun onWebRtcAudioRecordStart(){event("hardware_capture_start");scope.launch{captureObserved=true;if(!gate.canCapture(now()))halt("unauthorized_capture",true)else if(publicationReady){gate.state=PTTGate.State.TRANSMITTING;show()}}}
 override fun onWebRtcAudioRecordStop(){event("hardware_capture_stop");scope.launch{captureObserved=false}}
 })})))
 room=r
 scope.launch{r.events.collect{e->if(room !== r)return@collect;when(e){is RoomEvent.Reconnecting->halt("media_connection_loss",true);is RoomEvent.Disconnected->halt("media_disconnected",true);is RoomEvent.Reconnected->{connected=true;gate.connected();show();event("reconnected_no_reacquire")};is RoomEvent.TrackSubscribed->{event("remote_subscription");(e.track as? AudioTrack)?.addSink(RemotePCM())};else->{}}}}
 r.connect(login.getString("url"),login.getString("token"));connected=true;gate.connected();show();event("media_connected");startPoll()
 }catch(_:Exception){halt("connection_failure",true)}
 }
 private fun startPoll(){poll?.cancel();poll=scope.launch{while(isActive){try{val sent=now();val e=gate.epoch;if(e!=null){api("/renew",JSONObject().put("epoch",e));if(gate.epoch==e&&!gate.renew(sent,now()))halt("authorization_loss")};val s=api("/status");if(gate.epoch!=null&&(s.optString("owner")!="pixel"||s.optLong("epoch")!=gate.epoch))halt("authorization_loss");if(gate.epoch==null&&!gate.held){gate.state=if(s.optBoolean("busy"))PTTGate.State.BUSY else PTTGate.State.IDLE;show()}}catch(_:Exception){halt("controller_connection_loss",true);return@launch};delay(500)}}}
 private fun press(){event("physical_press");if(!connected||!gate.press())return;show();val generation=gate.generation;val sent=now()
 scope.launch{try{val grant=api("/request",JSONObject().put("requestId",UUID.randomUUID().toString()));if(!grant.optBoolean("granted")){gate.state=PTTGate.State.BUSY;show();event("deny");return@launch};val epoch=grant.getLong("epoch");if(gate.generation!=generation||!gate.grant(epoch,sent,now())){api("/release",JSONObject().put("epoch",epoch));return@launch};event("grant","epoch=$epoch");show();val r=room?:error("no room");if(!gate.canCapture(now()))return@launch
 while(r.localParticipant.permissions?.canPublish!=true){if(gate.generation!=generation||!gate.canCapture(now()))return@launch;delay(20)}
 val t=r.localParticipant.createAudioTrack();local=t;t.addSink(LocalPCM());gate.captureStarted(now());publishing=true;event("capture_start_requested")
 val ok=r.localParticipant.publishAudioTrack(t);publishing=false
 if(!ok||gate.generation!=generation||!gate.canCapture(now())){t.stop();r.localParticipant.unpublishTrack(t);t.dispose();if(gate.generation==generation)halt("publish_failure");return@launch}
 publicationReady=true;if(captureObserved)gate.state=PTTGate.State.TRANSMITTING;show();event("publication_ready")
 }catch(_:Exception){halt("authorization_or_publish_failure")}}
 }
 private fun release(){gate.held=false;halt("release_or_cancel");gate.release(connected);show()}
 private fun halt(reason:String,disconnected:Boolean=false){val epoch=gate.epoch;val oldSession=session;gate.stop(disconnected);if(disconnected)connected=false;show();event(reason)
 val t=local;local=null;publicationReady=false
 try{t?.stop();event("capture_stop_requested");if(t!=null){room?.localParticipant?.unpublishTrack(t);t.dispose()};event("publication_stop_completed")}catch(_:Exception){room?.disconnect();event("STOP_shutdown_unconfirmed")}
 if(epoch!=null)scope.launch{try{if(session==oldSession)api("/release",JSONObject().put("epoch",epoch));event("ownership_release_requested","epoch=$epoch")}catch(_:Exception){}}
 }
 private inner class LocalPCM:AudioTrackSink {private var voiced=0.0;private var logged=0L
 override fun onData(data:ByteBuffer,bits:Int,rate:Int,channels:Int,frames:Int,timestamp:Long){if(bits!=16)return;val b=data.duplicate().order(ByteOrder.LITTLE_ENDIAN);var power=0.0;var count=0;var crossings=0;var prev=0.0;while(b.remaining()>=2){val x=b.short.toDouble()/32768;power+=x*x;if(count>0&&(x>0)!=(prev>0))crossings++;prev=x;count++};if(count==0)return;val z=crossings.toDouble()/count;voiced=if(sqrt(power/count)>0.008&&z>0.005&&z<0.45)voiced+frames.toDouble()/rate else 0.0;val speech=voiced>=0.06
 scope.launch{if(gate.canCapture(now())&&speech){gate.lastSpeech=now();if(now()-logged>250){logged=now();event("last_qualifying_speech")}}}
 }}
 private inner class RemotePCM:AudioTrackSink {private var first=true;override fun onData(data:ByteBuffer,bits:Int,rate:Int,channels:Int,frames:Int,timestamp:Long){if(first){first=false;event("remote_first_pcm")}}}
 override fun onPause(){release();super.onPause()}
 override fun onDestroy(){halt("destroy",true);poll?.cancel();room?.disconnect();room?.release();scope.cancel();super.onDestroy()}
}
