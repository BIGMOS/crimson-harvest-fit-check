"""Build alpha-data.js: the highest level an Alpha clone can train each skill to.

Source: the clone state table mirrored at sde.hoboleaks.space (the same data the game client ships)."""
import json,os,urllib.request
OUT=os.path.join(os.path.dirname(__file__),'..','alpha-data.js')
rq=urllib.request.Request('https://sde.hoboleaks.space/tq/clonestates.json',headers={'User-Agent':'crimson-harvest-fit-check'})
d=json.load(urllib.request.urlopen(rq,timeout=30))
sets=[{int(k):v for k,v in r['skills'].items()} for r in d.values()]
caps={}
for st in sets:
    for k,v in st.items(): caps[k]=max(caps.get(k,0),v)
s='window.ALPHA='+json.dumps(caps,separators=(',',':'),sort_keys=True)+';'
open(OUT,'w',encoding='utf-8').write(s)
print('skills',len(caps),'same for every race',all(st==sets[0] for st in sets),'bytes',len(s))
