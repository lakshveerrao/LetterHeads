# The world keeps living when nobody is there (28 September 2026). Lakshveer: "irrespective of someone there, the
# world should keep evolving... the players come and go, the game world keeps evolving."
#
# The letters' lives only run inside a browser that keeps the world (your own tab for your valley, one visitor's tab
# for The World), while the calendar, history and ages always follow the real clock. So whenever a keeper finds that
# the world last lived some time ago (it was closed, empty, or its tab was asleep), it first lives through all of
# that time, on a clock that runs from then to now, so births, words, discoveries and the Chronicle carry the times
# they really happened. A long gap is lived through faster than real time within a few seconds of work, so nothing
# is skipped. People coming back then get "While you were away" with what happened since their last visit.
# Run from assemble.py via exec(), after polish_patch.py.

LIVING_JS = r'''
var CATCHING=false;
const LIVING={dt:.1,min:30000,last:null,budget:gap=>Math.min(12000,3000+gap/3600e3*1500)};
function spanText(ms){const m=Math.round(ms/60000);if(m<60)return`${Math.max(1,m)} minute${m===1?"":"s"}`;const h=Math.round(ms/3600000);if(h<48)return`${h} hour${h===1?"":"s"}`;const d=Math.round(ms/86400000);return`${d} day${d===1?"":"s"}`;}
function livingNote(text,pct){const el=document.getElementById("livingNote");if(!el)return;if(text==null){el.hidden=true;return;}el.hidden=false;el.querySelector("span").textContent=text;el.querySelector("i").style.width=Math.round((pct||0)*100)+"%";}
async function catchUp(){if(CATCHING||!S)return;const gap=S.livedAt?Date.now()-S.livedAt:0;if(!S.livedAt||gap<LIVING.min){S.livedAt=Date.now();return;}
  CATCHING=true;const realNow=Date.now,music=Music.on,from=S.livedAt,t0=performance.now(),before={simT:S.simT};let vnow=from,lived=0;
  const who=WORLD.on&&WORLD.mode==="world"?"The World":WORLD.on&&WORLD.mode==="mine"?"Your valley":"The valley";
  const run=(ms,cap)=>{const end=performance.now()+ms;let n=0;Date.now=()=>Math.round(vnow);Music.on=false;
    try{while(performance.now()<end&&n<cap){step(LIVING.dt);n++;}}finally{Date.now=realNow;Music.on=music;}return n;};
  try{let n=0;const c0=performance.now();vnow=from;n=run(60,40);const per=Math.max(.05,(performance.now()-c0)/Math.max(1,n));
    const gapS=gap/1000,budget=LIVING.budget(gap),target=Math.min(gapS,budget/per*LIVING.dt),ratio=gapS/target;lived=n*LIVING.dt;vnow=from+lived*ratio*1000;
    livingNote(`${who} was left alone for ${spanText(gap)}. The letters are living through that time now.`,0);
    while(lived<target&&performance.now()-t0<budget*1.6){const k=run(120,Math.ceil((target-lived)/LIVING.dt));
      lived+=k*LIVING.dt;vnow=from+lived*ratio*1000;livingNote(`${who} was left alone for ${spanText(gap)}. The letters are living through that time now.`,lived/target);await new Promise(r=>setTimeout(r,0));}
    LIVING.last={gap,lived,ratio,ms:Math.round(performance.now()-t0),from};}
  catch(e){console.error(e);}
  finally{Date.now=realNow;Music.on=music;S.livedAt=Date.now();CATCHING=false;livingNote(null);if(WORLD.on&&WORLD.keeper)WORLD.snapNow();save();}}
// "While you were away": what happened in this world since this person last looked at it
let AWAY_FROM=null,AWAY_DONE=false;
function awayStart(){AWAY_FROM=(S.visitor&&S.visitor.seenAt)||0;}
function awayTick(){if(!AWAY_DONE||!S||!S.visitor||document.hidden)return;S.visitor.seenAt=Date.now();}
function yearsAt(t){const real=Date.now;Date.now=()=>t;try{return yearsAgo();}finally{Date.now=real;}}
function showAway(){if(AWAY_DONE)return;AWAY_DONE=true;const since=AWAY_FROM;const gap=since?Date.now()-since:0;
  if(!since||gap<10*60000){if(since){if(S.visitor.adopted.length)showWelcome();else showStoryToast();}return;}
  if(document.getElementById("intro").style.display!=="none")return;
  const words=S.words.filter(w=>w.state!=="forming"&&(w.bornReal||0)>since),born=S.agents.filter(a=>(a.born||0)>since),found=S.history.filter(h=>h.t>since&&h.kind==="discovery"),chaps=(S.chapters||[]).filter(c=>c.t>since);
  const y0=yearsAt(since),y1=yearsAgo(),moved=historyLabel(y0)!==historyLabel(y1);
  const lines=S.history.filter(h=>h.t>since).slice(-7).reverse();
  const ad=S.visitor.adopted.map(agentById).filter(Boolean);const seen=S.visitor.lastSeen||{};
  const comps=ad.map(a=>{const news=(a.mem||[]).filter(m=>m.t>(seen[a.id]||since)).slice(0,3);emote(a,"love",6);return`<div class="comp"><h4>${esc(a.name)} missed you</h4>${news.length?`<ul>${news.map(m=>`<li>${esc(m.text)}</li>`).join("")}</ul>`:`<p class="muted">A quiet time. Nothing new to tell.</p>`}</div>`;}).join("");
  const facts=[`${words.length} new word${words.length===1?"":"s"}`,`${born.length} new letter${born.length===1?"":"s"}`];if(found.length)facts.push(`${found.length} discover${found.length===1?"y":"ies"}`);if(chaps.length)facts.push(`${chaps.length} new chapter${chaps.length===1?"":"s"}`);
  const where=WORLD.on&&WORLD.mode==="world"?"The World":"This valley";
  openSheet(`<h2 id="sheetTitle">While you were away</h2><p class="muted">You were gone ${spanText(gap)}. ${where} kept living: ${facts.join(", ")}.${moved?` History moved on from ${esc(historyLabel(y0))} to ${esc(historyLabel(y1))}.`:""}</p>
    ${lines.length?`<ul class="away">${lines.map(h=>`<li><span class="muted">${esc(timeAgo(h.t))}</span> ${esc(h.text)}</li>`).join("")}</ul>`:""}${comps}
    <div class="actions"><button class="main" id="awGo">Carry on</button><button id="awStory">Story so far</button>${ad.length?`<button id="awDash">Your letters</button>`:""}</div>`,"welcome");
  document.getElementById("awGo").onclick=closeSheet;document.getElementById("awStory").onclick=openStory;const d=document.getElementById("awDash");if(d)d.onclick=openDashboard;}
'''

rep('function save(){if(WORLD.remote)return;', LIVING_JS + '\nfunction save(){if(WORLD.remote)return;')

# the keeper's frame: never step while catching up; notice when the world has not lived for a while (a closed or
# sleeping tab, an empty world) and catch up first; otherwise the world has lived until now
rep('acc+=dtReal*(WORLD.on?1:SPEED*(fxOn?.35:1));let n=0;while(acc>=.1&&n<80){step(.1);acc-=.1;n++;}}',
    'if(CATCHING)acc=0;else if(S.livedAt&&Date.now()-S.livedAt>LIVING.min){acc=0;catchUp();}else{acc+=dtReal*(WORLD.on?1:SPEED*(fxOn?.35:1));let n=0;while(acc>=.1&&n<80){step(.1);acc-=.1;n++;}S.livedAt=Date.now();}}')
rep('if(WORLD.on)WORLD.visitorTick();', 'awayTick();if(WORLD.on)WORLD.visitorTick();')

# nothing on screen or in the speakers from the time that is being lived through; moments are still kept
rep('function hint(k){if(S.settings.tips===false)return;', 'function hint(k){if(CATCHING||S.settings.tips===false)return;')
rep('function companionAsk(a){', 'function companionAsk(a){if(CATCHING)return;')
rep('function companionAlert(a,text){', 'function companionAlert(a,text){if(CATCHING)return;')
rep('function makeMoment(o){if(tour||ATL.on)return;',
    'function makeMoment(o){if(CATCHING){const last=S.moments[0];if(last&&Date.now()-last.t<20000&&o.score<95)return;S.moments.unshift({id:Date.now(),t:Date.now(),day:dayN(),text:o.text,sub:o.sub||"",kind:o.kind,chapter:era(),who:(o.main!=null&&agentById(o.main)?.name)||null});if(S.moments.length>120)S.moments.length=120;return;}if(tour||ATL.on)return;')
rep('if(!WORLD.on)if(S.simT>=(S.neglectAt||0))', 'if(!WORLD.on&&!CATCHING)if(S.simT>=(S.neglectAt||0))')
# The World: nothing is sent while catching up, and the caught-up world goes out at once
rep('function sendLive(){if(!W.keeper||!S)return;', 'function sendLive(){if(!W.keeper||!S||CATCHING)return;')
rep('async function sendSnap(){if(!W.keeper||!S)return;', 'async function sendSnap(){if(!W.keeper||!S||CATCHING)return;')
rep('W.ev=e=>{if(W.keeper&&!W.remote)evq.push(e);};', 'W.ev=e=>{if(W.keeper&&!W.remote&&!CATCHING)evq.push(e);};W.snapNow=()=>sendSnap();')

# on start: a keeper catches up before anything else; then everyone gets "While you were away"
rep('updateCaption();requestAnimationFrame(frame);if(loadedExisting)setTimeout(()=>{if(S.visitor.adopted.length)showWelcome();else showStoryToast();},2500);',
    'awayStart();updateCaption();if(loadedExisting&&!WORLD.mirror&&S.livedAt&&Date.now()-S.livedAt>LIVING.min)catchUp().then(()=>setTimeout(showAway,600));else setTimeout(showAway,2500);if(!S.livedAt&&!WORLD.mirror)S.livedAt=Date.now();requestAnimationFrame(frame);')
rep("</style>", """#livingNote{position:fixed;left:50%;transform:translateX(-50%);top:calc(126px + env(safe-area-inset-top,0px));z-index:30;background:#1F2421;color:#F8F9F6;border-radius:14px;padding:10px 16px 12px;font-size:14px;font-weight:700;max-width:calc(100% - 24px);width:420px;box-shadow:0 6px 24px rgba(0,0,0,.3);pointer-events:none}
#livingNote b{display:block;height:4px;margin-top:8px;border-radius:2px;background:rgba(248,249,246,.2);overflow:hidden}#livingNote i{display:block;height:100%;width:0;background:#E8962F;transition:width .3s}
#livingNote[hidden]{display:none!important}body.broadcast #livingNote{display:none!important}
.away{padding-left:18px;margin:10px 0}.away li{margin:6px 0}.away .muted{font-size:12px;margin-right:4px}
</style>""")
rep('<button class="float" id="storyToast"></button>', '<div id="livingNote" hidden role="status"><span></span><b><i></i></b></div><button class="float" id="storyToast"></button>')
rep('window.__lango={get world(){return WORLD},', 'window.__lango={get world(){return WORLD},get living(){return LIVING},')
