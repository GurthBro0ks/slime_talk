import {createHmac,createPrivateKey,sign} from 'node:crypto';
import {readFileSync} from 'node:fs';
import http2 from 'node:http2';
import {ROOM} from './core.mjs';
const b64=o=>Buffer.from(JSON.stringify(o)).toString('base64url');
export function livekitJWT(key,secret,identity,video,ttl=60){const now=Math.floor(Date.now()/1000);const body=b64({alg:'HS256',typ:'JWT'})+'.'+b64({iss:key,sub:identity,iat:now,nbf:now-5,exp:now+ttl,video});return body+'.'+createHmac('sha256',secret).update(body).digest('base64url');}
export function mediaAdapter(env){
 const url=new URL(env.LIVEKIT_URL);if(url.protocol!=='wss:')throw Error('invalid media configuration');const origin='https://'+url.host;
 const jwt=(id,video)=>livekitJWT(env.LIVEKIT_API_KEY,env.LIVEKIT_API_SECRET,id,video);
 async function rpc(method,body){const r=await fetch(origin+'/twirp/livekit.RoomService/'+method,{method:'POST',headers:{Authorization:'Bearer '+jwt('controller',{roomAdmin:true,room:ROOM,roomList:true}), 'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(2500)});if(!r.ok){if(r.status===404&&method==='RemoveParticipant')return {};if(r.status===404&&method==='ListParticipants')return {participants:[]};throw Error('media operation failed');}return r.json();}
 return {
   token:async identity=>({url:env.LIVEKIT_URL,token:jwt(identity,{roomJoin:true,room:ROOM,canSubscribe:true,canPublish:false,canPublishData:false})}),
   permission:async(identity,allow)=>rpc('UpdateParticipant',{room:ROOM,identity,permission:{canSubscribe:true,canPublish:allow,canPublishData:false,canPublishSources:[2]}}),
   remove:identity=>rpc('RemoveParticipant',{room:ROOM,identity}),
   reset:async()=>{try{const r=await rpc('ListParticipants',{room:ROOM});for(const p of r.participants??[])await rpc('RemoveParticipant',{room:ROOM,identity:p.identity});}catch(e){throw e;}},
 };
}
export function apnsAdapter(env,log){
 const privateKey=createPrivateKey(readFileSync(env.APNS_KEY_FILE));
 return async(token,payload)=>{
 const now=Math.floor(Date.now()/1000);const body=b64({alg:'ES256',kid:env.APNS_KEY_ID})+'.'+b64({iss:env.APPLE_TEAM_ID,iat:now});const jwt=body+'.'+sign('sha256',Buffer.from(body),{key:privateKey,dsaEncoding:'ieee-p1363'}).toString('base64url');
 await new Promise((resolve,reject)=>{const client=http2.connect('https://api.push.apple.com');let done=false;
 const finish=(ok)=>{if(done)return;done=true;clearTimeout(timer);client.close();ok?resolve():reject(Error('apns failed'));};
 const timer=setTimeout(()=>{client.destroy();finish(false);},2500);client.on('error',()=>finish(false));
 const req=client.request({':method':'POST',':path':'/3/device/'+token,authorization:'bearer '+jwt,'apns-topic':'ai.slimy.slimetalk.feasibility.voip-ptt','apns-push-type':'pushtotalk','apns-priority':'10','apns-expiration':'0'});
 req.on('response',headers=>{log('apns_response',{status:headers[':status'],epoch:payload.epoch});finish(headers[':status']===200);});req.on('error',()=>finish(false));req.on('data',()=>{});req.end(JSON.stringify({aps:{'content-available':1},...payload}));
 });
 };
}
