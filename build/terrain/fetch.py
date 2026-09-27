import math,os,io,sys,urllib.request,numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
os.makedirs('tiles',exist_ok=True)
def tile(z,x,y):
    x%=2**z;p=f'tiles/{z}_{x}_{y}.png'
    if not os.path.exists(p):
        for i in range(4):
            try:
                d=urllib.request.urlopen(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',timeout=30).read();open(p,'wb').write(d);break
            except Exception as e: print('retry',z,x,y,e)
    a=np.asarray(Image.open(p).convert('RGB')).astype(np.float64)
    return a[:,:,0]*256+a[:,:,1]+a[:,:,2]/256-32768
def lon2x(lon,z): return (lon+180)/360*2**z*256
def lat2y(lat,z): r=math.radians(lat);return (1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*2**z*256
def sample(z,lons,lats):
    """bilinear sample elevation at arrays of lon/lat"""
    px=lon2x(lons,z);py=np.vectorize(lat2y)(lats,z)
    tx0,tx1=int(px.min()//256),int(px.max()//256);ty0,ty1=int(py.min()//256),int(py.max()//256)
    jobs=[(z,x,y) for y in range(ty0,ty1+1) for x in range(tx0,tx1+1)]
    with ThreadPoolExecutor(8) as ex: ts=list(ex.map(lambda j:tile(*j),jobs))
    W=(tx1-tx0+1)*256;H=(ty1-ty0+1)*256;M=np.zeros((H,W))
    for (zz,x,y),t in zip(jobs,ts): M[(y-ty0)*256:(y-ty0+1)*256,(x-tx0)*256:(x-tx0+1)*256]=t
    from scipy.ndimage import map_coordinates
    return map_coordinates(M,[py-ty0*256-.5,px-tx0*256-.5],order=1,mode='nearest')
