import json,math,heapq,numpy as np
from PIL import Image
from fetch import sample
GW,GH,KM=180,120,36.0
P=json.load(open('places.json'))
bm=np.asarray(Image.open('../nasa/mpl_toolkits/basemap_data/bmng.jpg').convert('RGB')).astype(np.float64)/255
from scipy.ndimage import map_coordinates,uniform_filter
def grid(lon,lat,nx,ny,km_w,km_h,sub=3):
    lons=lon+(np.arange(nx*sub)+.5-nx*sub/2)/(nx*sub)*km_w/(111.32*math.cos(math.radians(lat)))
    lats=lat-(np.arange(ny*sub)+.5-ny*sub/2)/(ny*sub)*km_h/110.57
    LO,LA=np.meshgrid(lons,lats);return LO,LA
def fillroute(h):
    H,W=h.shape;fl=h.copy();done=np.zeros_like(h,bool);pq=[]
    for j in range(H):
        for i in range(W):
            if i in(0,W-1) or j in(0,H-1):done[j,i]=1;heapq.heappush(pq,(fl[j,i],j,i))
    NB=[(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]
    while pq:
        v,j,i=heapq.heappop(pq)
        for di,dj in NB:
            ii,jj=i+di,j+dj
            if 0<=ii<W and 0<=jj<H and not done[jj,ii]:
                done[jj,ii]=1;fl[jj,ii]=max(h[jj,ii],v+1e-3);heapq.heappush(pq,(fl[jj,ii],jj,ii))
    order=np.argsort(-fl,axis=None);acc=np.ones(H*W);down=-np.ones(H*W,int);f=fl.ravel()
    for k in order:
        j,i=divmod(k,W);best=-1;bh=f[k]
        for di,dj in NB:
            ii,jj=i+di,j+dj
            if 0<=ii<W and 0<=jj<H:
                kk=jj*W+ii
                if f[kk]<bh:bh=f[kk];best=kk
        down[k]=best
        if best>=0:acc[best]+=acc[k]
    return acc.reshape(H,W),down
out=np.zeros((GH*len(P),GW,3),np.uint8);meta=[]
for n,p in enumerate(P):
    lon,lat=p['lon'],p['lat']
    LO,LA=grid(lon,lat,GW,GH,KM,KM*2/3)
    E=sample(11,LO.ravel(),LA.ravel()).reshape(GH*3,GW*3).reshape(GH,3,GW,3).mean(axis=(1,3))
    # moisture from Blue Marble greenness (bilinear, 5400x2700 equirectangular)
    LO1,LA1=grid(lon,lat,GW,GH,KM,KM*2/3,1)
    px=(LO1+180)/360*5400-.5;py=(90-LA1)/180*2700-.5
    ch=[map_coordinates(bm[:,:,c],[py,px],order=1) for c in range(3)]
    veg=(ch[1]-ch[0])/(ch[1]+ch[0]+1e-3)
    bright=(ch[0]+ch[1]+ch[2])/3
    moist=np.clip((veg+.12)/.3,0,1)*np.clip(1.3-bright*1.4,0,1)**.3
    # inflow: route over a 3x context at 600 m, find where water enters the window
    CW,CH=180,120 # context cells at 600 m = 108 x 72 km
    LO2,LA2=grid(lon,lat,CW,CH,KM*3,KM*2,1)
    E2=sample(9,LO2.ravel(),LA2.ravel()).reshape(CH,CW)
    if p.get('sea'):E2=np.where(E2<0,-50,E2)
    acc,down=fillroute(E2)
    inflow=[]
    # context cells covering the window: cols 60..119, rows 40..79 (each = 3x3 window cells)
    for k in range(CW*CH):
        j,i=divmod(k,CW);d=down[k]
        if d<0:continue
        jd,idd=divmod(d,CW)
        inside=lambda jj,ii:60<=ii<120 and 40<=jj<80
        if not inside(j,i) and inside(jd,idd) and acc.ravel()[k]>25:
            wi=(idd-60)*3+1;wj=(jd-40)*3+1
            inflow.append([int(wj*GW+wi),float(acc.ravel()[k])])
    # burn the rivers that enter into the window's heights so they flow through it as they really do
    paths=[]
    for k in range(CW*CH):
        j,i=divmod(k,CW);d=down[k]
        if d<0 or acc.ravel()[k]<300:continue
        jd,idd=divmod(d,CW)
        if not(60<=i<120 and 40<=j<80) and (60<=idd<120 and 40<=jd<80):
            pts=[];c=d
            while c>=0:
                cj,ci=divmod(c,CW)
                if not(60<=ci<120 and 40<=cj<80):pts.append(((ci-60)*3+1,(cj-40)*3+1));break
                pts.append(((ci-60)*3+1,(cj-40)*3+1));c=down[c]
            paths.append(pts)
    if p.get('course'):
        # a big river on a flat floor: follow the lowest ground from one edge to the other (least-cost path)
        from scipy.ndimage import minimum_filter
        import heapq as hq
        fl_=minimum_filter(E,size=15);cost=1+((E-fl_)/1.5)**2
        a_,b_=p['course'];edge=lambda s:{'S':[(GH-1,i) for i in range(GW)],'N':[(0,i) for i in range(GW)],'E':[(j,GW-1) for j in range(GH)],'W':[(j,0) for j in range(GH)]}[s]
        src=min(edge(a_),key=lambda c:E[c]);dst=set(edge(b_))
        dist={src:0};prev={};pq=[(0,src)];end=None
        while pq:
            dd,c=hq.heappop(pq)
            if c in dst:end=c;break
            if dd>dist.get(c,1e18):continue
            for dj,di in((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                nj,ni=c[0]+dj,c[1]+di
                if 0<=nj<GH and 0<=ni<GW:
                    nd=dd+cost[nj,ni]*(1.414 if dj and di else 1)
                    if nd<dist.get((nj,ni),1e18):dist[(nj,ni)]=nd;prev[(nj,ni)]=c;hq.heappush(pq,(nd,(nj,ni)))
        path=[end]
        while path[-1]!=src:path.append(prev[path[-1]])
        path=path[::-1];top=E[src]
        for i_,(y,x) in enumerate(path):E[y,x]=min(E[y,x],top-14-i_*.1)
        paths=[];inflow=[[int(path[3][0]*GW+path[3][1]),25000.0]]
    E0=E.copy()
    for pts in paths:
        cells=[]
        for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
            ns=max(abs(x1-x0),abs(y1-y0),1)
            for t in range(ns):
                x=round(x0+(x1-x0)*t/ns);y=round(y0+(y1-y0)*t/ns)
                if 0<=x<GW and 0<=y<GH:cells.append((y,x))
        if not cells:continue
        # follow the real valley floor between where the river enters and leaves (least-cost path)
        from scipy.ndimage import minimum_filter
        import heapq as hq
        fl_=minimum_filter(E0,size=11);cost=1+((E0-fl_)/1.5)**2
        src,dst=cells[0],cells[-1];dist={src:0};prev={};pq=[(0,src)]
        while pq:
            dd,c=hq.heappop(pq)
            if c==dst:break
            if dd>dist.get(c,1e18):continue
            for dj,di in((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                nj,ni=c[0]+dj,c[1]+di
                if 0<=nj<GH and 0<=ni<GW:
                    nd=dd+cost[nj,ni]*(1.414 if dj and di else 1)
                    if nd<dist.get((nj,ni),1e18):dist[(nj,ni)]=nd;prev[(nj,ni)]=c;hq.heappush(pq,(nd,(nj,ni)))
        if dst in prev or dst==src:
            pth=[dst]
            while pth[-1]!=src:pth.append(prev[pth[-1]])
            cells=pth[::-1]
        run=1e9
        for (y,x) in cells:
            y0,y1,x0,x1=max(0,y-1),min(GH,y+2),max(0,x-1),min(GW,x+2)
            run=min(run,E0[y0:y1,x0:x1].min())-0.1
            E[y,x]=min(E[y,x],run-12)
    inflow.sort(key=lambda q:-q[1])
    if not p.get('course'):
        if inflow:inflow[0][1]*=p.get('big',1)
        inflow=[[k,round(v*0.36,1)] for k,v in inflow[:6]]   # context cell = 9 window cells; scale to window flow units (~0.9/cell)
    print("  E",p["id"],np.isnan(E).sum(),E.min(),E.max(),len(paths));e=np.clip(np.round((E+12000)*4),0,65535).astype(np.uint16)
    out[n*GH:(n+1)*GH,:,0]=e>>8;out[n*GH:(n+1)*GH,:,1]=e&255;out[n*GH:(n+1)*GH,:,2]=np.round(moist*255)
    m=dict(p);m['inflow']=inflow;m['emin']=float(E.min());m['emax']=float(E.max());meta.append(m)
    print(p['id'],round(E.min()),round(E.max()),'moist',round(moist.mean(),2),'inflow',inflow[:3])
Image.fromarray(out).save('terrain.png',optimize=True)
json.dump(meta,open('terrain.json','w'))
