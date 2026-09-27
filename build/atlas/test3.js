const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const D=__dirname+'/';
(async()=>{
  const b=await chromium.launch();
  const ph=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});const q=await ph.newPage();const errs=[];q.on('pageerror',e=>errs.push(e.message));
  await q.goto('file://'+D+'letterheads.html');await q.waitForTimeout(2500);await q.evaluate(()=>document.getElementById('introQuiet')?.click());await q.evaluate(()=>__lango.atlas.dive());await q.waitForTimeout(2200);
  await q.tap('#atlasBtn');await q.waitForTimeout(3000);await q.screenshot({path:D+'shots/p_open.png'});
  await q.evaluate(()=>__lango.atlas.setYear(21000));await q.waitForTimeout(1500);await q.screenshot({path:D+'shots/p_21000.png'});
  const ov=await q.evaluate(()=>({sw:document.documentElement.scrollWidth,card:document.querySelector('.acard').getBoundingClientRect().top,zoomBottom:document.querySelector('.azoom').getBoundingClientRect().bottom}));console.log('phone',JSON.stringify(ov));
  // tap the valley marker
  await q.evaluate(()=>{__lango.atlas.setYear(null)});await q.waitForTimeout(1200);const vs=await q.evaluate(()=>__lango.atlas.state.vs);console.log('vs',JSON.stringify(vs));await q.touchscreen.tap(vs.x,vs.y);await q.waitForTimeout(1500);await q.screenshot({path:D+'shots/p_valley.png'});
  console.log('card',await q.evaluate(()=>document.getElementById('atlasTitle').textContent+' | '+document.getElementById('atlasSub').textContent));
  await q.tap('#atlasInfo');await q.waitForTimeout(800);await q.screenshot({path:D+'shots/p_ourworld.png'});
  console.log('sheet has about',await q.evaluate(()=>document.getElementById('sheetBody').innerText.includes('About the Atlas')));
  await q.evaluate(()=>document.getElementById('sheetClose').click());
  await q.tap('#atlasBtn');await q.waitForTimeout(2500);console.log('back in valley',await q.evaluate(()=>!__lango.atlas.state.on));await q.screenshot({path:D+'shots/p_back.png'});
  console.log('ERR',errs.join('|'));await b.close();})();
