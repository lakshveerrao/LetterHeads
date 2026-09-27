// ================= the valley's ground: real terrain where the valley really is =================
// Elevation: Tilezen/Mapzen terrain tiles (SRTM and others) sampled at 200 m; moisture: NASA Blue Marble greenness.
// Each place is a 36 by 24 km window; the letters' 7200 by 4800 world maps onto it.
let TERRA_READY=false,PLACE_I=0;
const PLACE_KM=36;
function terraLoad(){return new Promise(res=>{const img=new Image();img.onload=()=>{try{const c=document.createElement("canvas");c.width=img.width;c.height=img.height;const g=c.getContext("2d");g.drawImage(img,0,0);
  const d=g.getImageData(0,0,c.width,c.height).data,n=GW*GH;TERRA.forEach((p,pi)=>{p.elev=new Float32Array(n);p.moist=new Float32Array(n);for(let k=0;k<n;k++){const o=(pi*n+k)*4;p.elev[k]=(d[o]*256+d[o+1])/4-12000;p.moist[k]=d[o+2]/255;}});TERRA_READY=true;}catch(e){}groundLoad().then(res);};
  img.onerror=()=>res();img.src="data:image/png;base64,"+document.getElementById("terraData").textContent.trim();});}
// The ground itself: Copernicus Sentinel-2 imagery of each window (720 by 480 at 50 m), where modern towns,
// fields and reservoirs (found with ESA WorldCover) are replaced by real texture of the plant cover the
// pollen record gives for that era. One JPEG, the places stacked top to bottom in TERRA order.
let GROUND=null;const GPW=720,GPH=480;
function groundLoad(){return new Promise(res=>{const el=document.getElementById("groundData");if(!el){res();return;}const img=new Image();
  img.onload=()=>{try{const c=document.createElement("canvas");c.width=img.width;c.height=img.height;c.getContext("2d").drawImage(img,0,0);GROUND=c;}catch(e){}res();};img.onerror=()=>res();
  img.src="data:image/jpeg;base64,"+el.textContent.trim();});}
function placeIdx(y){y=Math.max(0,y);let i=0;while(i<TERRA.length-1&&y<=TERRA[i+1].y)i++;return i;}
function worldYear(){return S&&S.created?yearsAgo():HIST_SEG[0][2];}
function placeKey(y){const i=placeIdx(y),P=TERRA[i];return i+"|"+(P.sea?Math.round(seaLevel(y)/4)*4:0)+(P.rev?"|"+P.rev:"");}
function placeNow(){return TERRA[PLACE_I];}
// latitude and height give the warmth; the era's climate is added when the ground is drawn
function realTemp(lat,e){const T=28-.45*Math.max(0,Math.abs(lat)-12)-6*Math.max(0,e)/1000;return(T+2)/32;}
function realGround(key,h,water,temp,moist,fbm){const[pi,sl]=key.split("|").map(Number),P=TERRA[pi],E=P.elev,M=P.moist,N=GW*GH;PLACE_I=pi;
  const sea=P.sea?sl:-1e9,lo=P.sea?Math.min(sl,P.emin):P.emin;
  // the sea reaches only cells joined to the edge of the map below sea level
  const ocean=new Uint8Array(N);if(P.sea){const q=[];for(let k=0;k<N;k++){const i=k%GW,j=(k/GW)|0;if((i===0||j===0||i===GW-1||j===GH-1)&&E[k]<sea){ocean[k]=1;q.push(k);}}
    while(q.length){const k=q.pop(),i=k%GW,j=(k/GW)|0;for(const[di,dj]of[[1,0],[-1,0],[0,1],[0,-1]]){const ii=i+di,jj=j+dj;if(ii<0||jj<0||ii>=GW||jj>=GH)continue;const kk=jj*GW+ii;if(!ocean[kk]&&E[kk]<sea){ocean[kk]=1;q.push(kk);}}}}
  const lake=new Uint8Array(N);if(P.lake!=null){let s=-1,bd=1e9;for(let k=0;k<N;k++)if(E[k]<P.lake){lake[k]=1;}}
  for(let j=0;j<GH;j++)for(let i=0;i<GW;i++){const k=j*GW+i,e=E[k],nz=(fbm(i/7+30,j/7+11)-.5)*.006;
    if(ocean[k]){h[k]=-.05-(sea-e)/1500;water[k]=3;}else{h[k]=Math.max(.012,Math.min(1,(e-lo)/1000*.9+.02+nz));if(lake[k])water[k]=2;}
    temp[k]=clamp(realTemp(P.lat,e)+(fbm(i/30+9,j/30+3)-.5)*.06,0,1);
    moist[k]=clamp(Math.max(P.mfloor||0,M[k])*.8+(fbm(i/14+50,j/14)-.5)*.3+.05,0,1);}
  return P;}
// rivers green their banks (the Nile's strip of fields in the desert)
function riverGreen(water,moist,flow){const N=GW*GH,d=new Int16Array(N).fill(99),q=[];for(let k=0;k<N;k++)if(water[k]===1||water[k]===2){d[k]=0;q.push(k);}
  for(let qi=0;qi<q.length;qi++){const k=q[qi];if(d[k]>=7)continue;const i=k%GW,j=(k/GW)|0;for(const[di,dj]of[[1,0],[-1,0],[0,1],[0,-1]]){const ii=i+di,jj=j+dj;if(ii<0||jj<0||ii>=GW||jj>=GH)continue;const kk=jj*GW+ii;if(d[kk]>d[k]+1){d[kk]=d[k]+1;q.push(kk);}}}
  for(let k=0;k<N;k++)if(!water[k]&&d[k]<8)moist[k]=clamp(moist[k]+.42*(1-d[k]/8),0,1);}
// hill shading from the real heights, so valleys, cliffs and ridges read at a glance
function drawRelief(g,wpx,hpx){const P=placeNow();if(!P||!P.elev)return;const E=P.elev,c=document.createElement("canvas");c.width=GW;c.height=GH;const x=c.getContext("2d"),im=x.createImageData(GW,GH);
  for(let j=0;j<GH;j++)for(let i=0;i<GW;i++){const k=j*GW+i;if(MAP.water[k]){im.data[k*4+3]=0;continue;}const e=(ii,jj)=>E[clamp(jj,0,GH-1)*GW+clamp(ii,0,GW-1)];
    const dx=(e(i+1,j)-e(i-1,j))/400,dy=(e(i,j+1)-e(i,j-1))/400;const s=clamp((-dx*.7-dy*.7)*2.2,-1,1);const o=k*4;
    if(s<0){im.data[o]=40;im.data[o+1]=46;im.data[o+2]=52;im.data[o+3]=Math.round(-s*120);}else{im.data[o]=255;im.data[o+1]=250;im.data[o+2]=236;im.data[o+3]=Math.round(s*70);}}
  x.putImageData(im,0,0);g.save();g.imageSmoothingEnabled=true;g.imageSmoothingQuality="high";g.drawImage(c,0,0,wpx,hpx);g.restore();}
// when history moves the valley (or the sea rises), the families go with it
function relocate(force){if(!TERRA_READY||!S)return false;const key=placeKey(yearsAgo());if(!force&&MAP&&MAP.key===key)return false;
  const oldHome={x:HOME.x,y:HOME.y},oldPlace=MAP&&MAP.place!=null?MAP.place:(S.place?+S.place.split("|")[0]:-1),fresh=!S.place;
  const pts=S.agents.length?S.agents:[oldHome];const cx=pts.reduce((t,a)=>t+a.x,0)/pts.length,cy=pts.reduce((t,a)=>t+a.y,0)/pts.length;
  const ref=MAP&&MAP.place!=null?oldHome:(S.placeHome||{x:cx,y:cy});
  genWorld(key);const moved=oldPlace!==MAP.place,dx=moved?HOME.x-ref.x:0,dy=moved?HOME.y-ref.y:0;const hc=MAP.comp[cellIdx(HOME.x,HOME.y)];
  const land=p=>{p.x=clamp(p.x+dx,60,WORLD_W-60);p.y=clamp(p.y+dy,60,WORLD_H-60);const k=cellIdx(p.x,p.y);if(!MAP.water[k]&&(!moved||MAP.comp[k]===hc))return true;
    const n=nearestCell(p,kk=>!MAP.water[kk]&&!MAP.bank[kk]&&MAP.comp[kk]===hc,60);if(n<0){p.x=HOME.x;p.y=HOME.y;return false;}const c=cellCenter(n);p.x=c.x+(Math.random()-.5)*20;p.y=c.y+(Math.random()-.5)*20;return false;};
  for(const a of S.agents){land(a);if(a.hx!=null){a.hx+=dx;a.hy+=dy;}a.act=null;a.crossing=null;a.crossExit=null;a.path=null;a.lastComp=side(a.x,a.y);a.decideAt=S.simT+Math.random()*2;if(moved)a.map={t:{},r:{}};}
  for(const w of S.words){const p={x:w.x,y:w.y};land(p);w.x=clamp(p.x,170,WORLD_W-170);w.y=clamp(p.y,200,WORLD_H-130);}
  S.structs=S.structs.filter(s=>s.type!=="bridge"||(!moved&&MAP.water[s.k]===1));
  for(const s of S.structs){if(s.type==="bridge"){addBridge(s);continue;}const p={x:s.x,y:s.y};land(p);s.x=p.x;s.y=p.y;}
  S.seeds=(S.seeds||[]).filter(s=>{s.x+=dx;s.y+=dy;return!inWater(s.x,s.y);});S.beasts=[];S.herd=[];S.herdAt=0;
  if(moved){S.trees=[];MAP.trees.forEach(t=>S.trees.push({x:t.x,y:t.y,fruit:Math.max(1,t.max-1),max:t.max,t:Math.random()*30}));S.res=[];MAP.res.forEach((r,i)=>S.res.push({id:i,type:r.type,x:r.x,y:r.y,amt:r.max,max:r.max,t:0}));
    if(S.bridge){S.bridge.built=false;}S.words.forEach(w=>{w.builtBridge=false;});}
  else{S.trees=S.trees.filter(t=>!inWater(t.x,t.y));S.res=S.res.filter(r=>!inWater(r.x,r.y));}
  S.place=MAP.key;S.placeHome={x:HOME.x,y:HOME.y};if(!fresh&&oldPlace>=0&&typeof buildTerrain==="function"){buildTerrain();
    const P=placeNow();if(moved){const t=`The families have walked on, to ${P.name}.`;chron(t+" In our world, people were living here around this time.","world");addStory({kind:"world",ids:S.agents[0]?[S.agents[0].id]:[],main:S.agents[0]?.id,text:t,sub:"The Atlas shows where this is on the real Earth.",score:80,dur:14});}
    else if(P.sea){chron(`The coastline has moved. In our world, the sea rose and fell with the ice.`,"world");}}
  cam.x=cam.tx=clamp(cam.x+dx,0,WORLD_W);cam.y=cam.ty=clamp(cam.y+dy,0,WORLD_H);return true;}
// the opening: the whole Earth first, then down into the valley
let atlasIntroT=[];
function atlasIntroCancel(){atlasIntroT.forEach(clearTimeout);atlasIntroT=[];}
function atlasIntro(){openAtlas();const v=valleyAt(atlasY()),c=ATL.cam;c.z=c.tz=spanZ(170);c.x=c.tx=v.x;c.y=c.ty=v.yy+cardLift();}
function atlasIntroGo(){atlasIntroCancel();if(!ATL.on||S.settings.reduce)return;const v=valleyAt(atlasY());
  atlasIntroT.push(setTimeout(()=>{if(ATL.on&&!ATL.jr&&!ATL.sel)flyTo(v.lon,v.lat,12);},2400));
  atlasIntroT.push(setTimeout(()=>{if(ATL.on&&!ATL.jr&&!ATL.sel)diveIn();},6600));}
["pointerdown","wheel","keydown"].forEach(ev=>{document.getElementById("atlasCv").addEventListener(ev,atlasIntroCancel,{capture:true,passive:true});document.getElementById("atlasUI").addEventListener(ev,atlasIntroCancel,{capture:true,passive:true});});
// rivers drawn as smoothed chains, as wide as the water they carry
function drawRealRivers(g){const M=MAP,N=GW*GH,cc=k=>cellCenter(k),wOf=k=>clamp(8+Math.sqrt(M.flow[k])*.6,14,95);
  const hasUp=new Uint8Array(N);for(let k=0;k<N;k++)if(M.water[k]===1&&M.down[k]>=0)hasUp[M.down[k]]=1;
  const seen=new Uint8Array(N),chains=[];
  const walk=s=>{const pts=[];let k=s;while(k>=0){const c=cc(k);pts.push([c.x,c.y,wOf(k)]);if(M.water[k]!==1||seen[k])break;seen[k]=1;const d=M.down[k];if(d<0)break;k=d;}if(pts.length>1)chains.push(pts);};
  for(let k=0;k<N;k++)if(M.water[k]===1&&!hasUp[k])walk(k);for(let k=0;k<N;k++)if(M.water[k]===1&&!seen[k])walk(k);
  const smooth=p=>{for(let it=0;it<3;it++){const q=[p[0]];for(let i=0;i<p.length-1;i++){const a=p[i],b=p[i+1];q.push([a[0]*.75+b[0]*.25,a[1]*.75+b[1]*.25,a[2]*.75+b[2]*.25],[a[0]*.25+b[0]*.75,a[1]*.25+b[1]*.75,a[2]*.25+b[2]*.75]);}q.push(p[p.length-1]);p=q;}return p;};
  const sm=chains.map(smooth);
  // translucent passes are drawn solid on their own layer, then laid on at their alpha, so overlapping round caps never show as beads
  const PASS=[["rgb(70,64,44)",1,10,.45],["#3F6A70",1,0,1],["#4F7E84",.55,0,1],["rgb(170,200,200)",.12,0,.18]];
  let lay=null;
  for(const[col,f,add,al]of PASS){let t=g;if(al<1){if(!lay){lay=document.createElement("canvas");lay.width=g.canvas.width;lay.height=g.canvas.height;}t=lay.getContext("2d");t.setTransform(g.getTransform());t.clearRect(0,0,lay.width*4,lay.height*4);t.lineCap="round";t.lineJoin="round";}
    t.strokeStyle=col;for(const p of sm)for(let i=0;i<p.length-1;i++){const w=(p[i][2]+p[i+1][2])/2;if(f<.9&&w<24)continue;t.lineWidth=(w*f+add)/TS;t.beginPath();t.moveTo(p[i][0]/TS,p[i][1]/TS);t.lineTo(p[i+1][0]/TS,p[i+1][1]/TS);t.stroke();}
    if(t!==g){g.save();g.setTransform(1,0,0,1,0,0);g.globalAlpha=al;g.drawImage(lay,0,0);g.restore();}}}
// trees seen from above at an angle: a leafy crown lit from the north-west, with its shadow on the ground
const TREE_SPR=[];function treeSprite(v){if(TREE_SPR[v])return TREE_SPR[v];const c=document.createElement("canvas");c.width=c.height=160;const g=c.getContext("2d"),R=mulberry(900+v*31);g.translate(80,96);
  g.fillStyle="rgba(20,24,14,.28)";g.beginPath();g.ellipse(14,20,40,16,.2,0,Math.PI*2);g.fill();
  g.fillStyle="#4A3A28";g.fillRect(-4,-8,8,28);
  const pal=v%2?[[58,84,44],[76,104,54],[98,126,66],[124,148,82]]:[[70,86,46],[92,104,58],[118,126,72],[146,148,92]];
  for(let l=0;l<4;l++){const n=l===0?16:12-l*2;for(let i=0;i<n;i++){const a=R()*Math.PI*2,rr=R()*(30-l*6),x=Math.cos(a)*rr-l*4,y=-30+Math.sin(a)*rr*.8-l*4,cr=12-l*1.5+R()*5;const col=pal[l];const f=.92+R()*.16;
    g.fillStyle=`rgb(${col[0]*f|0},${col[1]*f|0},${col[2]*f|0})`;g.beginPath();g.arc(x,y,cr,0,Math.PI*2);g.fill();}}
  TREE_SPR[v]=c;return c;}
function drawTreeReal(tr,t){const sc=tr.sprout?clamp((S.simT-tr.sprout)/(tr.owner?160:240),.3,1):1;const v=((tr.x*7+tr.y*13)|0)%4;ctx.save();ctx.translate(tr.x,tr.y);ctx.scale(sc,sc);
  ctx.drawImage(treeSprite(v),-80,-96);ctx.fillStyle="#A8322A";for(let i=0;i<tr.fruit;i++){const an=i*1.3+.4;ctx.beginPath();ctx.arc(Math.cos(an)*18-2,-30+Math.sin(an)*13,3,0,Math.PI*2);ctx.fill();}
  if(tr.owner){ctx.strokeStyle="rgba(120,90,50,.5)";ctx.lineWidth=2;ctx.beginPath();ctx.ellipse(0,26,22,6,0,0,Math.PI*2);ctx.stroke();}ctx.restore();}
// the ground itself, painted like an aerial photograph of the real land: bare soil and sand, patchy grass and scrub,
// woods along the rivers, rock on steep slopes, all lit by a low sun from the north-west
const NOISE=(()=>{const n=256,a=new Float32Array(n*n),R=mulberry(771);const base=new Float32Array(64*64).map(()=>R());
  const vn=(x,y,p)=>{const xi=Math.floor(x),yi=Math.floor(y),xf=x-xi,yf=y-yi,s=t=>t*t*(3-2*t),g=(i,j)=>base[((j%p+p)%p)*64+((i%p+p)%p)];return lerp(lerp(g(xi,yi),g(xi+1,yi),s(xf)),lerp(g(xi,yi+1),g(xi+1,yi+1),s(xf)),s(yf));};
  for(let y=0;y<n;y++)for(let x=0;x<n;x++){let v=0,am=.5,f=4;for(let o=0;o<5;o++){v+=vn(x/n*f,y/n*f,f)*am;am*=.5;f*=2;}a[y*n+x]=v/.97;}return a;})();
const nz=(x,y)=>NOISE[((y|0)&255)*256+((x|0)&255)];
function paintRealGround(g,cw,ch,se){const P=placeNow(),E=P.elev,N=GW*GH,M=MAP,clim=CLIM*.6;
  const at=(i,j)=>E[clamp(j,0,GH-1)*GW+clamp(i,0,GW-1)];
  // per-cell fields: slope, local relief (for valley shade), nearness to water
  const FS=10,F=new Float32Array(N*FS);const wd=new Int16Array(N).fill(99),q=[];for(let k=0;k<N;k++)if(M.water[k]){wd[k]=0;q.push(k);}
  for(let qi=0;qi<q.length;qi++){const k=q[qi];if(wd[k]>=6)continue;const i=k%GW,j=(k/GW)|0;for(const[di,dj]of[[1,0],[-1,0],[0,1],[0,-1]]){const ii=i+di,jj=j+dj;if(ii<0||jj<0||ii>=GW||jj>=GH)continue;const kk=jj*GW+ii;if(wd[kk]>wd[k]+1){wd[kk]=wd[k]+1;q.push(kk);}}}
  for(let j=0;j<GH;j++)for(let i=0;i<GW;i++){const k=j*GW+i;let m=0,c=0;for(let dj=-3;dj<=3;dj++)for(let di=-3;di<=3;di++){m+=at(i+di,j+dj);c++;}
    const o=k*FS,wk=M.water[k];F[o]=(at(i+1,j)-at(i-1,j))/400;F[o+1]=(at(i,j+1)-at(i,j-1))/400;F[o+2]=clamp((E[k]-m/c)/40,-1,1);F[o+3]=clamp(1-wd[k]/6,0,1);F[o+4]=M.moist[k];F[o+5]=M.temp[k]+clim;F[o+6]=wk===2||wk===3?1:0;F[o+7]=wk>=2?clamp(-M.h[k]*8,0,1):0;F[o+8]=M.biome[k]===2?1:0;F[o+9]=M.biome[k]===5?1:0;}
  const img=g.createImageData(cw,ch),d=img.data,sx=GW/cw,sy=GH/ch;
  const bil=(fx,fy,o)=>{const i0=clamp(Math.floor(fx),0,GW-1),j0=clamp(Math.floor(fy),0,GH-1),i1=Math.min(GW-1,i0+1),j1=Math.min(GH-1,j0+1),tx=clamp(fx-i0,0,1),ty=clamp(fy-j0,0,1);
    return(F[(j0*GW+i0)*FS+o]*(1-tx)+F[(j0*GW+i1)*FS+o]*tx)*(1-ty)+(F[(j1*GW+i0)*FS+o]*(1-tx)+F[(j1*GW+i1)*FS+o]*tx)*ty;};
  const autumn=se==="autumn",winter=se==="winter",spring=se==="spring";
  const ph=GROUND&&GROUND.height>=(PLACE_I+1)*GPH?GROUND.getContext("2d").getImageData(0,PLACE_I*GPH,GPW,GPH).data:null,pux=GPW/cw,puy=GPH/ch;
  for(let py=0;py<ch;py++){const fy=(py+.5)*sy-.5;for(let px=0;px<cw;px++){const fx=(px+.5)*sx-.5,o=(py*cw+px)*4;
    const k=clamp(Math.round(fy),0,GH-1)*GW+clamp(Math.round(fx),0,GW-1),w=M.water[k];
    const n1=nz(px*1.73+py*.37,py*1.69-px*.41),n2=nz(px/5+97,py/5+31),n3=nz(px/26+13,py/26+177),n4=nz(px/90+61,py/90+5);
    let r,gg,b;
    const sw=bil(fx,fy,6);if(sw+(n2-.5)*.3>.5){const dp=bil(fx,fy,7);r=lerp(78,44,dp);gg=lerp(122,84,dp);b=lerp(128,108,dp);const f=1+(n1-.5)*.05+(n2-.5)*.06;d[o]=r*f;d[o+1]=gg*f;d[o+2]=b*f;d[o+3]=255;continue;}
    const gx=bil(fx,fy,0),gy=bil(fx,fy,1),rel=bil(fx,fy,2),wet=bil(fx,fy,3),m=bil(fx,fy,4),t=bil(fx,fy,5),slope=Math.hypot(gx,gy);
    // bare ground: sand in the dry, brown earth in the wet
    const dry=clamp(1-(m-.15)/.4,0,1);r=lerp(118,214,dry);gg=lerp(98,186,dry);b=lerp(72,138,dry);
    if(dry>.6){const rip=Math.sin(py*.9+px*.25+n3*9)*.5+.5;const u=(dry-.6)*.06*rip;r*=1+u;gg*=1+u;b*=1+u;}
    // plant cover, in patches
    let cov=clamp((m-.12)*1.5+(n3-.5)*.9+(n4-.5)*.5+wet*.45-(slope>.18?(slope-.18)*3:0),0,1);cov=cov*cov*(3-2*cov);
    let vr=lerp(150,86,clamp((m-.25)/.45,0,1)),vg=lerp(146,112,clamp((m-.25)/.45,0,1)),vb=lerp(92,54,clamp((m-.25)/.45,0,1));
    const fo=bil(fx,fy,8),mo=bil(fx,fy,9);if(wet>.4||fo>0){const u=Math.max(fo*.55,(wet-.4)*1.2);vr=lerp(vr,52,u);vg=lerp(vg,78,u);vb=lerp(vb,40,u);}
    if(t<.36){const u=clamp((.36-t)/.18,0,1);vr=lerp(vr,172,u);vg=lerp(vg,164,u);vb=lerp(vb,116,u);}
    if(autumn){vr=lerp(vr,176,.22);vg=lerp(vg,150,.22);vb=lerp(vb,84,.22);}else if(spring){vr=lerp(vr,110,.15);vg=lerp(vg,150,.15);vb=lerp(vb,70,.15);}
    const sc1=nz(px*.83+py*.31+17,py*.79-px*.29+53)*.55+nz(px*.37-py*.53+71,py*.41+px*.47+9)*.45;const scrub=cov>.25?1-clamp((sc1-.6)*6,0,1)*.3:1;vr*=scrub;vg*=scrub;vb*=scrub;
    r=lerp(r,vr,cov);gg=lerp(gg,vg,cov);b=lerp(b,vb,cov);
    // rock on steep ground, with layered streaks
    if(slope>.15){const u=clamp((slope-.15)/.25,0,.9),st=.9+Math.sin(bil(fx,fy,0)*0+(px*.3+py*.9)*.15+n2*4)*.08;r=lerp(r,158*st,u);gg=lerp(gg,148*st,u);b=lerp(b,132*st,u);}
    // wet margins of rivers and lakes
    if(wet>.8){const u=(wet-.8)*3;r=lerp(r,96,u*.6);gg=lerp(gg,92,u*.6);b=lerp(b,70,u*.6);}
    // the real ground, seen from orbit, laid over the painted one; bare rock still shows on the steepest slopes
    let photo=0;if(ph){const u=clamp((px+.5)*pux-.5,0,GPW-1.001),v=clamp((py+.5)*puy-.5,0,GPH-1.001),i0=u|0,j0=v|0,tx=u-i0,ty=v-j0,o0=(j0*GPW+i0)*4,o1=o0+GPW*4;
      const s=c=>(ph[o0+c]*(1-tx)+ph[o0+4+c]*tx)*(1-ty)+(ph[o1+c]*(1-tx)+ph[o1+4+c]*tx)*ty;let pr=s(0)*1.12,pg=s(1)*1.12,pb=s(2)*1.12;
      if(autumn){pr=lerp(pr,176,.14);pg=lerp(pg,150,.14);pb=lerp(pb,84,.14);}else if(winter){const l=(pr+pg+pb)/3;pr=lerp(pr,l*1.05,.35);pg=lerp(pg,l,.35);pb=lerp(pb,l*.95,.35);}
      photo=.9-clamp((slope-.3)/.3,0,.5);r=lerp(r,pr,photo);gg=lerp(gg,pg,photo);b=lerp(b,pb,photo);}
    // snow and frost in the cold
    const snowU=t<.06?1:(winter&&t<.35)?clamp((.35-t)/.15,0,1)*(.4+n2*.6):(mo>0&&t<.3)?mo*clamp((.3-t)/.1,0,1)*clamp(slope*3,0,1):0;
    if(snowU>0){r=lerp(r,236,snowU);gg=lerp(gg,238,snowU);b=lerp(b,240,snowU);}
    // sunlight from the north-west, darker hollows, lighter crests, and fine grain
    let sh=clamp(.92+(-gx*.7-gy*.7)*2.6,.6,1.25)*(1+rel*.1);sh=1+(sh-1)*(1-photo*.55);const f=sh*(1+(n1-.5)*.14*(1-photo*.6)+(n2-.5)*.08*(1-photo));
    d[o]=r*f;d[o+1]=gg*f;d[o+2]=b*f;d[o+3]=255;}}
  g.putImageData(img,0,0);}
// close up, the ground is rebuilt in sharp 480-unit tiles: the painted land, a fine grain of soil and grass,
// and scattered tufts, stones and flowers that suit each place
const GCH=480;let gChunks=new Map(),gTerrain=null,gBuilt=0,DETAIL=null;
function detailTex(){if(DETAIL)return DETAIL;const n=256,c=document.createElement("canvas");c.width=c.height=n;const g=c.getContext("2d"),im=g.createImageData(n,n),R=mulberry(4242);
  for(let y=0;y<n;y++)for(let x=0;x<n;x++){const v=128+(NOISE[((y*3)&255)*256+((x*3)&255)]-.5)*70+(NOISE[((y*7+50)&255)*256+((x*7+90)&255)]-.5)*50+(R()-.5)*26;const o=(y*n+x)*4;im.data[o]=im.data[o+1]=im.data[o+2]=clamp(v,0,255);im.data[o+3]=255;}
  g.putImageData(im,0,0);g.lineCap="round";for(let i=0;i<700;i++){const x=R()*n,y=R()*n,l=3+R()*6,a=-Math.PI/2+(R()-.5)*1.2;g.strokeStyle=R()<.5?"rgba(40,40,40,.35)":"rgba(230,230,230,.3)";g.lineWidth=.8+R()*.8;
    for(const[ox,oy]of[[0,0],[-n,0],[0,-n],[n,0],[0,n]]){g.beginPath();g.moveTo(x+ox,y+oy);g.lineTo(x+ox+Math.cos(a)*l,y+oy+Math.sin(a)*l);g.stroke();}}
  DETAIL=c;return c;}
function groundChunk(cx,cy){const key=cx+","+cy;let c=gChunks.get(key);if(c){gChunks.delete(key);gChunks.set(key,c);return c;}if(gBuilt>=2)return null;gBuilt++;
  c=document.createElement("canvas");c.width=c.height=GCH;const g=c.getContext("2d");g.imageSmoothingEnabled=true;g.imageSmoothingQuality="high";
  const s0=GCH/TS;g.drawImage(terrain,cx*s0-1,cy*s0-1,s0+2,s0+2,-TS,-TS,GCH+2*TS,GCH+2*TS);
  g.save();g.globalCompositeOperation="overlay";g.globalAlpha=.5;const pat=g.createPattern(detailTex(),"repeat");g.translate(-((cx*GCH)%256),-((cy*GCH)%256));g.fillStyle=pat;g.fillRect(0,0,GCH+256,GCH+256);g.restore();
  const R=mulberry(cx*7919+cy*104729+13),se=season(),clim=CLIM*.6;
  for(let i=0;i<340;i++){const x=R()*GCH,y=R()*GCH,wx=cx*GCH+x,wy=cy*GCH+y;if(wx>=WORLD_W||wy>=WORLD_H)continue;const k=cellIdx(wx,wy);if(MAP.water[k]||MAP.bank[k]&&R()<.5)continue;
    const m=MAP.moist[k],t=MAP.temp[k]+clim,r=R();
    if(t<.06)continue;
    if(r<m*.9){// a tuft of grass
      const dry=se==="autumn"||m<.3||t<.3;g.strokeStyle=dry?`rgba(${150+R()*30|0},${138+R()*20|0},${80+R()*20|0},.85)`:`rgba(${70+R()*30|0},${100+R()*30|0},${48+R()*20|0},.85)`;g.lineWidth=1.3;g.lineCap="round";
      const n=4+(R()*4|0),h=6+R()*7;for(let j=0;j<n;j++){const a=-Math.PI/2+(j/(n-1)-.5)*1.3+(R()-.5)*.3;g.beginPath();g.moveTo(x+(j-n/2)*1.2,y);g.quadraticCurveTo(x+Math.cos(a)*h*.4,y+Math.sin(a)*h*.6,x+Math.cos(a)*h,y+Math.sin(a)*h);g.stroke();}
      if((se==="spring"||se==="summer")&&m>.4&&R()<.18){g.fillStyle=["#E9D35A","#F1F0EA","#C77DB5","#E07A4F"][R()*4|0];for(let j=0;j<3;j++){g.beginPath();g.arc(x+(R()-.5)*10,y-4-R()*6,1.6,0,Math.PI*2);g.fill();}}}
    else if(r<m*.9+.12){// a stone
      const s=2+R()*4;g.fillStyle="rgba(30,28,24,.25)";g.beginPath();g.ellipse(x+1.5,y+1.5,s*1.2,s*.8,0,0,Math.PI*2);g.fill();const v=120+R()*50|0;g.fillStyle=`rgb(${v},${v-4},${v-12})`;g.beginPath();g.ellipse(x,y,s*1.2,s*.8,R(),0,Math.PI*2);g.fill();
      g.fillStyle="rgba(255,255,255,.25)";g.beginPath();g.ellipse(x-s*.35,y-s*.3,s*.45,s*.25,0,0,Math.PI*2);g.fill();}}
  gChunks.set(key,c);if(gChunks.size>36)gChunks.delete(gChunks.keys().next().value);return c;}
function drawGround(){if(gTerrain!==terrain){gChunks.clear();gTerrain=terrain;}gBuilt=0;ctx.drawImage(terrain,0,0,WORLD_W,WORLD_H);if(cam.z<.45)return;
  const x0=Math.max(0,Math.floor(VIEW.x0/GCH)),x1=Math.min(Math.ceil(WORLD_W/GCH)-1,Math.floor(VIEW.x1/GCH)),y0=Math.max(0,Math.floor(VIEW.y0/GCH)),y1=Math.min(Math.ceil(WORLD_H/GCH)-1,Math.floor(VIEW.y1/GCH));
  // nearest tiles first, so the middle of the screen sharpens first
  const list=[];for(let cy=y0;cy<=y1;cy++)for(let cx=x0;cx<=x1;cx++)list.push([cx,cy,Math.hypot((cx+.5)*GCH-cam.x,(cy+.5)*GCH-cam.y)]);list.sort((a,b)=>a[2]-b[2]);
  for(const[cx,cy]of list){const c=groundChunk(cx,cy);if(c)ctx.drawImage(c,cx*GCH,cy*GCH,GCH,GCH);}}
// the shadows of passing clouds drift over the land
function drawCloudShadows(){const t=S.settings.reduce?0:performance.now()/1000;ctx.save();
  for(let i=0;i<6;i++){const r=700+(i*211)%500,x=((i*1733+t*9)%(WORLD_W+2*r))-r,y=((i*2477+t*3.5)%(WORLD_H+2*r))-r;if(!inView(x,y,r))continue;
    const gr=ctx.createRadialGradient(x,y,r*.1,x,y,r);gr.addColorStop(0,"rgba(24,32,40,.16)");gr.addColorStop(.6,"rgba(24,32,40,.1)");gr.addColorStop(1,"rgba(24,32,40,0)");ctx.fillStyle=gr;ctx.beginPath();ctx.ellipse(x,y,r,r*.62,.3,0,Math.PI*2);ctx.fill();}
  ctx.restore();}

// real places, by their names today, so the valley can be found on a map
function drawPlaceLabels(){const P=placeNow();if(!P||!P.labels||!P.labels.length||cam.z>1.05)return;const al=clamp((1.05-cam.z)/.35,0,1);if(al<=0)return;
  const kx=WORLD_W*111.32*Math.cos(P.lat*Math.PI/180)/PLACE_KM,ky=WORLD_H*110.57/(PLACE_KM*2/3),z=cam.z,fs=15/z,fn=12/z;
  const pts=P.labels.map(([nm,note,la,lo])=>({nm,note,x:WORLD_W/2+(lo-P.lon)*kx,y:WORLD_H/2-(la-P.lat)*ky})).filter(p=>p.x>0&&p.y>0&&p.x<WORLD_W&&p.y<WORLD_H).sort((a,b)=>a.x-b.x);
  ctx.save();ctx.globalAlpha=al;ctx.lineJoin="round";ctx.textBaseline="middle";const boxes=[];
  for(const p of pts){ctx.font=`600 ${fs}px Spectral, Georgia, serif`;let w=ctx.measureText(p.nm).width;if(p.note){ctx.font=`italic 400 ${fn}px Spectral, Georgia, serif`;w=Math.max(w,ctx.measureText(p.note).width);}
    const h=(p.note?34:18)/z;// below the dot, else to its right, else above
    const opts=[[p.x-w/2,p.y+10/z,"center"],[p.x+10/z,p.y-h/2+2/z,"left"],[p.x-w/2,p.y-10/z-h,"center"],[p.x-10/z-w,p.y-h/2+2/z,"right"]];
    let pick=opts[0];for(const o of opts){if(!boxes.some(q=>o[0]<q[0]+q[2]&&o[0]+w>q[0]&&o[1]<q[1]+q[3]&&o[1]+h>q[1])){pick=o;break;}}boxes.push([pick[0],pick[1],w,h]);
    ctx.fillStyle="rgba(20,18,14,.6)";ctx.beginPath();ctx.arc(p.x,p.y,6/z,0,Math.PI*2);ctx.fill();ctx.fillStyle="#FBF6E6";ctx.beginPath();ctx.arc(p.x,p.y,3.4/z,0,Math.PI*2);ctx.fill();
    const tx=pick[2]==="center"?p.x:pick[2]==="left"?pick[0]:pick[0]+w;ctx.textAlign=pick[2];let ty=pick[1]+9/z;
    ctx.font=`600 ${fs}px Spectral, Georgia, serif`;ctx.lineWidth=4/z;ctx.strokeStyle="rgba(24,22,18,.75)";ctx.strokeText(p.nm,tx,ty);ctx.fillStyle="#FFF9EA";ctx.fillText(p.nm,tx,ty);
    if(p.note){ty+=16/z;ctx.font=`italic 400 ${fn}px Spectral, Georgia, serif`;ctx.lineWidth=3.4/z;ctx.strokeText(p.note,tx,ty);ctx.fillStyle="#F1E7CB";ctx.fillText(p.note,tx,ty);}}
  ctx.restore();}
