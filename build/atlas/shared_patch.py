# One shared world (28 September 2026). When the world server is reachable, everyone at letterheads.live sees the
# same world. One visitor's browser, the "keeper", runs the simulation and sends it to the server; everyone else is a
# "watcher" that draws the world it receives, smoothly, and sends its help to the keeper, which acts on it and answers.
# Each person's own things (companions, sparks, standing, settings) stay on their own device, never in the world.
# If the server can't be reached, or with ?solo, the game falls back to a private world saved in this browser.
# The server lives in world/ (a Cloudflare Worker). Its address comes from /world.json or ?world=wss://...
# Run from assemble.py via exec(), after growth_patch.py.

# ---- the start waits to join the world
rep('terraLoad().then(()=>{\nresize();const loadedExisting=load();\nif(!loadedExisting){genWorld();newWorld();S.place=MAP.key;S.placeHome={x:HOME.x,y:HOME.y};}',
    'terraLoad().then(()=>WORLD.join()).then(()=>{\nresize();const loadedExisting=load();\nif(!loadedExisting){genWorld();newWorld();S.place=MAP.key;S.placeHome={x:HOME.x,y:HOME.y};if(WORLD.on)WORLD.personal();}')
rep('buildTerrain();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{if(MAP.place==null)','if(WORLD.on)WORLD.started();buildTerrain();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{if(MAP.place==null)')

# ---- saving: in the shared world only your own things are saved here; the world itself lives on the server
rep('function save(){try{', 'function save(){if(WORLD.remote)return;if(WORLD.on){WORLD.savePersonal();return;}try{')
rep('const raw=localStorage.getItem(SAVE_KEY);', 'const raw=WORLD.on?WORLD.snapText:localStorage.getItem(SAVE_KEY);')
rep('S=d.S;nextId=d.nextId||5000;', 'S=d.S;nextId=d.nextId||5000;if(WORLD.on){WORLD.personal();if(d.stories)stories=d.stories;}')

# ---- the frame: watchers draw what they receive; nobody can speed up or slow down the shared world
rep('acc+=dtReal*SPEED*(fxOn?.35:1);let n=0;while(acc>=.1&&n<80){step(.1);acc-=.1;n++;}',
    'if(WORLD.mirror){WORLD.glide(dtReal);acc=0;}else{acc+=dtReal*(WORLD.on?1:SPEED*(fxOn?.35:1));let n=0;while(acc>=.1&&n<80){step(.1);acc-=.1;n++;}}')
rep('if(!tour&&!ATL.on&&tAnim>(director.nextPlace||0)){director.nextPlace=tAnim+4;relocate();}',
    'if(!tour&&!ATL.on&&tAnim>(director.nextPlace||0)){director.nextPlace=tAnim+4;if(!WORLD.mirror)relocate();}if(WORLD.on)WORLD.visitorTick();')
rep('${S.agents.length} letters · ${nw} word${nw===1?"":"s"}',
    '${S.agents.length} letters · ${nw} word${nw===1?"":"s"}${WORLD.on?(WORLD.down?" · reconnecting":" · "+WORLD.n+(WORLD.n===1?" person":" people")+" here"):""}')

# ---- your companions' troubles are yours: this part of the day runs on every device for its own person
i0=s.index('if(S.simT>=(S.neglectAt||0))');i1=s.index('else a.neglect=0;}}',i0)+len('else a.neglect=0;}}')
block=s[i0:i1]
s=s[:i0]+'if(!WORLD.on)'+block+s[i1:]
vt=block.replace('if(S.simT>=(S.neglectAt||0)){S.neglectAt=S.simT+30;','if(tAnim>=(VT.at||0)){VT.at=tAnim+30;')
vt=vt.replace('(a.lastAskV||0)','(VT.ask[a.id]||0)').replace('a.lastAskV=Date.now()','VT.ask[a.id]=Date.now()')
vt=vt.replace('(a.lastWave||0)','(VT.wave[a.id]||0)').replace('a.lastWave=Date.now()','VT.wave[a.id]=Date.now()')
vt=vt.replace('(a.lastNeglect||0)','(VT.lastNeg[a.id]||0)').replace('a.lastNeglect=Date.now()','VT.lastNeg[a.id]=Date.now()')
vt=vt.replace('a.neglect=(a.neglect||0)+30;if(a.neglect>=120','VT.neg[a.id]=(VT.neg[a.id]||0)+30;if(VT.neg[a.id]>=120').replace('a.neglect=0;','VT.neg[a.id]=0;')
assert 'a.neglect' not in vt and 'S.neglectAt' not in vt

# ---- help, ideas, adoption and gifts become commands that the keeper carries out
def cut(start,end,include_end=True):
    global s
    i=s.index(start);j=s.index(end,i)+(len(end) if include_end else 0);body=s[i:j];return i,j,body

# offer help
i,j,body=cut('out.querySelectorAll("[data-k]").forEach(b=>b.onclick=()=>{','});}\nfunction suggestLetters',False)
inner=body[len('out.querySelectorAll("[data-k]").forEach(b=>b.onclick=()=>{'):]
inner=inner.replace('const res=out.querySelector("[data-res]");','').replace('b.dataset.free','args.free').replace('b.dataset.k','args.k')
CMDS='CMD.help=(a,args,res)=>{if(!["water","fruit","rest","tend","friend"].includes(args.k))return;'+inner+'};\n'
s=s[:i]+'out.querySelectorAll("[data-k]").forEach(b=>b.onclick=()=>{WX("help",a,{k:b.dataset.k,free:b.dataset.free?1:0},out.querySelector("[data-res]"))'+s[j:]

# share an idea
i,j,body=cut('out.querySelectorAll("[data-idea]").forEach(b=>b.onclick=()=>{','save();});}\nfunction useAbility',False)
inner=body[len('out.querySelectorAll("[data-idea]").forEach(b=>b.onclick=()=>{'):]+'save();'
inner=inner.replace('const c=b.dataset.idea;const res=out.querySelector("[data-ires]");','const c=args.c;if(!CONCEPTS[c]||!S.firsts[c]||knows(a,c))return;')
CMDS+='CMD.idea=(a,args,res)=>{'+inner+'};\n'
s=s[:i]+'out.querySelectorAll("[data-idea]").forEach(b=>b.onclick=()=>WX("idea",a,{c:b.dataset.idea},out.querySelector("[data-ires]")));}'+s[j+len('save();});}'):]

# abilities
i,j,body=cut('function useAbility(id,a){if(!a)return;if(id==="idea"){ideaFlow(a);return;}const out=sheetBody.querySelector(`[data-out="${a.id}"]`);','\nfunction ',False)
inner=body[len('function useAbility(id,a){if(!a)return;if(id==="idea"){ideaFlow(a);return;}const out=sheetBody.querySelector(`[data-out="${a.id}"]`);'):]
assert inner.endswith('}')
CMDS+='CMD.ability=(a,args,out)=>{const id=args.id;if(!ABIL.some(x=>x.id===id)||id==="idea")return;'+inner[:-1]+'};\n'
s=s[:i]+'function useAbility(id,a){if(!a)return;if(id==="idea"){ideaFlow(a);return;}WX("ability",a,{id},sheetBody.querySelector(`[data-out="${a.id}"]`),()=>setTimeout(()=>renderDashboard(true),1500));}'+s[j:]

# adopt
old='document.querySelectorAll("#helpArea [data-n]").forEach(b=>b.onclick=()=>{const old=a.name;a.name=b.dataset.n;S.visitor.adopted.push(a.id);remember(a,"A visitor from beyond chose to be my companion.",true);chron(`A visitor adopted ${old}${old!==a.name?", now called "+a.name:""}.`,"people");save();openDashboard();});}'
rep(old,'document.querySelectorAll("#helpArea [data-n]").forEach(b=>b.onclick=()=>WX("adopt",a,{n:b.dataset.n},null,()=>openDashboard()));}')
CMDS+='CMD.adopt=(a,args,out)=>{if(S.visitor.adopted.includes(a.id)||S.visitor.adopted.length>=3)return;let n=String(args.n||"");if(n!==a.name&&(!NAMES.includes(n)||a.renamed))n=a.name;const old=a.name;if(n!==old)a.renamed=1;a.name=n;S.visitor.adopted.push(a.id);remember(a,"A visitor from beyond chose to be my companion.",true);chron(`A visitor adopted ${old}${old!==a.name?", now called "+a.name:""}.`,"people");save();};\n'

# let a companion go
old='''sheetBody.querySelectorAll("[data-letgo]").forEach(b=>b.onclick=()=>{const a=agentById(+b.dataset.letgo);if(!a||!confirm(`Let ${a.name} go? ${a.name} will remember, and other letters will hear of it.`))return;
    S.visitor.adopted=S.visitor.adopted.filter(id=>id!==a.id);emote(a,"grief",10);a.sad=Math.min(1,a.sad+.5);remember(a,"The visitor who adopted me let me go.",true);(S.visitor.trustIn=S.visitor.trustIn||{})[a.id]=-.5;
    rateVisitor(1,`You let ${a.name} go`,2);S.visitor.standing-=3;S.visitor.deeds.unshift({t:Date.now(),delta:-3,text:`You let ${a.name} go`});chron(`A visitor let ${a.name} go.`,"people");save();renderDashboard(true);});'''
rep(old,'''sheetBody.querySelectorAll("[data-letgo]").forEach(b=>b.onclick=()=>{const a=agentById(+b.dataset.letgo);if(!a||!confirm(`Let ${a.name} go? ${a.name} will remember, and other letters will hear of it.`))return;WX("letgo",a,{},null,()=>renderDashboard(true));});''')
CMDS+='''CMD.letgo=(a,args,out)=>{if(!S.visitor.adopted.includes(a.id))return;S.visitor.adopted=S.visitor.adopted.filter(id=>id!==a.id);emote(a,"grief",10);a.sad=Math.min(1,a.sad+.5);remember(a,"The visitor who adopted me let me go.",true);(S.visitor.trustIn=S.visitor.trustIn||{})[a.id]=-.5;
    rateVisitor(1,`You let ${a.name} go`,2);S.visitor.standing-=3;S.visitor.deeds.unshift({t:Date.now(),delta:-3,text:`You let ${a.name} go`});chron(`A visitor let ${a.name} go.`,"people");save();};\n'''

# bring a letter (from Your letters, and from Join)
old='''sheetBody.querySelectorAll("#giftRow [data-c]").forEach(b=>b.onclick=()=>{const c=b.dataset.c;if(S.visitor.gifts>0)S.visitor.gifts--;else if(!spend(GIFT_COST,`Brought a new ${c}`))return;const x=makeAgent(c,REFUGE.x+(rnd()-.5)*60,REFUGE.y+30,Date.now(),false);S.agents.push(x);remember(x,"I arrived at the Hearth refuge, brought by a visitor.");
    chron(`A new ${c} named ${x.name} arrived at the Hearth refuge, brought by a visitor.`,"people");addStory({kind:"arrival",ids:[x.id],text:`${x.name}, a new ${c}, has arrived at the refuge.`,sub:"Where will they choose to belong?",score:72,dur:20,main:x.id});Music.birth();save();renderDashboard(true);});'''
rep(old,'''sheetBody.querySelectorAll("#giftRow [data-c]").forEach(b=>b.onclick=()=>WX("gift",null,{c:b.dataset.c},null,()=>renderDashboard(true)));''')
old='''sheetBody.querySelectorAll("#giftRow [data-c]").forEach(b=>b.onclick=()=>{const c=b.dataset.c;const x=makeAgent(c,REFUGE.x+(rnd()-.5)*60,REFUGE.y+30,Date.now(),false);S.agents.push(x);S.visitor.gifts--;remember(x,"I arrived at the Hearth refuge, brought by a visitor.");chron(`A new ${c} named ${x.name} arrived at the Hearth refuge, brought by a visitor.`,"people");addStory({kind:"arrival",ids:[x.id],text:`${x.name}, a new ${c}, has arrived at the refuge.`,sub:"Where will they choose to belong?",score:72,dur:20,main:x.id});Music.birth();save();closeSheet();});'''
rep(old,'''sheetBody.querySelectorAll("#giftRow [data-c]").forEach(b=>b.onclick=()=>WX("gift",null,{c:b.dataset.c},null,()=>closeSheet()));''')
CMDS+='''CMD.gift=(a,args,out)=>{const c=String(args.c||"");if(!/^[A-Z]$/.test(c)||(LATE[c]&&!S.lateBorn?.[c])||S.agents.length>=72){out.textContent="The refuge is full right now.";return;}
  if(WORLD.remote){const k=WORLD.from;if(Date.now()-(WORLD.giftAt[k]||0)<300000){out.textContent="One new letter every five minutes, please.";return;}WORLD.giftAt[k]=Date.now();}
  if(S.visitor.gifts>0)S.visitor.gifts--;else if(!spend(GIFT_COST,`Brought a new ${c}`))return;const x=makeAgent(c,REFUGE.x+(rnd()-.5)*60,REFUGE.y+30,Date.now(),false);S.agents.push(x);remember(x,"I arrived at the Hearth refuge, brought by a visitor.");
  chron(`A new ${c} named ${x.name} arrived at the Hearth refuge, brought by a visitor.`,"people");addStory({kind:"arrival",ids:[x.id],text:`${x.name}, a new ${c}, has arrived at the refuge.`,sub:"Where will they choose to belong?",score:72,dur:20,main:x.id});Music.birth();save();};\n'''

# ---- words for a shared world
rep('Joining is free, needs no account, and lives only on this device.',
    '${WORLD.on?"Everyone at letterheads.live shares this one world. Joining is free and needs no account; your companions are remembered on this device.":"Joining is free, needs no account, and lives only on this device."}')
rep('The world lives while this page is open and is saved only in this browser: no accounts, no ads, no tracking.',
    '${WORLD.on?"Everyone at letterheads.live watches and helps this same world, live. Your companions and sparks are kept only in this browser: no accounts, no ads, no tracking.":"The world lives while this page is open and is saved only in this browser: no accounts, no ads, no tracking."}')
rep('''<p class="muted">Peek at another era (your world's own clock keeps running):</p>\n  <div class="actions"><button data-era="">Live</button><button data-era="150000">Speech and wandering</button><button data-era="20000">The Ice Age</button><button data-era="3800">First alphabet</button><button data-era="2000">Iron and cities</button><button data-era="100">Modern</button></div>''',
    '''${WORLD.on?"":`<p class="muted">Peek at another era (your world's own clock keeps running):</p>\n  <div class="actions"><button data-era="">Live</button><button data-era="150000">Speech and wandering</button><button data-era="20000">The Ice Age</button><button data-era="3800">First alphabet</button><button data-era="2000">Iron and cities</button><button data-era="100">Modern</button></div>`}''')

# ---- the connection itself
WORLD_JS=r'''
const VT={at:0,ask:{},wave:{},neg:{},lastNeg:{}};
const CMD={};
function WX(name,a,args,out,after){
  if(!WORLD.mirror){const o=out||document.createElement("div");CMD[name](a,args,o);if(after)after();return;}
  if(out)out.textContent="…";
  WORLD.cmd({name,id:a?a.id:null,args}).then(r=>{
    if(r.error){if(out)out.textContent=r.error==="busy"?"That's a lot of help at once. Give it a moment.":"The world is changing hands. Try again in a moment.";return;}
    if(r.visitor)S.visitor=r.visitor;if(out&&r.html!=null)out.innerHTML=r.html;WORLD.savePersonal();if(after)after();});
}
const WORLD=(()=>{
  const ME_KEY="letterheads_me_v1";
  const W={on:false,mirror:false,keeper:false,remote:false,from:null,down:false,n:1,snapText:null,giftAt:{},seen:new Set(),bridges:new Set()};
  let ws=null,url=null,rid=0,pending=new Map(),evq=[],started=false,liveT=null,snapT=null,lastLive=0,liveSimT=0,backoff=1000;
  const mobile=/Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
  const key=params.get("key")||"";
  async function pack(str){if(window.CompressionStream){const b=new Uint8Array(await new Response(new Blob([str]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer());const o=new Uint8Array(b.length+1);o[0]=1;o.set(b,1);return o;}
    const e=new TextEncoder().encode(str);const o=new Uint8Array(e.length+1);o[0]=0;o.set(e,1);return o;}
  async function unpack(buf){const u=new Uint8Array(buf);if(u[0]===1)return await new Response(new Blob([u.subarray(1)]).stream().pipeThrough(new DecompressionStream("gzip"))).text();return new TextDecoder().decode(u.subarray(1));}
  const round=(k,v)=>typeof v==="number"&&!Number.isInteger(v)?Math.round(v*100)/100:v;
  const HEAVY=["mem","core","bonds","map","ateAt","_tx","_ty"];
  function light(a){const o={};for(const k in a)if(!HEAVY.includes(k))o[k]=a[k];return o;}
  function send(m){if(ws&&ws.readyState===1)ws.send(typeof m==="string"||m instanceof Uint8Array?m:JSON.stringify(m));}
  function snapshotText(){const {visitor,settings,...world}=S;return JSON.stringify({S:world,nextId,stories},round);}
  async function sendSnap(){if(!W.keeper||!S)return;try{send(await pack(snapshotText()));}catch(e){}}
  function sendLive(){if(!W.keeper||!S)return;const m={t:"live",T:S.simT,nid:nextId,A:S.agents.map(light),W:S.words,B:S.beasts,H:S.herd,X:S.structs,wx:S.wx,st:stories,pl:S.place,ph:S.placeHome,
      tf:S.trees.map(t=>[t.fruit,t.burning||0,t.charred||0]),tn:S.trees.length,fi:S.firsts,dc:S.discovered,E:evq};evq=[];send(JSON.stringify(m,round));}
  W.ev=e=>{if(W.keeper&&!W.remote)evq.push(e);};
  function becomeKeeper(){W.keeper=true;W.mirror=false;if(S)S.agents.forEach(a=>{delete a._tx;delete a._ty;});
    clearInterval(liveT);clearInterval(snapT);liveT=setInterval(sendLive,500);snapT=setInterval(sendSnap,10000);if(started)sendSnap();}
  function becomeWatcher(){W.keeper=false;W.mirror=true;clearInterval(liveT);clearInterval(snapT);}
  function syncPlace(){if(!S||!MAP)return;if(S.place&&MAP.key!==S.place){genWorld(S.place);W.bridges=new Set();buildTerrain();if(S.placeHome){HOME.x=S.placeHome.x;HOME.y=S.placeHome.y;}}
    for(const t of S.structs||[])if(t.type==="bridge"&&t.built&&!CROSS.some(c=>c.id==="b"+t.k))addBridge(t);}
  function newStories(list){for(const o of list){const id=o.kind+"|"+o.born+"|"+o.text;if(W.seen.has(id))continue;W.seen.add(id);if(!started)continue;
      const hk={born:"word",forming:"word",discovery:"discover",threat:"danger",hurt:"danger",chapter:"chapter",dream:"dream"}[o.kind];if(hk)hint(hk);if(o.score>=86&&o.kind!=="forming")makeMoment(o);}
    if(W.seen.size>500)W.seen=new Set([...W.seen].slice(-200));}
  function applySnap(text){const d=JSON.parse(text);if(!d||!d.S)return;const old=new Map((S?S.agents:[]).map(a=>[a.id,a]));const mine={visitor:S.visitor,settings:S.settings};
    S=d.S;S.visitor=mine.visitor;S.settings=mine.settings;nextId=d.nextId||nextId;if(d.stories){newStories(d.stories);stories=d.stories;}
    for(const a of S.agents){const o=old.get(a.id);a._tx=a.x;a._ty=a.y;if(o&&Math.hypot(o.x-a.x,o.y-a.y)<300){a.x=o.x;a.y=o.y;}}liveSimT=S.simT;syncPlace();}
  function applyLive(m){if(!S)return;lastLive=performance.now();liveSimT=m.T;S.simT=m.T;nextId=m.nid;
    const by=new Map(S.agents.map(a=>[a.id,a]));S.agents=m.A.map(L=>{let a=by.get(L.id);if(!a){a=Object.assign({mem:[],core:[],bonds:{},map:{t:{},r:{}},ateAt:[]},L);a._tx=L.x;a._ty=L.y;return a;}
      const x=a.x,y=a.y;Object.assign(a,L);a._tx=L.x;a._ty=L.y;if(Math.hypot(x-L.x,y-L.y)<300){a.x=x;a.y=y;}return a;});
    const bb=new Map(S.beasts.map(b=>[b.id,b]));S.beasts=m.B.map(B=>{const o=bb.get(B.id);if(o&&Math.hypot(o.x-B.x,o.y-B.y)<300){const x=o.x,y=o.y;Object.assign(o,B);o._tx=B.x;o._ty=B.y;o.x=x;o.y=y;return o;}return B;});
    S.words=m.W;S.herd=m.H;S.structs=m.X;S.wx=m.wx;S.firsts=m.fi;S.discovered=m.dc;newStories(m.st);stories=m.st;
    if(m.tn===S.trees.length)m.tf.forEach((f,i)=>{const t=S.trees[i];t.fruit=f[0];t.burning=f[1];t.charred=f[2];});
    if(m.pl&&m.pl!==S.place){S.place=m.pl;S.placeHome=m.ph;}syncPlace();
    for(const e of m.E||[])onEvent(e);}
  // what the keeper's world did that matters to each person: their companions' deeds, and the sounds of the valley
  let _addDeed,_earn,_credit;const sfx={};
  function onEvent(e){const a=e.id!=null?agentById(e.id):null;
    if(e.t==="deed"&&a)_addDeed(a,e.d,e.x,e.g);
    else if(e.t==="earn"&&a&&isAdopted(a)){S.visitor.sparks+=e.n;S.visitor.sparkLog.unshift({t:Date.now(),n:e.n,text:`${a.name} ${e.x}`});if(S.visitor.sparkLog.length>60)S.visitor.sparkLog.length=60;refreshDashboard();}
    else if(e.t==="credit"&&a)_credit(a);
    else if(e.t==="sfx"&&sfx[e.f]&&Music.on)try{sfx[e.f].apply(Music,e.x||[]);}catch(err){}}
  function wrap(){_addDeed=addDeed;_earn=earn;_credit=credit;
    addDeed=function(a,d,x,g){if(a)W.ev({t:"deed",id:a.id,d,x,g:g?1:0});return _addDeed(a,d,x,g);};
    earn=function(a,k,n,x){if(!a)return;const first=!(a.ms&&a.ms[k]);if(!first)return;W.ev({t:"earn",id:a.id,n,x});if(isAdopted(a))return _earn(a,k,n,x);a.ms=a.ms||{};a.ms[k]=1;};
    credit=function(a,w){W.ev({t:"credit",id:a.id});_credit(a,w);return "";};
    for(const f of["birth","built","discovery","loss","tension","thunder","wordChord"]){const o=Music[f];if(typeof o!=="function")continue;sfx[f]=o;Music[f]=function(...x){W.ev({t:"sfx",f,x});return o.apply(Music,x);};}
    for(const f of["renderDashboard","refreshDashboard","openDashboard"]){}}
  W.personal=()=>{let me=null;try{me=JSON.parse(localStorage.getItem(ME_KEY)||"null");}catch(e){}
    const dv={adopted:[],gifts:1,standing:0,deeds:[],lastUse:{},tier:0,sparks:5,sparkLog:[],rep:4,repN:0,repLog:[]},ds={camera:"director",reduce:false,night:true,sound:false,vol:.6};
    let old=null;try{old=JSON.parse(localStorage.getItem(SAVE_KEY)||"null");}catch(e){}
    S.visitor=Object.assign(dv,me&&me.visitor||{});S.settings=Object.assign(ds,old&&old.S&&old.S.settings||{},me&&me.settings||{});
    S.visitor.adopted=S.visitor.adopted.filter(id=>S.agents.some(a=>a.id===id));};
  W.savePersonal=()=>{if(W.remote||!S)return;try{localStorage.setItem(ME_KEY,JSON.stringify({visitor:S.visitor,settings:S.settings}));}catch(e){}};
  W.visitorTick=()=>{VISITOR_TICK();};
  W.glide=dt=>{if(!S)return;if(S.simT<liveSimT+1.5)S.simT+=dt;const k=Math.min(1,dt*5);
    for(const a of S.agents){if(a._tx==null)continue;a._tx+=a.vx*dt;a._ty+=a.vy*dt;const nx=a.x+(a._tx-a.x)*k,ny=a.y+(a._ty-a.y)*k,moved=Math.hypot(nx-a.x,ny-a.y);a.x=nx;a.y=ny;
      const sp=Math.hypot(a.vx,a.vy);a.phase+=dt*sp*.16;a.gph=((a.gph??Math.random())+moved/(R_CYC*RS*(a.young?.8:1)))%1;}
    for(const b of S.beasts){if(b._tx==null)continue;b._tx+=b.vx*dt;b._ty+=b.vy*dt;b.x+=(b._tx-b.x)*k;b.y+=(b._ty-b.y)*k;b.phase=(b.phase||0)+dt*Math.hypot(b.vx,b.vy)*.2;}};
  W.cmd=m=>new Promise(res=>{const id=++rid;pending.set(id,res);send({t:"cmd",rid:id,...m,visitor:S.visitor});setTimeout(()=>{if(pending.has(id)){pending.delete(id);res({error:"timeout"});}},9000);});
  function runCmd(m){const reply=r=>send({t:"res",to:m.from,rid:m.rid,...r});
    if(!Object.prototype.hasOwnProperty.call(CMD,m.name))return reply({error:"unknown"});const a=m.id!=null?agentById(+m.id):null;if(m.id!=null&&!a)return reply({error:"gone"});
    const mine=S.visitor,v=Object.assign({adopted:[],gifts:0,standing:0,deeds:[],lastUse:{},tier:0,sparks:0,sparkLog:[],rep:4,repN:0,repLog:[]},m.visitor&&typeof m.visitor==="object"?m.visitor:{});
    if(!Array.isArray(v.adopted))v.adopted=[];v.adopted=v.adopted.filter(x=>typeof x==="number").slice(0,3);for(const k of["deeds","sparkLog","repLog"])if(!Array.isArray(v[k]))v[k]=[];
    const out=document.createElement("div");S.visitor=v;W.remote=true;W.from=m.from;try{CMD[m.name](a,m.args||{},out);}catch(e){}finally{W.remote=false;W.from=null;S.visitor=mine;}
    reply({html:out.innerHTML,visitor:v});}
  function connect(onWelcome){let socket;try{socket=new WebSocket(url);}catch(e){onWelcome(null);return;}ws=socket;socket.binaryType="arraybuffer";
    socket.onopen=()=>send({t:"hello",visible:!document.hidden,mobile,key});
    socket.onmessage=async e=>{if(typeof e.data!=="string"){const text=await unpack(e.data);if(!started){W.snapText=text;onWelcome&&onWelcome("snap");return;}if(W.mirror)applySnap(text);return;}
      let m;try{m=JSON.parse(e.data);}catch(err){return;}
      if(m.t==="welcome"){W.down=false;backoff=1000;W.n=m.n||1;if(!started){if(m.keeper){W.keeper=true;if(!m.hasSnap)onWelcome&&onWelcome("new");}else W.mirror=true;}
        else{if(m.keeper&&!W.keeper)becomeKeeper();else if(!m.keeper&&W.keeper)becomeWatcher();}}
      else if(m.t==="count")W.n=m.n;
      else if(m.t==="role"){if(m.keeper)becomeKeeper();else becomeWatcher();}
      else if(m.t==="live"){if(W.mirror&&started)applyLive(m);}
      else if(m.t==="cmd"){if(W.keeper&&started)runCmd(m);}
      else if(m.t==="res"){const r=pending.get(m.rid);if(r){pending.delete(m.rid);r(m);}}};
    socket.onclose=()=>{if(ws!==socket)return;ws=null;if(!started){onWelcome(null);return;}W.down=true;setTimeout(()=>connect(null),backoff);backoff=Math.min(15000,backoff*2);};}
  W.join=async()=>{if(params.has("solo"))return;url=params.get("world");
    if(!url){try{const r=await fetch("/world.json",{cache:"no-store"});if(r.ok){const j=await r.json();url=j.url;}}catch(e){}}
    if(!url||!/^wss?:\/\//.test(url))return;
    const how=await new Promise(res=>{let done=false;const fin=v=>{if(!done){done=true;res(v);}};setTimeout(()=>fin(null),6000);connect(fin);});
    if(!how){try{ws&&ws.close();}catch(e){}ws=null;W.keeper=W.mirror=false;return;}
    W.on=true;if(how==="new")W.snapText=null;};
  W.started=()=>{started=true;wrap();if(W.keeper)becomeKeeper();else{becomeWatcher();applySnap(W.snapText);}
    document.addEventListener("visibilitychange",()=>send({t:"vis",on:!document.hidden}));};
  return W;})();
'''
# The per-person day (see above) becomes a function every device runs for itself.
WORLD_JS=WORLD_JS.replace('W.visitorTick=()=>{VISITOR_TICK();};','W.visitorTick=()=>{if(!S||!started)return;'+vt+'};')
rep('function save(){if(WORLD.remote)', WORLD_JS+CMDS+'function save(){if(WORLD.remote)')
rep('window.__lango={','window.__lango={get world(){return WORLD},wx:WX,')
