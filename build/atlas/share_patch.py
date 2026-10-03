# Clips you can share (3 October 2026). Lakshveer: short 10-second clips for social media, cinematic and
# curiosity-arousing, made without burning tokens. When your letters say a world first, a word with a real story,
# or any word you choose to film, the browser records a tall clip of that moment: a hook (0-2 s), the letters
# gathering and saying your word, and an ending question with the link. Nothing leaves the device until you share.
# Run after history_patch.py.

SHARE_JS = r'''
// ================= clips: 10 seconds of your letters, ready to share =================
const CLIP={on:null,film:false,last:null};
function clipMime(){if(!window.MediaRecorder)return null;for(const m of["video/mp4;codecs=avc1.42E01E,mp4a.40.2","video/mp4","video/webm;codecs=vp9,opus","video/webm;codecs=vp8,opus","video/webm"])try{if(MediaRecorder.isTypeSupported(m))return m;}catch(e){}return null;}
function clipCan(){return!!(clipMime()&&cv.captureStream&&!document.body.classList.contains("broadcast"));}
function clipHook(text,first){const f=HWORD.get(text);if(f)return[`${text} has a real story`,agoText(f.ya).replace(/^about /,"from ")];if(first)return["No letter has ever","said this word before"];return["Letters only agree","if they want to"];}
function clipStart(id,text,m){if(!clipCan())return;if(CLIP.on)clipAbort();const oc=document.createElement("canvas");oc.width=720;oc.height=1280;const st=oc.captureStream(30);
  let dest=null;try{if(Music.on&&Music.ctx&&Music.master){dest=Music.ctx.createMediaStreamDestination();Music.master.connect(dest);for(const t of dest.stream.getAudioTracks())st.addTrack(t);}}catch(e){dest=null;}
  const mime=clipMime();let rec;try{rec=new MediaRecorder(st,{mimeType:mime,videoBitsPerSecond:5e6});}catch(e){try{rec=new MediaRecorder(st);}catch(x){return;}}
  const c={id,text,m,oc,g:oc.getContext("2d"),st,dest,rec,mime:rec.mimeType||mime,chunks:[],t0:performance.now(),said:0,end:0,drawn:0,hook:clipHook(text,m.first),names:[]};
  rec.ondataavailable=e=>{if(e.data&&e.data.size)c.chunks.push(e.data);};rec.onstop=()=>clipDone(c);rec.start();CLIP.on=c;}
function clipStop(c,keep){c.keep=keep;try{if(c.rec.state!=="inactive")c.rec.stop();else clipDone(c);}catch(e){}try{if(c.dest)Music.master.disconnect(c.dest);}catch(e){}if(CLIP.on===c)CLIP.on=null;}
function clipAbort(){if(CLIP.on)clipStop(CLIP.on,false);}
function clipDone(c){for(const t of c.st.getTracks())t.stop();if(!c.keep||!c.chunks.length)return;const blob=new Blob(c.chunks,{type:(c.mime||"video/webm").split(";")[0]});
  CLIP.last={blob,text:c.text,ext:/mp4/.test(c.mime)?"mp4":"webm",who:c.who};clipToast();}
// gathering can take a while: keep at most the last 6 seconds before the word is said
function clipTick(){const c=CLIP.on;if(!c)return;const now=performance.now(),s=(S.spoken||[]).find(x=>x.id===c.id);
  if(document.hidden||(!s&&!c.said)&&now-c.t0>45000){clipAbort();return;}
  if(s&&s.state!=="say"&&!c.said&&now-c.t0>6000){const{id,text,m}=c;clipStop(c,false);clipStart(id,text,m);return;}
  if(s&&s.state==="say"&&!c.said){c.said=now;c.names=(s.ids||[]).map(i=>agentById(i)).filter(Boolean);c.who=c.names[0]?.name;}
  if(c.said&&!c.end&&now-c.said>4200)c.end=now;
  if(c.end&&now-c.end>2300){clipStop(c,true);return;}
  if(s&&!c.end&&!SPELL.glide&&!drag){const tx=s.x+10*K,ty=s.y-70;cam.x+=(tx-cam.x)*.06;cam.y+=(ty-cam.y)*.06;if(cam.z<1.3)cam.z+=(1.3-cam.z)*.05;}
  if(now-c.drawn<30)return;c.drawn=now;clipDraw(c,s,now);}
function clipDraw(c,s,now){const g=c.g,OW=720,OH=1280,dpr=cv.width/W;let cw=H*9/16,ch=H;if(cw>W){cw=W;ch=W*16/9;}if(ch>H){ch=H;cw=H*9/16;}
  let fx=W/2,fy=H/2;if(s){const p=w2s(s.x+10*K,s.y-70);fx=p[0];fy=p[1];}const sx=clamp(fx-cw/2,0,W-cw),sy=clamp(fy-ch/2,0,H-ch);
  g.fillStyle="#000";g.fillRect(0,0,OW,OH);try{g.drawImage(cv,sx*dpr,sy*dpr,cw*dpr,ch*dpr,0,0,OW,OH);}catch(e){}
  // a warm film grade and vignette
  const vg=g.createRadialGradient(OW/2,OH/2,OH*.25,OW/2,OH/2,OH*.75);vg.addColorStop(0,"rgba(0,0,0,0)");vg.addColorStop(1,"rgba(20,10,0,.55)");g.fillStyle=vg;g.fillRect(0,0,OW,OH);
  g.fillStyle="rgba(255,170,80,.06)";g.fillRect(0,0,OW,OH);
  const t=(now-c.t0)/1000,bar=120;g.fillStyle="#000";g.fillRect(0,0,OW,bar);g.fillRect(0,OH-bar,OW,bar);
  g.textAlign="center";g.textBaseline="middle";
  g.fillStyle="#F0B060";g.font="700 30px Spectral, Georgia, serif";g.fillText("Letterheads",OW/2,54);
  g.fillStyle="#C9CFC6";g.font="400 22px 'Atkinson Hyperlegible', sans-serif";g.fillText(historyLabel(),OW/2,90);
  g.fillStyle="#F8F9F6";g.font="700 26px 'Atkinson Hyperlegible', sans-serif";g.fillText("letterheads.live",OW/2,OH-60);
  const shadow=(f)=>{g.save();g.shadowColor="rgba(0,0,0,.85)";g.shadowBlur=18;f();g.restore();};
  if(t<2.6){const a=Math.min(1,t/.4)*Math.min(1,(2.6-t)/.4);g.globalAlpha=a;g.fillStyle="rgba(0,0,0,.45)";g.fillRect(0,bar,OW,OH-2*bar);
    shadow(()=>{g.fillStyle="#FFFFFF";g.font="700 56px Spectral, Georgia, serif";g.fillText(c.hook[0],OW/2,OH/2-40);g.fillStyle="#FFD08A";g.fillText(c.hook[1],OW/2,OH/2+34);});g.globalAlpha=1;}
  else if(c.said&&!c.end){const k=(now-c.said)/1000;g.globalAlpha=Math.min(1,k/.5);
    shadow(()=>{g.fillStyle="#FFD08A";g.font="700 64px Spectral, Georgia, serif";g.fillText(`+${c.m.n} ✦`,OW/2,OH-bar-120);
      g.fillStyle="#F8F9F6";g.font="700 28px 'Atkinson Hyperlegible', sans-serif";g.fillText(c.names.length?`${listNames(c.names.slice(0,4).map(a=>a.name))} said ${c.text}`:`They said ${c.text}`,OW/2,OH-bar-60);});g.globalAlpha=1;}
  else if(!c.said){shadow(()=>{g.fillStyle="#F8F9F6";g.font="700 30px 'Atkinson Hyperlegible', sans-serif";g.fillText(`Will they say ${c.text}?`,OW/2,OH-bar-60);});}
  if(c.end){const k=Math.min(1,(now-c.end)/600);g.fillStyle=`rgba(10,12,11,${.82*k})`;g.fillRect(0,bar,OW,OH-2*bar);g.globalAlpha=k;
    const f=HWORD.get(c.text);shadow(()=>{g.fillStyle="#F8F9F6";g.font="700 50px Spectral, Georgia, serif";g.fillText(f?"What else happened":"What will your",OW/2,OH/2-70);g.fillText(f?"in our world?":"letters say?",OW/2,OH/2-10);
      g.fillStyle="#FFD08A";g.font="700 34px 'Atkinson Hyperlegible', sans-serif";g.fillText("Spell a word at letterheads.live",OW/2,OH/2+70);});g.globalAlpha=1;}}
let clipToastT=0;
function clipToast(){const el=$p("clipToast");if(!el||!CLIP.last)return;el.innerHTML=`<span>🎬 Your clip of <b>${esc(CLIP.last.text)}</b> is ready.</span><button type="button" class="btn-primary" id="clipShare">Share</button><button type="button" class="ct-x" aria-label="Close">×</button>`;
  const tray=$p("spellTray");if(SPELL.on){tray.insertBefore(el,tray.firstChild);el.classList.add("in-tray");}else{document.body.appendChild(el);el.classList.remove("in-tray");}
  el.hidden=false;$p("clipShare").onclick=clipShare;el.querySelector(".ct-x").onclick=()=>{el.hidden=true;};clearTimeout(clipToastT);clipToastT=setTimeout(()=>{el.hidden=true;},20000);}
async function clipShare(){const L=CLIP.last;if(!L)return;const link=momentLink({who:L.who}),text=`My letters just said ${L.text} in Letterheads, a world of letters living through real history. ${link}`;
  const file=new File([L.blob],`letterheads-${L.text.toLowerCase()}.${L.ext}`,{type:L.blob.type});
  try{if(navigator.canShare&&navigator.canShare({files:[file]})){await navigator.share({files:[file],text});return;}}catch(e){if(e&&e.name==="AbortError")return;}
  let copied=false;try{await navigator.clipboard.writeText(text);copied=true;}catch(e){}
  const a=document.createElement("a");a.href=URL.createObjectURL(L.blob);a.download=file.name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),60000);
  note(copied?"Clip saved, and the words are copied. Post them with it.":"Clip saved.");}
'''
rep('function save(){if(WORLD.remote)return;', SHARE_JS + '\nfunction save(){if(WORLD.remote)return;')
# film world firsts, words with a story, and any word you ask to film
rep('seen:false,text});msg.textContent=', 'seen:false,text});if(clipCan()&&(r.first||HWORD.has(text)||CLIP.film)&&!tutOn())clipStart(r.id,text,{n:r.n,first:r.first});CLIP.film=false;$p("stFilm").setAttribute("aria-pressed","false");msg.textContent=')
rep('histWatch();', 'histWatch();clipTick();', 1)
rep('<button class="btn-primary" id="stSay" disabled>Say it</button></form>', '<button type="button" id="stFilm" class="st-film" aria-pressed="false" aria-label="Film my next word as a 10-second clip" title="Film my next word">🎬</button><button class="btn-primary" id="stSay" disabled>Say it</button></form>')
rep('$p("hRibbon").onclick=()=>openOurWorld();', '$p("hRibbon").onclick=()=>openOurWorld();$p("stFilm").hidden=!clipCan();$p("stFilm").onclick=()=>{CLIP.film=!CLIP.film;$p("stFilm").setAttribute("aria-pressed",String(CLIP.film));$p("stMsg").textContent=CLIP.film?"Your next word will be filmed as a 10-second clip.":"";};')
rep('<aside id="hCard" role="status" hidden></aside>', '<aside id="hCard" role="status" hidden></aside>\n<div id="clipToast" role="status" hidden></div>')
rep('HQ,HFACTS,eraMoment,nextEra,ribbonHTML,histAfter}},', 'HQ,HFACTS,eraMoment,nextEra,ribbonHTML,histAfter,CLIP,clipStart,clipCan}},')

SHARE_CSS = r'''
.st-film{width:44px;height:44px;border-radius:22px;border:1px solid #5B645E;background:transparent;font-size:19px;cursor:pointer;flex-shrink:0}.st-film[aria-pressed="true"]{background:#E8962F;border-color:#E8962F}.st-film[hidden]{display:none}
#clipToast{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(84px + env(safe-area-inset-bottom,0px));z-index:7;width:min(440px,calc(100% - 24px));display:flex;align-items:center;gap:10px;background:#1F2421;color:#F8F9F6;border:2px solid #E8962F;border-radius:18px;padding:8px 6px 8px 16px;box-shadow:0 8px 28px rgba(0,0,0,.3);font-size:15px}
#clipToast[hidden]{display:none}#clipToast span{flex:1}#clipToast .btn-primary{height:40px;padding:0 18px}#clipToast .ct-x{width:40px;height:40px;border:none;background:transparent;color:#D3D8D0;font-size:20px;cursor:pointer}
#clipToast.in-tray{position:static;transform:none;width:auto;margin:0 40px 10px 0;box-shadow:none}body.spelling #clipToast:not(.in-tray){display:none}
body.atlas-on #clipToast,body.broadcast #clipToast,body.filming #clipToast{display:none!important}
'''
i = s.rindex('</style>'); s = s[:i] + SHARE_CSS + s[i:]
