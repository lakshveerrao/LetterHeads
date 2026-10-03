import base64,re
import os
O=os.path.dirname(os.path.abspath(__file__))+'/'
s=open(O+'original.html').read()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    assert n==count, (n,old[:80])
    s=s.replace(old,new)
CSS=r"""
#atlasCv{position:fixed;inset:0;width:100%;height:100%;display:block;opacity:0;pointer-events:none;transition:opacity .9s ease;touch-action:none;cursor:grab}
#atlasCv.on{opacity:1;pointer-events:auto}#atlasCv:active{cursor:grabbing}
#atlasUI{display:none}body.atlas-on #atlasUI{display:block}
body.atlas-on .caption,body.atlas-on .zoom:not(.azoom),body.atlas-on .tour-btn,body.atlas-on #elsewhere,body.atlas-on #returnBtn,body.atlas-on #hint,body.atlas-on #storyToast{display:none!important}
body.atlas-on .brand{color:#F6F2E8;text-shadow:0 1px 8px rgba(0,0,0,.7)}body.atlas-on .brand small{color:#E6E1D4}
#atlasBtn.on{background:#E8962F}
.acard{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(16px + env(safe-area-inset-bottom,0px));width:min(640px,calc(100% - 24px));background:rgba(20,26,24,.93);color:var(--card-ink);border-radius:22px;padding:16px 20px 18px;display:flex;flex-direction:column;gap:10px;box-shadow:0 6px 24px rgba(0,0,0,.35)}
.acard p{margin:0 40px 0 0;font-family:Spectral,Georgia,serif;font-size:clamp(20px,3vw,26px);line-height:1.2}
.acard .sub{font-size:14px;line-height:1.45;color:var(--card-muted)}
.atime{display:flex;align-items:center;gap:10px;font-size:13px;color:var(--card-muted)}.atime input{flex:1;min-width:0;accent-color:#E8962F;min-height:32px}.atime label{flex-shrink:0;min-width:112px}
.atime button{flex-shrink:0;min-height:36px;padding:0 14px;border-radius:18px;border:1px solid #8C958E;background:transparent;color:var(--card-ink);font-size:14px}
.acard .row{justify-content:flex-start;gap:8px}.acard .btn-primary,.acard .btn-ghost{height:44px;padding:0 18px;font-size:15px}
.aclose{position:absolute;right:10px;top:10px;width:40px;height:40px;border-radius:20px;border:1px solid rgba(255,255,255,.3);background:transparent;color:#F8F9F6;font-size:18px}
.zoom.azoom{bottom:calc(250px + env(safe-area-inset-bottom,0px))}
#atlasStop{display:none}body.journey #atlasStop{display:inline-block}
body.journey .atime,body.journey #atlasDive,body.journey #atlasJourney,body.journey #atlasInfo,body.journey .aclose,body.journey .azoom{display:none!important}
@media (max-width:600px){.acard{padding:14px 16px 16px;gap:8px}.acard p{font-size:20px}.acard .sub{font-size:13px}.acard .btn-primary,.acard .btn-ghost{height:44px;padding:0 12px;font-size:14px}.acard .wide{display:none}.atime label{min-width:0}}
"""
rep("</style>",CSS+"</style>")
rep('<div class="top">','<canvas id="atlasCv" tabindex="-1" aria-label="The Atlas: the real Earth. Drag to explore, scroll or pinch to zoom, tap a glowing cluster or a marked event to learn about it."></canvas>\n<div class="top">')
rep('  <button class="round" id="soundBtn"','  <button class="round" id="atlasBtn" aria-label="Open the Atlas: the real Earth"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="10" cy="10" r="7.5"/><path d="M2.5 10h15M10 2.5c2.4 2.2 3.4 4.7 3.4 7.5s-1 5.3-3.4 7.5c-2.4-2.2-3.4-4.7-3.4-7.5s1-5.3 3.4-7.5z"/></svg></button>\n  <button class="round" id="soundBtn"')
UI="""<section id="atlasUI">
  <div class="zoom azoom"><button class="round" id="atlasIn" aria-label="Zoom in on the Earth"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M10 4v12M4 10h12"/></svg></button><button class="round" id="atlasOut" aria-label="Zoom out from the Earth"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 10h12"/></svg></button></div>
  <div class="acard" aria-live="polite">
    <button class="aclose" id="atlasSelClose" aria-label="Back to the whole Earth" hidden>×</button>
    <p id="atlasTitle">The Atlas</p><div class="sub" id="atlasSub"></div>
    <div class="atime"><label for="atlasTime" id="atlasWhen">Now in this world</label><input type="range" id="atlasTime" min="0" max="1000" step="1" aria-label="Look at another time in history"><button id="atlasNow" hidden>Now</button></div>
    <div class="row"><button class="btn-primary" id="atlasDive">Dive in<span class="wide"> to the valley</span></button><button class="btn-ghost" id="atlasJourney">▶ Journey</button><button class="btn-ghost" id="atlasInfo">In our world</button><button class="btn-ghost" id="atlasStop">Stop the journey</button></div>
  </div>
</section>
"""
rep('<section class="caption" aria-live="polite">',UI+'<section class="caption" aria-live="polite">')
earth=base64.b64encode(open(O+'earth.jpg','rb').read()).decode()
layers=base64.b64encode(open(O+'layers.png','rb').read()).decode()
rep('<script>\n(()=>{','<script type="text/plain" id="atlasEarth">'+earth+'</script>\n<script type="text/plain" id="atlasLayers">'+layers+'</script>\n<script>\n(()=>{')
# history helpers take an optional year
rep('function historyLabel(){const y=yearsAgo();','function historyLabel(y=yearsAgo()){')
rep('function eraNow(){const y=yearsAgo();','function eraNow(y=yearsAgo()){')
rep('function openOurWorld(){const e=eraNow();const y=yearsAgo();\n  openSheet(`<h2 id="sheetTitle">In our world</h2><p class="muted">${esc(historyLabel())} · ${esc(e.name)}</p>',
    'function openOurWorld(yy){const fromAtlas=typeof yy==="number",y=fromAtlas?yy:yearsAgo();const e=eraNow(y);\n  openSheet(`<h2 id="sheetTitle">In our world</h2><p class="muted">${esc(historyLabel(y))} · ${esc(e.name)}</p>')
rep("Places are named by the letters themselves, so no family ever stands for a real people.</p>`,\"ourworld\");}",
    "Places are named by the letters themselves, so no family ever stands for a real people.</p>${fromAtlas?ATLAS_ABOUT:\"\"}`,\"ourworld\");}")
# mammoths only where the valley really is mammoth country
rep('function herdTick(dt){S.herd=S.herd||[];const y=yearsAgo();\n','function herdTick(dt){S.herd=S.herd||[];const y=yearsAgo();\n  if(y>10000&&!valleyAt(y).mam){S.herd=[];return;}\n')
rep('function makeMoment(o){if(tour)return;','function makeMoment(o){if(tour||ATL.on)return;')
rep('function startTour(){if(tour)return;','function startTour(){if(tour)return;if(ATL.on)closeAtlas(true);')
# the Atlas draws instead of the valley once it has faded in
rep('  ctx.setTransform(DPR,0,0,DPR,0,0);ctx.fillStyle="#D5DBC8";ctx.fillRect(0,0,W,H);worldTransform();',
    '  if(ATL.on){atlasFrame(dtReal);if(ATL.full){requestAnimationFrame(frame);return;}}\n  ctx.setTransform(DPR,0,0,DPR,0,0);ctx.fillStyle="#D5DBC8";ctx.fillRect(0,0,W,H);worldTransform();')
rep('if(tAnim>45)hint("tap");','if(tAnim>45)hint("tap");if(tAnim>150&&!S.settings.atlasSeen)hint("atlas");')
rep('dream:"Every letter has its own dream. Tap a letter to see what it hopes for."};','dream:"Every letter has its own dream. Tap a letter to see what it hopes for.",atlas:"Tap the globe, or zoom all the way out, to see where this valley is on the real Earth."};')
# zooming out past the whole valley opens the Atlas
rep('cv.addEventListener("wheel",e=>{e.preventDefault();takeControl();const[wx,wy]=s2w(e.clientX,e.clientY);',
    'let atlasPull=0;cv.addEventListener("wheel",e=>{e.preventDefault();if(e.deltaY>0&&cam.z<=minZ()*1.02){atlasPull+=e.deltaY;if(atlasPull>350){atlasPull=0;openAtlas();}return;}atlasPull=0;takeControl();const[wx,wy]=s2w(e.clientX,e.clientY);')
rep('if(pointers.size===2){const[p1,p2]=[...pointers.values()];const d=Math.hypot(p1.x-p2.x,p1.y-p2.y);if(drag&&drag.pd)cam.z=clamp(cam.z*d/drag.pd,minZ(),2.4);',
    'if(pointers.size===2){const[p1,p2]=[...pointers.values()];const d=Math.hypot(p1.x-p2.x,p1.y-p2.y);if(drag&&drag.pd){const nz=cam.z*d/drag.pd;if(nz<minZ()&&cam.z<=minZ()*1.02){drag.pull=(drag.pull||1)*d/drag.pd;if(drag.pull<.72){pointers.clear();drag=null;openAtlas();return;}}cam.z=clamp(nz,minZ(),2.4);}')
rep('document.getElementById("zoomOut").onclick=()=>{takeControl();','document.getElementById("zoomOut").onclick=()=>{if(cam.z<=minZ()*1.02){openAtlas();return;}takeControl();')
# menu
rep('<button id="mTour" class="main">▶ Show me around</button>','<button id="mTour" class="main">▶ Show me around</button><button id="mAtlas">🌍 The Atlas</button>')
rep('document.getElementById("mStory").onclick=openStory;','document.getElementById("mStory").onclick=openStory;document.getElementById("mAtlas").onclick=()=>{closeSheet();openAtlas();};')
rep('Zoom all the way out to see the whole continent.</li>','Zoom all the way out to see the whole valley, and further still to open the Atlas.</li><li>The Atlas shows the real Earth from NASA imagery. Seas and ice sheets change with the history clock, and glowing clusters mark where Letterheads live, following humanity\'s real routes. The valley we follow has a real place on it, though its landscape is imagined.</li>')
# test hook
rep('get MAP(){return MAP}};','get MAP(){return MAP},atlas:{open:()=>{atlasIntroCancel();openAtlas();},dive:()=>{atlasIntroCancel();diveIn();},journey:()=>startJourney(),setYear:y=>{atlasIntroCancel();ATL.year=y;atlasCard();},get state(){return ATL},valleyAt:y=>valleyAt(y),seaLevel:y=>seaLevel(y),iceFrac:y=>iceFrac(y)},relocate:()=>relocate(),get place(){return TERRA_READY?placeNow():null},get placeKey(){return MAP.key}};')
# the Atlas code itself, before the captions section
A=open(O+'atlas.js').read()
import json as _j
TM=_j.load(open(O+'../terrain/terrain.json'))
A=A.replace(A[A.index('const VALLEY_PATH=['):A.index('function valleyAt(')],'const VALLEY_PATH=TERRA.map(p=>({y:p.y,lon:p.lon,lat:p.lat,name:p.name,mam:!!p.mam}));\n')
A='const TERRA='+_j.dumps(TM,ensure_ascii=False)+';\n'+open(O+'realworld.js').read()+A
A+='''const ATLAS_ABOUT=`<h3>About the Atlas</h3><ul><li>Imagery: NASA Blue Marble Next Generation with topography and bathymetry (5400 by 2700), from NASA's Earth Observatory.</li><li>Coasts and shelves: NOAA ETOPO1 global relief at 10 arc-minutes; land appears wherever the sea floor lies above the sea level of the moment.</li><li>Sea level: an approximate curve after Spratt and Lisiecki (2016) and Lambeck and colleagues (2014). <span class="muted">To be verified by experts.</span></li><li>Ice sheets: outlines hand-traced at the last glacial maximum after Dyke (2004) and Hughes and colleagues (2016), grown and shrunk with the sea level. <span class="muted">Approximate; to be verified by experts.</span></li><li>The valley's shape: real heights from the Tilezen terrain tiles (SRTM, ETOPO1 and other public elevation data) at 200 metres, for a 36 by 24 kilometre window around a real site of each era. Rivers follow the real land.</li><li>The valley's ground: contains modified Copernicus Sentinel data (2021 to 2023), processed by ESA, from the Sentinel-2 Cloud-Optimized GeoTIFFs on the Registry of Open Data on AWS (Element 84), at 50 metres. Modern towns, farmland, roads and reservoirs were found with ESA WorldCover 2021 (v200, 10 metres; CC BY 4.0) and replaced with real texture of the plant cover the pollen record gives for each era, copied from natural ground in the same scene or a similar place. For the Ice Age sites the texture comes from the Kurai steppe in the Altai, a living analogue of the mammoth steppe with larch on its north slopes. <span class=\"muted\">The mix of cover is our reading of the sources below; to be verified by experts.</span></li><li>Place names: real sites and today's towns, placed from their coordinates on Wikipedia.</li>${TERRA.map(p=>`<li>${p.name[0].toUpperCase()+p.name.slice(1)}: ${p.veg||""}</li>`).join("")}<li>Trees, stones and the letters themselves are the game's own.</li><li>Routes and dates: the earliest widely accepted evidence; debated dates are shown as ranges. <span class="muted">Most are still to be verified by experts.</span></li></ul>`;
'''
rep('// ================= captions =================',A+'// ================= captions =================')
# atlas button state
s=s.replace('document.body.classList.add("atlas-on");atlasCv.classList.add("on");','document.body.classList.add("atlas-on");atlasCv.classList.add("on");{const b=document.getElementById("atlasBtn");b.classList.add("on");b.setAttribute("aria-label","Back to the valley");}')
s=s.replace('document.body.classList.remove("atlas-on");atlasCv.classList.remove("on");','document.body.classList.remove("atlas-on");atlasCv.classList.remove("on");{const b=document.getElementById("atlasBtn");b.classList.remove("on");b.setAttribute("aria-label","Open the Atlas: the real Earth");}')

# ---------- real ground ----------
# the rain-swollen river: one stroke per width, so overlapping round caps don't show as beads
rep('ctx.lineCap="round";for(const sg of MAP.segs){if(!inView(sg.x0,sg.y0,200))continue;ctx.lineWidth=sg.w+lv*38;ctx.beginPath();ctx.moveTo(sg.x0,sg.y0);ctx.lineTo(sg.x1,sg.y1);ctx.stroke();}ctx.restore();}','ctx.lineCap="round";ctx.lineJoin="round";const B=new Map();for(const sg of MAP.segs){if(!inView(sg.x0,sg.y0,200))continue;const w=Math.round((sg.w+lv*38)/6)*6;let p=B.get(w);if(!p){p=new Path2D();B.set(w,p);}p.moveTo(sg.x0,sg.y0);p.lineTo(sg.x1,sg.y1);}for(const[w,p]of B){ctx.lineWidth=w;ctx.stroke(p);}ctx.restore();}')
rep('  {const dtm=performance.now()-_t0;perfAvg','  if(MAP.place!=null&&TERRA_READY)drawPlaceLabels();\n  {const dtm=performance.now()-_t0;perfAvg')
terra=base64.b64encode(open(O+'../terrain/terrain.png','rb').read()).decode()
ground=base64.b64encode(open(O+'../imagery/ground.jpg','rb').read()).decode()
rep('<script type="text/plain" id="atlasEarth">','<script type="text/plain" id="terraData">'+terra+'</script>\n<script type="text/plain" id="groundData">'+ground+'</script>\n<script type="text/plain" id="atlasEarth">')
rep('function genWorld(){\n  const R=mulberry(SEED),','function genWorld(key){\n  key=key||placeKey(worldYear());CROSS=[];REFUGE={x:0,y:0};const real=TERRA_READY;const R=mulberry(SEED+(real?+key.split("|")[0]*7919:0)),')
i0=s.index('  for(let j=0;j<GH;j++)for(let i=0;i<GW;i++){const dx=(i/GW-.5)*1.2');i1=s.index('  // fill the dips first')
s=s[:i0]+'  let RP=null;if(real)RP=realGround(key,h,water,temp,moist,fbm);else{\n'+s[i0:i1]+'  }\n'+s[i1:]
rep('const order=[];for(let k=0;k<N;k++)if(!water[k])order.push(k);order.sort((a,b)=>fl[b]-fl[a]);','const order=[];for(let k=0;k<N;k++)if(!water[k])order.push(k);order.sort((a,b)=>fl[b]-fl[a]);if(RP)for(const[k,v]of RP.inflow)if(!water[k])flow[k]+=v;')
rep('const segs=[];for(const k of order){if(flow[k]>=RT&&!water[k])water[k]=1;}','const segs=[];for(const k of order){if(flow[k]>=RT&&!water[k])water[k]=1;}if(RP)riverGreen(water,moist,flow);')
rep('const sc=-Math.abs(temp[k]-.52)*3-Math.abs(moist[k]-.5)+Math.min(nearC,4)*.3+R()*.3;','const sc=-Math.abs(temp[k]-.52)*3-Math.abs(moist[k]-.5)+Math.min(nearC,4)*.3+R()*.3-(RP?Math.hypot(c.x-WORLD_W/2,c.y-WORLD_H/2)/1500:0);')
rep('MAP={h,water,biome,temp,moist,flow,down,comp,cross,bank,segs,size,nc};','MAP={h,water,biome,temp,moist,flow,down,comp,cross,bank,segs,size,nc,key,place:RP?+key.split("|")[0]:null};')
# start: wait for the terrain, then build the world where history says the valley is
rep('resize();genWorld();const loadedExisting=load();if(!loadedExisting)newWorld();else{(S.structs||[]).filter(t=>t.type==="bridge"&&t.built).forEach(addBridge);}',
 'terraLoad().then(()=>{\nresize();const loadedExisting=load();\nif(!loadedExisting){genWorld();newWorld();S.place=MAP.key;S.placeHome={x:HOME.x,y:HOME.y};}\nelse if(TERRA_READY&&S.place!==placeKey(yearsAgo())){MAP=null;relocate(true);}\nelse{genWorld(TERRA_READY?S.place:undefined);(S.structs||[]).filter(t=>t.type==="bridge"&&t.built).forEach(addBridge);}')
j=s.rindex('})();\n</script>')
s=s[:j]+'if(!params.get("follow")&&!S.settings.reduce){atlasIntro();if(S.settings.introSeen)atlasIntroGo();}\n});\n'+s[j:]
rep('document.getElementById("introGo").onclick=()=>close(true);','document.getElementById("introGo").onclick=()=>{close(true);atlasIntroGo();};')
rep('document.getElementById("introQuiet").onclick=()=>close(false);','document.getElementById("introQuiet").onclick=()=>{close(false);atlasIntroGo();};')
rep('setTimeout(()=>{if(ib.style.display!=="none")close(false);},14000);','setTimeout(()=>{if(ib.style.display!=="none"){close(false);atlasIntroGo();}},14000);')
# place name in the top line, and follow history to new places
rep('${historyLabel()} · ${S.agents.length} letters','${historyLabel()}${TERRA_READY?" "+placeNow().short:""} · ${S.agents.length} letters')
rep('if(tAnim>=(director.nextCap||0)){director.nextCap=tAnim+1;','if(tAnim>=(director.nextCap||0)){director.nextCap=tAnim+1;if(!tour&&!ATL.on&&tAnim>(director.nextPlace||0)){director.nextPlace=tAnim+4;relocate();}')
rep('S.settings.historyPreview=v===""?null:+v;S.herdAt=0;','S.settings.historyPreview=v===""?null:+v;S.herdAt=0;relocate();')
# atlas hint: shown once, after the opening flight lands in the valley
rep('if(tAnim>150&&!S.settings.atlasSeen)hint("atlas");','if(tAnim>12)hint("atlas");')
rep('atlas:"Tap the globe, or zoom all the way out, to see where this valley is on the real Earth."','atlas:"This valley is a real place. Tap Atlas at the top, or zoom all the way out, to see it on the real Earth."')
# labelled Atlas button
s=s.replace('<button class="round" id="atlasBtn" aria-label="Open the Atlas: the real Earth">','<button class="round atlas-pill" id="atlasBtn" aria-label="Open the Atlas: the real Earth">',1)
s=s.replace('3.4-7.5z"/></svg></button>\n  <button class="round" id="soundBtn"','3.4-7.5z"/></svg><span>Atlas</span></button>\n  <button class="round" id="soundBtn"',1)
rep("</style>","""#atlasBtn.atlas-pill{width:auto;padding:0 14px 0 11px;gap:6px;font-weight:600;font-size:15px;display:inline-flex;align-items:center;box-shadow:0 0 0 2px rgba(232,150,47,.55),0 2px 10px rgba(232,150,47,.35)}
#atlasBtn.atlas-pill svg{width:20px;height:20px}
@media (max-width:440px){#soundBtn{display:none}#atlasBtn.atlas-pill{padding:0 12px 0 9px;font-size:14px}}
@media (max-width:330px){#atlasBtn.atlas-pill span{display:none}#atlasBtn.atlas-pill{padding:0 11px}}
</style>""")

rep('const RT=lf[Math.floor(lf.length*.035)]||60;','const RT=RP?Math.max(lf[Math.floor(lf.length*.012)]||60,RP.rt||500):lf[Math.floor(lf.length*.035)]||60;')
rep('w:clamp(14+Math.sqrt(flow[k])*1.6,16,62)','w:RP?clamp(8+Math.sqrt(flow[k])*.45,14,72):clamp(14+Math.sqrt(flow[k])*1.6,16,62)')
rep('if(MAP.biome[k]!==5||MAP.water[k])continue;','if(MAP.biome[k]!==5||MAP.water[k])continue;if(MAP.place!=null&&(i%6||j%4||MAP.h[k]<.66))continue;')
rep('const w=MAP.water[k],b=MAP.biome[k],t=MAP.temp[k]+CLIM;','const w=MAP.water[k],b=MAP.biome[k],t=MAP.temp[k]+CLIM*(MAP.place!=null?.6:1);')

rep('g.lineCap="round";g.lineJoin="round";for(const sg of MAP.segs){g.strokeStyle="#8FB0B8";','g.lineCap="round";g.lineJoin="round";if(MAP.place!=null)drawRealRivers(g);else for(const sg of MAP.segs){g.strokeStyle="#8FB0B8";')
rep('  for(const sg of MAP.segs){if(sg.w<30)continue;','  if(MAP.place==null)for(const sg of MAP.segs){if(sg.w<30)continue;')

rep('<li>The world is an invented continent that works like Earth: rivers run downhill to the sea, mountains cast rain shadows, the north is cold and the south warm. It is the same world for everyone.</li>','<li>The valley is a real place: its hills, rivers and coasts come from real elevation data for a site where people lived at this point in history, and its warmth from the real latitude and the Ice Age climate. As history moves on, the families move along humanity\'s route, from the Omo valley to the Tiber. It is the same world for everyone.</li>')

rep('  for(let j=0;j<GH;j++)for(let i=0;i<GW;i++){g.fillStyle=cellColor(j*GW+i,se);g.fillRect(i*cs,j*cs,cs+1,cs+1);}\n  try{','  if(MAP.place!=null&&TERRA_READY)paintRealGround(g,terrain.width,terrain.height,se);else{for(let j=0;j<GH;j++)for(let i=0;i<GW;i++){g.fillStyle=cellColor(j*GW+i,se);g.fillRect(i*cs,j*cs,cs+1,cs+1);}\n  try{')
rep('tg.filter="blur(3px)";tg.drawImage(terrain,0,0);g.drawImage(tmp,0,0);}catch(e){}','tg.filter="blur(3px)";tg.drawImage(terrain,0,0);g.drawImage(tmp,0,0);}catch(e){}}')

rep('function drawTree(tr,t){const sc=','function drawTree(tr,t){if(MAP.place!=null&&!tr.charred&&!(tr.burning>S.simT)){drawTreeReal(tr,t);return;}const sc=')
rep('if(document.fonts&&document.fonts.ready)document.fonts.ready.then(buildTerrain);','if(document.fonts&&document.fonts.ready)document.fonts.ready.then(()=>{if(MAP.place==null)buildTerrain();});')

rep('ctx.imageSmoothingEnabled=true;ctx.drawImage(terrain,0,0,WORLD_W,WORLD_H);drawCrossings(tAnim);','ctx.imageSmoothingEnabled=true;if(MAP.place!=null&&TERRA_READY){drawGround();drawCloudShadows();}else ctx.drawImage(terrain,0,0,WORLD_W,WORLD_H);drawCrossings(tAnim);')

exec(open(O+'trailer_patch.py').read())
exec(open(O+'product_patch.py').read())
exec(open(O+'growth_patch.py').read())
exec(open(O+'shared_patch.py').read())
exec(open(O+'polish_patch.py').read())
exec(open(O+'living_patch.py').read())
exec(open(O+'move_patch.py').read())
exec(open(O+'quiet_patch.py').read())
exec(open(O+'play_patch.py').read())
exec(open(O+'broadcast_patch.py').read())
open(O+'letterheads.html','w').write(s)
open(O+'../../site/play/index.html','w').write(s)  # the live site serves the game at /play/
print(len(s))
