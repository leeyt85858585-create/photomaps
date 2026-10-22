import sys,os;H=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,H)
from tm import *
import numpy as np
import math,json,re
G=sys.argv[1];BB=json.load(open(H+'/bboxes.json'))[G]
def ld(p):
    t=open(p,encoding='utf8').read()
    if t.startswith('{"g"'): t=t.split('\n',1)[1]
    return json.loads(t)['elements']
hw=ld(sys.argv[2]);poi=ld(sys.argv[3])
s=open(H+'/../../index.html',encoding='utf8').read()
D=json.loads(re.search(r'const DATA = (\[.*?\]);\n',s,re.S).group(1))
COM={'restaurant','cafe','bar','pub','fast_food','ice_cream','fuel','bank','pharmacy','theatre','cinema','karaoke_box'}
P=[];SUB=[]
for x in poi:
    t=x.get('tags',{})
    if t.get('railway')=='subway_entrance': SUB.append(fwd(x['lat'],x['lon']));continue
    if 'shop' in t or t.get('amenity') in COM or 'tourism' in t or t.get('leisure') in ('amusement_arcade','escape_game'):
        P.append(fwd(x['lat'],x['lon']))
for d in D: P.append(fwd(d['la'],d['lo']))
print('poi',len(P),'sub',len(SUB))
from collections import defaultdict
def hashpts(pts,g):
    h=defaultdict(list)
    for p in pts:h[(int(p[0]//g),int(p[1]//g))].append(p)
    return h
HP=hashpts(P,30);HS=hashpts(SUB,80)
def count(h,g,x,y,r):
    n=0;ix,iy=int(x//g),int(y//g)
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for p in h.get((ix+dx,iy+dy),()):
                if (p[0]-x)**2+(p[1]-y)**2<=r*r:n+=1
    return n
CF={'pedestrian':2.5,'living_street':2.0,'footway':1.2,'steps':0.6,'path':0.8,'residential':1.0,'unclassified':1.0,'service':0.8,'tertiary':1.3,'secondary':1.3,'primary':1.1,'road':1.0}
# slots(old)
_SL=[('we',range(14,18)),('we',range(18,22)),('wd',range(14,18)),('wd',range(18,22))]
O4=np.load(H+'/slot4.npy');I4={c:i for i,c in enumerate(json.load(open(H+'/slot4_ids.json')))}
def vec(k):
    if k is None: return np.zeros(20)
    o=O4[k]  # 5 slots x [L,Lf,T,G]
    return np.concatenate([o[:,0]+o[:,2]+o[:,3], o[:,1], o[:,2], o[:,1]+o[:,2]])
cache={}
def cv(k):
    if k not in cache: cache[k]=vec(k)
    return cache[k]
def pbil(la,lo):
    x,y=fwd(la,lo);fx=(x-125)/250;fy=(y-125)/250;x0=math.floor(fx);y0=math.floor(fy);tx=fx-x0;ty=fy-y0;r=np.zeros(20)
    for dx,dy,ww in ((0,0,(1-tx)*(1-ty)),(1,0,tx*(1-ty)),(0,1,(1-tx)*ty),(1,1,tx*ty)):
        r+=cv(I4.get(cellid((x0+dx)*250+1,(y0+dy)*250+1)[0]))*ww
    return r
def split(wi,g,cf):
    cur=[g[0]];L=0
    def flush(cur,L):
        if len(cur)>=2 and L>0:
            pieces.append([wi,cur,L,cf,(cur[0][0]+cur[-1][0])/2,(cur[0][1]+cur[-1][1])/2])
    for a,b in zip(g,g[1:]):
        xa,ya=fwd(*a);xb,yb=fwd(*b);dl=math.hypot(xb-xa,yb-ya)
        n=max(1,int(math.ceil(dl/40)))
        for i in range(1,n+1):
            q=(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n)
            cur.append(q);L+=dl/n
            if L>=35: flush(cur,L);cur=[q];L=0
    flush(cur,L)
pieces=[]  # (way idx, [pts latlon], L, wpm, cellid, mid)
for wi,wy in enumerate(hw):
    t=wy['tags'];h=t.get('highway')
    if h not in CF: continue
    if t.get('tunnel') in ('yes','building_passage') and h not in ('footway','pedestrian'): continue
    if t.get('indoor')=='yes' or t.get('level','0').startswith('-'): continue
    if h=='service' and t.get('service') in ('parking_aisle','driveway','drive-through'): continue
    if t.get('access') in ('private','no'): continue
    cf=CF[h]
    if h=='footway' and t.get('footway')=='crossing': cf=0.4
    g=[(p['lat'],p['lon']) for p in wy['geometry']]
    split(wi,g,cf)
pieces=[p for p in pieces if BB[0]<=p[4]<=BB[2] and BB[1]<=p[5]<=BB[3]]
print('pieces',len(pieces))
# weights
S=defaultdict(float)
for pc in pieces:
    x,y=fwd(pc[4],pc[5]);n=min(count(HP,30,x,y,30),12);sb=1.5 if count(HS,80,x,y,80) else 1.0
    pc[3]=pc[3]*(1+0.4*n)*sb
    c=cellid(x,y)[0];pc.append(c);S[c]+=pc[3]*pc[2]
Sv=np.array(list(S.values()));SMIN=1567.96;print('SMIN',SMIN)
vals=[]
for pc in pieces:
    v=pbil(pc[4],pc[5])*pc[3]/max(S[pc[6]],SMIN)*10  # people per 10m
    pc.append(v);vals.append(v)
V=np.array(vals)
# breaks: pooled quantiles per family (tot / young) so time-of-day differences show
br=[]
for fam in (slice(0,5),slice(5,10),slice(10,15),slice(15,20)):
    pool=V[:,fam].ravel();pool=pool[pool>0]
    br.append([float(np.quantile(pool,q)) for q in (0.3,0.55,0.75,0.9,0.97)])
BR0=json.load(open(H+'/../../flow_hongdae.json'))['br'] if G!='hongdae' else br
br=BR0
print('breaks',br)
def cls(v,b): return sum(v>=x for x in b)
out=[];cur=None
for pc in pieces:
    code=''.join(str(cls(pc[7][i],br[i//5])) for i in range(20))
    if cur and cur['w']==pc[0] and cur['c']==code:
        cur['p'].extend(pc[1][1:])
    else:
        cur={'w':pc[0],'c':code,'p':list(pc[1])};out.append(cur)
def enc(p):
    a=[];px=py=0
    for la,lo in p:
        x=int(round(la*1e5));y=int(round(lo*1e5));a+= [x-px,y-py];px,py=x,y
    return a
res=[[o['c'],enc(o['p'])] for o in out]
json.dump({'g':G,'bb':BB,'v':'26.10 생활인구(내국인·단기·장기 외국인) · OSM 2026.06','br':br,'r':res},open(H+'/../../flow_'+G+'.json','w'),separators=(',',':'))
import os;print('runs',len(res),os.path.getsize(H+'/../../flow_'+G+'.json'))
# top streets sanity: print highest weekend-afternoon pieces names
top=sorted(pieces,key=lambda p:-p[7][12])[:15]
for p in top: print(hw[p[0]]['tags'].get('name'),hw[p[0]]['tags'].get('highway'),round(p[4],5),round(p[5],5),round(p[7][0],1))
