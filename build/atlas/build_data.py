# Builds the Atlas data layers from NASA Blue Marble NG and NOAA ETOPO (10 arc-minute).
import numpy as np, io, base64, json
from PIL import Image, ImageDraw
from scipy import ndimage
Image.MAX_IMAGE_PIXELS=None
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'nasa')+'/'  # Blue Marble and ETOPO inputs, see README
import os
O=os.path.dirname(os.path.abspath(__file__))+'/'
# ---- base imagery
im=Image.open(D+'mpl_toolkits/basemap_data/bmng.jpg').convert('RGB')
for q in (72,78):
    b=io.BytesIO();im.save(b,'JPEG',quality=q,optimize=True,progressive=True);print('bmng q',q,len(b.getvalue()))
b=io.BytesIO();im.save(b,'JPEG',quality=80,optimize=True,progressive=True);open(O+'earth.jpg','wb').write(b.getvalue())
# ---- elevation: upsample to 2048x1024 (pixel centres)
MW,MH=2048,1024
g=np.load(D+'etopo_m180.npy')  # 1081 rows (lat 90..-90) x 2160 cols (lon -180..180)
lat=90-(np.arange(MH)+.5)*180/MH; lon=-180+(np.arange(MW)+.5)*360/MW
ry=(90-lat)*6; rx=(lon+180)*6
YY,XX=np.meshgrid(ry,rx,indexing='ij')
gw=np.concatenate([g,g[:,:1]],axis=1)
elev=ndimage.map_coordinates(gw,[YY,XX],order=1,mode='nearest')
# ocean connected to the open sea at today's level (wraps east-west)
wet=elev<0
lab,n=ndimage.label(np.concatenate([wet,wet],axis=1))
lab=lab[:,:MW]; big=np.bincount(lab.ravel()); big[0]=0; ocean_id=big.argmax()
# merge labels that touch across the seam
seamL=lab[:,0];seamR=np.concatenate([wet,wet],axis=1)
ocean=(lab==ocean_id)
# also keep any label connected via the seam wrap to the ocean
full,_=ndimage.label(np.concatenate([wet,wet,wet],axis=1))
mid=full[:,MW:2*MW]; ids=np.unique(mid[ocean]); ocean=np.isin(mid,ids[ids>0])
expos=ocean&(elev>-150)
R=np.zeros((MH,MW),np.uint8)
R[expos]=np.clip(np.round(-elev[expos]/0.6),1,250).astype(np.uint8)
print('exposable px',expos.sum())
# ---- ice sheets at the Last Glacial Maximum (hand-traced, approximate)
POLY=json.load(open(O+'ice_lgm.json'))
G=np.zeros((MH,MW),np.float32)
X=lambda lo:(lo+180)/360*MW; Y=lambda la:(90-la)/180*MH
rng=np.random.default_rng(7)
noise=ndimage.gaussian_filter(rng.standard_normal((MH,MW)),6); noise/=np.abs(noise).max()
for name,p in POLY.items():
    pts=[(X(a),Y(b)) for a,b in p['pts']]; cx,cy=X(p['c'][0]),Y(p['c'][1])
    for _ in range(3):  # Chaikin smoothing: no straight polygon edges
        q=[]
        for k in range(len(pts)):
            a=pts[k];b=pts[(k+1)%len(pts)]
            q+= [(a[0]*.75+b[0]*.25,a[1]*.75+b[1]*.25),(a[0]*.25+b[0]*.75,a[1]*.25+b[1]*.75)]
        pts=q
    big=[(cx+(x-cx)*1.1,cy+(y-cy)*1.1) for x,y in pts]
    m=Image.new('L',(MW,MH),0);ImageDraw.Draw(m).polygon(big,fill=1);m=np.asarray(m).astype(bool)
    # distance from centre to the farthest polygon edge along each direction
    ang=np.linspace(-np.pi,np.pi,1441);Rmax=np.zeros_like(ang)
    P=np.array(pts+[pts[0]])
    for i,th in enumerate(ang):
        d=np.array([np.cos(th),np.sin(th)]);best=0
        for k in range(len(P)-1):
            a=P[k]-[cx,cy];e=P[k+1]-P[k]
            den=d[0]*(-e[1])-d[1]*(-e[0])
            if abs(den)<1e-9: continue
            t=(a[0]*(-e[1])-a[1]*(-e[0]))/den; s=(d[0]*a[1]-d[1]*a[0])/den
            if t>0 and 0<=s<=1: best=max(best,t)
        Rmax[i]=best
    yy,xx=np.nonzero(m); th=np.arctan2(yy-cy,xx-cx); rr=np.hypot(xx-cx,yy-cy)
    Rm=np.interp(th,ang,Rmax); rank=rr/np.maximum(Rm,1)*(1+.09*noise[yy,xx]);ok=rank<.999;yy,xx,rank=yy[ok],xx[ok],rank[ok]
    cur=G[yy,xx]; G[yy,xx]=np.where(cur>0,np.minimum(cur,rank+1e-3),rank+1e-3)
Gc=np.zeros((MH,MW),np.uint8); Gc[G>0]=np.clip(1+G[G>0]*254,1,255).astype(np.uint8)
img=np.stack([R,Gc,np.zeros_like(R)],axis=2)
Image.fromarray(img,'RGB').save(O+'layers.png',optimize=True)
import os;print('layers.png',os.path.getsize(O+'layers.png'),'earth.jpg',os.path.getsize(O+'earth.jpg'))
