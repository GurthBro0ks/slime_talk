import {randomBytes, randomUUID, createHash, timingSafeEqual} from 'node:crypto';
export const ROOM = 'slime-talk-feasibility';
export const CHANNEL = '838d72ab-e627-4e79-90a4-884f9e3d7bad';
export class Rejected extends Error { constructor(code=403) { super('rejected'); this.code=code; } }
const digest = s => createHash('sha256').update(s).digest();
// All mutations, including remote permission changes, are serialized. Failed
// revocation leaves the owner in place and blocks every subsequent grant.
export class Controller {
  constructor({devices, media, wake=async()=>{}, clock=()=>performance.now(), log=()=>{}}) {
    this.devices=devices; this.media=media; this.wake=wake; this.clock=clock; this.log=log;
    this.sessions=new Map(); this.owner=null; this.epoch=0; this.queue=Promise.resolve();
  }
  serial(fn) { const p=this.queue.then(fn); this.queue=p.catch(()=>{}); return p; }
  session(token) { const s=this.sessions.get(digest(token).toString('hex')); if(!s || s.expiry<=this.clock()) throw new Rejected(401); s.expiry=this.clock()+3600000; return s; }
  async login(device, key) { return this.serial(async()=>{
    if(!Object.hasOwn(this.devices,device) || typeof key!=='string' || !timingSafeEqual(digest(key),digest(this.devices[device]))) throw new Rejected(401);
    for(const [id,s] of this.sessions) if(s.device===device) { if(this.owner?.identity===s.identity) await this.clear('session_invalidated'); await this.media.remove(s.identity); this.sessions.delete(id); }
    const token=randomBytes(32).toString('base64url'); const s={device,identity:randomUUID(),expiry:this.clock()+3600000,push:null,requests:new Set()};
    this.sessions.set(digest(token).toString('hex'),s);
    return {session:token,device,channel:CHANNEL,...await this.media.token(s.identity),clientLeaseMs:2000};
  }); }
  async clear(reason) {
    if(!this.owner)return;
    const old=this.owner;
    await this.media.permission(old.identity,false); // fail closed on any uncertain response
    this.owner=null; this.log(reason,{epoch:old.epoch});
  }
  async sweep() { if(this.owner && this.owner.until<=this.clock()) await this.clear('lease_expiry'); }
  async request(token, requestId) { return this.serial(async()=>{
    const s=this.session(token); await this.sweep(); this.log('request_received',{});
    if(typeof requestId!=='string'||! /^[a-f0-9-]{36}$/.test(requestId)) throw new Rejected(400);
    if(s.requests.has(requestId))throw new Rejected(409);s.requests.add(requestId);
    if(s.requests.size>10000)throw new Rejected(401);
    if(this.owner) { this.log('deny',{epoch:this.owner.epoch}); return {granted:false}; }
    const epoch=++this.epoch;
    // Reserve before remote mutation. A timeout/error must NOT allow another owner.
    this.owner={identity:s.identity,device:s.device,epoch,requestId,until:this.clock()+4000};
    try { await this.media.permission(s.identity,true); }
    catch(e) { this.owner.until=0; throw e; }
    this.owner.until=this.clock()+4000;
    this.log('grant',{epoch,leaseMs:4000});
    for(const target of this.sessions.values()) if(target.identity!==s.identity && target.push) {
      this.wake(target.push,{epoch,speaker:s.device}).catch(()=>this.log('apns_failed',{epoch}));
    }
    return {granted:true,epoch,clientLeaseMs:2000};
  }); }
  async renew(token,epoch) { return this.serial(async()=>{
    const s=this.session(token); await this.sweep();
    if(!this.owner || this.owner.identity!==s.identity || this.owner.epoch!==epoch)throw new Rejected(409);
    this.owner.until=this.clock()+4000; this.log('lease_renew',{epoch,leaseMs:4000}); return {epoch,clientLeaseMs:2000};
  }); }
  async release(token,epoch) { return this.serial(async()=>{
    const s=this.session(token); await this.sweep();
    if(!this.owner)return {released:true};
    if(this.owner.identity!==s.identity||this.owner.epoch!==epoch)throw new Rejected(409);
    await this.clear('release'); return {released:true};
  }); }
  async status(token) { return this.serial(async()=>{this.session(token);await this.sweep();return {busy:!!this.owner,owner:this.owner?.device??null,epoch:this.owner?.epoch??null};}); }
  async push(token,value) { return this.serial(async()=>{const s=this.session(token);if(s.device!=='iphone'||typeof value!=='string'||! /^[0-9a-f]{32,512}$/.test(value))throw new Rejected(400);s.push=value;return {registered:true};}); }
  async tick(){return this.serial(async()=>{await this.sweep();for(const [id,s] of this.sessions)if(s.expiry<=this.clock()&&this.owner?.identity!==s.identity)this.sessions.delete(id);});}
}
