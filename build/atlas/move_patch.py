# Your letters on another device (28 September 2026). Companions, sparks and your own valley used to live only in
# one browser. Now a private link carries them to another phone or computer. Your valley's world itself is kept on
# the world server, so the new device picks it up from there, and whichever device has it open is its keeper.
# Run from assemble.py via exec(), after living_patch.py.

# a valley owner also gets the server's copy of their valley, and starts from whichever copy lived last
rep('if(!started){if(m.keeper){W.keeper=true;if(!m.hasSnap||W.mode==="mine")onWelcome&&onWelcome(W.mode==="mine"?"mine":"new");}else if(W.mode==="mine"){W.mirror=true;onWelcome&&onWelcome("mine");}',
    'if(!started){if(m.keeper){W.keeper=true;if(!m.hasSnap)onWelcome&&onWelcome(W.mode==="mine"?"mine":"new");}else if(W.mode==="mine"){W.mirror=true;if(!m.hasSnap)onWelcome&&onWelcome("mine");}')
rep('const raw=WORLD.on&&!WORLD.own?WORLD.snapText:localStorage.getItem(SAVE_KEY);',
    'const raw=WORLD.on&&!WORLD.own?WORLD.snapText:WORLD.on&&WORLD.own?ownValleyText():localStorage.getItem(SAVE_KEY);')

MOVE_JS = r'''
const MOVE_ME="letterheads_valley_me";
// The owner's valley: this device's saved copy, or the server's copy when that one lived later (another device of
// the owner kept it since), with this person's own companions and settings kept either way.
function ownValleyText(){const local=localStorage.getItem(SAVE_KEY),snap=WORLD.snapText;if(!snap)return local;
  let L=null,R=null;try{L=local&&JSON.parse(local);}catch(e){}try{R=JSON.parse(snap);}catch(e){}if(!R||!R.S)return local;
  if(L&&L.S&&(L.S.livedAt||0)>=(R.S.livedAt||0)&&L.S.created===R.S.created)return local;
  let me=null;try{me=JSON.parse(localStorage.getItem(MOVE_ME)||"null");}catch(e){}
  const src=L&&L.S&&L.S.created===R.S.created?L.S:me||{};
  R.S.visitor=Object.assign({adopted:[],gifts:1,standing:0,deeds:[],lastUse:{},tier:0,sparks:5,sparkLog:[],rep:4,repN:0,repLog:[]},src.visitor||{});
  R.S.settings=Object.assign({camera:"director",reduce:false,night:true,sound:false,vol:.6},src.settings||{});
  R.S.visitor.adopted=(R.S.visitor.adopted||[]).filter(id=>R.S.agents.some(a=>a.id===id));
  return JSON.stringify({S:R.S,nextId:R.nextId||5000});}
async function b64pack(obj){const s=JSON.stringify(obj);let bytes;
  if(window.CompressionStream)bytes=new Uint8Array(await new Response(new Blob([s]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer());else bytes=new TextEncoder().encode(s);
  let bin="";for(const b of bytes)bin+=String.fromCharCode(b);return(window.CompressionStream?"z":"p")+btoa(bin).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");}
async function b64unpack(t){const kind=t[0];const bin=atob(t.slice(1).replace(/-/g,"+").replace(/_/g,"/"));const u=Uint8Array.from(bin,c=>c.charCodeAt(0));
  const s=kind==="z"?await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream("gzip"))).text():new TextDecoder().decode(u);return JSON.parse(s);}
const trimVisitor=v=>v&&{...v,deeds:(v.deeds||[]).slice(0,30),sparkLog:(v.sparkLog||[]).slice(0,20),repLog:(v.repLog||[]).slice(0,20)};
async function moveLink(){const get=k=>{try{return JSON.parse(localStorage.getItem(k)||"null");}catch(e){return null;}};
  const me=get("letterheads_me_v1"),valley=WORLD.my();let vme=null;
  if(valley){const own=WORLD.own&&S?{visitor:S.visitor,settings:S.settings}:(get(SAVE_KEY)||{}).S;if(own)vme={visitor:trimVisitor(own.visitor),settings:own.settings};}
  const data={v:1,at:Date.now(),me:me&&{visitor:trimVisitor(me.visitor),settings:me.settings},valley,vme};
  return location.origin+"/play/#move="+await b64pack(data);}
function moveSection(){return`<h3>On another device</h3><p class="muted">Your companions, sparks and your own valley are kept in this browser. A private link moves them to your phone or another computer.</p>
  <div class="actions"><button id="mvMake">Make a link to move them</button></div><p class="vlink" id="mvLink" hidden></p><p class="muted" id="mvOut" aria-live="polite"></p>`;}
function bindMove(){const b=document.getElementById("mvMake");if(!b)return;b.onclick=async()=>{const u=await moveLink();const el=document.getElementById("mvLink");el.textContent=u;el.hidden=false;
  let copied=false;try{await navigator.clipboard.writeText(u);copied=true;}catch(e){}
  document.getElementById("mvOut").textContent=(copied?"Copied. ":"")+"Open this link on the other device. Keep it to yourself: anyone who opens it gets your letters and your valley.";};}
// arriving with a move link: say what will move, and move it only when the person says so
async function takeMove(){const m=/^#move=([A-Za-z0-9_-]+)$/.exec(location.hash);if(!m)return;let d=null;try{d=await b64unpack(m[1]);}catch(e){}
  history.replaceState(null,"",location.pathname+location.search);if(!d||d.v!==1)return;
  const n=(d.me&&d.me.visitor&&d.me.visitor.adopted||[]).length,vn=d.valley&&d.valley.id?`${d.valley.name||"your"}${d.valley.name?"'s":""} valley`:null;
  const mine=WORLD.my(),clash=d.valley&&mine&&mine.id!==d.valley.id,hasOwn=!!localStorage.getItem(SAVE_KEY);
  const yes=await new Promise(res=>{openSheet(`<h2 id="sheetTitle">Move your letters here?</h2><p class="muted">From your other device: ${n} companion${n===1?"":"s"} in The World${vn?`, and ${esc(vn)}`:""}. They replace whatever this browser has.${(clash||(!mine&&d.valley&&hasOwn))?" This browser's own valley is kept aside, not deleted.":""}</p>
    <div class="actions"><button class="main" id="mvYes">Move them here</button><button id="mvNo">Not now</button></div>`,"move");
    document.getElementById("mvYes").onclick=()=>res(true);document.getElementById("mvNo").onclick=()=>res(false);document.getElementById("sheetClose").addEventListener("click",()=>res(false),{once:true});});
  if(!yes){closeSheet();return;}
  try{if(d.me)localStorage.setItem("letterheads_me_v1",JSON.stringify(d.me));
    if(d.valley&&d.valley.id&&d.valley.token){if(!mine||mine.id!==d.valley.id){const old=localStorage.getItem(SAVE_KEY);if(old)localStorage.setItem(SAVE_KEY+"_kept_"+Date.now(),old);localStorage.removeItem(SAVE_KEY);}
      localStorage.setItem("letterheads_valley_v1",JSON.stringify(d.valley));if(d.vme)localStorage.setItem(MOVE_ME,JSON.stringify(d.vme));}}catch(e){}
  location.replace("/play/"+(params.get("world")?"?world="+encodeURIComponent(params.get("world")):""));await new Promise(()=>{});}
'''
rep('function save(){if(WORLD.remote)return;', MOVE_JS + '\nfunction save(){if(WORLD.remote)return;')
rep('W.join=async()=>{if(params.has("solo"))return;', 'W.join=async()=>{await takeMove();if(params.has("solo"))return;')
rep('<h3>Valleys open around the world</h3>', '${moveSection()}<h3>Valleys open around the world</h3>')
rep('fetchValleys().then(l=>{const el=document.getElementById("vList");', 'bindMove();fetchValleys().then(l=>{const el=document.getElementById("vList");')

rep('your companions are remembered on this device.', 'your companions are kept in this browser, and Valleys can move them to another device.')
rep('"The world lives while this page is open and is saved only in this browser: no accounts, no ads, no tracking."', '"The world keeps living while this page is closed, and is saved only in this browser: no accounts, no ads, no tracking."')
