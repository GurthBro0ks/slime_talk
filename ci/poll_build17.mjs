import {createPrivateKey, sign} from 'node:crypto';
import {setTimeout as sleep} from 'node:timers/promises';
const app='6816454718', bundle='ai.slimy.slimetalk.feasibility';
const safe=v=>typeof v==='string' && /^[A-Za-z0-9_.:+ -]{1,160}$/.test(v)?v:'unknown';
const out=(k,v)=>console.log(k+'='+v);
try {
 const key=createPrivateKey(process.env.ASC_API_KEY_P8);
 if(key.asymmetricKeyType!=='ec'||key.asymmetricKeyDetails?.namedCurve!=='prime256v1')throw Error();
 const enc=v=>Buffer.from(JSON.stringify(v)).toString('base64url');
 async function get(path){
  const u=new URL(path,'https://api.appstoreconnect.apple.com');
  if(u.origin!=='https://api.appstoreconnect.apple.com'||!u.pathname.startsWith('/v1/'))throw Error();
  const now=Math.floor(Date.now()/1000);
  const raw=enc({alg:'ES256',kid:process.env.ASC_KEY_ID,typ:'JWT'})+'.'+enc({iss:process.env.ASC_ISSUER_ID,iat:now,exp:now+120,aud:'appstoreconnect-v1',scope:['GET '+u.pathname+u.search]});
  const jwt=raw+'.'+sign('sha256',Buffer.from(raw),{key,dsaEncoding:'ieee-p1363'}).toString('base64url');
  const r=await fetch(u,{method:'GET',redirect:'error',headers:{Authorization:'Bearer '+jwt,Accept:'application/json'},signal:AbortSignal.timeout(20000)});
  const body=await r.json();
  if(!r.ok){
   out('APPLE_HTTP_STATUS',r.status);
   const errors=Array.isArray(body.errors)?body.errors:[];
   out('OWNER_ACTION_REQUIRED',errors.some(e=>/agreement|legal|contract|export|encryption|attestation|content.rights|billing/i.test(String(e.detail))));
   throw Error();
  }
  return body;
 }
 const a=await get('/v1/apps/'+app);
 if(a.data?.id!==app||a.data?.attributes?.bundleId!==bundle)throw Error();
 out('APP_ID_MATCH','yes');
 const deadline=Date.now()+20*60*1000;
 let found=false,usable=false,processing='unknown';
 for(let attempt=0;Date.now()<deadline;attempt++){
  const data=await get('/v1/builds?filter[app]='+app+'&filter[version]=17&include=preReleaseVersion,buildBetaDetail&limit=200');
  if(!Array.isArray(data.data)||data.links?.next)throw Error();
  const matches=data.data.filter(b=>String(b.attributes?.version)==='17' && (data.included??[]).some(x=>x.type==='preReleaseVersions'&&x.id===b.relationships?.preReleaseVersion?.data?.id&&x.attributes?.version==='0.1.0'));
  if(matches.length>1)throw Error();
  found=matches.length===1;
  out('POLL_TIMESTAMP_UTC',new Date().toISOString());
  out('BUILD_17_FOUND',found?'yes':'no');
  out('BUILD_RESOURCE_ID',found?safe(matches[0].id):'none');
  if(found){
   const b=matches[0];
   const beta=(data.included??[]).find(x=>x.type==='buildBetaDetails'&&x.id===b.relationships?.buildBetaDetail?.data?.id);
   processing=safe(b.attributes?.processingState);
   const internal=safe(beta?.attributes?.internalBuildState);
   out('BUILD_PROCESSING_STATE',processing);
   out('INTERNAL_BUILD_STATE',internal);
   out('TESTFLIGHT_VISIBILITY','server_record_found; UI_not_checked');
   if(/EXPORT|COMPLIANCE|ENCRYPTION/.test(internal)){
    out('OWNER_ACTION_REQUIRED','yes; inspect exact Apple question privately');
    throw Error();
   }
   usable=processing==='VALID'&&b.attributes?.expired===false&&['READY_FOR_BETA_TESTING','IN_BETA_TESTING'].includes(internal);
   if(usable||['FAILED','INVALID'].includes(processing))break;
  }else{
   out('BUILD_PROCESSING_STATE','unknown');
   out('TESTFLIGHT_VISIBILITY','no_server_build_record; UI_not_checked');
  }
  const remaining=deadline-Date.now();
  if(remaining<=60000)break;
  await sleep(60000);
 }
 out('DISTRIBUTION_RESULT',usable?'PASS':found&&processing==='PROCESSING'?'PARTIAL; still_processing':'BLOCKED; no_usable_build; no_further_retry; Apple_support_escalation');
 if(!usable)process.exitCode=1;
} catch {
 out('DISTRIBUTION_RESULT','BLOCKED; read_or_owner_action_required; sensitive_details_suppressed; no_retry');
 process.exitCode=1;
}
