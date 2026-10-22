import csv,numpy as np,json,os
C='/tmp/work/pop2/csv'
SL=[(['20261010','20261011','20261017','20261018'],range(13,18)),
    (['20261010','20261011','20261017','20261018'],range(18,22)),
    (['20261016','20261010','20261017'],range(22,24)),
    (['20261007','20261008','20261013','20261014','20261015','20261016'],range(18,22)),
    (['20261007','20261008','20261013','20261014','20261015','20261016'],range(15,18))]
days=sorted({d for s in SL for d in s[0]})
cells={}
def cid(i):
    i=i.strip()
    if i not in cells: cells[i]=len(cells)
    return cells[i]
N=12000
# per day: arrays N x 24 for Ltot, Lf, T, G
D={}
v=lambda x:0.0 if x in('*','') else float(x)
for d in days:
    a=np.zeros((4,N,24));have=[0,0,0,0]
    p=f'{C}/250_LOCAL_RESD_{d}.csv'
    with open(p,encoding='cp949',newline='') as fh:
        rd=csv.reader(fh);next(rd)
        for r in rd:
            i=cid(r[3]);h=int(r[1]);a[0,i,h]+=v(r[4]);a[1,i,h]+=sum(v(x) for x in r[20:26])
    have[0]=have[1]=1
    for k,nm in ((2,'TEMP'),(3,'LONG')):
        p=f'{C}/250_FORN_{nm}_{d}.csv'
        if os.path.exists(p):
            with open(p,encoding='cp949',newline='') as fh:
                rd=csv.reader(fh);next(rd)
                for r in rd:
                    i=cid(r[3]);h=int(r[1]);a[k,i,h]+=v(r[4])
            have[k]=1
    D[d]=(a,have);print(d,have,len(cells),flush=True)
n=len(cells)
OUT=np.zeros((n,len(SL),4))
for si,(ds,hr) in enumerate(SL):
    for k in range(4):
        vals=[D[d][0][k,:n][:,list(hr)].mean(1) for d in ds if D[d][1][k]]
        OUT[:,si,k]=np.mean(vals,0)
np.save('/tmp/work/pop/slot4.npy',OUT)
json.dump(list(cells.keys()),open('/tmp/work/pop/slot4_ids.json','w'))
print('done',n)
