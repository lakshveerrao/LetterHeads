const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const D=__dirname+'/';
const only=process.argv[2]?process.argv[2].split(','):null;
(async()=>{const b=await chromium.launch();const p=await (await b.newContext({viewport:{width:1440,height:900}})).newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
  await p.goto('file://'+D+'letterheads.html');await p.waitForTimeout(2500);await p.evaluate(()=>{document.getElementById('introQuiet')?.click();__lango.atlas.dive();});await p.waitForTimeout(2500);
  const T=require(D+'../terrain/places.json').map(t=>[t.id,t.y]);
  for(const [id,y] of T){if(only&&!only.includes(id))continue;
    for(const z of [.32,.9]){await p.evaluate(([y,z])=>{const L=__lango;L.S.settings.historyPreview=y-10;L.relocate();L.cam.mode="free";L.cam.x=L.cam.tx=L.HOME.x;L.cam.y=L.cam.ty=L.HOME.y;L.cam.z=L.cam.tz=z;document.querySelectorAll('.caption,#hint').forEach(e=>e.style.visibility='hidden');},[y,z]);
    await p.waitForTimeout(2200);await p.screenshot({path:D+`shots/g_${id}_${z}.png`});}}
  console.log('ERR',errs.join('\n'));await b.close();})();
