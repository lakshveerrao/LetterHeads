const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const D=__dirname+'/';
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1440,height:900}})).newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file://'+D+'letterheads.html');await p.waitForTimeout(2000);await p.evaluate(()=>{document.getElementById('introQuiet')?.click();__lango.atlas.dive();});await p.waitForTimeout(2500);
  for(const y of [300000,80000,62000,50000,46000,36000,26000,16000,9000,8300,3600,2800]){await p.evaluate(y=>{const L=__lango;L.S.settings.historyPreview=y;L.relocate();L.cam.mode="free";L.cam.x=L.cam.tx=L.HOME.x;L.cam.y=L.cam.ty=L.HOME.y;L.cam.z=L.cam.tz=.5;document.querySelectorAll('.caption,#hint').forEach(e=>e.style.visibility='hidden');},y);
    await p.waitForTimeout(1300);await p.screenshot({path:D+`shots/g_${y}.png`});}
  console.log('ERR',errs.join('\n'));await b.close();})();
