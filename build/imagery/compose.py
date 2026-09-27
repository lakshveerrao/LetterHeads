# Builds each site's ground image: real Sentinel-2 pixels wherever today's cover (ESA WorldCover)
# matches what the pollen record says grew there in that era; elsewhere real texture patches of the
# right cover type, copied from natural ground in the same scene (or a similar site).
import json,numpy as np,os
from PIL import Image
from scipy.ndimage import gaussian_filter,zoom
D=os.path.dirname(os.path.abspath(__file__))
W,H=720,480
PL=json.load(open(D+'/../terrain/places.json'))
TER=np.asarray(Image.open(D+'/../terrain/terrain.png').convert('RGB')).astype(np.float64)
T,S,G,B=0,1,2,3
MOD={T:[10],S:[20],G:[30,90,100],B:[60]}
# era cover fractions (tree, shrub, grass/steppe, bare) and colour grade for grass: [desat, warm]
R={
 'omo':      dict(keep=True),
 'nile':     dict(f=(.25,.05,.70,0),keepB=True,grade=(0,0),fb={G:['galilee','omo'],T:['omo','hatay']}),
 'galilee':  dict(f=(.12,.28,.60,0),grade=(.15,.1)),
 'hatay':    dict(f=(.35,.25,.40,0),grade=(.1,.05),fb={G:['galilee','argolid']}),
 'irongates':dict(analog='altai',f=(.35,0,.65,0),grade=(0,0)),
 'moravia':  dict(analog='altai',f=(.30,0,.70,0),grade=(0,0)),
 'vezere':   dict(analog='altai',f=(.15,0,.85,0),grade=(0,0)),
 'dogger':   dict(analog='altai',f=(.10,0,.90,0),grade=(0,0),fb={T:['vezere'],G:['vezere','moravia']}),
 'vienna':   dict(f=(.72,0,.28,0),grade=(0,0),fb={G:['irongates','moravia','vezere']}),
 'argolid':  dict(f=(.40,.30,.30,0),grade=(.1,.25)),
 'tiber':    dict(f=(.50,.10,.40,0),grade=(0,.05),fb={S:['argolid'],G:['argolid','galilee']}),
}
def elev(n):
    t=TER[n*120:(n+1)*120];return zoom((t[:,:,0]*256+t[:,:,1])/4-12000,4,order=1)
def load(pid):
    if not os.path.exists(f'{D}/{pid}_s2.png'):return None,None
    return np.asarray(Image.open(f'{D}/{pid}_s2.png').convert('RGB')).astype(np.float32),np.load(f'{D}/{pid}_wc.npy')
PATCH,STEP=40,28
def candidates(img,wc,c,rng):
    from scipy.ndimage import uniform_filter
    ok=uniform_filter(np.isin(wc,MOD[c]).astype(np.float32),PATCH)[PATCH//2:H-PATCH//2,PATCH//2:W-PATCH//2]
    for th in (.9,.8,.7,.6):
        ys,xs=np.nonzero(ok>th)
        if len(ys)>=400:break
    if len(ys)==0:return []
    sel=rng.choice(len(ys),min(1500,len(ys)),replace=False)
    # prefer calm, even patches: no gullies, ponds or cliff shadows cut into the texture
    sd=np.array([img[ys[i]:ys[i]+PATCH,xs[i]:xs[i]+PATCH].mean(-1).std() for i in sel])
    sel=sel[np.argsort(sd)[:max(20,len(sel)//4)]]
    don=img[np.isin(wc,MOD[c])];med=np.median(don,0) if len(don) else None
    return [(img,ys[i],xs[i],med) for i in sel]
def synth(cands,rng):
    acc=np.zeros((H+2*PATCH,W+2*PATCH,3),np.float32);wt=np.zeros((H+2*PATCH,W+2*PATCH,1),np.float32)
    ramp=np.minimum(np.arange(PATCH)+1,PATCH-np.arange(PATCH)).astype(np.float32);ramp=np.minimum(ramp/(PATCH-STEP),1)
    win=(ramp[:,None]*ramp[None,:])[:,:,None]
    for y in range(-PATCH//2,H,STEP):
        for x in range(-PATCH//2,W,STEP):
            img,py,px,med=cands[rng.integers(len(cands))];p=img[py:py+PATCH,px:px+PATCH];p=p-(p.reshape(-1,3).mean(0)-med)*.75
            if rng.random()<.5:p=p[:,::-1]
            yy,xx=y+PATCH//2,x+PATCH//2;acc[yy:yy+PATCH,xx:xx+PATCH]+=p*win;wt[yy:yy+PATCH,xx:xx+PATCH]+=win
    return (acc/np.maximum(wt,1e-3))[PATCH//2:PATCH//2+H,PATCH//2:PATCH//2+W]
def grade(a,g):
    ds,wm=g;l=a.mean(-1,keepdims=True);a=a+(l-a)*ds;a[:,:,0]*=1+wm*.25;a[:,:,2]*=1-wm*.2;return a
def smooth_noise(rng,s):
    n=gaussian_filter(rng.random((H,W)),s);return (n-n.mean())/(n.std()+1e-6)
data={p['id']:load(p['id']) for p in PL};data['altai']=load('altai')
info={}
for n,p in enumerate(PL):
    pid=p['id'];r=R[pid];img,wc=data[pid];rng=np.random.default_rng(1000+n)
    if img is None:img=np.zeros((H,W,3),np.float32);wc=np.full((H,W),80,np.uint8)
    if r.get('keep'):
        era=np.full((H,W),G,np.int8)
        for c,m in MOD.items():era[np.isin(wc,m)]=c
    else:
        E=elev(n);rel=np.clip(-(E-gaussian_filter(E,25))/30,-1,1);gy,gx=np.gradient(E,50);slope=np.hypot(gx,gy)
        north=np.clip(gy*8,-1,1)  # ground rising to the south faces north: cool, moist, where trees hold on
        sT=1.2*(wc==10)*(not r.get('analog'))+.9*rel+(1.4*north if r.get('analog') else .3*north)+.6*smooth_noise(rng,10)+.3*smooth_noise(rng,3)
        sB=6*slope+1.5*(wc==60)+.3*smooth_noise(rng,6)
        sS=.8*(wc==20)+smooth_noise(rng,8)+.4*slope
        era=np.full((H,W),G,np.int8);free=np.ones((H,W),bool)
        if r.get('keepB'):era[wc==60]=B;free[wc==60]=False
        N=int(free.sum())
        for c,sc,f in ((T,sT,r['f'][0]),(B,sB,r['f'][3]),(S,sS,r['f'][1])):
            k=int(f*N)
            if k<=0:continue
            v=np.where(free,sc,-1e9).ravel();idx=np.argpartition(-v,k)[:k];era.ravel()[idx]=c;free.ravel()[idx]=False
    out=img.copy();keep=np.zeros((H,W),bool)
    for c,m in MOD.items():
        if not r.get('analog'):keep|=(era==c)&np.isin(wc,m)
    stats={}
    for c in (T,S,G,B):
        need=(era==c)&~keep
        if need.sum()==0:continue
        cands=candidates(img,wc,c,rng) if not r.get('analog') else [];src=pid
        if r.get('analog'):cands=candidates(*data[r['analog']],c,rng);src=r['analog']
        for alt in r.get('fb',{}).get(c,[])+{S:['argolid','omo','hatay'],B:['omo','nile'],T:['vezere'],G:['vezere']}[c]:
            if len(cands)>=40:break
            ai,aw=data[alt]
            if ai is None:continue
            cands=candidates(ai,aw,c,rng);src=alt
        if len(cands)<5:print(pid,'no donors for',c);continue
        tex=synth(cands,rng)
        a=gaussian_filter(need.astype(np.float32),1.2)[:,:,None]
        out=out*(1-a)+tex*a;stats[int(c)]=src
    if not r.get('keep') and r['grade'][0]+r['grade'][1]>0:
        gm=gaussian_filter((era==G).astype(np.float32),1)[:,:,None];out=out*(1-gm)+grade(out.copy(),r['grade'])*gm
    info[pid]=dict(donors=stats,kept=float(keep.mean()),era=[float((era==c).mean()) for c in (T,S,G,B)])
    Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save(f'{D}/{pid}_ground.jpg',quality=82)
    print(pid,info[pid],flush=True)
json.dump(info,open(D+'/ground_info.json','w'),indent=1)
