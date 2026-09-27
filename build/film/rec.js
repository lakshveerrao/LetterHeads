const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const fs=require('fs');const D=__dirname+'/';
const mode=process.argv[2]||'test';const FPS=30,DUR=86.5;
(async()=>{const b=await chromium.launch();const ctx=await b.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1});const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await ctx.addInitScript(()=>{let t=0;const q=[];const d0=Date.now();performance.now=()=>t;Date.now=()=>d0+t;
  window.requestAnimationFrame=cb=>{q.push(cb);return q.length;};window.cancelAnimationFrame=()=>{};
  window.__adv=ms=>{t+=ms;const a=q.splice(0);for(const cb of a){try{cb(t)}catch(e){console.error(e)}}};});
 await p.goto('file://'+D+'film.html');
 for(let i=0;i<200;i++){await p.evaluate(()=>window.__adv(33));await p.waitForTimeout(20);if(await p.evaluate(()=>!!(window.__lango&&__lango.place)))break;}
 await p.evaluate(()=>{const L=__lango;L.atlas.dive();});await p.waitForTimeout(2500);await p.evaluate(()=>{const L=__lango;for(let i=0;i<30;i++)__adv(33);L.S.settings.night=true;L.S.settings.sound=false;for(let i=0;i<20000;i++)L.F.step(.1);document.fonts&&0;});
 await p.addScriptTag({path:D+'director.js'});
 for(let i=0;i<40;i++)await p.evaluate(()=>__adv(33));
 fs.mkdirSync(D+'frames',{recursive:true});
 const times=mode==='test'?[15,34,36]:null;
 const N=Math.round(DUR*FPS);const t0=Date.now();
 if(times){for(const t of times){const r=await p.evaluate(t=>__film.frame(t),t);await p.screenshot({path:D+`frames/test_${String(t).replace('.','_')}.jpg`,type:'jpeg',quality:80});console.log(t,JSON.stringify(r));}}
 else for(let f=0;f<N;f++){await p.evaluate(t=>__film.frame(t),f/FPS);await p.screenshot({path:D+`frames/f${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});if(f%150===0)console.log('frame',f,'of',N,((Date.now()-t0)/1000|0)+'s');}
 console.log('ERR',errs.slice(0,5).join('\n'));await b.close();})();
