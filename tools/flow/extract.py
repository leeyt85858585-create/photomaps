# Seoul.osm.gz -> per region hw/poi json in overpass-like format
import gzip,json,sys
import xml.etree.ElementTree as ET
BB=json.load(open(__import__('os').path.dirname(__import__('os').path.abspath(__file__))+'/bboxes.json'))
E=0.003
R={g:[b[0]-E,b[1]-E,b[2]+E,b[3]+E] for g,b in BB.items() if g!='hongdae'}
def inr(la,lo): return [g for g,b in R.items() if b[0]<=la<=b[2] and b[1]<=lo<=b[3]]
nodes={}  # id->(lat,lon) only those in any region (+ margin for ways crossing)
OUTH={g:[] for g in R};OUTP={g:[] for g in R}
U=[min(b[0] for b in R.values())-0.01,min(b[1] for b in R.values())-0.01,max(b[2] for b in R.values())+0.01,max(b[3] for b in R.values())+0.01]
POIK=('shop','amenity','tourism','leisure')
cnt=0
for ev,el in ET.iterparse(gzip.open(sys.argv[1]),events=('end',)):
    t=el.tag
    if t=='node':
        la=float(el.get('lat'));lo=float(el.get('lon'))
        if U[0]<=la<=U[2] and U[1]<=lo<=U[3]:
            nodes[el.get('id')]=(la,lo)
            tags={c.get('k'):c.get('v') for c in el.iter('tag')}
            if tags and (any(k in tags for k in POIK) or tags.get('railway')=='subway_entrance'):
                for g in inr(la,lo): OUTP[g].append({'type':'node','lat':la,'lon':lo,'tags':tags})
        el.clear()
    elif t=='way':
        tags={c.get('k'):c.get('v') for c in el.iter('tag')}
        if 'highway' in tags:
            geo=[nodes.get(nd.get('ref')) for nd in el.iter('nd')]
            if all(geo) and geo:
                gs=set()
                for la,lo in geo: gs.update(inr(la,lo))
                for g in gs: OUTH[g].append({'type':'way','tags':tags,'geometry':[{'lat':a,'lon':b} for a,b in geo]})
        el.clear()
    elif t=='relation':
        el.clear()
for g in R:
    json.dump({'elements':OUTH[g]},open(f'{sys.argv[2]}/{g}_hw.json','w'))
    json.dump({'elements':OUTP[g]},open(f'{sys.argv[2]}/{g}_poi.json','w'))
    print(g,len(OUTH[g]),len(OUTP[g]))
