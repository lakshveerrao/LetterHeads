import os,sys,json,math,re,urllib.request,numpy as np,rasterio,mgrs
from rasterio.windows import from_bounds
from pyproj import Transformer
from scipy.ndimage import map_coordinates
from PIL import Image
os.environ['CURL_CA_BUNDLE']='/root/.ccr/ca-bundle.crt';os.environ['GDAL_DISABLE_READDIR_ON_OPEN']='EMPTY_DIR'
os.environ['GDAL_HTTP_MULTIRANGE']='YES';os.environ['VSI_CACHE']='TRUE'
D=os.path.dirname(os.path.abspath(__file__))
B='https://sentinel-cogs.s3.us-west-2.amazonaws.com/'
W,H,KM=720,480,36.0
P={p['id']:p for p in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../terrain/places.json')))}
# modern analogue of the glacial mammoth steppe with larch taiga islands: the Kurai steppe, Altai
P['altai']={'id':'altai','lon':87.95,'lat':50.23}
MONTHS={'altai':[7,8],'omo':[1,2,12],'nile':[3,4,5,10,11],'galilee':[4,5,6],'hatay':[5,6,7],'irongates':[6,7,8],'moravia':[6,7,8],
 'vezere':[6,7,8],'vienna':[6,7,8],'argolid':[5,6,7],'tiber':[6,7,8]}
def get(u):
    with urllib.request.urlopen(u,timeout=60) as r:return r.read()
def grid(p):
    lon,lat=p['lon'],p['lat']
    lons=lon+(np.arange(W)+.5-W/2)/W*KM/(111.32*math.cos(math.radians(lat)))
    lats=lat-(np.arange(H)+.5-H/2)/H*(KM*2/3)/110.57
    return np.meshgrid(lons,lats)
def scenes(tile,yr,mo):
    z,b,sq=tile[:2],tile[2],tile[3:5]
    x=get(B+f'?list-type=2&prefix=sentinel-s2-l2a-cogs/{int(z)}/{b}/{sq}/{yr}/{mo}/&delimiter=/').decode()
    return re.findall(r'<Prefix>(sentinel-s2-l2a-cogs/[^<]+_L2A/)</Prefix>',x)
def run(pid):
    p=P[pid];LO,LA=grid(p);m=mgrs.MGRS()
    tiles=sorted({m.toMGRS(float(LA[j,i]),float(LO[j,i]),MGRSPrecision=0) for j in (0,H//2,H-1) for i in (0,W//2,W-1)})
    cand=[]
    for t in tiles:
        for yr in (2023,2022,2021):
            for mo in MONTHS[pid]:
                for pre in scenes(t,yr,mo):
                    name=pre.rstrip('/').split('/')[-1]
                    try:it=json.loads(get(B+pre+name+'.json'))
                    except Exception as e:continue
                    pr=it['properties'];cand.append((pr.get('eo:cloud_cover',100),pr.get('s2:nodata_pixel_percentage',0),pre,t))
    cand.sort();print(pid,tiles,len(cand),'best',cand[:3],flush=True)
    rgb=np.zeros((H,W,3),np.float32);done=np.zeros((H,W),bool);used=[]
    for cc,nd,pre,t in cand:
        if cc>40:break
        with rasterio.open('/vsicurl/'+B+pre+'TCI.tif') as r:
            tr=Transformer.from_crs('EPSG:4326',r.crs,always_xy=True);X,Y=tr.transform(LO,LA)
            need=~done
            win=from_bounds(X[need].min()-100,Y[need].min()-100,X[need].max()+100,Y[need].max()+100,r.transform).round_offsets().round_lengths()
            try:win=win.intersection(rasterio.windows.Window(0,0,r.width,r.height))
            except Exception:continue
            f=4;a=r.read(window=win,out_shape=(3,max(1,int(win.height)//f),max(1,int(win.width)//f))).astype(np.float32)
            wt=r.window_transform(win)
            col=(X-wt.c)/wt.a/f-.5;row=(Y-wt.f)/wt.e/f-.5
        with rasterio.open('/vsicurl/'+B+pre+'SCL.tif') as s:
            win2=from_bounds(*rasterio.windows.bounds(win,r.transform),s.transform).round_offsets().round_lengths()
            sc=s.read(1,window=win2,out_shape=(max(1,int(win2.height)//2),max(1,int(win2.width)//2)))
            wt2=s.window_transform(win2)
            scl=map_coordinates(sc,[(Y-wt2.f)/wt2.e/2-.5,(X-wt2.c)/wt2.a/2-.5],order=0,cval=0)
        v=np.stack([map_coordinates(a[c],[row,col],order=1,cval=0) for c in range(3)],-1)
        ok=(~done)&(v.min(-1)>0)&~np.isin(scl,[0,1,3,8,9,10])
        if ok.sum()<50:continue
        rgb[ok]=v[ok];done|=ok;used.append(pre.split('/')[-2]);print(pid,'+',used[-1],cc,round(done.mean(),4),flush=True)
        if done.mean()>.998:break
    Image.fromarray(rgb.clip(0,255).astype(np.uint8)).save(f'{D}/{pid}_s2.png')
    np.save(f'{D}/{pid}_s2mask.npy',done)
    json.dump({'scenes':used,'filled':float(done.mean())},open(f'{D}/{pid}_s2.json','w'))
if __name__=='__main__':run(sys.argv[1])
