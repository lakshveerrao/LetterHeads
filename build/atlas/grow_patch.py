# Grow (3 October 2026): make words do things, ask friends for letters, and lead your letters yourself.
#   - Waking words: RAIN, SUN, FEAST, DRINK, REST, HEAL, FRUIT and SEED can be said and woken for 10-15 sparks;
#     when the letters say a woken word, it happens: rain falls, the sun comes out, trees fill with fruit, nearby
#     letters eat, drink, rest or heal. Everything is decided by the world's keeper, like every other reward.
#   - Ask a friend: "I'm one Q away from QUEEN". The link opens your page with a Send button; your friend earns
#     10 sparks for sending, and you get the letter free and 10 sparks the next time you play.
#   - Lead: tap Lead on a companion, then tap where to go (or use the arrow keys). Hungry, thirsty or exhausted
#     letters won't follow, and a lead ends after a while if you stop.
# Run after share_patch.py.

GROW_JS = r'''
// ================= grow: waking words, asking friends, leading your letters =================
const WAKE={RAIN:{cost:15,d:"rain falls on the valley",no:()=>S.wx.rain?"It's already raining.":null,go:sp=>{S.wx.rain=true;S.wx.until=S.simT+120+rnd()*60;return"and the clouds answered. Rain began to fall.";}},
  SUN:{cost:10,d:"the rain stops and the sun comes out",no:()=>S.wx.rain?null:"The sun is already out.",go:sp=>{S.wx.rain=false;S.wx.next=S.simT+420+rnd()*300;return"and the clouds broke. The sun came out.";}},
  FEAST:{cost:15,d:"every letter nearby eats its fill",go:sp=>{const n=wakeNear(sp,a=>{a.hunger=0;a.joy=Math.min(1,(a.joy||0)+.2);});return`and ${n} letter${n===1?"":"s"} nearby ate their fill.`;}},
  DRINK:{cost:10,d:"every letter nearby drinks",go:sp=>{const n=wakeNear(sp,a=>{a.thirst=0;});return`and ${n} thirsty letter${n===1?"":"s"} drank.`;}},
  REST:{cost:10,d:"every letter nearby is rested",go:sp=>{const n=wakeNear(sp,a=>{a.energy=1;});return`and ${n} tired letter${n===1?"":"s"} felt rested.`;}},
  HEAL:{cost:15,d:"hurt letters nearby are healed",go:sp=>{const n=wakeNear(sp,a=>{a.hurt=0;a.energy=Math.max(a.energy,.6);});return`and the letters nearby felt whole again.`;}},
  FRUIT:{cost:15,d:"trees nearby fill with fruit",go:sp=>{let n=0;for(const t of S.trees)if(Math.hypot(t.x-sp.x,t.y-sp.y)<700&&t.max){t.fruit=t.max;n++;}return n?`and ${n} tree${n===1?"":"s"} nearby filled with fruit.`:"but there were no trees near enough to listen.";}}};
WAKE.SEED=WAKE.FRUIT;
function wakeNear(sp,f){let n=0;for(const a of S.agents)if(Math.hypot(a.x-sp.x,a.y-sp.y)<600){f(a);n++;}return n;}
function wakeDo(sp){const w=WAKE[sp.wake];if(!w)return;let line="";try{line=w.go(sp);}catch(e){return;}const ms=sp.ids.map(agentById).filter(Boolean);
  const t=`${listNames(ms.map(a=>a.name))} said ${sp.text}, ${line}`;chron(t,"word");addStory({kind:"wake",sp:sp.id,ids:sp.ids,text:t,sub:"A visitor woke the word.",score:86,dur:14,main:sp.ids[0]});try{Music.discovery();}catch(e){}}
function wakeRow(){const el=$p("stWake");if(!el)return;const t=$p("stIn").value,w=WAKE[t];if(!w||!LEXSET.has(t)){el.innerHTML="";return;}const v=vPlay(),ok=v.sparks>=w.cost;
  el.innerHTML=`<span>✨ <b>${t}</b> is a waking word: ${esc(w.d)}.</span><button type="button" class="st-chip get" id="stWakeGo" ${ok?"":"disabled"}>Say and wake it · ${w.cost} ✦</button>`;$p("stWakeGo").onclick=()=>sayIt(true);}
async function askFriend(c,w){if(!pgLink())await pgPublish();const l=pgLink();if(!l){note("Couldn't reach the server. Try again soon.");return;}
  const url=`${l}&give=${c}&w=${w}`,text=`I'm one ${c} away from ${w} in Letterheads. Can you send me ${art(c)} ${c}? We both get 10 ✦.`;
  try{if(navigator.share){await navigator.share({text,url});return;}}catch(e){if(e&&e.name==="AbortError")return;}
  try{await navigator.clipboard.writeText(text+" "+url);note("Your ask is copied. Send it to a friend.");}catch(e){note(url);}}
async function sendGift(p,c){const r=await pgCall("/page/give",p,{vt:PG.vt,ch:c});const b=$p("pgGive");
  if(r&&r.ok){let got={};try{got=JSON.parse(localStorage.getItem("letterheads_gave_v1")||"{}");}catch(e){}const k=p+":"+new Date().toISOString().slice(0,10);
    if(!got[k]){got[k]=1;try{localStorage.setItem("letterheads_gave_v1",JSON.stringify(got));}catch(e){}const v=vPlay();v.sparks+=10;v.earned+=10;dockTick();}
    if(b){b.disabled=true;b.textContent=`Sent! You both get 10 ✦`;}}
  else if(b){b.disabled=true;b.textContent=r&&r.why==="already"?"You've already sent one today":r&&r.why==="full"?"They have plenty of gifts waiting":"Couldn't send. Try again soon";}}
// lead a companion: tap where to go
const LEAD={on:false,id:null,keyAt:0};
function leadStart(a){if(!isAdopted(a))return;closeSheet();LEAD.on=true;LEAD.id=a.id;cam.mode="follow";cam.follow=a.id;
  const el=$p("leadBar");el.innerHTML=`<span>Leading <b>${esc(a.name)}</b>. Tap where to go${matchMedia("(pointer:coarse)").matches?"":", or use the arrow keys"}.</span><button type="button" class="st-chip" id="leadStop">Stop</button>`;el.hidden=false;$p("leadStop").onclick=leadStop;document.body.classList.add("leading");}
function leadStop(){LEAD.on=false;$p("leadBar").hidden=true;document.body.classList.remove("leading");}
function leadTo(x,y){const a=agentById(LEAD.id);if(!a){leadStop();return;}const out=document.createElement("div");LEAD.mark={x,y,t:performance.now()};
  WX("lead",a,{x,y},out,()=>{const m=out.textContent;if(m)note(m);});}
CMD.lead=(a,args,out)=>{const say=t=>{if(out)out.textContent=t;};if(!a||!isAdopted(a))return say("Only your companions follow you.");const x=+args.x,y=+args.y;if(!Number.isFinite(x)||!Number.isFinite(y))return;
  if(urgentNeed(a))return say(`${a.name} is too ${a.hunger>.75?"hungry":a.thirst>.75?"thirsty":"tired"} to follow right now.`);
  if(a.act&&(a.act.type==="say"||a.act.type==="await"))return say(`${a.name} is busy saying a word.`);if(a.crossing!=null)return say(`${a.name} is crossing the river.`);
  const tx=clamp(x,0,WORLD_W),ty=clamp(y,0,WORLD_H),wp=route(a,tx,ty);if(wp===null)return say(`${a.name} can't find a way there.`);
  if(a.act)done(a);a.act={type:"led",tx,ty,t:0,wp,arrived:false,until:S.simT+60};emote(a,"joy",3);say("");};
document.addEventListener("keydown",e=>{if(!LEAD.on)return;if(e.key==="Escape"){leadStop();return;}if(SPELL.on)return;const d={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[e.key];if(!d)return;
  e.preventDefault();e.stopImmediatePropagation();const now=performance.now();if(now-LEAD.keyAt<1600)return;LEAD.keyAt=now;const a=agentById(LEAD.id);if(a)leadTo(a.x+d[0]*260,a.y+d[1]*260);},true);
function drawLead(){if(!LEAD.on||!LEAD.mark)return;const k=(performance.now()-LEAD.mark.t)/1000;if(k>2.5)return;ctx.save();ctx.strokeStyle=`rgba(232,150,47,${1-k/2.5})`;ctx.lineWidth=3;ctx.beginPath();ctx.arc(LEAD.mark.x,LEAD.mark.y,14+k*16,0,Math.PI*2);ctx.stroke();ctx.restore();}
'''
rep('function save(){if(WORLD.remote)return;', GROW_JS + '\nfunction save(){if(WORLD.remote)return;')

# waking words are charged and decided on the keeper, inside the spell command
rep('  const first=!S.vocab[text]&&!S.discovered.includes(text);if(first&&Object.keys(S.vocab).length<9000)S.vocab[text]=Date.now();\n  const rw=spellReward(v,text,first);',
    '  let wk=null;if(args.wake&&WAKE[text]){const W0=WAKE[text],why=W0.no&&W0.no();if(why)return R({ok:false,msg:why});if(v.sparks<W0.cost)return R({ok:false,msg:`Waking ${text} costs ${W0.cost} ✦. Spell more words to earn them.`});v.sparks-=W0.cost;wk=text;}\n  const first=!S.vocab[text]&&!S.discovered.includes(text);if(first&&Object.keys(S.vocab).length<9000)S.vocab[text]=Date.now();\n  const rw=spellReward(v,text,first);')
rep('const sp=startSpoken(text,p.ms,{by:"v",vk,first,n:rw.n,sd:p.sd});', 'const sp=startSpoken(text,p.ms,{by:"v",vk,first,n:rw.n,sd:p.sd});if(wk)sp.wake=wk;')
rep('sp.state="say";sp.sayAt=S.simT;', 'sp.state="say";sp.sayAt=S.simT;if(sp.wake)wakeDo(sp);')
rep('function sayIt(){', 'function sayIt(wake){')
rep('WX("spell",null,{text,ids:SPELL.ids,x:cam.x,y:cam.y},out,', 'WX("spell",null,{text,ids:SPELL.ids,x:cam.x,y:cam.y,wake:wake===true?1:0},out,')
rep('function renderTiles(){', 'function renderTiles(){wakeRow();')
rep('<p id="stMsg" class="st-msg" aria-live="polite"></p>', '<div id="stWake" class="st-row st-wake"></div><p id="stMsg" class="st-msg" aria-live="polite"></p>')
# ask a friend for the missing letter, from the spelling tray
rep('''${free?"(free)":`(${cost} ✦)`}</button></div>`;}''', '''${free?"(free)":`(${cost} ✦)`}</button><button type="button" class="st-chip" data-ask="${id.away.c}" data-for="${id.away.w}">Ask a friend</button></div>`;}''')
rep('el.innerHTML=h;el.querySelectorAll("[data-w]")', 'el.innerHTML=h;el.querySelectorAll("[data-ask]").forEach(b=>b.onclick=()=>askFriend(b.dataset.ask,b.dataset.for));el.querySelectorAll("[data-w]")')
# a friend's ask opens their page with a Send button; gifts arrive with the next claim
rep('const d=await pgCall("/page",p);if(d)pgShow(d);}', 'const d=await pgCall("/page",p);if(d)pgShow(d,p);}')
rep('function pgShow(d){', 'function pgShow(d,pid){const qs=new URLSearchParams(location.search),give=(qs.get("give")||"").toUpperCase(),gw=(qs.get("w")||"").toUpperCase();')
rep('''   <div class="actions"><button class="main" type="button" data-pg="play">Spell your own words</button>''',
    '''   ${/^[A-Z]$/.test(give)&&pid?`<div class="pg-ask"><p><b>They're one ${give} away${LEXSET.has(gw)?` from ${gw}`:""}.</b> Send them ${art(give)} ${give}, and you both get 10 ✦.</p><div class="actions"><button class="main" type="button" id="pgGive" data-pg="give" data-p="${pid}" data-c="${give}">Send ${art(give)} ${give}</button></div></div>`:""}
   <div class="actions"><button class="main" type="button" data-pg="play">Spell your own words</button>''')
rep('  else if(k==="share"){await pgPublish();pgShare();}});', '  else if(k==="share"){await pgPublish();pgShare();}\n  else if(k==="give"){b.disabled=true;sendGift(b.dataset.p,b.dataset.c);}});')
rep('''    note(`${r.n/5} new ${r.n===5?"person":"people"} opened your links: +${r.n} ✦`);dockTick();}}''',
    '''    note(`${r.n/5} new ${r.n===5?"person":"people"} opened your links: +${r.n} ✦`);dockTick();}
  if(Array.isArray(r.gifts)&&r.gifts.length){const v=vPlay(),gs=r.gifts.filter(c=>/^[A-Z]$/.test(c));v.gifts=(v.gifts||0)+gs.length;v.sparks+=10*gs.length;v.earned+=10*gs.length;
    setTimeout(()=>note(`${gs.length===1?"A friend":gs.length+" friends"} sent you ${listNames(gs.map(c=>art(c)+" "+c))}: +${10*gs.length} ✦, and ${gs.length===1?"a free letter":"free letters"} to bring.`),6500);dockTick();}}''')
# leading
rep('<button id="cDash">Your letters</button>', '<button id="cLead">Lead ${esc(a.name)}</button><button id="cDash">Your letters</button>')
rep('const db=document.getElementById("cDash");if(db)db.onclick=openDashboard;}', 'const db=document.getElementById("cDash");if(db)db.onclick=openDashboard;const lb=document.getElementById("cLead");if(lb)lb.onclick=()=>leadStart(a);}')
rep('if(best){if(SPELL.on)spellTap(best);', 'if(LEAD.on&&!SPELL.on&&(!best||best.id!==LEAD.id))leadTo(wx,wy);else if(best){if(SPELL.on)spellTap(best);')
rep('    case"say":case"await":return;', '    case"say":case"await":return;\n    case"led":if(S.simT>act.until||urgentNeed(a))done(a);return;')
rep('*(act.type==="flee"?1.6:act.type==="say"?1.9:1)', '*(act.type==="flee"?1.6:act.type==="say"?1.9:act.type==="led"?1.4:1)')
rep('    case"await":return`${a.name} has noticed you,', '    case"led":return`${a.name} is following the way a visitor showed.`;\n    case"await":return`${a.name} has noticed you,')
rep('drawSpoken(tAnim);drawSpellMarks(tAnim);', 'drawSpoken(tAnim);drawSpellMarks(tAnim);drawLead();')
rep('<div id="clipToast" role="status" hidden></div>', '<div id="clipToast" role="status" hidden></div>\n<div id="leadBar" role="status" hidden></div>')
rep('CLIP,clipStart,clipCan,PG,pgPublish,pgClaim}},', 'CLIP,clipStart,clipCan,PG,pgPublish,pgClaim,WAKE,LEAD,leadStart,leadTo}},')

GROW_CSS = r'''
.st-wake:empty{display:none}.st-wake span{flex:1;min-width:200px}
.pg-ask{background:#FFF3DF;border-radius:14px;padding:12px 14px;margin:12px 0}.pg-ask p{margin:0 0 10px}
#leadBar{position:fixed;left:50%;transform:translateX(-50%);top:calc(74px + env(safe-area-inset-top,0px));z-index:7;width:min(460px,calc(100% - 24px));display:flex;align-items:center;gap:10px;background:#1F2421;color:#F8F9F6;border-radius:16px;padding:8px 8px 8px 16px;box-shadow:0 6px 24px rgba(0,0,0,.3);font-size:15px}
#leadBar[hidden]{display:none}#leadBar span{flex:1}body.leading #hCard{top:calc(140px + env(safe-area-inset-top,0px))}
body.atlas-on #leadBar,body.broadcast #leadBar,body.filming #leadBar{display:none!important}
'''
i = s.rindex('</style>'); s = s[:i] + GROW_CSS + s[i:]
