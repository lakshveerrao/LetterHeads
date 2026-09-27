s=open('../atlas/letterheads.html').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a[:50];s=s.replace(a,b)
rep('const SPEED=Math.max','let SPEED=Math.max')
rep('window.__lango={','window.__lango={F:{step:d=>step(d),ax,ay,spanZ,get ATL(){return ATL},openAtlas,closeAtlas,diveIn,setSpeed:v=>{SPEED=v},atlasY:()=>atlasY(),seaLevel,get W(){return W},get H(){return H},addStory:o=>addStory(o),chron:(t,k)=>chron(t,k),get tAnim(){return tAnim}},')
rep('function valleyHour(){const d=new Date();','function valleyHour(){if(window.__hour!=null)return window.__hour;const d=new Date();')
s=s.replace('if(gBuilt>=2)return null;gBuilt++;','gBuilt++;',1)
open('film.html','w').write(s)
s=open('film.html').read()
s=s.replace('if(momentFx&&tAnim<momentFx.until){const k=','if(false&&momentFx&&tAnim<momentFx.until){const k=',1)
s=s.replace('const fxOn=momentFx&&tAnim<momentFx.until&&!S.settings.reduce;','const fxOn=false;',1)
open('film.html','w').write(s)
