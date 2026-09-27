const {chromium}=require(require('child_process').execSync('npm root -g').toString().trim()+'/playwright');
const D=__dirname+'/';
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});
for(const [w,h,n] of [[1440,900,'desk'],[390,844,'phone']]){
 const p=await b.newPage({viewport:{width:w,height:h}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('file://'+D+'letterheads.html');await p.waitForTimeout(4000);
 await p.screenshot({path:D+`shots/t13_${n}_atlas.png`,clip:{x:0,y:0,width:w,height:Math.min(h,160)}});
 await p.evaluate(()=>__lango.atlas&&__lango.atlas.dive&&__lango.atlas.dive());await p.waitForTimeout(3500);
 await p.evaluate(()=>{document.getElementById('introQuiet')?.click();});await p.waitForTimeout(800);
 await p.screenshot({path:D+`shots/t13_${n}_valley.png`,clip:{x:0,y:0,width:w,height:Math.min(h,160)}});
 const geo=await p.evaluate(()=>{const l=document.getElementById('trailerLink').getBoundingClientRect(),t=document.getElementById('tourBtn').getBoundingClientRect();return{linkBottom:Math.round(l.bottom),tourTop:Math.round(t.top)}});console.log(n,'geo',JSON.stringify(geo));await p.click('#trailerLink');await p.waitForTimeout(2000);
 const st=await p.evaluate(()=>({open:!document.getElementById('trailerDlg').hidden,src:document.getElementById('trailerVid').getAttribute('src'),note:document.getElementById('trailerNote').textContent,focus:document.activeElement.id}));
 await p.screenshot({path:D+`shots/t13_${n}_dlg.png`});
 await p.keyboard.press('Escape');await p.waitForTimeout(300);
 const closed=await p.evaluate(()=>document.getElementById('trailerDlg').hidden);
 // menu entry
 await p.click('#menuBtn');await p.waitForTimeout(400);await p.click('#mTrailer');await p.waitForTimeout(400);
 const viaMenu=await p.evaluate(()=>!document.getElementById('trailerDlg').hidden);await p.click('#trailerClose');
 console.log(n,JSON.stringify({st,closed,viaMenu,sw:await p.evaluate(()=>document.documentElement.scrollWidth)}),errs);}
await b.close();})();
