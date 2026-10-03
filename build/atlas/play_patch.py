# Playing with your letters (3 October 2026). Lakshveer: people should really play, earn sparks by taking part, and
# spend them to grow their world; dead simple to understand, yet hard to put down. The whole game in three lines:
#   1. Spell a word: tap letters, or type it. Your letters ask the others, and if they agree, they say it.
#   2. Every word earns sparks: longer words more, new words double, world firsts five times, quick words in a row
#      climb a combo, and words the world needs right now earn triple.
#   3. Spend sparks to grow: bring the letter you're missing; every spark also fills one level bar that opens more.
# Spoken words are new: any letters can say a word together for a moment and then go back to their lives, so words
# are no longer limited by families. Every word said joins the world's vocabulary, and letters later say those words
# on their own. The old standing, tiers and star rating fold into the level bar. Phones get a slim one-line caption.
# Run from assemble.py via exec(), after quiet_patch.py and before broadcast_patch.py.

LEX = open(O + '../play/lexicon.txt').read().strip()
rep('<script>\n(()=>{', '<script type="text/plain" id="lexicon">' + LEX + '</script>\n<script>\n(()=>{')

PLAY_JS = r'''
// ================= play: spell words, earn sparks, grow =================
const LEX=document.getElementById("lexicon").textContent.split("\n"),LEXSET=new Set(LEX);
const NEEDS={water:{n:"water",w:"WATER RAIN RIVER LAKE POND DRINK WELL SPRING STREAM WAVE SEA OCEAN SHORE WET SPLASH SWIM ICE SNOW FLOW BROOK CREEK TIDE MIST DEW CUP"},
  food:{n:"food",w:"FOOD FRUIT BERRY NUT EAT MEAL SEED ROOT FISH EGG HONEY APPLE PLUM FIG GRAIN BREAD SOUP FEAST HUNT GATHER PICK RIPE CORN BEAN RICE PEAR"},
  warmth:{n:"warmth",w:"FIRE WARM HEAT SUN FLAME BURN EMBER COAL GLOW LIGHT TORCH HEARTH COAT FUR WOOL HUT HOME ROOF SHELTER BLANKET WOOD LOG SPARK"},
  rest:{n:"rest",w:"REST SLEEP BED NAP DREAM CALM QUIET NEST SHADE NIGHT MOON STAR DOZE PILLOW EASE PEACE STILL SOFT SAFE"},
  friends:{n:"friendship",w:"FRIEND HUG LOVE CARE JOY KIND HELP SHARE GIFT SMILE LAUGH PLAY SING DANCE HOPE TRUST HAND HEART TOGETHER FAMILY BOND"},
  explore:{n:"discovery",w:"PATH TRAIL MAP HILL CLIMB WALK RUN FIND SEEK LOOK EYE SKY CAVE STONE ROCK TOOL ROPE BRIDGE RAFT NEW WILD JOURNEY"}};
for(const k in NEEDS){NEEDS[k].list=NEEDS[k].w.split(" ").filter(w=>LEXSET.has(w));NEEDS[k].set=new Set(NEEDS[k].list);}
function needNow(){const as=S.agents.filter(a=>!a.young);if(!as.length)return"explore";const av=k=>as.reduce((t,a)=>t+(a[k]||0),0)/as.length;
  const sc={water:av("thirst"),food:av("hunger"),rest:1-av("energy"),friends:(1-av("social"))*.8,warmth:nightAlpha()>.2||season()==="winter"?.62:0};
  let best="explore",bv=.45;for(const k in sc)if(sc[k]>bv){bv=sc[k];best=k;}return best;}
const glowKey=()=>(S.glow&&NEEDS[S.glow.k])?S.glow.k:"explore",glowSet=()=>NEEDS[glowKey()].set;
// the visitor's play record: sparks to spend, sparks ever earned (the level), and the words they have spelled
function vPlay(v){v=v||S.visitor;if(!v.words||typeof v.words!=="object"||Array.isArray(v.words))v.words={};if(typeof v.earned!=="number")v.earned=Math.max(0,v.sparks||0);
  if(!Array.isArray(v.firsts))v.firsts=[];v.combo=v.combo||0;v.lastWordAt=v.lastWordAt||0;return v;}
const LV=n=>10*n*(n-1);
function levelOf(e){let L=1;while(L<99&&LV(L+1)<=e)L++;return L;}
const maxCompanions=L=>3+(L>=4)+(L>=7)+(L>=10);
const LEVEL_OPENS={2:"sharing ideas and encouraging your companions to explore",3:"asking companions to teach",4:"a 4th companion",5:"backing a family's work",7:"a 5th companion",10:"a 6th companion"};
const nextOpen=L=>{for(let n=L+1;n<=10;n++)if(LEVEL_OPENS[n])return[n,LEVEL_OPENS[n]];return null;};
// sparks your companions earn on their own: at most 50 a day, so playing always pays more than waiting
function passiveAdd(n,text){const v=vPlay();const day=new Date().toDateString();if(!v.passive||v.passive.d!==day)v.passive={d:day,n:0};const k=Math.max(0,Math.min(n,50-v.passive.n));if(!k)return 0;
  v.passive.n+=k;v.sparks+=k;v.earned+=k;v.sparkLog.unshift({t:Date.now(),n:k,text});if(v.sparkLog.length>60)v.sparkLog.length=60;return k;}
// ---------- spoken words: letters come together, say a word, and go back to their lives ----------
const canSay=a=>a&&a.crossing==null&&!(a.act&&(a.act.type==="say"||a.act.type==="flee"))&&!(S.spoken||[]).some(s=>s.ids.includes(a.id));
function sayYes(a,v){const fond=((v.trustIn||{})[a.id])||0;
  if(a.sleeping)return[rnd()<.3,`${a.name} is asleep`];if(a.hurt>S.simT)return[rnd()<.35,`${a.name} is hurt`];
  if(urgentNeed(a))return[rnd()<.25,a.thirst>.75?`${a.name} is too thirsty`:a.hunger>.75?`${a.name} is too hungry`:`${a.name} is too tired`];
  const p=.8+fond*.15+(a.joy-.5)*.15+(v.adopted.includes(a.id)?.15:0)-(a.young?.1:0)-((a.tr&&a.tr.caution)||0)*.08;return[rnd()<p,`${a.name} wants to do something else right now`];}
function landSide(p){let sd=side(p.x,p.y);if(sd<0){const k=nearestCell(p,k=>!MAP.water[k],30);if(k>=0){const c=cellCenter(k);p.x=c.x;p.y=c.y;sd=MAP.comp[k];}}return sd;}
// choose who says each letter: the letters the person tapped, or the nearest free ones; each decides for itself
function pickFor(text,ids,anchor,v){const used=new Set(),given=(ids||[]).map(id=>id!=null?agentById(+id):null),refused=[];
  const fixed=given.filter((a,i)=>a&&a.ch===text[i]&&canSay(a));const c0=fixed.length?{x:fixed.reduce((t,a)=>t+a.x,0)/fixed.length,y:fixed.reduce((t,a)=>t+a.y,0)/fixed.length}:{x:anchor.x,y:anchor.y};
  const sd=landSide(c0);const ms=[];
  for(let i=0;i<text.length;i++){const c=text[i],g=given[i]&&given[i].ch===c&&canSay(given[i])&&!used.has(given[i].id)?given[i]:null;
    const near=S.agents.filter(a=>a!==g&&a.ch===c&&!used.has(a.id)&&canSay(a)&&side(a.x,a.y)===sd&&Math.hypot(a.x-c0.x,a.y-c0.y)<1600).sort((p,q)=>Math.hypot(p.x-c0.x,p.y-c0.y)-Math.hypot(q.x-c0.x,q.y-c0.y));
    const cands=(g?[g]:[]).concat(near).slice(0,3);if(!cands.length)return{missing:c};let got=null;
    for(const a of cands){const[yes,why]=sayYes(a,v);if(yes){got=a;break;}refused.push(why);}
    if(!got)return{fail:true,refused};ms[i]=got;used.add(got.id);}
  return{ms,refused,sd};}
function startSpoken(text,ms,o){S.spoken=S.spoken||[];const sd=o.sd!=null?o.sd:side(ms[0].x,ms[0].y);
  const G={x:ms.reduce((t,m)=>t+m.x,0)/ms.length,y:ms.reduce((t,m)=>t+m.y,0)/ms.length};
  if(side(G.x,G.y)!==sd){const k=nearestCell(G,k=>!MAP.water[k]&&MAP.comp[k]===sd,30);if(k>=0){const c=cellCenter(k);G.x=c.x;G.y=c.y;}}
  G.x=clamp(G.x,200,WORLD_W-200);G.y=clamp(G.y,240,WORLD_H-120);
  const sp={id:nextId++,text,ids:ms.map(m=>m.id),x:G.x,y:G.y,t0:S.simT,state:"gather",by:o.by,vk:o.vk||null,first:!!o.first,n:o.n||0};S.spoken.push(sp);
  ms.forEach((m,i)=>{const tx=G.x+(i-(ms.length-1)/2)*54,ty=G.y;done(m);m.sleeping=false;m.act={type:"say",sp:sp.id,tx,ty,t:0,wp:route(m,tx,ty)||[],arrived:false};
    ms.forEach(o2=>{if(o2!==m)bond(m,o2,.03);});});
  return sp;}
function spellReward(v,text,first){const now=Date.now(),mine=!v.words[text],glow=glowSet().has(text);let n=text.length;const parts=[`${text.length} letters`];
  if(mine){v.combo=now-v.lastWordAt<60000?Math.min(3,v.combo+1):1;n*=2;parts.push("new to you ×2");}else{v.combo=now-v.lastWordAt<60000?v.combo:0;n=Math.max(1,Math.floor(n/2));parts.push("said before, half");}
  v.lastWordAt=now;if(first){n*=5;parts.push("first in the world ×5");}if(glow){n*=3;parts.push("the world needs it ×3");}if(v.combo>1){n*=v.combo;parts.push(`combo ×${v.combo}`);}
  n=Math.min(n,600);v.sparks+=n;v.earned+=n;v.words[text]=now;const ks=Object.keys(v.words);if(ks.length>4000)for(const k of ks.sort((p,q)=>v.words[p]-v.words[q]).slice(0,ks.length-4000))delete v.words[k];
  if(first){v.firsts.unshift(text);if(v.firsts.length>200)v.firsts.length=200;}
  v.sparkLog.unshift({t:now,n,text:`You spelled ${text}`});if(v.sparkLog.length>60)v.sparkLog.length=60;return{n,parts,combo:v.combo,mine,glow};}
CMD.spell=(a0,args,out)=>{const v=vPlay(S.visitor);S.spoken=S.spoken||[];S.vocab=S.vocab||{};const text=String(args.text||"").toUpperCase().slice(0,12);
  const R=o=>{out.innerHTML=`<span data-r="${esc(JSON.stringify(o))}">${esc(o.msg||"")}</span>`;};
  if(!/^[A-Z]{3,12}$/.test(text)||!LEXSET.has(text))return R({ok:false,msg:`${text||"That"} isn't a word the letters know.`});
  const vk=WORLD.from||"me";if(S.spoken.some(s=>s.vk===vk&&s.state==="gather"&&S.simT-s.t0<20))return R({ok:false,wait:true,msg:"Your last word is still coming together."});
  if(S.spoken.length>=14)return R({ok:false,msg:"Lots of words are being said right now. Try again in a moment."});
  const ax=+args.x,ay=+args.y,anchor={x:Number.isFinite(ax)?clamp(ax,0,WORLD_W):cam.x,y:Number.isFinite(ay)?clamp(ay,0,WORLD_H):cam.y};
  const ids=Array.isArray(args.ids)?args.ids.slice(0,12).map(x=>Number.isFinite(+x)&&x!==null?+x:null):[];
  const p=pickFor(text,ids,anchor,v);
  if(p.missing){const late=LATE[p.missing]&&!S.lateBorn?.[p.missing];return R({ok:false,missing:p.missing,late:!!late,msg:late?`There is no ${p.missing} in the world yet. It hasn't been invented.`:`There's no ${p.missing} free nearby.`});}
  if(p.fail)return R({ok:false,refused:p.refused,msg:`${p.refused.slice(-2).join(", and ")}. Try other letters, or try again soon.`});
  const first=!S.vocab[text]&&!S.discovered.includes(text);if(first&&Object.keys(S.vocab).length<9000)S.vocab[text]=Date.now();
  const rw=spellReward(v,text,first);const names=p.ms.map(m=>m.name);
  const sp=startSpoken(text,p.ms,{by:"v",vk,first,n:rw.n,sd:p.sd});
  p.ms.forEach(m=>{remember(m,`A visitor asked me to say ${text} with ${listNames(names.filter(n=>n!==m.name))}.`);(v.trustIn=v.trustIn||{})[m.id]=clamp(((v.trustIn[m.id])||0)+.03,-1,1);});
  if(first)chron(`${listNames(names)} said ${text}, because a visitor spelled it. No one in the world had ever said ${text} before.`,"word");
  addStory({kind:"spoken",sp:sp.id,ids:sp.ids,text:`${listNames(names)} are coming together to say ${text}.`,sub:first?"No one in the world has ever said this word before.":"A visitor spelled it, and they agreed.",score:first?90:74,dur:14,main:sp.ids[0]});
  if(!WORLD.remote)save();
  R({ok:true,id:sp.id,n:rw.n,parts:rw.parts,first,combo:rw.combo,glow:rw.glow,names,msg:`${listNames(names)} agreed.`});};
CMD.await=(a0,args,out)=>{const ids=Array.isArray(args.ids)?args.ids.slice(0,3):[];for(const id of ids){const a=agentById(+id);if(!a||!canSay(a)||urgentNeed(a)||a.crossing!=null||(a.act&&a.act.type==="meet"))continue;
  done(a);a.act={type:"await",tx:a.x,ty:a.y,t:0,wp:[],arrived:true,until:S.simT+30};emote(a,"wonder",4);}};
// letters use the words the world has learned, on their own
function selfSay(){const V=Object.keys(S.vocab||{});if(V.length<2)return;const free=S.agents.filter(a=>!a.young&&canSay(a)&&!urgentNeed(a)&&!a.sleeping&&!(a.act&&a.act.type==="meet"));if(free.length<3)return;
  const a=free[Math.floor(rnd()*free.length)];const near=free.filter(b=>dist(a,b)<560&&side(b.x,b.y)===side(a.x,a.y));
  for(let k=0;k<80;k++){const w=V[Math.floor(rnd()*V.length)];if(w.length>6||!w.includes(a.ch))continue;const pool=[a,...near.filter(b=>b!==a)],ms=[];let ok=true;
    for(const c of w){const i=pool.findIndex(b=>b.ch===c);if(i<0){ok=false;break;}ms.push(pool[i]);pool.splice(i,1);}if(!ok)continue;
    const sp=startSpoken(w,ms,{by:"self"});S.selfSaid=S.selfSaid||{};const names=ms.map(m=>m.name);
    if(!S.selfSaid[w]){S.selfSaid[w]=1;chron(`${listNames(names)} said ${w} on their own. They learned it from a word a visitor taught the world.`,"word");}
    ms.forEach(m=>remember(m,`We said ${w} together, ${listNames(names.filter(n=>n!==m.name))} and I.`));
    addStory({kind:"spoken",sp:sp.id,ids:sp.ids,text:`${listNames(names)} are getting together to say ${w}.`,sub:"Nobody asked them. It's a word they learned.",score:66,dur:12,main:sp.ids[0]});return;}}
function spokenTick(){S.spoken=S.spoken||[];for(const a of S.agents)if(a.act&&a.act.type==="await"&&(S.simT>a.act.until||urgentNeed(a)))done(a);
  if(S.simT>=(S.glowAt||0)){S.glowAt=S.simT+30;S.glow={k:needNow()};}
  for(const sp of[...S.spoken]){const ms=sp.ids.map(agentById);
    if(sp.state==="gather"){const all=ms.every(m=>!m||!m.act||m.act.sp!==sp.id||m.act.arrived||Math.hypot(m.x-m.act.tx,m.y-m.act.ty)<40);
      if(all||S.simT-sp.t0>40){sp.state="say";sp.sayAt=S.simT;ms.forEach(m=>{if(!m)return;m.joy=Math.min(1,m.joy+.15);m.social=Math.min(1,m.social+.25);emote(m,"joy",5);});
        if(sp.by!=="self"||rnd()<.5)Music.wordChord(sp.text);endStories(s=>s.sp===sp.id);}}
    else if(S.simT-sp.sayAt>6||S.simT-sp.t0>80){ms.forEach(m=>{if(m&&m.act&&m.act.sp===sp.id)done(m);});S.spoken.splice(S.spoken.indexOf(sp),1);}}
  if(S.simT>=(S.selfSayAt||0)){S.selfSayAt=S.simT+55+rnd()*45;if(!WORLD.mirror)selfSay();}}
function drawSpoken(t){for(const sp of S.spoken||[]){if(!inView(sp.x,sp.y,500))continue;ctx.save();
    if(sp.state==="gather"){ctx.strokeStyle="rgba(232,150,47,.75)";ctx.lineWidth=2.5/Math.max(.6,cam.z);ctx.setLineDash([7,7]);ctx.lineDashOffset=-t*30;
      for(const id of sp.ids){const m=agentById(id);if(!m||!m.act||m.act.sp!==sp.id)continue;ctx.beginPath();ctx.moveTo(m.x+10*K,m.y-30*K);ctx.lineTo(m.act.tx+10*K,m.act.ty-30*K);ctx.stroke();}
      ctx.setLineDash([]);ctx.font="600 36px Spectral, Georgia, serif";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillStyle="rgba(31,36,33,.38)";ctx.fillText(sp.text+"…",sp.x+10*K,sp.y-150);}
    else{const e=S.simT-sp.sayAt,k=clamp(e/.5,0,1),fade=clamp((6-e)/1.2,0,1),s=1+.35*Math.sin(k*Math.PI)*(1-k*.4);ctx.globalAlpha=fade;
      for(const id of sp.ids){const m=agentById(id);if(!m)continue;const g=ctx.createRadialGradient(m.x+10*K,m.y-40*K,4,m.x+10*K,m.y-40*K,70);g.addColorStop(0,"rgba(255,190,90,.45)");g.addColorStop(1,"rgba(255,190,90,0)");ctx.fillStyle=g;ctx.fillRect(m.x+10*K-70,m.y-40*K-70,140,140);}
      ctx.font=`700 ${Math.round(56*s)}px Spectral, Georgia, serif`;ctx.textAlign="center";ctx.textBaseline="middle";ctx.lineJoin="round";
      ctx.shadowColor="rgba(232,150,47,.9)";ctx.shadowBlur=26;ctx.lineWidth=8;ctx.strokeStyle="#1F2421";ctx.strokeText(sp.text,sp.x+10*K,sp.y-150);ctx.fillStyle="#FFF4E2";ctx.fillText(sp.text,sp.x+10*K,sp.y-150);ctx.shadowBlur=0;
      if(sp.first){ctx.font="700 15px 'Atkinson Hyperlegible', sans-serif";ctx.fillStyle="#E8962F";ctx.fillText("FIRST IN THE WORLD",sp.x+10*K,sp.y-198);}}
    ctx.restore();}}
// ---------- the spell tray, the dock, the coach ----------
const SPELL={on:false,ids:[],mine:new Map(),lastIdeas:0,shown:null};
const PLAY_KEY="letterheads_play_v1";let TUT=(()=>{try{return JSON.parse(localStorage.getItem(PLAY_KEY)||"null")||{step:0};}catch(e){return{step:0};}})();
const tutSave=()=>{try{localStorage.setItem(PLAY_KEY,JSON.stringify(TUT));}catch(e){}};
const tutOn=()=>TUT.step>0&&TUT.step<9;
const $p=id=>document.getElementById(id);
function pendingSparks(){let n=0;for(const m of SPELL.mine.values())if(!m.seen)n+=m.n;return n;}
function dockTick(){const v=vPlay(),shown=Math.max(0,v.sparks-pendingSparks()),earned=Math.max(0,v.earned-pendingSparks()),L=levelOf(earned);
  $p("pdN").textContent=shown;$p("pdLv").textContent=`Level ${L}`;$p("pdBar").style.width=Math.round(clamp((earned-LV(L))/(LV(L+1)-LV(L)),0,1)*100)+"%";
  if(SPELL.shown&&L>SPELL.shown.L)levelUp(L);SPELL.shown={L};
  const cb=$p("pdCombo"),left=60000-(Date.now()-v.lastWordAt);if(v.combo>1&&left>0){cb.hidden=false;cb.querySelector("b").textContent=`Combo ×${v.combo}`;cb.querySelector("i i").style.width=Math.round(left/600)+"%";}else cb.hidden=true;const sc=$p("stCombo");sc.hidden=cb.hidden;if(!cb.hidden)sc.textContent=`×${v.combo} · ${Math.ceil(left/1000)}s`;}
function levelUp(L){const o=LEVEL_OPENS[L];const el=$p("lvToast");el.innerHTML=`<b>Level ${L}</b>${o?`<span>Opens ${esc(o)}</span>`:`<span>Keep spelling.</span>`}`;el.hidden=false;el.classList.remove("go");void el.offsetWidth;el.classList.add("go");
  setTimeout(()=>{el.hidden=true;},3600);if(Music.on&&Music.discovery)try{Music.discovery();}catch(e){}}
function availHere(){return S.agents.filter(a=>inView(a.x,a.y,60)&&canSay(a)&&!a.young);}
function countsOf(list){const c=new Array(26).fill(0);for(const a of list)c[a.ch.charCodeAt(0)-65]++;return c;}
function missingFor(w,c){const need=new Array(26).fill(0);let miss=null,n=0;for(const ch of w){const i=ch.charCodeAt(0)-65;need[i]++;if(need[i]>c[i]){n++;miss=ch;if(n>1)return[2,null];}}return[n,miss];}
function ideas(){const v=vPlay(),av=availHere(),c=countsOf(av),out={can:[],away:null,glow:[]};const gs=glowSet();
  for(const w of NEEDS[glowKey()].list){const[n]=missingFor(w,c);if(n===0)out.glow.push(w);if(out.glow.length>=3)break;}
  for(let i=0;i<LEX.length&&i<20000;i++){const w=LEX[i];if(w.length>7)continue;const[n,miss]=missingFor(w,c);
    if(PLAIN.has(w))continue;if(n===0&&!v.words[w]&&out.can.length<4&&!gs.has(w))out.can.push(w);
    else if(n===1&&!out.away&&w.length>=4&&w.length<=6&&i<9000&&!v.words[w]&&!(LATE[miss]&&!S.lateBorn?.[miss]))out.away={w,c:miss};
    if(out.can.length>=4&&out.away)break;}
  return out;}
function renderIdeas(){if(!SPELL.on)return;SPELL.lastIdeas=tAnim;const v=vPlay(),id=ideas(),el=$p("stIdeas");const gk=NEEDS[glowKey()];let h="";
  const chip=w=>`<button type="button" class="st-chip${glowSet().has(w)?" glow":""}" data-w="${w}">${w}</button>`;
  if(id.glow.length)h+=`<div class="st-row"><span class="st-k">The world needs ${esc(gk.n)} words, ×3:</span>${id.glow.map(chip).join("")}</div>`;
  else h+=`<div class="st-row"><span class="st-k">Words about ${esc(gk.n)} earn ×3 right now, like ${gk.list.slice(0,3).join(", ")}.</span></div>`;
  if(id.can.length)h+=`<div class="st-row"><span class="st-k">You could spell:</span>${id.can.map(chip).join("")}</div>`;
  if(id.away){const free=v.gifts>0,cost=GIFT_COST,ok=free||v.sparks>=cost;h+=`<div class="st-row"><span class="st-k">You're one ${id.away.c} away from <b>${id.away.w}</b>.</span><button type="button" class="st-chip get" data-get="${id.away.c}" data-for="${id.away.w}" ${ok?"":"disabled"}>Bring ${art(id.away.c)} ${id.away.c} ${free?"(free)":`(${cost} ✦)`}</button></div>`;}
  el.innerHTML=h;el.querySelectorAll("[data-w]").forEach(b=>b.onclick=()=>{setSpell(b.dataset.w,[]);});
  el.querySelectorAll("[data-get]").forEach(b=>b.onclick=()=>bringLetter(b.dataset.get,b.dataset.for));}
function bringLetter(c,forWord){const out=document.createElement("div");const msg=$p("stMsg");msg.textContent=`Calling ${art(c)} ${c}…`;
  WX("gift",null,{c,x:cam.x,y:cam.y+80},out,()=>{const t=out.textContent;if(t){msg.textContent=t;return;}msg.textContent=`${art(c)==="an"?"An":"A"} ${c} is on the way.${forWord?` Spell ${forWord} when it arrives.`:""}`;if(forWord)setSpell(forWord,[]);
    if(TUT.step===3){TUT.step=4;TUT.want=forWord;tutSave();coach(`Here comes your ${c}. Now spell ${forWord}.`);}renderIdeas();});}
const PLAIN=new Set("THE AND FOR THAT YOU THIS WITH WAS ARE HAVE NOT BUT FROM THEY HIS HER SHE HIM ITS OUR OUT ALL CAN HAS HAD WHO WHAT WHEN WHERE WHICH WILL WOULD THERE THEIR THEM THEN THAN THESE THOSE BEEN WERE ANY SOME SUCH VERY JUST ALSO INTO ONLY OVER YOUR MORE MOST MUCH MANY EACH SAME BOTH DOES DID DOING BEING ABOUT AFTER AGAIN ONCE HERE HOW WHY OFF OWN SHOULD COULD MAY MIGHT MUST SHALL YET NOR".split(" "));
const EASY=new Set("SUN SEA ANT EAT TEA RED HAT TOP NET TEN HOT ONE RUN SIT EGG ICE ART OAK OWL FUN JOY HUG MAP CUP BOX FOX BEE EYE EAR ARM LEG KEY DAY SKY CAT DOG PEN PIN TIN RAT MAT NUT HEN DEN POT DOT WET YES SON BAT BED BUS CAR COW FAN FIG HAM JAM LID MUD NAP OLD PET RUG SAD TOY VAN WEB ZOO AIR ASH BIG BOW DEW DIG EGO ELF END FIN FLY GEM GUM HAY HIP HOP INK JET KIT LAP LOG MIX NOD OAR OWN PAN PEA PIG RAY RIB ROD ROW SAW SEW SHY SKI SOW SPY TAP TOE TUB URN WAX WIN YAK YAM".split(" "));
function setSpell(text,ids){text=String(text||"").toUpperCase().replace(/[^A-Z]/g,"").slice(0,12);SPELL.ids=[...text].map((ch,i)=>{const a=ids[i]!=null?agentById(ids[i]):null;return a&&a.ch===ch?a.id:null;});
  const inp=$p("stIn");if(inp.value!==text)inp.value=text;renderTiles();}
function renderTiles(){const text=$p("stIn").value,ok=text.length>=3&&LEXSET.has(text),el=$p("stTiles");
  el.innerHTML=text?[...text].map((ch,i)=>`<span class="st-tile${SPELL.ids[i]!=null?" picked":""}">${ch}</span>`).join(""):`<span class="st-ph">Tap letters in the world, or type a word</span>`;
  el.classList.toggle("real",ok);$p("stSay").disabled=!ok;$p("stSay").textContent=ok?`Say ${text}`:"Say it";
  const m=$p("stMsg");if(text.length>=3&&!ok){m.textContent=`${text} isn't a word yet. Keep going.`;SPELL.soft=true;}else if(SPELL.soft){m.textContent="";SPELL.soft=false;}}
function spellTap(a){const inp=$p("stIn");const i=SPELL.ids.indexOf(a.id);let t=inp.value,ids=[...SPELL.ids];
  if(i>=0){t=t.slice(0,i)+t.slice(i+1);ids.splice(i,1);}else{if(t.length>=12)return;t+=a.ch;ids.push(a.id);}
  inp.value=t;SPELL.ids=ids;renderTiles();emote(a,"wonder",2);}
function frameOn(list){if(!list.length)return;let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;for(const a of list){x0=Math.min(x0,a.x);x1=Math.max(x1,a.x+20);y0=Math.min(y0,a.y-90);y1=Math.max(y1,a.y);}
  const co=$p("coach"),trayH=Math.min(H*.5,innerWidth<=600?330:280),top=co.hidden?(innerWidth<=600?70:80):co.getBoundingClientRect().bottom+8,availH=Math.max(160,H-trayH-top-20),z=clamp(Math.min((W-80)/(x1-x0+160),availH/(y1-y0+180)),Math.max(minZ(),.75),1.35);
  const sy=top+availH/2;SPELL.glide={x:(x0+x1)/2,y:(y0+y1)/2+(H/2-sy)/z,z,t:0};}
function frameNear(){const av=S.agents.filter(a=>canSay(a)&&!a.young).sort((p,q)=>Math.hypot(p.x-cam.x,p.y-cam.y)-Math.hypot(q.x-cam.x,q.y-cam.y)).slice(0,9);frameOn(av);}
function openSpell(focus,noFrame){if(ATL.on||tour)return;const was=SPELL.on;SPELL.on=true;document.body.classList.add("spelling");$p("spellTray").hidden=false;takeControl();if(!was&&!noFrame)frameNear();renderTiles();renderIdeas();if(focus)$p("stIn").focus();}
function closeSpell(){SPELL.on=false;document.body.classList.remove("spelling");$p("spellTray").hidden=true;}
function sayIt(){const text=$p("stIn").value;if(!(text.length>=3&&LEXSET.has(text)))return;const out=document.createElement("div"),msg=$p("stMsg");$p("stSay").disabled=true;
  WX("spell",null,{text,ids:SPELL.ids,x:cam.x,y:cam.y},out,()=>{const el=out.querySelector("[data-r]");let r=null;try{r=el&&JSON.parse(el.dataset.r);}catch(e){}
    if(!r){msg.textContent=out.textContent||"The world is busy. Try again.";renderTiles();return;}
    if(r.ok){SPELL.mine.set(r.id,{n:r.n,parts:r.parts,first:r.first,combo:r.combo,at:Date.now(),seen:false});msg.textContent=`${r.msg} Watch them say it.`;setSpell("",[]);
      if(TUT.step===1){TUT.step=2;tutSave();coach("They're coming together. Every word earns sparks ✦.");}else if(TUT.step===2){TUT.step=3;tutSave();}else if(TUT.step===4&&(!TUT.want||text===TUT.want)){TUT.step=5;tutSave();}}
    else{msg.textContent=r.msg;if(r.missing&&!r.late){const v=vPlay(),free=v.gifts>0;msg.innerHTML=`${esc(r.msg)} <button type="button" class="st-chip get" id="stGet" ${free||v.sparks>=GIFT_COST?"":"disabled"}>Bring ${art(r.missing)} ${r.missing} ${free?"(free)":`(${GIFT_COST} ✦)`}</button>`;$p("stGet").onclick=()=>bringLetter(r.missing,text);}renderTiles();}
    renderIdeas();dockTick();});}
// sparks burst out when the letters actually say your word
function burstAt(x,y,m){const b=document.createElement("div");b.className="burst";b.style.left=x+"px";b.style.top=y+"px";
  b.innerHTML=`<b>+${m.n} ✦</b>${m.first?`<span class="gold">First in the world</span>`:""}<span>${esc(m.parts.join(" · "))}</span>`;document.body.appendChild(b);setTimeout(()=>b.remove(),2600);
  const dk=$p("pdSparks").getBoundingClientRect();for(let i=0;i<Math.min(14,4+m.n/4);i++){const p=document.createElement("i");p.className="bpart";p.textContent="✦";p.style.left=x+(Math.random()-.5)*80+"px";p.style.top=y+(Math.random()-.5)*40+"px";document.body.appendChild(p);
    requestAnimationFrame(()=>{p.style.transitionDelay=(i*40)+"ms";p.style.transform=`translate(${dk.left+30-x}px,${dk.top+20-y}px) scale(.6)`;p.style.opacity="0";});setTimeout(()=>p.remove(),1500+i*40);}}
function playFrame(){if(!S)return;const sp=S.spoken||[];
  if(SPELL.glide){const g=SPELL.glide,now=performance.now();g.t=g.s?(now-g.s)/1000:(g.s=now,0);const k=Math.min(1,g.t/.8),e=k*k*(3-2*k);if(!g.f)g.f={x:cam.x,y:cam.y,z:cam.z};cam.x=lerp(g.f.x,g.x,e);cam.y=lerp(g.f.y,g.y,e);cam.z=lerp(g.f.z,g.z,e);if(k>=1)SPELL.glide=null;}
  for(const[id,m]of SPELL.mine){if(m.seen)continue;const s=sp.find(x=>x.id===id);
    if(s&&s.state==="say"){m.seen=true;const[x,y]=w2s(s.x+10*K,s.y-150);const on=x>0&&x<W&&y>0&&y<H;burstAt(on?x:W/2,on?y:H*.4,m);setTimeout(dockTick,900);
      if(TUT.step===2&&!TUT.saidFirst){TUT.saidFirst=1;tutSave();coach(`+${m.n} ✦ for your first word! Now spell any word you like. Quick words in a row earn more.`);}
      else if(TUT.step===3&&!TUT.saidSecond){TUT.saidSecond=1;tutSave();coach(m.combo>1?`Combo ×${m.combo}! Words within a minute of each other keep multiplying.`:"Every new word you spell earns double.");setTimeout(tutAway,4500);}
      else if(TUT.step===5)tutEnd();}
    else if(!s&&Date.now()-m.at>3000||Date.now()-m.at>45000){m.seen=true;burstAt(W/2,H*.45,m);setTimeout(dockTick,900);}}
  for(const[id,m]of SPELL.mine)if(m.seen&&Date.now()-m.at>60000)SPELL.mine.delete(id);
  if(SPELL.on&&tAnim-SPELL.lastIdeas>4)renderIdeas();
  }
function tutAway(){if(TUT.step!==3)return;const id=ideas();if(id.away&&vPlay().gifts>0){coach(`You're one ${id.away.c} away from ${id.away.w}. Bring ${art(id.away.c)} ${id.away.c}: your first one is free.`);if(!SPELL.on)openSpell(false);renderIdeas();}
  else tutEnd();}
function tutEnd(){TUT.step=6;tutSave();coach("That's the whole game. Your letters keep living when you leave, and earn you sparks while you're away. Sparks fill your level bar, and each level opens something new.",true);}
function coach(text,end){const co=$p("coach");co.querySelector("span").textContent=text;co.hidden=false;const b=$p("coachOk");b.hidden=!end;if(end)b.onclick=()=>{co.hidden=true;TUT.step=9;tutSave();};}
// the first 30 seconds: spell a short word with letters on screen
function tutStart(){if(TUT.step!==0)return;const v=vPlay();if(Object.keys(v.words).length){TUT.step=9;tutSave();return;}
  const av=availHere().filter(a=>Math.hypot(a.x-cam.x,a.y-cam.y)<1100&&!urgentNeed(a));if(av.length<4)return;const c=countsOf(av);let best=null;
  for(let i=0;i<4000;i++){const x=LEX[i];if(x.length!==3||!EASY.has(x)||missingFor(x,c)[0]!==0)continue;
    for(const a0 of av.filter(a=>a.ch===x[0])){const used=new Set([a0.id]),pick=[a0];for(const ch of x.slice(1)){const b=av.filter(a=>a.ch===ch&&!used.has(a.id)).sort((p,q)=>dist(p,a0)-dist(q,a0))[0];used.add(b.id);pick.push(b);}
      const spread=Math.max(...pick.map(p=>dist(p,a0)))+i*.05;if(!best||spread<best.spread)best={w:x,ids:pick.map(p=>p.id),spread};}}
  if(!best)return;const w=best.w,ids=best.ids;
  TUT.step=1;TUT.target={w,ids};tutSave();WX("await",null,{ids},null);openSpell(false,true);coach(`Spell your first word: tap ${listNames([...w].map(ch=>"the "+ch))} in the world, then Say ${w}. Or type it.`);frameOn(ids.map(agentById));}
function tutCheck(){if(TUT.step===0&&tAnim>6&&!ATL.on&&!tour&&!document.body.classList.contains("broadcast")&&document.getElementById("intro").style.display==="none"&&!sheet.classList.contains("open")&&!CATCHING)tutStart();}
function drawSpellMarks(t){if(!SPELL.on)return;const tg=TUT.step===1&&TUT.target?TUT.target.ids:[];ctx.save();
  for(const a of S.agents){if(!inView(a.x,a.y,40))continue;const cx=a.x+10*K,cy=a.y-42*K,i=SPELL.ids.indexOf(a.id);
    if(i>=0){ctx.strokeStyle="#E8962F";ctx.lineWidth=4;ctx.beginPath();ctx.arc(cx,cy,40,0,Math.PI*2);ctx.stroke();ctx.fillStyle="#E8962F";ctx.beginPath();ctx.arc(cx+30,cy-38,13,0,Math.PI*2);ctx.fill();
      ctx.fillStyle="#1F2421";ctx.font="700 15px 'Atkinson Hyperlegible', sans-serif";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText(String(i+1),cx+30,cy-38);}
    else if(tg.includes(a.id)){const p=.5+.5*Math.sin(t*5);ctx.strokeStyle=`rgba(232,150,47,${.5+.5*p})`;ctx.lineWidth=3+3*p;ctx.beginPath();ctx.arc(cx,cy,38+6*p,0,Math.PI*2);ctx.stroke();}
    else if(canSay(a)&&!a.young){ctx.strokeStyle="rgba(232,150,47,.45)";ctx.lineWidth=2;ctx.setLineDash([5,6]);ctx.beginPath();ctx.arc(cx,cy,34,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);}}
  ctx.restore();}
function playInit(){$p("pdSpell").onclick=()=>SPELL.on?closeSpell():openSpell(!matchMedia("(pointer:coarse)").matches);$p("pdSparks").onclick=openDashboard;
  $p("stClose").onclick=closeSpell;$p("stForm").onsubmit=e=>{e.preventDefault();sayIt();};
  $p("stIn").oninput=()=>setSpell($p("stIn").value,SPELL.ids);$p("stBack").onclick=()=>{const t=$p("stIn").value;setSpell(t.slice(0,-1),SPELL.ids.slice(0,-1));};
  $p("coachX").onclick=()=>{$p("coach").hidden=true;if(tutOn()){TUT.step=9;tutSave();}};
  addEventListener("keydown",e=>{if(e.ctrlKey||e.metaKey||e.altKey)return;const tg=e.target,typing=tg&&(tg.tagName==="INPUT"||tg.tagName==="TEXTAREA"||tg.tagName==="SELECT"||tg.isContentEditable);
    if(e.key==="Escape"&&SPELL.on){closeSpell();return;}if(typing||sheet.classList.contains("open")||ATL.on||tour||document.getElementById("intro").style.display!=="none"||document.body.classList.contains("broadcast"))return;
    if(/^[a-zA-Z]$/.test(e.key)){e.preventDefault();if(!SPELL.on)openSpell(true);const inp=$p("stIn");inp.focus();setSpell(inp.value+e.key.toUpperCase(),SPELL.ids);}});
  document.querySelector(".caption").addEventListener("click",e=>{if(e.target.closest("button"))return;if(innerWidth<=600)e.currentTarget.classList.toggle("open");});
  setInterval(()=>{if(!S)return;dockTick();tutCheck();},1000);dockTick();}
'''
rep('function save(){if(WORLD.remote)return;', PLAY_JS + '\nfunction save(){if(WORLD.remote)return;')

# the world: spoken words live, letters hurry to say them, and nobody gets pulled into a family mid-word
rep('function formable(a){return!a.word&&!a.young&&a.act?.type!=="meet"&&', 'function formable(a){return!a.word&&!a.young&&a.act?.type!=="meet"&&a.act?.type!=="say"&&')
rep('*(act.type==="flee"?1.6:1)', '*(act.type==="flee"?1.6:act.type==="say"?1.9:1)')
rep('  for(const a of S.agents){const w=wordById(a.word);a.homeNow=', '  spokenTick();\n  for(const a of S.agents){const w=wordById(a.word);a.homeNow=')
rep('else{for(const a of order)drawEmber(a,tAnim);drawBadges();drawSelection();}', 'else{for(const a of order)drawEmber(a,tAnim);drawBadges();drawSelection();}drawSpoken(tAnim);drawSpellMarks(tAnim);')
rep('document.getElementById("shareBtn").style.display=tAnim<shareUntil&&lastMoment?"":"none";', 'document.getElementById("shareBtn").style.display=tAnim<shareUntil&&lastMoment?"":"none";playFrame();')
rep('    case"meet":return w?`${a.name} is on the way to ${w.text}.`:`${a.name} is walking.`;',
    '    case"await":return`${a.name} has noticed you, and is waiting to see what you’ll spell.`;\n    case"say":{const sp=(S.spoken||[]).find(s=>s.id===act.sp);return sp?(sp.state==="say"?`${a.name} is saying ${sp.text} with the others.`:`${a.name} is hurrying to say ${sp.text}.`):`${a.name} is walking.`;}\n    case"meet":return w?`${a.name} is on the way to ${w.text}.`:`${a.name} is walking.`;')
rep('forming:"a word is forming",', 'forming:"a word is forming",spoken:"letters are saying a word",')
# a tap picks a letter while spelling, instead of opening its card
rep('let best=null,bd=Math.max(44,72/Math.max(.6,cam.z));\n  for(const a of S.agents){const d=', 'let best=null,bd=Math.max(SPELL.on?60:44,(SPELL.on?100:72)/Math.max(.6,cam.z));\n  for(const a of S.agents){if(SPELL.on&&!canSay(a))continue;const d=')
rep('if(best){sel=best.id;openCard(best);updateCaption();}', 'if(best){if(SPELL.on)spellTap(best);else{sel=best.id;openCard(best);updateCaption();}}')
# The World: spoken words and what the world needs travel with the live frames
rep('X:S.structs,wx:S.wx,st:stories,', 'X:S.structs,SP:S.spoken||[],gl:S.glow||null,wx:S.wx,st:stories,')
rep('S.words=m.W;S.herd=m.H;', 'S.words=m.W;S.spoken=Array.isArray(m.SP)?m.SP:[];if(m.gl)S.glow=m.gl;S.herd=m.H;')
rep('v.adopted=v.adopted.filter(x=>typeof x==="number").slice(0,3);', 'v.adopted=v.adopted.filter(x=>typeof x==="number").slice(0,6);')
# a brought letter can walk in right where you are, instead of at the refuge
rep('else if(!spend(GIFT_COST,`Brought a new ${c}`))return;const x=makeAgent(c,REFUGE.x+(rnd()-.5)*60,REFUGE.y+30,Date.now(),false);S.agents.push(x);remember(x,"I arrived at the Hearth refuge, brought by a visitor.");\n  chron(`A new ${c} named ${x.name} arrived at the Hearth refuge, brought by a visitor.`,"people");',
    'else if(!spend(GIFT_COST,`Brought a new ${c}`))return;let gx=REFUGE.x+(rnd()-.5)*60,gy=REFUGE.y+30,here=false;{const px=+args.x,py=+args.y;if(Number.isFinite(px)&&Number.isFinite(py)){const k=nearestCell({x:clamp(px,200,WORLD_W-200),y:clamp(py,240,WORLD_H-120)},k=>!MAP.water[k]&&MAP.biome[k]!==5,30);if(k>=0){const cc=cellCenter(k);gx=cc.x+(rnd()-.5)*60;gy=cc.y;here=true;}}}\n  const x=makeAgent(c,gx,gy,Date.now(),false);S.agents.push(x);remember(x,here?"I arrived in the valley, called by a visitor who needed me for a word.":"I arrived at the Hearth refuge, brought by a visitor.");\n  chron(`A new ${c} named ${x.name} arrived ${here?"in the valley":"at the Hearth refuge"}, brought by a visitor.`,"people");')
rep('addStory({kind:"arrival",ids:[x.id],text:`${x.name}, a new ${c}, has arrived at the refuge.`', 'addStory({kind:"arrival",ids:[x.id],text:`${x.name}, a new ${c}, has arrived${here?"":" at the refuge"}.`')

# sparks your companions earn on their own are capped at 50 a day, and all sparks fill the level bar
rep('function earn(a,key,n,text){if(!a||!isAdopted(a))return;a.ms=a.ms||{};if(a.ms[key])return;a.ms[key]=1;S.visitor.sparks+=n;\n  S.visitor.sparkLog.unshift({t:Date.now(),n,text:`${a.name} ${text}`});if(S.visitor.sparkLog.length>60)S.visitor.sparkLog.length=60;refreshDashboard();}',
    'function earn(a,key,n,text){if(!a||!isAdopted(a))return;a.ms=a.ms||{};if(a.ms[key])return;a.ms[key]=1;passiveAdd(n,`${a.name} ${text}`);refreshDashboard();}')
rep('else if(e.t==="earn"&&a&&isAdopted(a)){S.visitor.sparks+=e.n;S.visitor.sparkLog.unshift({t:Date.now(),n:e.n,text:`${a.name} ${e.x}`});if(S.visitor.sparkLog.length>60)S.visitor.sparkLog.length=60;refreshDashboard();}',
    'else if(e.t==="earn"&&a&&isAdopted(a)){passiveAdd(+e.n||0,`${a.name} ${e.x}`);refreshDashboard();}')

# one level instead of standing, tiers and stars
rep('function tierOf(){if(!S.visitor.adopted.length)return 0;let t=1;for(let i=2;i<TIERS.length;i++)if(S.visitor.standing>=TIERS[i].at)t=i;return t;}',
    'const TIER_LV=[0,1,2,3,5];function tierOf(){if(!S.visitor.adopted.length)return 0;const L=levelOf(vPlay().earned);let t=1;for(let i=2;i<5;i++)if(L>=TIER_LV[i])t=i;return t;}')
rep('if(S.visitor.adopted.length>=3){document.getElementById("helpArea").innerHTML=`<p class="muted">You already have 3 companions, the pilot limit.',
    'if(S.visitor.adopted.length>=maxCompanions(levelOf(vPlay().earned))){const L=levelOf(vPlay().earned),nx=[4,7,10].find(n=>n>L);document.getElementById("helpArea").innerHTML=`<p class="muted">You have ${S.visitor.adopted.length} companions.${nx?` Level ${nx} opens one more: spell words to get there.`:""}')
rep('CMD.adopt=(a,args,out)=>{if(S.visitor.adopted.includes(a.id)||S.visitor.adopted.length>=3)return;', 'CMD.adopt=(a,args,out)=>{if(S.visitor.adopted.includes(a.id)||S.visitor.adopted.length>=maxCompanions(levelOf(vPlay().earned)))return;')
rep('<p class="muted">What your companions do in their world adds to, or takes away from, what you can do. Good deeds open abilities; leaving a word or refusing a starving letter closes them again.</p>',
    '<p class="muted">Spell words to earn sparks. Every spark fills your level bar, and each level opens something new.</p>')
rep('<h3>How letters see you: ${stars(v.rep)}</h3><p class="muted">${v.repN?`From ${v.repN} experiences.`:"No one has rated you yet."} Letters talk: helping raises it; letting companions go or ignoring them in trouble lowers it, and new letters decide whether to trust you by it.</p>${v.repLog.slice(0,4).map(d=>`<div class="deed">${"★".repeat(d.r)} ${esc(d.text)} <span class="muted">${timeAgo(d.t)}</span></div>`).join("")}',
    '')
rep('<h3>Your standing: ${esc(TIERS[tier].n)}</h3><div class="meter" role="img" aria-label="Progress to next level"><i style="width:${Math.round(pct*100)}%"></i></div>\n  <p class="muted">${v.standing} points${nextT?` · ${nextT.at-v.standing} more to become a ${nextT.n}`:" · highest level"}</p>',
    '${(()=>{const vp=vPlay(v),L=levelOf(vp.earned),nx=nextOpen(L),ws=Object.keys(vp.words).sort((p,q)=>vp.words[q]-vp.words[p]);return`<h3>Level ${L}</h3><div class="meter" role="img" aria-label="Progress to level ${L+1}"><i style="width:${Math.round(clamp((vp.earned-LV(L))/(LV(L+1)-LV(L)),0,1)*100)}%"></i></div><p class="muted">${LV(L+1)-vp.earned} more sparks to level ${L+1}.${nx?` Level ${nx[0]} opens ${esc(nx[1])}.`:""}</p><h3>Your words: ${ws.length}</h3>${vp.firsts.length?`<p>First in the world: ${vp.firsts.slice(0,12).map(w=>`<b class="goldw">${esc(w)}</b>`).join(" ")}</p>`:""}<p class="muted">${ws.length?esc(ws.slice(0,24).join(" · ")):"Spell your first word: tap Spell a word at the bottom."}</p>`;})()}')
rep('<h3>Your sparks: ${v.sparks}</h3><p class="muted">Sparks are earned only when your companions achieve something for the first time: joining a word, learning or teaching a skill, building, exploring new land, a world first. You spend them to act. A refused offer returns them. Standing decides what you may do; sparks pay for doing it.</p>',
    '<h3>Your sparks: ${v.sparks}</h3><p class="muted">You earn sparks by spelling words. Your companions also earn some on their own when they do something for the first time, up to 50 a day. Spend them to bring letters and help your companions; a refused offer returns them.</p>')
rep('${esc(ab.d)}${!open&&ab.tier?` Opens at ${TIERS[ab.tier].n}.`:""}', '${esc(ab.d)}${!open&&ab.tier?(ab.tier===1||!S.visitor.adopted.length?` Opens when you adopt a letter${ab.tier>1?`, at level ${TIER_LV[ab.tier]}`:""}.`:` Opens at level ${TIER_LV[ab.tier]}.`):""}')

# the first look: the whole game in three lines
rep('''    <h2 class="intro-h">Two ways to be here</h2>
    <ul class="intro-list">
      <li><b>Watch:</b> the camera follows the best stories for you. Nothing to learn.</li>
      <li><b>Take part:</b> adopt a letter and help it. It may listen, or choose its own way.</li>
    </ul>
    <h2 class="intro-h">Four things to know</h2>
    <p class="intro-four">A letter is a person · The glow is its life · A glowing box is a family (a word) · The caption says what is happening now</p>''',
'''    <h2 class="intro-h">How to play</h2>
    <ol class="intro-list">
      <li><b>Spell a word.</b> Tap letters, or type it. If they agree, they say it.</li>
      <li><b>Every word earns sparks ✦.</b> New words earn more, and quick words in a row earn a combo.</li>
      <li><b>Spend sparks to grow:</b> bring new letters, and level up to adopt more companions.</li>
    </ol>
    <p class="intro-four">Or just watch: the world lives on its own, and the camera follows the best stories.</p>''')
rep('''<h2 id="sheetTitle">What is this?</h2><p>''', '''<h2 id="sheetTitle">What is this?</h2><h3>How to play</h3><ol class="rules"><li>Spell real words with the letters you see: tap them, or type.</li><li>Letters can say no. Try again, or try other letters.</li><li>Words earn sparks. New words earn more, and firsts in the world earn the most.</li><li>Words the world needs right now earn triple.</li><li>Spend sparks on new letters and on helping your companions. Every spark fills your level bar.</li></ol><p>''')
rep('function hint(k){if(CATCHING||', 'function hint(k){if(CATCHING||tutOn()||')
rep('const b=(document.querySelector(".caption").offsetHeight+34)+"px";', 'const b=Math.round(innerHeight-Math.min(document.querySelector(".caption").getBoundingClientRect().top,document.getElementById(SPELL.on?"spellTray":"playDock").getBoundingClientRect().top)+10)+"px";')
rep('if(el.style.display!=="none")el.style.bottom=(document.querySelector(".caption").offsetHeight+34)+"px";', '')

PLAY_HTML = '''<div id="playDock"><button type="button" id="pdSparks" class="pd-sp" aria-label="Your sparks and level. Open your letters"><span class="pd-n">✦ <b id="pdN">0</b></span><span class="pd-l"><span id="pdLv">Level 1</span><i class="pd-bar"><i id="pdBar"></i></i></span></button><div id="pdCombo" hidden><b>Combo ×2</b><i><i></i></i></div><button type="button" id="pdSpell" class="btn-primary">Spell a word</button></div>
<section id="spellTray" hidden aria-label="Spell a word"><button type="button" class="st-x" id="stClose" aria-label="Close">×</button>
  <div class="st-top"><div id="stTiles" class="st-tiles" aria-live="polite"></div><span id="stCombo" class="st-combo" hidden></span><button type="button" id="stBack" class="st-back" aria-label="Remove the last letter">⌫</button></div>
  <form id="stForm" autocomplete="off"><input id="stIn" maxlength="12" autocapitalize="characters" autocorrect="off" spellcheck="false" placeholder="Type a word" aria-label="Type a word"><button class="btn-primary" id="stSay" disabled>Say it</button></form>
  <p id="stMsg" class="st-msg" aria-live="polite"></p><div id="stIdeas"></div></section>
<div id="coach" role="status" hidden><span></span><button type="button" id="coachOk" class="btn-primary" hidden>Got it</button><button type="button" id="coachX" aria-label="Skip the tips">×</button></div>
<div id="lvToast" role="status" hidden></div>
'''
rep('<button id="tourBtn" class="tour-btn">', PLAY_HTML + '<button id="tourBtn" class="tour-btn">')

PLAY_CSS = r'''
#playDock{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(14px + env(safe-area-inset-bottom,0px));z-index:5;display:flex;align-items:center;gap:8px;background:rgba(31,36,33,.92);border-radius:28px;padding:6px 6px 6px 8px;box-shadow:0 6px 24px rgba(0,0,0,.22);max-width:calc(100% - 24px)}
.pd-sp{display:flex;align-items:center;gap:10px;height:44px;padding:0 12px;border:none;border-radius:22px;background:transparent;color:#F8F9F6;font:inherit;cursor:pointer}
.pd-n{font-size:18px;font-weight:700;color:#F0B060;white-space:nowrap}.pd-n b{color:#F8F9F6}
.pd-l{display:flex;flex-direction:column;gap:4px;font-size:12px;color:#D3D8D0;min-width:64px;text-align:left}.pd-bar{display:block;height:5px;border-radius:3px;background:rgba(248,249,246,.18);overflow:hidden}.pd-bar i{display:block;height:100%;width:0;background:#E8962F;transition:width .6s}
#pdSpell{height:44px;padding:0 20px;font-size:16px;white-space:nowrap}
#pdCombo{display:flex;flex-direction:column;gap:3px;color:#FFD08A;font-size:13px;white-space:nowrap}#pdCombo>i{display:block;width:70px;height:4px;border-radius:2px;background:rgba(255,208,138,.2);overflow:hidden}#pdCombo>i>i{display:block;height:100%;background:#FFD08A}
#pdCombo[hidden]{display:none}
.caption{bottom:calc(76px + env(safe-area-inset-bottom,0px));padding:12px 20px 14px;gap:10px;transition:opacity .4s}
.caption p{font-size:clamp(18px,2.6vw,24px)}
.zoom{bottom:calc(240px + env(safe-area-inset-bottom,0px))}
body.spelling .caption,body.spelling #playDock{display:none}
#spellTray{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:6;width:min(560px,calc(100% - 20px));background:#1F2421;color:#F8F9F6;border-radius:22px;padding:14px 16px 14px;box-shadow:0 8px 30px rgba(0,0,0,.35)}
#spellTray[hidden]{display:none}
.st-x{position:absolute;right:8px;top:8px;width:40px;height:40px;border-radius:20px;border:none;background:transparent;color:#D3D8D0;font-size:22px;cursor:pointer}
.st-top{display:flex;align-items:center;gap:8px;margin-right:40px;min-height:52px}
.st-tiles{display:flex;flex-wrap:wrap;gap:6px;flex:1;min-width:0}
.st-tile{width:40px;height:48px;border-radius:9px;background:#F8F9F6;color:#1F2421;display:flex;align-items:center;justify-content:center;font:700 26px Spectral,Georgia,serif;box-shadow:0 2px 0 rgba(0,0,0,.35)}
.st-tile.picked{box-shadow:0 0 0 3px #E8962F}.st-tiles.real .st-tile{background:#FFE7C2}
.st-ph{color:#AEB6B0;font-size:15px}
.st-combo{flex-shrink:0;height:30px;padding:0 10px;border-radius:15px;background:#E8962F;color:#1F2421;font-weight:700;font-size:13px;display:flex;align-items:center}.st-combo[hidden]{display:none}
.st-back{width:44px;height:44px;border-radius:22px;border:1px solid #5B645E;background:transparent;color:#F8F9F6;font-size:18px;cursor:pointer;flex-shrink:0}
#stForm{display:flex;gap:8px;margin-top:10px}#stIn{flex:1;min-width:0;height:44px;border-radius:22px;border:1px solid #5B645E;background:#2A302C;color:#F8F9F6;padding:0 16px;font:700 17px 'Atkinson Hyperlegible',sans-serif;letter-spacing:.08em;text-transform:uppercase}
#stIn::placeholder{letter-spacing:0;text-transform:none;font-weight:400;color:#9AA39C}#stSay{height:44px;padding:0 18px;flex-shrink:0}#stSay:disabled{opacity:.45}
.st-msg{margin:8px 2px 0;font-size:14px;color:#FFD08A;min-height:0}.st-msg:empty{display:none}
#stIdeas{margin-top:6px}.st-row{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:6px;font-size:13px;color:#D3D8D0}.st-k{margin-right:2px}
.st-chip{height:32px;padding:0 12px;border-radius:16px;border:1px solid #5B645E;background:transparent;color:#F8F9F6;font:700 13px 'Atkinson Hyperlegible',sans-serif;letter-spacing:.04em;cursor:pointer}
.st-chip.glow{border-color:#E8962F;color:#FFD08A}.st-chip.get{background:#E8962F;border-color:#E8962F;color:#1F2421;letter-spacing:0}.st-chip:disabled{opacity:.45}
#coach{position:fixed;left:50%;transform:translateX(-50%);top:calc(74px + env(safe-area-inset-top,0px));z-index:7;width:min(460px,calc(100% - 24px));background:#F7F8F5;color:#1F2421;border-radius:16px;padding:12px 44px 12px 16px;box-shadow:0 6px 24px rgba(0,0,0,.25);font-size:15px;line-height:1.4;display:flex;flex-direction:column;gap:8px;align-items:flex-start}
#coach[hidden]{display:none}#coach button#coachX{position:absolute;right:4px;top:4px;width:40px;height:40px;border:none;background:transparent;font-size:20px;color:#5A635D;cursor:pointer}#coachOk{height:40px;padding:0 18px}
#lvToast{position:fixed;left:50%;top:38%;transform:translate(-50%,-50%);z-index:9;background:#1F2421;color:#F8F9F6;border:2px solid #E8962F;border-radius:20px;padding:16px 26px;text-align:center;pointer-events:none;box-shadow:0 10px 40px rgba(0,0,0,.4)}
#lvToast[hidden]{display:none}#lvToast b{display:block;font:700 34px Spectral,Georgia,serif;color:#F0B060}#lvToast span{font-size:15px}#lvToast.go{animation:lvpop 3.6s ease both}
@keyframes lvpop{0%{opacity:0;transform:translate(-50%,-40%) scale(.8)}12%{opacity:1;transform:translate(-50%,-50%) scale(1.06)}20%{transform:translate(-50%,-50%) scale(1)}85%{opacity:1}100%{opacity:0}}
.burst{position:fixed;z-index:8;transform:translate(-50%,-50%);pointer-events:none;text-align:center;animation:burst 2.6s ease-out both;text-shadow:0 2px 10px rgba(0,0,0,.55)}
.burst b{display:block;font:700 38px Spectral,Georgia,serif;color:#FFD08A}.burst span{display:block;font-size:13px;font-weight:700;color:#F8F9F6;max-width:260px}.burst .gold{color:#F0B060;letter-spacing:.08em;text-transform:uppercase}
@keyframes burst{0%{opacity:0;transform:translate(-50%,-30%) scale(.6)}15%{opacity:1;transform:translate(-50%,-60%) scale(1.15)}30%{transform:translate(-50%,-70%) scale(1)}80%{opacity:1}100%{opacity:0;transform:translate(-50%,-120%)}}
.bpart{position:fixed;z-index:8;pointer-events:none;color:#FFD08A;font-style:normal;font-size:20px;transition:transform 1.1s cubic-bezier(.5,0,.75,0),opacity 1.1s ease-in;text-shadow:0 0 8px rgba(232,150,47,.9)}
.goldw{color:#9A5A10;background:#FFE7C2;border-radius:6px;padding:1px 6px}ol.rules{padding-left:20px}ol.rules li{margin:4px 0}
body.spelling .tour-btn,body.spelling #returnBtn,body.spelling #elsewhere,body.spelling #hint,body.atlas-on #playDock,body.atlas-on #spellTray,body.atlas-on #coach,body.filming #playDock,body.filming #spellTray,body.filming #coach,body.broadcast #playDock,body.broadcast #spellTray,body.broadcast #coach,body.broadcast .burst,body.broadcast .bpart{display:none!important}
@media (max-width:600px){
  .caption{bottom:calc(72px + env(safe-area-inset-bottom,0px));padding:9px 14px;border-radius:16px;gap:6px;align-items:stretch;cursor:pointer}
  .caption p{font-size:16px;line-height:1.3;text-align:left;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
  .caption .sub,.caption .row{display:none}.caption.open .row{display:flex;justify-content:flex-start}.caption.open .sub{display:block;text-align:left;margin-top:0}.caption.open p{-webkit-line-clamp:unset}
  .caption .btn-primary,.caption .btn-ghost{height:40px;padding:0 14px;font-size:14px}
  .zoom:not(.azoom){display:none}.hint{font-size:14px;padding:8px 6px 8px 12px}
  #playDock{left:12px;right:12px;transform:none;justify-content:space-between;max-width:none}
  .pd-sp{padding:0 8px;gap:8px}.pd-l{min-width:56px}#pdSpell{padding:0 16px}#pdCombo>i{width:48px}
  .st-tile{width:34px;height:42px;font-size:22px}.st-row{font-size:12px}
}
'''
i = s.rindex('</style>'); s = s[:i] + PLAY_CSS + s[i:]
rep('awayStart();updateCaption();', 'awayStart();updateCaption();playInit();')
rep('window.__lango={get world(){return WORLD},', 'window.__lango={get world(){return WORLD},get play(){return{SPELL,TUT,ideas,lex:LEX.length,levelOf,vPlay}},')
# arrived letters wait in line for the others, instead of wandering off
rep('function perform(a,dt){\n  const act=a.act;if(!act)return;act.t+=dt;const w=wordById(a.word);\n  switch(act.type){', 'function perform(a,dt){\n  const act=a.act;if(!act)return;act.t+=dt;const w=wordById(a.word);\n  switch(act.type){\n    case"say":case"await":return;')
