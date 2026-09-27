const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const D=__dirname+'/';
(async()=>{
  const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1440,height:900}})).newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error'&&!/fonts|ERR_CERT/.test(m.text()))errs.push('console '+m.text())});
  await p.goto('file://'+D+'letterheads.html');await p.waitForTimeout(2000);
  await p.screenshot({path:D+'shots/r_intro.png'});
  await p.evaluate(()=>document.getElementById('introQuiet')?.click());
  await p.waitForTimeout(3500);await p.screenshot({path:D+'shots/r_fly.png'});
  await p.waitForTimeout(6000);await p.screenshot({path:D+'shots/r_landed.png'});
  console.log('atlas on after intro?',await p.evaluate(()=>__lango.atlas.state.on),await p.evaluate(()=>__lango.placeKey));
  const ys=[300000,80000,62000,50000,46000,36000,26000,16000,9000,8300,3600,2800];
  for(const y of ys){
    const r=await p.evaluate(y=>{__lango.S.settings.historyPreview=y;const t0=performance.now();__lango.relocate();const L=__lango;const inW=L.S.agents.filter(a=>L.MAP.water[Math.floor(a.y/40)*180+Math.floor(a.x/40)]).length;
      L.cam.mode="free";L.cam.x=L.cam.tx=3600;L.cam.y=L.cam.ty=2400;L.cam.z=L.cam.tz=Math.min(innerWidth/7200,innerHeight/4800);
      return {key:L.placeKey,ms:Math.round(performance.now()-t0),inWater:inW,home:[Math.round(L.HOME.x),Math.round(L.HOME.y)],rivers:L.MAP.segs.length,cross:L.CROSS.length}},y);
    await p.waitForTimeout(1200);await p.screenshot({path:D+`shots/r_${y}.png`});
    console.log(y,JSON.stringify(r),await p.evaluate(()=>document.getElementById('eraLine').textContent));
  }
  console.log('ERR',errs.join('\n'));await b.close();})();
