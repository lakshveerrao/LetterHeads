const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const D=__dirname+'/';
(async()=>{
  const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});
  const ctx=await b.newContext({viewport:{width:1440,height:900}});
  const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push('pageerror '+e.message));p.on('console',m=>{if(m.type()==='error')errs.push('console '+m.text())});
  await p.goto('file://'+D+'original.html');await p.waitForTimeout(3000);
  await p.evaluate(()=>{document.getElementById('introQuiet')?.click();});await p.waitForTimeout(1000);
  const before=await p.evaluate(()=>{const S=__lango.S;localStorage.setItem('x','1');return{created:S.created,n:S.agents.length,names:S.agents.slice(0,5).map(a=>a.name).join(',')}});
  await p.evaluate(()=>window.dispatchEvent(new Event('visibilitychange')));await p.evaluate(()=>{/* force save */});await p.waitForTimeout(16000);
  await p.goto('file://'+D+'letterheads.html');await p.waitForTimeout(3000);
  const after=await p.evaluate(()=>{const S=__lango.S;return{created:S.created,n:S.agents.length,names:S.agents.slice(0,5).map(a=>a.name).join(',')}});
  console.log('SAVE before',JSON.stringify(before),'after',JSON.stringify(after));
  await p.screenshot({path:D+'shots/valley.png'});
  await p.evaluate(()=>__lango.atlas.open());await p.waitForTimeout(2500);
  await p.screenshot({path:D+'shots/atlas_live.png'});
  const ft=await p.evaluate(()=>new Promise(r=>{const t=[];let l=performance.now();function f(n){t.push(n-l);l=n;if(t.length<90)requestAnimationFrame(f);else r(t)}requestAnimationFrame(f)}));
  ft.sort((a,b)=>a-b);console.log('frame ms median',ft[45].toFixed(1),'p95',ft[85].toFixed(1));
  for(const y of [300000,150000,65000,45000,21000,14000,8000,3800,0]){await p.evaluate(y=>__lango.atlas.setYear(y),y);await p.waitForTimeout(700);await p.screenshot({path:D+`shots/atlas_${y}.png`});
    const st=await p.evaluate(y=>({sl:__lango.atlas.seaLevel(y).toFixed(0),ice:__lango.atlas.iceFrac(y).toFixed(2),v:__lango.atlas.valleyAt(y).name,title:document.getElementById('atlasTitle').textContent,sub:document.getElementById('atlasSub').textContent}),y);console.log(y,JSON.stringify(st));}
  console.log('ERRORS',errs.length,errs.slice(0,10).join('\n'));
  await b.close();
})();
