const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const D=__dirname+'/';
(async()=>{
  const b=await chromium.launch();
  const ctx=await b.newContext({viewport:{width:1440,height:900}});
  const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push('pageerror '+e.message));
  await p.goto('file://'+D+'letterheads.html');await p.waitForTimeout(2500);
  await p.evaluate(()=>document.getElementById('introQuiet')?.click());await p.evaluate(()=>__lango.atlas.dive());await p.waitForTimeout(2200);
  const vt=await p.evaluate(()=>new Promise(r=>{const t=[];let l=performance.now();function f(n){t.push(n-l);l=n;if(t.length<90)requestAnimationFrame(f);else r(t)}requestAnimationFrame(f)}));vt.sort((a,b)=>a-b);console.log('valley frame median',vt[45].toFixed(1));
  await p.evaluate(()=>__lango.atlas.open());await p.waitForTimeout(3000);await p.screenshot({path:D+'shots/b_open.png'});
  // world view
  for(const y of [150000,21000,11000,0]){await p.evaluate(y=>{const A=__lango.atlas.state;A.cam.tz=0.01;A.cam.tx=(20+180)*15;A.cam.ty=(90-25)*15;__lango.atlas.setYear(y);},y);await p.waitForTimeout(2500);await p.screenshot({path:D+`shots/w_${y}.png`});}
  const at=await p.evaluate(()=>new Promise(r=>{const t=[];let l=performance.now();function f(n){t.push(n-l);l=n;if(t.length<90)requestAnimationFrame(f);else r(t)}requestAnimationFrame(f)}));at.sort((a,b)=>a-b);console.log('atlas frame median',at[45].toFixed(1));
  // tap a cluster (Sahul) at a zoomed view
  await p.evaluate(()=>{__lango.atlas.setYear(20000);const A=__lango.atlas.state;A.cam.tz=1.2;A.cam.tx=(132.9+180)*15;A.cam.ty=(90+12.5)*15;});await p.waitForTimeout(2500);
  const pos=await p.evaluate(()=>{const A=__lango.atlas.state;const x=(132.9+180)*15,y=(90+12.5)*15;return[((x-A.cam.x)*A.cam.z)+innerWidth/2,(y-A.cam.y)*A.cam.z+innerHeight/2]});
  await p.mouse.click(pos[0],pos[1]);await p.waitForTimeout(2200);await p.screenshot({path:D+'shots/b_sahul.png'});
  console.log('sel',await p.evaluate(()=>document.getElementById('atlasTitle').textContent+' | '+document.getElementById('atlasSub').textContent));
  // journey: capture each stop
  await p.evaluate(()=>{__lango.atlas.setYear(null);__lango.atlas.state.sel=null;__lango.atlas.journey();});
  for(let i=0;i<13;i++){await p.waitForTimeout(i==0?4200:8100);await p.screenshot({path:D+`shots/j_${String(i).padStart(2,'0')}.png`});console.log('J',i,await p.evaluate(()=>{const J=__lango.atlas.state.jr;return J?J.i+' '+Math.round(J.year):'done'}));}
  await p.waitForTimeout(6000);
  // dive
  await p.evaluate(()=>__lango.atlas.dive());await p.waitForTimeout(700);await p.screenshot({path:D+'shots/b_dive1.png'});await p.waitForTimeout(2500);await p.screenshot({path:D+'shots/b_dive2.png'});
  console.log('after dive atlas on?',await p.evaluate(()=>__lango.atlas.state.on),'cam.z',await p.evaluate(()=>__lango.cam.z.toFixed(2)));
  // wheel out opens atlas
  for(let i=0;i<30;i++){await p.mouse.wheel(0,200);await p.waitForTimeout(40);}await p.waitForTimeout(1500);
  console.log('wheel opened atlas?',await p.evaluate(()=>__lango.atlas.state.on));
  console.log('ERRORS',errs.join('\n'));
  // phone
  const ph=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2,isMobile:true,hasTouch:true});const q=await ph.newPage();q.on('pageerror',e=>console.log('PHONE pageerror',e.message));
  await q.goto('file://'+D+'letterheads.html');await q.waitForTimeout(2500);await q.evaluate(()=>document.getElementById('introQuiet')?.click());await q.evaluate(()=>__lango.atlas.open());await q.waitForTimeout(3000);await q.screenshot({path:D+'shots/p_open.png'});
  await q.evaluate(()=>__lango.atlas.setYear(21000));await q.waitForTimeout(1500);await q.screenshot({path:D+'shots/p_21000.png'});
  const ov=await q.evaluate(()=>({sw:document.documentElement.scrollWidth,card:document.querySelector('.acard').getBoundingClientRect().toJSON(),zoom:document.querySelector('.azoom').getBoundingClientRect().toJSON()}));console.log('phone',JSON.stringify(ov));
  await b.close();
})();
