package ai.slimy.slimetalk.feasibility
class PTTGate {
 enum class State { IDLE,REQUESTING,AUTHORIZED_PREPARING,TRANSMITTING,BUSY,WAIT_FOR_RELEASE,DISCONNECTED }
 var state=State.DISCONNECTED; var held=false;var epoch:Long?=null;var deadline=0L;var lastSpeech=0L;var generation=0;var capture=false
 fun connected(){if(!held)state=State.IDLE}
 fun press():Boolean {if(held || state !in listOf(State.IDLE,State.BUSY))return false;held=true;generation++;state=State.REQUESTING;return true}
 fun grant(e:Long,sent:Long,now:Long):Boolean {if(!held||state!=State.REQUESTING||now>=sent+2000)return false;epoch=e;deadline=sent+2000;state=State.AUTHORIZED_PREPARING;return true}
 fun renew(sent:Long,now:Long):Boolean {if(epoch==null||now>=deadline||now>=sent+2000)return false;deadline=sent+2000;return true}
 fun canCapture(now:Long)=held&&epoch!=null&&now<deadline&&state in listOf(State.AUTHORIZED_PREPARING,State.TRANSMITTING)
 fun captureStarted(now:Long){capture=true;lastSpeech=now}
 fun stop(disconnected:Boolean=false){generation++;epoch=null;capture=false;state=if(held)State.WAIT_FOR_RELEASE else if(disconnected)State.DISCONNECTED else State.IDLE}
 fun release(connected:Boolean){held=false;stop(!connected)}
 fun expiry(now:Long):String?=if(epoch!=null&&now>=deadline)"authorization_loss" else if(capture&&now-lastSpeech>=3000)"silence_expiry" else null
}
