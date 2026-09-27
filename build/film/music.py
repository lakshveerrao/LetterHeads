import numpy as np,wave
SR=44100;DUR=86.5;N=int(SR*DUR)
L=np.zeros(N);R=np.zeros(N)
rng=np.random.default_rng(7)
def add(sig,t,pan=0.,g=1.):
    i=int(t*SR);n=min(len(sig),N-i)
    if n<=0:return
    L[i:i+n]+=sig[:n]*g*(1-pan)*.5*2**.5;R[i:i+n]+=sig[:n]*g*(1+pan)*.5*2**.5
def env(n,a=.005,d=.2,s=0.,r=.1,sl=None):
    t=np.arange(n)/SR;e=np.minimum(t/a,1)
    e=np.where(t>a,s+(1-s)*np.exp(-(t-a)/d),e)
    if sl:e*=np.clip((sl-t)/r+1,0,1)
    return e
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR);y=np.empty_like(x);v=0.
    for i in range(len(x)):v=(1-a)*x[i]+a*v;y[i]=v
    return y
def lpv(x,fc):  # vectorised-ish one-pole via scipy
    from scipy.signal import lfilter
    a=np.exp(-2*np.pi*fc/SR);return lfilter([1-a],[1,-a],x)
def hp(x,fc):return x-lpv(x,fc)
nt=lambda m:440*2**((m-69)/12)
def kick(g=1.):
    n=int(.5*SR);t=np.arange(n)/SR;f=45+120*np.exp(-t*30);ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t*7)*g
def boom(len_=3.):
    n=int(len_*SR);t=np.arange(n)/SR;f=30+70*np.exp(-t*4);ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-t*1.2)+lpv(rng.standard_normal(n),900)*np.exp(-t*3)*.6
    return s
def hat(g=.2):
    n=int(.08*SR);return hp(rng.standard_normal(n),7000)*np.exp(-np.arange(n)/SR*60)*g
def snare(g=.4):
    n=int(.25*SR);t=np.arange(n)/SR;return (hp(rng.standard_normal(n),1500)*np.exp(-t*18)+np.sin(2*np.pi*190*t)*np.exp(-t*25))*g
def pad(notes,t0,t1,g=.12,bright=1800,att=1.5):
    n=int((t1-t0)*SR);t=np.arange(n)/SR;s=np.zeros(n)
    for m in notes:
        for det in(-.12,.12):
            f=nt(m+det/1);s+=((2*((t*f)%1)-1))
    s=lpv(s,bright);e=np.minimum(t/att,1)*np.clip((t[-1]-t)/1.2,0,1);return s*e*g/len(notes)
def pluck(m,g=.3,dec=4.):
    n=int(1.2*SR);t=np.arange(n)/SR;f=nt(m)
    return (np.sin(2*np.pi*f*t)+.4*np.sin(4*np.pi*f*t)+.15*np.sin(6*np.pi*f*t))*np.exp(-t*dec)*g
def bell(m,g=.2):
    n=int(3*SR);t=np.arange(n)/SR;f=nt(m)
    return (np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*2)+.25*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*4))*np.exp(-t*1.1)*g
def riser(t0,t1,g=.25):
    n=int((t1-t0)*SR);t=np.arange(n)/SR;u=t/t[-1];x=rng.standard_normal(n)
    y=np.zeros(n);blk=2048
    for i in range(0,n,blk):y[i:i+blk]=hp(lpv(x[i:i+blk],300+6000*u[i]**2),200)[:len(y[i:i+blk])]
    add(y*u**2*g,t0)
def whoosh(t,g=.35):
    n=int(.6*SR);tt=np.arange(n)/SR;x=lpv(rng.standard_normal(n),2500)*np.sin(np.pi*tt/tt[-1])**2;add(x*g,t-.3,pan=.3)
CUTS=[3.2,8.6,16.6,19.6,21.4,24,25.8,27.6,31,33.2,36.4,39,46,47.6,51,55,60.4]
# ---- intro: drone, heartbeat, boom
add(pad([33,40],0,3.3,g=.25,bright=400,att=1.2),0)
for t in(.35,.75,1.15):add(kick(.5),t)
add(boom(3.5)*.9,1.6)
# ---- Earth and title
add(pad([45,52,59,60,64],3.2,8.8,g=.16,bright=1400,att=1.6),3.2)
add(boom(2.5)*.5,3.2)
for i,m in enumerate([69,72,76,79,81,84]):add(bell(m,.12),4.1+i*.17,pan=(i%2-.5)*.6)
# ---- Omo: gentle plucks at 100 bpm, A minor pentatonic
bt=60/100;seq=[57,60,64,67,69,67,64,60]
t=8.6;i=0
while t<16.4:
    add(pluck(seq[i%8]+(12 if i%16>=8 else 0),.22),t,pan=((i%4)-1.5)*.25)
    if i%4==0:add(kick(.35),t)
    t+=bt/2;i+=1
add(pad([45,52,57,60],8.6,16.8,g=.1,bright=900),8.6)
# ---- the race: accelerating drums 16.6 -> 46
t=16.6;beat=0
while t<46:
    u=(t-16.6)/(46-16.6);bpm=112+40*u;b=60/bpm
    add(kick(.9),t);add(hat(.12),t+b/2,pan=.4)
    if beat%2==1:add(snare(.28),t)
    bass=[33,33,36,31][(beat//4)%4]
    for k in(0,.5):
        n=int(b/2*SR);tt=np.arange(n)/SR;f=nt(bass+12);s=lpv((2*((tt*f)%1)-1),500+900*u)*np.exp(-tt*6)*.28;add(s,t+k*b)
    t+=b;beat+=1
add(pad([45,52,57,60,64],16.6,39.2,g=.08,bright=1200,att=3),16.6)
riser(35,39,.18)
# flood: sea swell
n=int(7*SR);tt=np.arange(n)/SR;sea=lpv(rng.standard_normal(n),500)*(0.4+0.6*np.sin(np.pi*tt/7))*.35;add(sea,39)
add(pad([41,48,53,57],39,46.3,g=.14,bright=800,att=2),39)
# ---- farmers to Rome: brighter, C major, 124 bpm
t=46;beat=0;b=60/124
while t<60.3:
    add(kick(.75),t);add(hat(.1),t+b/2,pan=-.4)
    if beat%2==1:add(snare(.22),t)
    if beat%2==0:add(pluck([72,76,79,84,79,76,74,72][(beat//2)%8],.14),t,pan=.3)
    t+=b;beat+=1
add(pad([48,55,60,64,67],46,60.6,g=.1,bright=1600,att=1.5),46)
# ---- back to Earth: drums drop, crescendo, clock
add(boom(3)*.6,60.4)
add(pad([41,48,57,60,64],60.4,72.2,g=.2,bright=1000,att=6),60.4)
t=61.;k=0
while t<72:
    n=int(.03*SR);add(hp(rng.standard_normal(n),3000)*np.exp(-np.arange(n)/SR*120)*.25,t,pan=.2*(1 if k%2 else -1))
    t+=max(.09,.5-.035*k);k+=1
riser(68,72,.25)
# ---- end: final hit and chord
add(boom(5)*1.0,72)
add(pad([45,52,57,61,64,69],72,86.5,g=.22,bright=2200,att=.3),72)
for i,m in enumerate([81,76,73,69]):add(bell(m,.14),76+i*.35,pan=(i%2-.5)*.5)
for c in CUTS:
    whoosh(c,.28)
    if c>=16.6 and c<60:add(boom(1.2)*.35,c)
# master
m=np.stack([L,R],1);m=np.tanh(m*1.4)/np.tanh(1.4);m/=np.max(np.abs(m))*1.05
fade=np.ones(N);fade[-int(1.5*SR):]=np.linspace(1,0,int(1.5*SR));m*=fade[:,None]
w=wave.open('score.wav','wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((m*32767).astype(np.int16).tobytes());w.close()
print('ok')
