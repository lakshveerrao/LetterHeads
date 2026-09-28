# One shared world (28 September 2026). When the world server is reachable, everyone at letterheads.live sees the
# same world. One visitor's browser, the "keeper", runs the simulation and sends it to the server; everyone else is a
# "watcher" that draws the world it receives, smoothly, and sends its help to the keeper, which acts on it and answers.
# Each person's own things (companions, sparks, standing, settings) stay on their own device, never in the world.
# If the server can't be reached, or with ?solo, the game falls back to a private world saved in this browser.
# The server lives in world/ (a Cloudflare Worker). Its address comes from /world.json or ?world=wss://...
# Run from assemble.py via exec(), after growth_patch.py.

# ---- the start waits to join the world
rep('terraLoad().then(()=>{\nresize();const loadedExisting=load();\nif(!loadedExisting){genWorld();newWorld();S.place=MAP.key;S.placeHome={x:HOME.x,y:HOME.y};}',
    'terraLoad().then(()=>WORLD.join()).then(()=>{\nresize();const loadedExisting=load();\nif(!loadedExisting){genWorld();newWorld();S.place=MAP.key;S.placeHome={x:HOME.x,y:HOME.y};if(WORLD.on&&!WORLD.own)WORLD.personal();}')
rep('buildTerrain();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{if(MAP.place==null)','if(WORLD.on)WORLD.started();buildTerrain();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{if(MAP.place==null)')

# ---- saving: in the shared world only your own things are saved here; the world itself lives on the server
rep('function save(){try{', 'function save(){if(WORLD.remote)return;if(WORLD.on&&!WORLD.own){WORLD.savePersonal();return;}try{')
rep('const raw=localStorage.getItem(SAVE_KEY);', 'const raw=WORLD.on&&!WORLD.own?WORLD.snapText:localStorage.getItem(SAVE_KEY);')
rep('S=d.S;nextId=d.nextId||5000;', 'S=d.S;nextId=d.nextId||5000;if(WORLD.on&&!WORLD.own){WORLD.personal();if(d.stories)stories=d.stories;}')

# ---- the frame: watchers draw what they receive; nobody can speed up or slow down the shared world
rep('acc+=dtReal*SPEED*(fxOn?.35:1);let n=0;while(acc>=.1&&n<80){step(.1);acc-=.1;n++;}',
    'if(WORLD.mirror){WORLD.glide(dtReal);acc=0;}else{acc+=dtReal*(WORLD.on?1:SPEED*(fxOn?.35:1));let n=0;while(acc>=.1&&n<80){step(.1);acc-=.1;n++;}}')
rep('if(!tour&&!ATL.on&&tAnim>(director.nextPlace||0)){director.nextPlace=tAnim+4;relocate();}',
    'if(!tour&&!ATL.on&&tAnim>(director.nextPlace||0)){director.nextPlace=tAnim+4;if(!WORLD.mirror)relocate();}if(WORLD.on)WORLD.visitorTick();')
rep('${S.agents.length} letters · ${nw} word${nw===1?"":"s"}',
    '${S.agents.length} letters · ${nw} word${nw===1?"":"s"}${WORLD.on?" · "+WORLD.here():""}')

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
    '''${WORLD.on&&!WORLD.own?"":`<p class="muted">Peek at another era (your world's own clock keeps running):</p>\n  <div class="actions"><button data-era="">Live</button><button data-era="150000">Speech and wandering</button><button data-era="20000">The Ice Age</button><button data-era="3800">First alphabet</button><button data-era="2000">Iron and cities</button><button data-era="100">Modern</button></div>`}''')

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
  let ME_KEY="letterheads_me_v1";
  const W={on:false,mirror:false,keeper:false,own:false,mode:null,vid:null,vname:null,live:true,remote:false,from:null,down:false,n:1,snapText:null,giftAt:{},seen:new Set(),bridges:new Set(),valleys:[],base:null};
  let ws=null,url=null,rid=0,pending=new Map(),evq=[],early=[],started=false,liveT=null,snapT=null,metaT=null,lastLive=0,liveSimT=0,backoff=1000;
  const MY_KEY="letterheads_valley_v1";
  W.my=()=>{try{return JSON.parse(localStorage.getItem(MY_KEY)||"null");}catch(e){return null;}};
  W.setMy=o=>{try{localStorage.setItem(MY_KEY,JSON.stringify(o));}catch(e){}};
  W.ensureMy=()=>{let m=W.my();if(m&&m.id&&m.token)return m;const r=n=>{const a=new Uint8Array(n);crypto.getRandomValues(a);return[...a].map(b=>"abcdefghijkmnpqrstuvwxyz23456789"[b%32]).join("");};
    m={id:r(10),token:r(32),name:null,listed:true};W.setMy(m);return m;};
  W.link=id=>location.origin+"/v/"+id;
  W.here=()=>{if(W.down)return"reconnecting";if(W.mode==="mine")return W.n>1?`${W.n-1} visiting`:"only you here";
    if(W.mode==="visit")return W.live?`${W.n} here`:"resting, its owner is away";return W.n+(W.n===1?" person":" people")+" here";};
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
  function sendMeta(){if(!W.keeper||!W.own||!S)return;const m=W.my()||{};if(!m.name&&m.id){m.name=W.autoName();W.setMy(m);}let v=null;try{v=valleyAt(yearsAgo());}catch(e){}
    send({t:"meta",name:m.name||W.autoName(),listed:m.listed!==false,x:v?v.x:0,yy:v?v.yy:0,y:yearsAgo(),place:v?v.name:"",letters:S.agents.length,words:S.words.filter(w=>w.state!=="forming").length});}
  W.autoName=()=>{const a=S&&(S.agents.find(x=>S.visitor&&S.visitor.adopted.includes(x.id))||S.agents.find(x=>!x.young));return a&&/^[A-Z][a-z]{1,11}$/.test(a.name)?a.name:"Asha";};
  W.sendMeta=sendMeta;
  function becomeKeeper(){W.keeper=true;W.mirror=false;W.live=true;if(S)S.agents.forEach(a=>{delete a._tx;delete a._ty;});
    clearInterval(liveT);clearInterval(snapT);clearInterval(metaT);liveT=setInterval(sendLive,500);snapT=setInterval(sendSnap,10000);if(W.own)metaT=setInterval(sendMeta,30000);
    if(started){sendSnap();sendMeta();const q=early;early=[];q.forEach(runCmd);}}
  function becomeWatcher(){W.keeper=false;W.mirror=true;clearInterval(liveT);clearInterval(snapT);clearInterval(metaT);}
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
  W.glide=dt=>{if(!S)return;if(performance.now()-lastLive>2500){for(const a of S.agents)if(a._tx!=null){a.vx*=.9;a.vy*=.9;}}if(S.simT<liveSimT+1.5)S.simT+=dt;const k=Math.min(1,dt*5);
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
    socket.onopen=()=>{const h={t:"hello",visible:!document.hidden,mobile,key};if(W.mode==="mine")h.own=W.ensureMy().token;send(h);};
    socket.onmessage=async e=>{if(typeof e.data!=="string"){const text=await unpack(e.data);if(!started){W.snapText=text;onWelcome&&onWelcome("snap");return;}if(W.mirror)applySnap(text);return;}
      let m;try{m=JSON.parse(e.data);}catch(err){return;}
      if(m.t==="welcome"){W.down=false;backoff=1000;W.n=m.n||1;W.live=m.live!==false;if(m.name)W.vname=m.name;
        if(!started){if(m.keeper){W.keeper=true;if(!m.hasSnap||W.mode==="mine")onWelcome&&onWelcome(W.mode==="mine"?"mine":"new");}else if(W.mode==="mine"){W.mirror=true;onWelcome&&onWelcome("mine");}else{W.mirror=true;if(!m.hasSnap)onWelcome&&onWelcome("empty");}}
        else{if(m.keeper&&!W.keeper)becomeKeeper();else if(!m.keeper&&W.keeper)becomeWatcher();}}
      else if(m.t==="count"){W.n=m.n;if(m.live!=null)W.live=m.live;}
      else if(m.t==="role"){if(m.keeper)becomeKeeper();else becomeWatcher();}
      else if(m.t==="live"){if(W.mirror&&started)applyLive(m);}
      else if(m.t==="cmd"){if(W.keeper&&started)runCmd(m);else if(W.keeper)early.push(m);}
      else if(m.t==="res"){const r=pending.get(m.rid);if(r){pending.delete(m.rid);r(m);}}};
    socket.onclose=()=>{if(ws!==socket)return;ws=null;if(!started){onWelcome(null);return;}W.down=true;setTimeout(()=>connect(null),backoff);backoff=Math.min(15000,backoff*2);};}
  W.join=async()=>{if(params.has("solo"))return;let base=params.get("world");
    if(!base){try{const r=await fetch("/world.json",{cache:"no-store"});if(r.ok){const j=await r.json();base=j.url;}}catch(e){}}
    if(!base||!/^wss?:\/\//.test(base))return;W.base=base.split("?")[0];
    const v=(params.get("v")||"").toLowerCase(),my=W.my();
    if(v&&/^[a-z0-9]{6,16}$/.test(v)){W.vid=v;W.mode=my&&my.id===v?"mine":"visit";}else W.mode="world";
    if(W.mode==="mine")W.own=true;if(W.mode==="visit")ME_KEY="letterheads_me_v1:"+v;
    url=W.base+"?w="+(W.mode==="world"?"world":W.vid);
    const how=await new Promise(res=>{let done=false;const fin=x=>{if(!done){done=true;res(x);}};setTimeout(()=>fin(null),6000);connect(fin);});
    if(how==="empty"){try{ws&&ws.close();}catch(e){}location.replace("/play/?nov=1");await new Promise(()=>{});}
    if(!how){try{ws&&ws.close();}catch(e){}ws=null;W.keeper=W.mirror=false;if(W.mode!=="mine"&&W.mode!=="world"){W.mode=null;}W.own=false;return;}
    W.on=true;if(how==="new"||how==="mine")W.snapText=null;};
  W.started=()=>{started=true;wrap();if(W.keeper)becomeKeeper();else{becomeWatcher();if(W.snapText)applySnap(W.snapText);}
    document.addEventListener("visibilitychange",()=>send({t:"vis",on:!document.hidden}));};
  return W;})();
'''
# The per-person day (see above) becomes a function every device runs for itself.
WORLD_JS=WORLD_JS.replace('W.visitorTick=()=>{VISITOR_TICK();};','W.visitorTick=()=>{if(!S||!started)return;'+vt+'};')
rep('function save(){if(WORLD.remote)', WORLD_JS+CMDS+'function save(){if(WORLD.remote)')
rep('window.__lango={','window.__lango={get world(){return WORLD},wx:WX,')

# Words still coming together are drawn as dashed lines and announced in the caption, so the top line counts them too.
rep('${nw} word${nw===1?"":"s"}${WORLD.on?', '${nw} word${nw===1?"":"s"}${S.words.length>nw?" ("+(S.words.length-nw)+" forming)":""}${WORLD.on?')

# ---- valleys: The World, your own valley, and anyone else's (28 September 2026)
rep('Watch the trailer</button></div>\n  <div class="spacer"></div>', 'Watch the trailer</button><button class="trailer-link place-link" id="placeLink" type="button" hidden></button></div>\n  <div class="spacer"></div>')
rep("</style>", """.place-link{display:flex;margin-top:2px;text-decoration-color:#7FB8A4}
body.has-place .tour-btn{top:calc(116px + env(safe-area-inset-top,0px))}@media (max-width:480px){body.has-place .tour-btn{top:calc(96px + env(safe-area-inset-top,0px))}}
body.broadcast .place-link{display:none!important}
#atlasVisit[hidden],#placeLink[hidden]{display:none!important}
.vrow{display:flex;align-items:center;gap:10px;padding:8px 0;border-top:1px solid rgba(31,36,33,.12)}.vrow:first-child{border-top:none}
.vrow .vt{flex:1;min-width:0}.vrow .vt b{display:block}.vrow .vt span{font-size:13px;color:#5A635D}
.vlink{word-break:break-all;font-size:13px;background:rgba(31,36,33,.06);padding:8px 10px;border-radius:8px;user-select:all}
</style>""")
rep('<button id="mAbout">What is this?</button></div>', '<button id="mAbout">What is this?</button><button id="mValleys">🏡 Valleys</button></div>')
rep('<div class="actions"><button id="mReset">Start a new world</button></div>`,"menu");',
    '${WORLD.on&&!WORLD.own?"":`<div class="actions"><button id="mReset">Start a new world</button></div>`}`,"menu");document.getElementById("mValleys").onclick=()=>openValleys();')
rep('document.getElementById("mReset").onclick=()=>{', 'const mr=document.getElementById("mReset");if(mr)mr.onclick=()=>{')
# the place pill under the name shows where you are, and opens the Valleys panel
rep('document.getElementById("eraLine").textContent=`', 'WORLD.pill();document.getElementById("eraLine").textContent=`')
# a traveller from someone's valley arriving in The World
CMDS2 = r'''
CMD.arrive=(a,args,out)=>{const c=String(args.ch||"");if(!/^[A-Z]$/.test(c)||(LATE[c]&&!S.lateBorn?.[c])||S.agents.length>=72)return;
  const from=NAMES.includes(args.from)?args.from:null,where=from?`${from}'s valley`:"another valley";const x=makeAgent(c,REFUGE.x+(rnd()-.5)*60,REFUGE.y+30,Date.now(),false);if(NAMES.includes(args.n))x.name=args.n;S.agents.push(x);
  remember(x,`I travelled here from ${where}.`,true);chron(`${x.name}, ${art(c)} ${c}, arrived at the Hearth refuge from ${where}.`,"people");
  addStory({kind:"arrival",ids:[x.id],text:`${x.name}, ${art(c)} ${c}, has arrived from ${where}.`,sub:"A traveller from another valley. Where will they belong?",score:76,dur:20,main:x.id});Music.birth();};
WORLD.pill=()=>{const b=document.getElementById("placeLink");if(!b)return;if(!WORLD.on||document.body.classList.contains("broadcast")){b.hidden=true;return;}b.hidden=false;document.body.classList.add("has-place");
  const name=WORLD.mode==="world"?"🌍 The World":WORLD.mode==="mine"?"🏡 Your valley":`🏡 ${WORLD.vname||"A"}'s valley`;const t=`${name} · ${WORLD.here()}`;if(b.textContent!==t)b.textContent=t;};
document.getElementById("placeLink").onclick=()=>openValleys();
function goValley(id){const w=params.get("world");location.href=(id?"/play/?v="+id:"/play/")+(w?(id?"&":"?")+"world="+encodeURIComponent(w):"");}
async function fetchValleys(){if(!WORLD.base)return[];try{const r=await fetch(WORLD.base.replace(/^ws/,"http").replace(/\/ws$/,"/valleys"),{cache:"no-store"});const j=await r.json();WORLD.valleys=(j.valleys||[]).filter(v=>v.id!==WORLD.vid);WORLD.valleysAt=Date.now();return WORLD.valleys;}catch(e){return[];}}
function valleyRows(list){return list.slice(0,12).map(v=>`<div class="vrow"><div class="vt"><b>${esc(v.name)}'s valley</b><span>${v.online?"Open now":"Resting"}${v.watching?` · ${v.watching} watching`:""} · ${esc(v.place||"")} · ${v.letters} letters, ${v.words} word${v.words===1?"":"s"}</span></div><div class="actions" style="margin:0"><button data-go="${esc(v.id)}">Visit</button></div></div>`).join("");}
function openValleys(){const my=WORLD.my(),mine=WORLD.mode==="mine";
  const here=WORLD.mode==="world"?"You are in The World: one valley that everyone shares, live.":mine?"You are in your own valley. Anyone with its link can watch it and help its letters while you have it open.":`You are visiting ${esc(WORLD.vname||"someone")}'s valley.`;
  const names=mine?[...new Set(S.agents.filter(a=>!a.young&&/^[A-Z][a-z]{1,11}$/.test(a.name)).map(a=>a.name))].slice(0,8):[];const cur=(my&&my.name)||(mine?WORLD.autoName():null);
  const travellers=mine?S.agents.filter(a=>!a.young).slice(0,40).sort((p,q)=>(p.word?1:0)-(q.word?1:0)).slice(0,6):[];
  openSheet(`<h2 id="sheetTitle">Valleys</h2><p class="muted">${here}</p>
  <div class="actions">${WORLD.mode!=="world"?`<button data-go="" class="main">🌍 Go to The World</button>`:""}${!mine?`<button id="vMine" ${WORLD.mode==="world"?'class="main"':""}>🏡 ${my?"Go to my valley":"Start my own valley"}</button>`:""}</div>
  ${mine?`<h3>Share your valley</h3><p class="vlink" id="vLink">${esc(WORLD.link(WORLD.vid))}</p><div class="actions"><button id="vShare" class="main">Share the link</button></div>
  <h3>Its name</h3><p class="muted">Your valley is named after one of its letters: <b>${esc(cur)}'s valley</b>.</p><div class="actions">${names.map(n=>`<button data-name="${esc(n)}"${n===cur?' class="main"':""}>${esc(n)}</button>`).join("")}</div>
  <div class="opt"><label for="vListed">Show it on the Atlas for anyone to visit</label><input type="checkbox" id="vListed" ${my&&my.listed===false?"":"checked"}></div>
  <h3>Send a letter to The World</h3><p class="muted">A letter from your valley can travel to The World, where everyone will see it arrive. It leaves your valley for good.</p>
  <div class="actions" id="vSend">${travellers.map(a=>`<button data-send="${a.id}">${esc(a.name)}, ${art(a.ch)} ${a.ch}</button>`).join("")}</div><p class="muted" id="vSendOut" aria-live="polite"></p>`:""}
  <h3>Valleys open around the world</h3><div id="vList"><p class="muted">Looking…</p></div><p class="muted">They glow on the Atlas too.</p>`,"valleys");
  const bind=()=>sheetBody.querySelectorAll("[data-go]").forEach(b=>b.onclick=()=>goValley(b.dataset.go));bind();
  const vm=document.getElementById("vMine");if(vm)vm.onclick=()=>goValley(WORLD.ensureMy().id);
  if(mine){document.getElementById("vShare").onclick=async()=>{const u=WORLD.link(WORLD.vid),t=`Come and see ${cur}'s valley on Letterheads: letters living through 300,000 years of history.`;
      try{if(navigator.share){await navigator.share({title:"Letterheads",text:t,url:u});return;}}catch(e){return;}try{await navigator.clipboard.writeText(u);document.getElementById("vShare").textContent="Link copied";}catch(e){}};
    sheetBody.querySelectorAll("[data-name]").forEach(b=>b.onclick=()=>{const m=WORLD.ensureMy();m.name=b.dataset.name;WORLD.setMy(m);WORLD.sendMeta();openValleys();});
    document.getElementById("vListed").onchange=e=>{const m=WORLD.ensureMy();m.listed=e.target.checked;WORLD.setMy(m);WORLD.sendMeta();};
    sheetBody.querySelectorAll("[data-send]").forEach(b=>b.onclick=()=>sendToWorld(agentById(+b.dataset.send),b));}
  fetchValleys().then(l=>{const el=document.getElementById("vList");if(!el)return;el.innerHTML=l.length?valleyRows(l):`<p class="muted">No other valleys are open right now. Start yours and share it.</p>`;bind();});}
function sendToWorld(a,btn){const out=document.getElementById("vSendOut");if(!a||!WORLD.base)return;if(!confirm(`Send ${a.name} to The World? ${a.name} will leave your valley for good.`))return;
  out.textContent=`${a.name} is setting off…`;let done=false;const fin=t=>{if(done)return;done=true;out.textContent=t;try{ws.close();}catch(e){}};
  const ws=new WebSocket(WORLD.base+"?w=world");setTimeout(()=>fin("The World couldn't be reached. Try again in a moment."),9000);
  ws.onopen=()=>ws.send(JSON.stringify({t:"hello",courier:true,visible:false}));
  ws.onmessage=e=>{if(typeof e.data!=="string")return;const m=JSON.parse(e.data);
    if(m.t==="welcome")ws.send(JSON.stringify({t:"cmd",rid:1,name:"arrive",args:{ch:a.ch,n:a.name,from:(WORLD.my()||{}).name||WORLD.autoName()}}));
    if(m.t==="res"){if(m.error){fin(m.error==="wait"?"One traveller every two minutes, please.":"The World couldn't take a traveller right now.");return;}
      if(a.word)leaveWord(a,"It set off for The World.");S.agents=S.agents.filter(x=>x!==a);S.visitor.adopted=S.visitor.adopted.filter(id=>id!==a.id);
      chron(`${a.name} set off for The World, and everyone there saw it arrive.`,"people");save();if(btn)btn.remove();fin(`${a.name} is on the way. Go to The World to see ${a.name} arrive at the Hearth refuge.`);}};
  ws.onerror=()=>fin("The World couldn't be reached. Try again in a moment.");}
if(params.get("nov"))setTimeout(()=>{const tb=document.getElementById("storyToast");tb.textContent="That valley hasn't opened yet, so here is The World.";tb.style.display="block";tb.onclick=()=>{tb.style.display="none";};setTimeout(()=>{tb.style.display="none";},9000);},4000);
'''
rep('function save(){if(WORLD.remote)', CMDS2+'function save(){if(WORLD.remote)')

# ---- the Atlas shows every open valley
rep('  // the valley we follow\n', '''  // everyone else's valleys
  if(WORLD.on&&ATL.on&&Date.now()-(WORLD.valleysAt||0)>60000){WORLD.valleysAt=Date.now();fetchValleys();}
  for(const o of WORLD.valleys||[]){const h=hash01(o.id.charCodeAt(0)*7+o.id.charCodeAt(1)*13+o.id.charCodeAt(2)),a=h*6.283,d=30+hash01(o.id.charCodeAt(3)*5+o.id.charCodeAt(4))*40;
    const sx=asx(o.x)+Math.cos(a)*d,sy=asy(o.yy)+Math.sin(a)*d;o.sx=sx;o.sy=sy;if(sx<-40||sx>W+40||sy<-40||sy>H+40)continue;const on=o.online,selO=ATL.sel&&ATL.sel.o===o;
    g.globalAlpha=on?1:.55;g.drawImage(gl,sx-9,sy-9,18,18);g.globalAlpha=1;g.fillStyle=on?"#BFF0DA":"#9FB7AE";g.beginPath();g.arc(sx,sy,3.4,0,Math.PI*2);g.fill();g.strokeStyle="#1F2421";g.lineWidth=1;g.stroke();
    if(selO){g.setLineDash([4,4]);g.strokeStyle="#7FB8A4";g.lineWidth=2;g.beginPath();g.arc(sx,sy,12,0,Math.PI*2);g.stroke();g.setLineDash([]);}
    if(selO||z>1.1||(on&&z>.6))aLabel(o.name+"'s valley",sx,sy-14,{font:"600 12px 'Atkinson Hyperlegible', sans-serif",col:on?"#E6FFF3":"#C9D6D0"});}
  // the valley we follow
''')
rep('function atlasHit(px,py){const y=atlasY();if(ATL.vs&&Math.hypot(px-ATL.vs.x,py-ATL.vs.y)<26)return{v:true};let best=null,bd=26;',
    'function atlasHit(px,py){const y=atlasY();if(ATL.vs&&Math.hypot(px-ATL.vs.x,py-ATL.vs.y)<26)return{v:true};let best=null,bd=26;\n  for(const o of WORLD.valleys||[]){if(o.sx==null)continue;const d=Math.hypot(px-o.sx,py-o.sy);if(d<bd*.8){bd=d/.8;best={o};}}')
rep('      else if(h){ATL.sel=h;const o=h.n||h.e;', '      else if(h&&h.o){ATL.sel=h;}\n      else if(h){ATL.sel=h;const o=h.n||h.e;')
rep('  if(ATL.sel&&ATL.sel.n){const n=ATL.sel.n;', '''  {const vb=document.getElementById("atlasVisit");if(vb){vb.hidden=!(ATL.sel&&ATL.sel.o);if(ATL.sel&&ATL.sel.o)vb.onclick=()=>goValley(ATL.sel.o.id);}}
  if(ATL.sel&&ATL.sel.o){const o=ATL.sel.o;tEl.textContent=o.name+"'s valley";sEl.textContent=`${o.online?"Open right now":"Resting until its owner comes back"}${o.watching?`, with ${o.watching} watching`:""}. It lies in ${o.place||"the valley"}, ${yearLabel(o.y)}. ${o.letters} letters and ${o.words} word${o.words===1?"":"s"} live there.`;}
  else if(ATL.sel&&ATL.sel.n){const n=ATL.sel.n;''')
rep('<div class="row"><button class="btn-primary" id="atlasDive">', '<div class="row"><button class="btn-primary" id="atlasVisit" hidden>Visit this valley</button><button class="btn-primary" id="atlasDive">')
