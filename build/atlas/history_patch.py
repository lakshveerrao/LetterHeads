# History you play (3 October 2026). Lakshveer: people should learn history, evolution and the language through
# play, "not as a lecture but as a part of the game", with more real, factual references; one should really feel
# the evolution of the planet, civilization and language. No AI calls at runtime.
#   - Words with a story: spelling a word such as FIRE, POT or WHEEL for the first time shows a one-line
#     "In our world" card with the real fact and its source, earns +10 sparks, and goes into your history book.
#     World-first discoveries in the valley (fire, tools, pottery...) show the same real card to whoever watches.
#   - The alphabet's own story: the first time each letter joins one of your words, a small card shows what it
#     began as (A an ox's head, O an eye...). New letters born in history (G, J, U, W...) show theirs.
#   - Era turns become a short cinematic moment, and a thin ribbon along the top shows where the world is in
#     history; the In our world sheet shows every age and how long until the next.
# Facts live in build/history/facts.json (each checked against its source). Run after play_patch.py.

import json
HF = [f for f in json.load(open(O + '../history/facts.json')) if f.get('checked')]
for f in HF:
    assert len(f['text']) <= 170 and f['src'][1].startswith('https://'), f['id']

LETTER_STORY = {
 "A": "A began about 3,800 years ago as a drawing of an ox's head, called aleph. Turn an A upside down and you can still see the horns.",
 "B": "B began as a house, called bet. The Greeks named their first two letters alpha and beta, and that is where the word alphabet comes from.",
 "C": "C comes from gimel, which may have been a throwing stick. The Romans used C for the K sound, and later made G from it.",
 "D": "D began as a door, called dalet. The Greeks made it delta, a triangle, and the Romans rounded one side.",
 "E": "E began as a little figure with raised arms, perhaps someone calling out. The Phoenicians called it he.",
 "F": "F comes from waw, a hook or peg. Waw is also the great-grandparent of U, V, W and Y.",
 "G": "G is a Roman invention. About 2,250 years ago a small bar was added to C, so G and K sounds could be told apart.",
 "H": "H comes from het, probably a fence or a courtyard wall.",
 "I": "I began as yod, an arm with its hand. It shrank into the smallest letter, and much later J grew out of it.",
 "J": "For centuries J was just a fancy way of writing I. Only about 500 years ago did printers begin to treat it as a letter of its own.",
 "K": "K began as kaph, the open palm of a hand.",
 "L": "L began as lamed, a shepherd's staff for guiding animals.",
 "M": "M began as mem, water. Its zigzag is the waves.",
 "N": "N began as nun, which in the oldest pictures looks like a snake.",
 "O": "O began as ayin, an eye. It has hardly changed shape in nearly 4,000 years.",
 "P": "P began as pe, a mouth. The Greeks called it pi.",
 "Q": "Q comes from qoph. Nobody is sure what it first showed: perhaps a monkey, perhaps the eye of a needle.",
 "R": "R began as resh, a head. The Romans gave it a leg, so it could not be mistaken for P.",
 "S": "S began as shin, probably a tooth. The Greeks turned it on its side to make sigma.",
 "T": "T began as taw, a mark or a cross, and has kept nearly the same shape ever since.",
 "U": "To the Romans, U and V were one letter. Only about 500 years ago did printers split them in two.",
 "V": "V comes from waw, a hook, through the Greek upsilon. Romans carved V for both the U and the V sound.",
 "W": "W is a doubled U. Medieval scribes wrote two side by side, which is why English still calls it double U.",
 "X": "X came to the Romans from Greek alphabets, where it stood for the sound ks, just as it does in BOX.",
 "Y": "Y is the Greek upsilon. The Romans borrowed it about 2,000 years ago to spell Greek words.",
 "Z": "Z comes from zayin, perhaps a weapon. The Romans dropped it, then brought it back for Greek words, so it went to the very end.",
}
for k, v in LETTER_STORY.items():
    assert len(v) <= 150, k
LETTER_SRC = json.load(open(O + '../history/letters_src.json'))

HIST_JS = r'''
// ================= history you play: real facts, the alphabet's story, the ages =================
const HFACTS=__HF__,HWORD=new Map();for(const f of HFACTS)for(const w of f.words)HWORD.set(w,f);
const LSTORY=__LS__,LSRC=__LSRC__;
const CONCEPT_WORDS={tool:["TOOL","STONE"],fire:["FIRE"],cook:["COOK"],shelter:["HUT","WOOD","LOG"],fish:["FISH"],plant:["SEED","FARM","WHEAT"],bridge:["BRIDGE","TRACK"],clothing:["CLOTH","COAT","WEAR"],pottery:["POT","CLAY"],cross:["BOAT","RAFT"]};
const HB={f:{},l:{}};try{Object.assign(HB,JSON.parse(localStorage.getItem("letterheads_book_v1")||"{}"));}catch(e){}
function hbSave(){try{localStorage.setItem("letterheads_book_v1",JSON.stringify(HB));}catch(e){}}
const HQ=[];let hCardUntil=0,hCardHold=false;
function agoText(y){if(y>=1e6)return`about ${+(y/1e6).toFixed(1)} million years ago`;const r=y>=10000?Math.round(y/1000)*1000:y>=1000?Math.round(y/100)*100:Math.round(y/10)*10;return`about ${r.toLocaleString()} years ago`;}
function hWhen(ya){const y=yearsAgo();if(y<0)return"";const now=historyLabel(y);return ya>y*1.08+50?`Your letters live ${now}, so this already happened long before them.`:ya<y*.92-50?`Your letters live ${now}, so this is still in their future.`:`Your letters live ${now}: right about now.`;}
function hBookLine(){return`History book: ${Object.keys(HB.f).length} of ${HFACTS.length} stories · ${Object.keys(HB.l).length} of 26 letters`;}
function pictoSvg(ch){const d=PICTO[ch];return d?`<svg viewBox="-10 -68 40 46" aria-hidden="true"><path d="${d}" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>`:"";}
function hQueue(c){if(HQ.some(q=>q.key===c.key))return;HQ.push(c);}
function hFact(f,how){if(!f||HB.f[f.id])return false;HB.f[f.id]=Date.now();hbSave();hQueue({key:"f"+f.id,kind:"fact",f,how});return true;}
function hLetter(ch){if(!LSTORY[ch]||HB.l[ch])return false;HB.l[ch]=Date.now();hbSave();hQueue({key:"l"+ch,kind:"letter",ch});return true;}
// after your word is said: its real story first, or else the story of a letter you have not used before
function histAfter(m){if(!m||!m.text||tutOn())return;const f=HWORD.get(m.text);if(f&&hFact(f,m.text))return;for(const ch of m.text)if(hLetter(ch))return;}
function hShow(c){const el=$p("hCard");let h;
  if(c.kind==="fact"){const f=c.f;h=`<small>In our world${c.how?` · <b>${esc(c.how)}</b>`:""}</small><p class="hc-t">${esc(f.text)}</p><p class="hc-w">${esc(hWhen(f.ya))}</p><a class="hc-s" href="${esc(f.src[1])}" target="_blank" rel="noopener">${esc(f.src[0])} ↗</a>`;}
  else if(c.kind==="letter"){h=`<small>The story of <b>${c.ch}</b>${c.born?" · just born":""}</small><div class="hc-l">${pictoSvg(c.ch)}<span class="hc-big">${c.ch}</span><p class="hc-t">${esc(LSTORY[c.ch])}</p></div><a class="hc-s" href="${esc(LSRC[1])}" target="_blank" rel="noopener">${esc(LSRC[0])} ↗</a>`;}
  el.innerHTML=h+`<span class="hc-b">${esc(hBookLine())}</span><button type="button" class="hc-x" aria-label="Close">×</button>`;
  el.querySelector(".hc-x").onclick=()=>{hCardUntil=0;el.hidden=true;};el.onpointerenter=()=>hCardHold=true;el.onpointerleave=()=>hCardHold=false;
  el.hidden=false;el.classList.remove("in");void el.offsetWidth;el.classList.add("in");hCardUntil=performance.now()+(c.kind==="fact"?15000:11000);}
// watch the world for discoveries, new letters and new ages, whoever caused them
let hFirsts=null,hBorn=null;
function eraKey(){return WORLD.on?"world":"v"+(S.created||0);}
function histWatch(){if(!S)return;const now=performance.now(),el=$p("hCard");
  if(!hFirsts){hFirsts=new Set(Object.keys(S.firsts||{}));hBorn=new Set(Object.keys(S.lateBorn||{}));}
  for(const c in S.firsts||{})if(!hFirsts.has(c)){hFirsts.add(c);const f=(CONCEPT_WORDS[c]||[]).map(w=>HWORD.get(w)).find(Boolean);if(f)hFact(f,"");}
  for(const ch in S.lateBorn||{})if(!hBorn.has(ch)){hBorn.add(ch);if(LSTORY[ch]){HB.l[ch]=HB.l[ch]||Date.now();hbSave();hQueue({key:"b"+ch,kind:"letter",ch,born:1});}}
  eraWatch();
  const busy=document.body.classList.contains("broadcast")||document.body.classList.contains("atlas-on")||document.body.classList.contains("filming")||tutOn()||!$p("eraMoment").hidden||!$p("lvToast").hidden||document.querySelector(".burst");
  if(!el.hidden&&!hCardHold&&now>hCardUntil){el.hidden=true;hCardUntil=0;}
  if(el.hidden&&HQ.length&&!busy&&now>(histWatch.gap||0)){hShow(HQ.shift());histWatch.gap=now+16000;}
  ribbonTick();}
// the ages: a thin ribbon along the top, and a short cinematic moment when a new age begins
const ERA_M=[];function monthOf(y){for(const[m0,m1,y0,y1]of HIST_SEG)if(y<=y0&&y>=y1)return m0+(m1-m0)*(y0-y)/(y0-y1);return y>300000?0:36;}
for(const e of ERAS.slice(0,-1))ERA_M.push([monthOf(Math.min(e.from,300000)),monthOf(Math.max(e.to,0)),e]);
function nowMonth(){const y=yearsAgo();return y<0?36:monthOf(y);}
function untilText(ms){const d=ms/86400000;return d<1.5?"within a day":d<45?`in about ${Math.round(d)} days`:`in about ${Math.round(d/30.44)} months`;}
function nextEra(){const m=nowMonth();const i=ERA_M.findIndex(([a,b])=>m>=a&&m<b);if(i<0||i>=ERA_M.length-1)return null;const left=(ERA_M[i][1]-m)*MONTH;return{e:ERA_M[i+1][2],left};}
function ribbonHTML(){const m=nowMonth(),nx=nextEra();
  return`<div class="hr-big" role="img" aria-label="The ages of the world, and where yours is now">${ERA_M.map(([a,b,e])=>`<div class="hr-seg${m>=b?" past":m>=a?" now":""}" style="flex:${(b-a).toFixed(2)}" title="${esc(e.name)}"><i>${m>=a&&m<b?`<b style="left:${((m-a)/(b-a)*100).toFixed(1)}%"></b>`:""}</i></div>`).join("")}</div>
   ${nx&&S.settings.historyPreview==null?`<p class="muted">Next age: <b>${esc(nx.e.name)}</b>, ${untilText(nx.left)} of real time. The world keeps moving through history whether or not anyone is watching.</p>`:""}`;}
let ribbonAt=0;function ribbonTick(){const now=performance.now();if(now<ribbonAt)return;ribbonAt=now+5000;const r=$p("hRibbon");if(!r)return;const m=nowMonth();
  r.querySelector("b").style.left=(m/36*100).toFixed(2)+"%";const e=eraNow(),nx=nextEra();r.setAttribute("aria-label",`${e.name}, ${historyLabel()}.${nx?` Next: ${nx.e.name}, ${untilText(nx.left)}.`:""} Open In our world.`);r.title=r.getAttribute("aria-label");}
function eraWatch(){if(!$p("eraMoment").hidden||tutOn()||document.body.classList.contains("broadcast")||document.body.classList.contains("atlas-on"))return;
  if(S.settings.historyPreview!=null)return;const e=eraNow();let seen={};try{seen=JSON.parse(localStorage.getItem("letterheads_era_v1")||"{}");}catch(x){}
  const k=eraKey();if(seen[k]===e.name)return;const had=seen[k];seen[k]=e.name;try{localStorage.setItem("letterheads_era_v1",JSON.stringify(seen));}catch(x){}
  if(had)eraMoment(e);}
function eraMoment(e){const el=$p("eraMoment");const first=e.text.split(/(?<=\.)\s/)[0];
  el.innerHTML=`<i class="em-bar"></i><i class="em-bar b"></i><div class="em-in"><small>A new age begins</small><h2>${esc(e.name)}</h2><p class="em-y">${esc(historyLabel())} in our world</p><p>${esc(first)}</p><button type="button" class="btn-ghost em-more">Read more</button></div>`;
  el.hidden=false;document.body.classList.add("era-on");el.classList.remove("go");void el.offsetWidth;el.classList.add("go");try{if(Music.on)Music.discovery();}catch(x){}
  const close=()=>{el.hidden=true;document.body.classList.remove("era-on");clearTimeout(eraMoment.t);};el.onclick=ev=>{close();if(ev.target.classList.contains("em-more"))openOurWorld();};eraMoment.t=setTimeout(close,8000);}
function histBookHTML(){const fs=HFACTS.filter(f=>HB.f[f.id]).sort((p,q)=>HB.f[q.id]-HB.f[p.id]);
  return`<h3>Your history book</h3><p class="muted">${esc(hBookLine())}. Spell words like ${HFACTS.filter(f=>!HB.f[f.id]).slice(0,3).map(f=>f.words[0]).join(", ")||"any word"} to find more real stories.</p>
   <p class="hb-l">${"ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map(ch=>`<span class="${HB.l[ch]?"got":""}" title="${HB.l[ch]?esc(LSTORY[ch]):"Spell a word with "+ch+" to find its story"}">${ch}</span>`).join("")}</p>
   ${fs.length?`<ul class="hb-f">${fs.slice(0,40).map(f=>`<li><b>${f.words[0]}</b> ${esc(f.text)} <a href="${esc(f.src[1])}" target="_blank" rel="noopener">${esc(f.src[0])}</a></li>`).join("")}</ul>`:""}`;}
'''.replace('__HF__', json.dumps(HF, ensure_ascii=False)).replace('__LS__', json.dumps(LETTER_STORY, ensure_ascii=False)).replace('__LSRC__', json.dumps(LETTER_SRC, ensure_ascii=False))
rep('function save(){if(WORLD.remote)return;', HIST_JS + '\nfunction save(){if(WORLD.remote)return;')

# a word with a story earns +10 the first time you spell it (computed on the keeper, like every reward)
rep('v.lastWordAt=now;if(first){n*=5;', 'v.lastWordAt=now;if(mine&&HWORD.has(text)&&!HWORD.get(text).words.some(w=>w!==text&&v.words[w])){n+=10;parts.push("a word with a story +10");}if(first){n*=5;')
# remember which word was said, so its story can follow the sparks
rep('SPELL.mine.set(r.id,{n:r.n,parts:r.parts,first:r.first,combo:r.combo,at:Date.now(),seen:false});', 'SPELL.mine.set(r.id,{n:r.n,parts:r.parts,first:r.first,combo:r.combo,at:Date.now(),seen:false,text});')
rep('burstAt(on?x:W/2,on?y:H*.4,m);setTimeout(dockTick,900);', 'burstAt(on?x:W/2,on?y:H*.4,m);setTimeout(dockTick,900);setTimeout(()=>histAfter(m),2000);')
rep('m.seen=true;burstAt(W/2,H*.45,m);setTimeout(dockTick,900);}}', 'm.seen=true;burstAt(W/2,H*.45,m);setTimeout(dockTick,900);setTimeout(()=>histAfter(m),2000);}}')
rep('if(SPELL.on&&tAnim-SPELL.lastIdeas>4)renderIdeas();', 'if(SPELL.on&&tAnim-SPELL.lastIdeas>4)renderIdeas();histWatch();')
# words with a story among the spelling ideas
rep('const v=vPlay(),av=availHere(),c=countsOf(av),out={can:[],away:null,glow:[]};const gs=glowSet();',
    'const v=vPlay(),av=availHere(),c=countsOf(av),out={can:[],away:null,glow:[],hist:[]};const gs=glowSet();\n  for(const[w,f]of HWORD){if(out.hist.length>=2)break;if(!HB.f[f.id]&&!v.words[w]&&!out.hist.includes(w)&&missingFor(w,c)[0]===0)out.hist.push(w);}')
rep('if(id.can.length)h+=`<div class="st-row"><span class="st-k">You could spell:</span>',
    'if(id.hist.length)h+=`<div class="st-row"><span class="st-k">Words with a real story, +10:</span>${id.hist.map(w=>`<button type="button" class="st-chip hist" data-w="${w}">📜 ${w}</button>`).join("")}</div>`;\n  if(id.can.length)h+=`<div class="st-row"><span class="st-k">You could spell:</span>')
rep('id.can.map(chip).join("")}</div>`;', 'id.can.filter(w=>!id.hist.includes(w)).map(chip).join("")}</div>`;')
# the history book in your dashboard, the ages in the In our world sheet
rep('"Spell your first word: tap Spell a word at the bottom."}</p>`;})()}', '"Spell your first word: tap Spell a word at the bottom."}</p>${histBookHTML()}`;})()}')
rep('<p class="muted">${esc(historyLabel(y))} · ${esc(e.name)}</p><p>${esc(e.text)}</p>', '<p class="muted">${esc(historyLabel(y))} · ${esc(e.name)}</p><p>${esc(e.text)}</p>${fromAtlas?"":ribbonHTML()}')
rep('<li>Spend sparks on new letters and on helping your companions. Every spark fills your level bar.</li></ol>',
    '<li>Spend sparks on new letters and on helping your companions. Every spark fills your level bar.</li></ol><p class="muted">Some words have a real story from our world, like FIRE, POT or WHEEL. Spell them to fill your history book.</p>')

HIST_HTML = '''<button type="button" id="hRibbon" aria-label="Open In our world"><i></i><b></b></button>
<aside id="hCard" role="status" hidden></aside>
<div id="eraMoment" role="dialog" aria-label="A new age begins" hidden></div>
'''
rep('<button id="tourBtn" class="tour-btn">', HIST_HTML + '<button id="tourBtn" class="tour-btn">')
rep('awayStart();updateCaption();playInit();', 'awayStart();updateCaption();playInit();$p("hRibbon").onclick=()=>openOurWorld();')
rep('get play(){return{SPELL,TUT,ideas,lex:LEX.length,levelOf,vPlay}},', 'get play(){return{SPELL,TUT,ideas,lex:LEX.length,levelOf,vPlay,HB,HQ,HFACTS,eraMoment,nextEra,ribbonHTML,histAfter}},')

HIST_CSS = r'''
#hRibbon{position:fixed;left:0;right:0;top:0;height:14px;z-index:4;border:none;padding:0;background:transparent;cursor:pointer}
#hRibbon i{position:absolute;left:0;right:0;top:0;height:4px;background:linear-gradient(90deg,#8C6A44 0 25%,#9FB7C8 25% 50%,#8DAF6A 50% 66.4%,#C08A4A 66.4% 75%,#8F8F9A 75% 91.7%,#4F7FA8 91.7%);opacity:.75}
#hRibbon b{position:absolute;top:-2px;width:8px;height:8px;margin-left:-4px;border-radius:50%;background:#FFD08A;box-shadow:0 0 0 2px #1F2421,0 0 10px 3px rgba(255,208,138,.9)}
#hCard{position:fixed;left:50%;transform:translateX(-50%);top:calc(74px + env(safe-area-inset-top,0px));z-index:7;width:min(440px,calc(100% - 24px));background:#FBF6EA;color:#1F2421;border-radius:16px;padding:12px 44px 12px 16px;box-shadow:0 8px 28px rgba(0,0,0,.28);border-left:5px solid #C9862F;font-size:15px;line-height:1.4}
#hCard[hidden]{display:none}#hCard.in{animation:hcin .5s ease both}
@keyframes hcin{from{opacity:0;transform:translate(-50%,-16px)}to{opacity:1;transform:translate(-50%,0)}}
#hCard small{display:block;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#8A5A1A}#hCard small b{color:#1F2421;letter-spacing:.06em}
#hCard .hc-t{margin:6px 0 4px;font:500 17px/1.4 Spectral,Georgia,serif}#hCard .hc-w{margin:0 0 6px;font-size:13px;color:#5A635D}
#hCard .hc-s{font-size:13px;color:#7A4A10}#hCard .hc-b{display:block;margin-top:6px;font-size:12px;color:#5A635D}
#hCard .hc-x{position:absolute;right:4px;top:4px;width:40px;height:40px;border:none;background:transparent;font-size:20px;color:#5A635D;cursor:pointer}
#hCard .hc-l{display:flex;align-items:center;gap:10px}#hCard .hc-l svg{width:44px;height:50px;flex-shrink:0;color:#8A5A1A}#hCard .hc-big{font:700 40px Spectral,Georgia,serif;flex-shrink:0;color:#1F2421}
#eraMoment{position:fixed;inset:0;z-index:20;display:flex;align-items:center;justify-content:center;background:rgba(10,12,11,.68);color:#F8F9F6;text-align:center;cursor:pointer}
#eraMoment[hidden]{display:none}#eraMoment .em-bar{position:absolute;left:0;right:0;top:0;height:13vh;background:#000}#eraMoment .em-bar.b{top:auto;bottom:0}
#eraMoment.go .em-bar{animation:emtop 1s ease both}#eraMoment.go .em-bar.b{animation-name:embot}
@keyframes emtop{from{transform:translateY(-100%)}to{transform:none}}@keyframes embot{from{transform:translateY(100%)}to{transform:none}}
#eraMoment .em-in{max-width:min(560px,calc(100% - 40px));padding:0 10px}#eraMoment.go .em-in{animation:emin 1.6s .5s ease both}
@keyframes emin{from{opacity:0;letter-spacing:.2em}to{opacity:1;letter-spacing:normal}}
#eraMoment small{font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:#FFD08A}#eraMoment h2{font:700 clamp(34px,7vw,60px)/1.1 Spectral,Georgia,serif;margin:10px 0}
#eraMoment .em-y{color:#D3D8D0;margin:0 0 14px}#eraMoment p{font-size:17px;line-height:1.45}#eraMoment .em-more{margin-top:10px;color:#F8F9F6;border-color:#F8F9F6}
.hr-big{display:flex;gap:3px;margin:14px 0 8px}.hr-seg{min-width:0}.hr-seg i{display:block;position:relative;height:10px;border-radius:5px;background:#E3E6E0}.hr-seg.past i{background:#C9862F}.hr-seg.now i{background:linear-gradient(90deg,#C9862F,#F0C890)}
.hr-seg b{position:absolute;top:-4px;width:18px;height:18px;margin-left:-9px;border-radius:50%;background:#FFD08A;border:3px solid #1F2421}
.hr-seg span{display:block;font-size:11px;line-height:1.2;margin-top:6px;color:#5A635D;overflow:hidden;text-overflow:ellipsis}.hr-seg.now span{color:#1F2421;font-weight:700}
.st-chip.hist{border-color:#C9862F;color:#FFE7C2}
.hb-l{display:flex;flex-wrap:wrap;gap:4px}.hb-l span{width:28px;height:32px;border-radius:6px;display:flex;align-items:center;justify-content:center;font:700 17px Spectral,Georgia,serif;background:#EEF0EC;color:#AEB6B0}.hb-l span.got{background:#FFE7C2;color:#7A4A10}
.hb-f{padding-left:18px}.hb-f li{margin:6px 0;font-size:14px}.hb-f a{font-size:12px}
body.era-on #elsewhere,body.era-on .tour-btn,body.era-on #returnBtn,body.era-on .zoom,body.era-on .hint,body.era-on .caption,body.era-on #playDock,body.era-on #hCard,body.atlas-on #hRibbon,body.filming #hRibbon,body.broadcast #hRibbon,body.atlas-on #hCard,body.filming #hCard,body.broadcast #hCard{display:none!important}
@media (max-width:600px){#hCard{font-size:14px;padding:10px 42px 10px 14px}#hCard .hc-t{font-size:16px}.hr-seg span{font-size:9px}}
'''
i = s.rindex('</style>'); s = s[:i] + HIST_CSS + s[i:]
