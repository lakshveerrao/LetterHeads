// Film director: everything is a function of film time t (seconds). One call per frame.
(()=>{const L=__lango,F=L.F,A=F.ATL;
const css=document.createElement('style');css.textContent=`
body *{visibility:hidden!important}#atlasCv{transition:none!important;z-index:5}body.atlas-on #world{visibility:hidden!important}#world,#atlasCv,#cut,#cut *{visibility:visible!important}
#cut{position:fixed;inset:0;z-index:99999;pointer-events:none;font-family:Spectral,Georgia,serif;color:#FFF8E6}
#cut .fc-vig{position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.45) 100%)}
#cut .fc-black{position:absolute;inset:0;background:#07080B;opacity:0}
#cut .fc-flash{position:absolute;inset:0;background:#FFF6E0;opacity:0}
#cut .fc-ctr{position:absolute;left:64px;bottom:58px;text-shadow:0 2px 18px rgba(0,0,0,.7)}
#cut .fc-ctr .n{font:700 108px/1 'Atkinson Hyperlegible',sans-serif;letter-spacing:-2px;font-variant-numeric:tabular-nums}
#cut .fc-ctr .u{font:700 22px 'Atkinson Hyperlegible',sans-serif;letter-spacing:8px;margin-top:6px;color:#F2B45A}
#cut .fc-tag{position:absolute;right:64px;bottom:64px;text-align:right;text-shadow:0 2px 14px rgba(0,0,0,.8)}
#cut .fc-tag .p{font:600 40px Spectral,serif}#cut .fc-tag .s{font:400 20px 'Atkinson Hyperlegible',sans-serif;opacity:.85;margin-top:4px}
#cut .fc-cap{position:absolute;left:50%;top:84px;transform:translateX(-50%);width:1500px;text-align:center;font:600 50px/1.2 Spectral,serif;text-shadow:0 3px 24px rgba(0,0,0,.85)}
#cut .fc-big{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);text-align:center;text-shadow:0 4px 40px rgba(0,0,0,.6)}
#cut .fc-big .h{font:600 170px/1 Spectral,serif;letter-spacing:4px}#cut .fc-big .h2{font:400 44px/1.3 Spectral,serif;margin-top:18px}
#cut .fc-big .h3{font:700 26px 'Atkinson Hyperlegible',sans-serif;letter-spacing:6px;margin-top:40px;color:#F2B45A}
#cut .fc-bars{position:absolute;left:0;right:0;height:0;background:#000}`;
document.head.appendChild(css);
const cut=document.createElement('div');cut.id='cut';cut.innerHTML=`<div class="fc-vig"></div><div class="fc-black"></div><div class="fc-ctr"><div class="n"></div><div class="u">YEARS AGO</div></div><div class="fc-tag"><div class="p"></div><div class="s"></div></div><div class="fc-cap"></div><div class="fc-big"><div class="h"></div><div class="h2"></div><div class="h3"></div></div><div class="fc-flash"></div>`;document.body.appendChild(cut);
const $=q=>cut.querySelector(q);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)),lerp=(a,b,u)=>a+(b-a)*u,ease=u=>u<.5?2*u*u:1-Math.pow(-2*u+2,2)/2,sm=u=>{u=clamp(u,0,1);return u*u*(3-2*u);};
const fadeIO=(t,a,b,f=.35)=>clamp(Math.min((t-a)/f,(b-t)/f),0,1);
const logY=(y0,y1,u)=>Math.exp(lerp(Math.log(y0+60),Math.log(y1+60),u))-60;
function fmt(y){y=Math.round(y);if(y<=0)return"TODAY";if(y>=10000)y=Math.round(y/100)*100;else if(y>=1000)y=Math.round(y/10)*10;return y.toLocaleString("en-US");}
// ---------- the valley ----------
function goValley(y,warm){if(A.on)F.closeAtlas(true);L.S.settings.historyPreview=y;L.relocate();for(let i=0;i<(warm||0);i++)F.step(.1);L.cam.mode="free";}
function focus(){const ag=L.S.agents.filter(a=>!a.dead);let x=0,y=0;ag.forEach(a=>{x+=a.x;y+=a.y});return{x:x/ag.length,y:y/ag.length};}
function setCam(x,y,z){const c=L.cam;c.x=c.tx=x;c.y=c.ty=y;c.z=c.tz=z;}
function labelAt(name){const P=L.place;if(!P||!P.labels)return null;const l=P.labels.find(l=>l[0]===name);if(!l)return null;
  const W=7200,H=4800,kx=W*111.32*Math.cos(P.lat*Math.PI/180)/36,ky=H*110.57/24;return{x:W/2+(l[3]-P.lon)*kx,y:H/2-(l[2]-P.lat)*ky};}
// ---------- the Atlas ----------
function goAtlas(){if(!A.on){F.openAtlas();A.full=true;}if(A.jr)A.jr=null;A.sel=null;}
function aCam(lon,lat,deg){const c=A.cam,z=F.spanZ(deg);c.x=c.tx=F.ax(lon);c.y=c.ty=F.ay(lat);c.z=c.tz=z;}
function aFly(a,b,u){const e=ease(clamp(u,0,1));const lon=lerp(a[0],b[0],e),lat=lerp(a[1],b[1],e);const deg=Math.exp(lerp(Math.log(a[2]),Math.log(b[2]),e));aCam(lon,lat,deg);}
const PL={omo:[35.97,4.8],nile:[32.65,25.72],galilee:[35.55,32.82],hatay:[36,36.1],iron:[22.25,44.65],moravia:[16.62,48.88],vezere:[1.05,44.97],dogger:[2.45,54.4],vienna:[16.45,48.2],argolid:[22.75,37.65],tiber:[12.48,41.88]};
// ---------- shots ----------
// each: [start, end, kind, opts]
const S=[];const sh=(a,b,k,o)=>S.push({a,b,k,o});
sh(0,3.2,'black',{});
sh(3.2,8.6,'atlas',{from:[18,12,340],to:[36,6,46],y0:300000,y1:300000});
sh(8.6,16.6,'valley',{y:299990,warm:900,z0:0.36,z1:1.3,dx0:-420,dx1:260,dy:-40,hour:9.5,place:'Omo Kibish',sub:'Ethiopia · real ground from Copernicus Sentinel-2',label:'Omo Kibish'});
sh(16.6,19.6,'atlas',{from:[36,6,46],to:[32.6,25.7,30],y0:299990,y1:80000});
sh(19.6,21.4,'valley',{y:79990,warm:300,z0:0.3,z1:0.8,dx0:0,dx1:120,hour:11,place:'The Nile',sub:'Luxor, Egypt',label:'Karnak',onLabel:true});
sh(21.4,24,'atlas',{from:[32.6,25.7,30],to:[35.6,33.5,22],y0:80000,y1:62000});
sh(24,25.8,'valley',{y:61990,warm:300,z0:0.3,z1:0.8,dx0:-100,dx1:60,hour:13,place:'Galilee',sub:'Israel',label:'Tiberias',onLabel:true});
sh(25.8,27.6,'valley',{y:49990,warm:300,z0:0.34,z1:0.8,dx0:80,dx1:-60,hour:16,place:'Hatay',sub:'Türkiye, by the Mediterranean',label:'Samandağ',onLabel:true});
sh(27.6,31,'atlas',{from:[36,36,24],to:[20,46,40],y0:50000,y1:46000});
sh(31,33.2,'valley',{y:45990,warm:300,z0:0.3,z1:0.75,dx0:-80,dx1:80,hour:null,cyc:3,place:'The Iron Gates',sub:'the Danube gorge, Romania',label:'Dubova',onLabel:true});
sh(33.2,36.4,'valley',{y:35990,warm:900,z0:0.34,z1:0.7,dx0:-200,dx1:150,hour:null,cyc:3.2,place:'Dolní Věstonice',sub:'Moravia, Czechia',label:'Dolní Věstonice',herd:true});
sh(36.4,39,'valley',{y:25990,warm:300,z0:0.3,z1:0.8,dx0:60,dx1:-80,hour:null,cyc:2.6,place:'The Vézère',sub:'Dordogne, France',label:'Les Eyzies',onLabel:true});
sh(39,46,'flood',{y0:16500,y1:8400,z:.2,place:'Doggerland',sub:'between Britain and Europe'});
sh(46,47.6,'atlas',{from:[8,52,34],to:[16.4,48.2,20],y0:8400,y1:8300});
sh(47.6,51,'valley',{y:8290,warm:600,z0:0.38,z1:0.9,dx0:-150,dx1:150,hour:10,place:'The Danube',sub:'Vienna, Austria · first farmers',label:'Vienna'});
sh(51,55,'valley',{y:3590,warm:600,z0:0.3,z1:0.85,dx0:0,dx1:0,hour:17.5,place:'The Argolid',sub:'Greece · Mycenae',label:'Mycenae',onLabel:true});
sh(55,60.4,'valley',{y:2790,warm:600,z0:0.3,z1:0.85,dx0:0,dx1:0,hour:19.6,place:'The Palatine Hill',sub:'Rome · the first huts',label:'Palatine Hill',onLabel:true});
sh(60.4,72,'atlas',{from:[12.5,41.9,14],to:[20,15,340],y0:2790,y1:0});
sh(72,86.5,'end',{});
const CAP=[[9.2,12.4,"Every letter is alive."],[12.6,16.3,"They get hungry. Make friends. Chase dreams.<br>Choose who to become a word with."],
 [17,19.4,"One family. Walking the real route of humanity."],[21.7,23.8,"Every hill, river and coast is real."],
 [28,30.8,"Into Europe."],[33.5,36.2,"Mammoths on the steppe."],[36.7,38.9,"The ice returns. The seas fall 120 metres."],[39.4,45.6,"Then the ice melts,<br>and the sea swallows Doggerland."],
 [47.9,50.8,"The first farmers."],[51.3,54.8,"Hut by hut. Fire by fire. Word by word."],[55.4,60.1,"The first huts of Rome."],[62,71,"Leave it running. Come back tomorrow.<br>See what they became."]];
let cur=null;const T0=performance.now();
window.__film={shots:S,frame(t){
  const s=S.find(s=>t>=s.a&&t<s.b)||S[S.length-1];const u=(t-s.a)/(s.b-s.a),o=s.o;
  if(cur!==s){cur=s;
    if(s.k==='atlas'||s.k==='black'||s.k==='end')goAtlas();
    if(s.k==='valley'){goValley(o.y,o.warm);const f=o.onLabel&&labelAt(o.label)||focus();s.fx=f.x;s.fy=f.y;if(o.herd){for(let i=0;i<2400&&!(L.S.herd||[]).length;i++)F.step(.1);const h=(L.S.herd||[])[0];if(h){s.fx=(f.x+h.x)/2;s.fy=(f.y+h.y)/2;}}}
    if(s.k==='flood'){goValley(o.y0,300);s.fx=3600;s.fy=2400;}}
  let year=300000,tag=null,tagS='';
  if(s.k==='black'){year=300000;const c=A.cam;aCam(18,12,340);A.year=300000;}
  if(s.k==='atlas'||s.k==='end'){const e=s.k==='end'?{from:[20,15,340],to:[20,15,340],y0:0,y1:0}:o;aFly(e.from,e.to,s.k==='end'?1:u);year=logY(e.y0,e.y1,sm(u));A.year=year;}
  if(s.k==='valley'){year=o.y;let f=focus();if(o.herd&&(L.S.herd||[]).length){const h=L.S.herd;f={x:h.reduce((t,m)=>t+m.x,0)/h.length*.6+f.x*.4,y:h.reduce((t,m)=>t+m.y,0)/h.length*.6+f.y*.4};}const pu=1-Math.pow(1-clamp(u/.55,0,1),3);const zz=Math.exp(lerp(Math.log(o.z0),Math.log(o.z1),pu));setCam(lerp(s.fx,f.x,pu)+lerp(o.dx0,o.dx1,u)*.4,lerp(s.fy,f.y-40,pu),zz);window.__hour=o.hour!=null?o.hour:(7+((t-s.a)/o.cyc*12)%12);tag=o.place;tagS=o.sub;F.setSpeed(o.cyc?60:12);}
  if(s.k==='flood'){year=logY(o.y0,o.y1,sm(u));L.S.settings.historyPreview=year;L.relocate();setCam(3600,2400,o.z+.04*u);window.__hour=10;tag=o.place;tagS=o.sub;F.setSpeed(20);}
  // overlay
  $('.fc-ctr').style.opacity=s.k==='black'?0:s.k==='end'?clamp(1-(t-72)/1,0,1):1;$('.fc-ctr .n').textContent=fmt(year);$('.fc-ctr .u').style.opacity=year<=0?0:1;
  const moving=(s.k==='atlas'&&o.y0!==o.y1)||s.k==='flood';$('.fc-ctr .n').style.filter=moving?'blur(.6px)':'none';
  $('.fc-tag').style.opacity=tag?fadeIO(t,s.a,s.b,.25):0;if(tag){$('.fc-tag .p').textContent=tag;$('.fc-tag .s').textContent=tagS;}
  const c=CAP.find(c=>t>=c[0]&&t<c[1]);$('.fc-cap').style.opacity=c?fadeIO(t,c[0],c[1],.3):0;if(c&&$('.fc-cap').innerHTML!==c[2])$('.fc-cap').innerHTML=c[2];
  // big titles
  let h='',h2='',h3='',bo=0;
  if(t<3.2){if(t>=.3&&t<1.6){h2='300,000 years of being human.';bo=fadeIO(t,.3,1.6,.3);}else if(t>=1.6){h='in 90 seconds.';bo=fadeIO(t,1.6,3.25,.15);}}
  else if(t>=4.1&&t<8.1){h='LETTERHEADS';h2='A world of living letters, on the real Earth.';bo=fadeIO(t,4.1,8.1,.4);}
  else if(t>=73){h='LETTERHEADS';h2='The game you can play without playing.';h3=t>=76?'LETTERHEADS.LIVE &nbsp;·&nbsp; BUILT WITH CLAUDE':'';bo=clamp((t-73)/.8,0,1)*clamp((86.5-t)/.8,0,1);}
  const big=$('.fc-big');big.style.opacity=bo;if($('.fc-big .h').innerHTML!==h)$('.fc-big .h').innerHTML=h;if($('.fc-big .h2').innerHTML!==h2)$('.fc-big .h2').innerHTML=h2;if($('.fc-big .h3').innerHTML!==h3)$('.fc-big .h3').innerHTML=h3;
  const punch=t>=1.6&&t<3.2?1+.25*Math.exp(-(t-1.6)*9):1;big.style.transform=`translateY(-50%) scale(${punch})`;
  // black and flashes
  let bl=0;if(t<3.2)bl=1;else if(t<3.8)bl=1-(t-3.2)/.6;if(t>=72)bl=clamp((t-72)/1.2,0,.72);if(t>86)bl=clamp(.72+(t-86)*.6,0,1);$('.fc-black').style.opacity=bl;
  let fl=0;for(const x of S){if(x.a<3.3||x.a>=72)continue;const d=t-x.a;if(d>=0&&d<.35)fl=Math.max(fl,(x.k==='valley'||x.k==='flood'?.85:.55)*(1-d/.35));}$('.fc-flash').style.opacity=fl;
  window.__adv(1000/30);return{year,shot:s.k,herd:(L.S.herd||[]).length};}};
})();
