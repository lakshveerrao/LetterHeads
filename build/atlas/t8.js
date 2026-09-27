const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const D=__dirname+'/../';
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1200,height:800}});const p=await ctx.newPage();
  await p.goto('file://'+D+'artifact-files/686b03e0-5433-4194-aa42-f47e42824255/index.html');await p.waitForTimeout(2000);await p.evaluate(()=>document.getElementById('introQuiet')?.click());
  await p.waitForTimeout(17000);const before=await p.evaluate(()=>{const d=JSON.parse(localStorage.getItem('langoworld_proto_v3'));return{created:d.S.created,n:d.S.agents.length,words:d.S.words.length,place:d.S.place||null,x:Math.round(d.S.agents[0].x)}});
  await p.close();const q=await ctx.newPage();const errs=[];q.on('pageerror',e=>errs.push(e.message));
  await q.goto('file://'+D+'atlas/letterheads.html');await q.waitForTimeout(3000);
  const after=await q.evaluate(()=>{const L=__lango;const inW=L.S.agents.filter(a=>L.MAP.water[Math.floor(a.y/40)*180+Math.floor(a.x/40)]).length;const words=L.S.words.map(w=>[Math.round(w.x),Math.round(w.y)]);return{created:L.S.created,n:L.S.agents.length,words:L.S.words.length,place:L.S.place,inWater:inW,x:Math.round(L.S.agents[0].x),atlas:L.atlas.state.on}});
  console.log('before',JSON.stringify(before));console.log('after',JSON.stringify(after));console.log('ERR',errs.join('|'));await b.close();})();
