import os,sys,json,math,numpy as np,rasterio
from rasterio.windows import from_bounds
os.environ['CURL_CA_BUNDLE']='/root/.ccr/ca-bundle.crt';os.environ['GDAL_DISABLE_READDIR_ON_OPEN']='EMPTY_DIR'
from fetch_s2 import grid,P,W,H,D
def tname(la,lo):
    a=int(math.floor(la/3)*3);o=int(math.floor(lo/3)*3)
    return f"{'N' if a>=0 else 'S'}{abs(a):02d}{'E' if o>=0 else 'W'}{abs(o):03d}"
def run(pid):
    LO,LA=grid(P[pid]);cls=np.zeros((H,W),np.uint8)
    names=np.vectorize(tname)(LA,LO)
    for n in np.unique(names):
        sel=names==n
        u=f'/vsicurl/https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_{n}_Map.tif'
        with rasterio.open(u) as r:
            win=from_bounds(LO[sel].min()-.002,LA[sel].min()-.002,LO[sel].max()+.002,LA[sel].max()+.002,r.transform).round_offsets().round_lengths()
            f=2;a=r.read(1,window=win,out_shape=(int(win.height)//f,int(win.width)//f))
            wt=r.window_transform(win)
        # mode over each 50 m output pixel would be nicer; nearest at 20 m is fine
        c=((LO[sel]-wt.c)/wt.a/f).astype(int).clip(0,a.shape[1]-1);rr=((LA[sel]-wt.f)/wt.e/f).astype(int).clip(0,a.shape[0]-1)
        cls[sel]=a[rr,c]
    np.save(f'{D}/{pid}_wc.npy',cls)
    u,k=np.unique(cls,return_counts=True);print(pid,dict(zip(u.tolist(),(k/k.sum()).round(3).tolist())),flush=True)
if __name__=='__main__':
    for pid in sys.argv[1:]:run(pid)
