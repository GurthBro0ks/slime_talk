import http from 'node:http';
import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {Controller,Rejected} from './core.mjs';
import {mediaAdapter,apnsAdapter} from './adapters.mjs';
export function serverFor(core){
 const rate=new Map();
 return http.createServer(async(req,res)=>{
   res.setHeader('Content-Type','application/json');res.setHeader('Cache-Control','no-store');
   try{
     if(req.method!=='POST')throw new Rejected(405);
     const bucket=Math.floor(Date.now()/1000), key=req.socket.remoteAddress;let limit=rate.get(key);if(!limit||limit.bucket!==bucket)limit={bucket,n:0};rate.set(key,limit);if(++limit.n>40)throw new Rejected(429);if(rate.size>1000)rate.clear();
     let size=0,chunks=[];for await(const chunk of req){size+=chunk.length;if(size>4096)throw new Rejected(413);chunks.push(chunk);}let body;try{body=JSON.parse(Buffer.concat(chunks).toString());}catch{throw new Rejected(400);}
     const token=(req.headers.authorization??'').replace(/^Bearer /,'');let answer;
     switch(req.url){case '/login':answer=await core.login(body.device,body.key);break;case '/request':answer=await core.request(token,body.requestId);break;case '/renew':answer=await core.renew(token,body.epoch);break;case '/release':answer=await core.release(token,body.epoch);break;case '/status':answer=await core.status(token);break;case '/push':answer=await core.push(token,body.token);break;default:throw new Rejected(404);}
     res.end(JSON.stringify(answer));
   }catch(e){res.statusCode=e instanceof Rejected?e.code:503;res.end(JSON.stringify({error:res.statusCode}));}
 });
}
if(import.meta.url===pathToFileURL(process.argv[1]).href){
 const env=process.env;const devices=JSON.parse(readFileSync(env.DEVICE_KEYS_FILE,'utf8'));for(const [name,key]of Object.entries(devices))if(!['pixel','iphone'].includes(name)||typeof key!=='string'||key.length<32)throw Error('invalid device configuration');
 const log=(event,fields)=>console.log(JSON.stringify({time:new Date().toISOString(),mono_ms:Math.round(performance.now()),event,...fields}));
 const media=mediaAdapter(env);await media.reset();
 const core=new Controller({devices,media,wake:apnsAdapter(env,log),log});
 setInterval(()=>core.tick().catch(()=>log('revoke_failed',{})),100).unref();
 const server=serverFor(core);server.requestTimeout=4000;server.headersTimeout=5000;server.listen(8787,'127.0.0.1',()=>log('listening',{}));
}
