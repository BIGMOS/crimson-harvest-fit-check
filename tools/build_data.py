"""Build eve-data.js for crimson-checker.html from the official EVE SDE (sde-download/sde.zip)."""
import sys,json,os
sys.path.insert(0,os.path.dirname(__file__))
from sde import rows,en
OUT=os.path.join(os.path.dirname(__file__),'..','eve-data.js')
attrs={a['_key']:a for a in rows('dogmaAttributes')}
effects={e['_key']:e for e in rows('dogmaEffects')}
groups={g['_key']:g for g in rows('groups')}
dog={d['_key']:d for d in rows('typeDogma')}
meta=next(rows('_sde'))
KEEP_CATS={6,7,8,16,18,32}
T={};usedE=set();usedA=set()
npc_src={}
NPC_NAMES={'tet':[('Tetrimon Crucifier',4),('Tetrimon Crusader',4),('Tetrimon Heretic',3),('Tetrimon Augoror',3),('Tetrimon Curse',3),('Tetrimon Omen',3),('Tetrimon Oracle',2),('Tetrimon Commander',1)],
           'bra':[('Harvest Savior',2),('Harvest Shepherd',2),('Harvest Exsanguinator',4),('Harvest Follower',4),('Harvest Cleric',2),('Harvest Prophet',4),('Harvest Sage',4),('Harvest Diviner',2),('Harvest Overseer',1)]}
want={n for l in NPC_NAMES.values() for n,_ in l}
alltypes={}
for t in rows('types'):
    g=groups.get(t['groupID']);
    if not g: continue
    name=en(t.get('name'))
    alltypes[t['_key']]=t
    if g['categoryID']==11 and name in want: npc_src[name]=t['_key']
    if not t.get('published') or g['categoryID'] not in KEEP_CATS: continue
    d=dog.get(t['_key'],{})
    a={x['attributeID']:x['value'] for x in d.get('dogmaAttributes',[])}
    for k,f in ((38,'capacity'),(4,'mass'),(161,'volume'),(162,'radius')):
        if f in t and k not in a: a[k]=t[f]
    e=[x['effectID'] for x in d.get('dogmaEffects',[])]
    T[t['_key']]=[name,t['groupID'],a,e]
    usedE.update(e);usedA.update(a)
E={}
for i in usedE:
    e=effects[i];mods=[]
    for m in e.get('modifierInfo',[]):
        if 'modifiedAttributeID' not in m or 'modifyingAttributeID' not in m: continue
        mods.append([m['domain'],m['func'],m['modifiedAttributeID'],m['modifyingAttributeID'],m['operation'],m.get('skillTypeID',0),m.get('groupID',0)])
        usedA.update((m['modifiedAttributeID'],m['modifyingAttributeID']))
    E[i]=[e['effectCategoryID'],mods,e['name'],e.get('dischargeAttributeID',0),e.get('durationAttributeID',0)]
A={i:[attrs[i]['name'],attrs[i].get('defaultValue',0),1 if attrs[i].get('stackable') else 0,1 if attrs[i].get('highIsGood') else 0] for i in usedA if i in attrs}
G={i:[en(g['name']),g['categoryID']] for i,g in groups.items() if g['categoryID'] in KEEP_CATS}
# NPCs
AN={a['name']:i for i,a in attrs.items()}
def npc(name):
    tid=npc_src[name];t=alltypes[tid]
    d={attrs[x['attributeID']]['name']:x['value'] for x in dog[tid]['dogmaAttributes']}
    effs=[effects[x['effectID']]['name'] for x in dog[tid]['dogmaEffects']]
    D=('emDamage','thermalDamage','kineticDamage','explosiveDamage')
    tur=[0,0,0,0]
    if 'targetAttack' in effs and d.get('speed'):
        tur=[d.get(x,0)*d.get('damageMultiplier',1)/(d['speed']/1000) for x in D]
    mis=[0,0,0,0];mname=None
    if 'missileLaunchingForEntity' in effs and d.get('entityMissileTypeID'):
        mt=int(d['entityMissileTypeID']);md={attrs[x['attributeID']]['name']:x['value'] for x in dog[mt]['dogmaAttributes']}
        mname=en(alltypes[mt]['name'])
        mis=[md.get(x,0)*d.get('missileDamageMultiplier',1)/(d['missileLaunchDuration']/1000) for x in D]
    neut=0;nrange=0
    if 'npcBehaviorEnergyNeutralizer' in effs:
        neut=d.get('energyNeutralizerAmount',0)/(d.get('behaviorEnergyNeutralizerDuration',1e9)/1000);nrange=d.get('behaviorEnergyNeutralizerRange',0)+d.get('behaviorEnergyNeutralizerFalloff',0)
    ew=[]
    if 'npcBehaviorWebifier' in effs: ew.append('web %dkm'%(d.get('behaviorWebifierRange',0)/1000))
    if 'behaviorWarpDisrupt' in effs: ew.append('point %dkm'%(d.get('behaviorWarpDisruptRange',0)/1000))
    if 'behaviorWarpScramble' in effs or 'npcBehaviorWarpScrambler' in effs: ew.append('scram')
    if neut: ew.append('neut %.1f GJ/s to ~%dkm'%(neut,nrange/1000))
    if 'npcBehaviorTrackingDisruptor' in effs: ew.append('tracking disruptor')
    if 'npcBehaviorGuidanceDisruptor' in effs: ew.append('guidance disruptor')
    if 'behaviorTargetPainter' in effs: ew.append('target painter')
    if 'npcBehaviorRemoteArmorRepairer' in effs: ew.append('remote armor rep')
    rep=0
    if 'npcBehaviorArmorRepairer' in effs: rep=d.get('behaviorArmorRepairerAmount',0)/(d.get('behaviorArmorRepairerDuration',1e9)/1000)
    res=lambda p:[d.get(p+x,1) for x in ('EmDamageResonance','ThermalDamageResonance','KineticDamageResonance','ExplosiveDamageResonance')]
    hullres=[d.get(x,1) for x in ('emDamageResonance','thermalDamageResonance','kineticDamageResonance','explosiveDamageResonance')]
    return {'n':name,'c':en(groups[t['groupID']]['name']).replace('Irregular ',''),'tur':[round(x,2) for x in tur],'mis':[round(x,2) for x in mis],'misName':mname,
            'neut':round(neut,2),'ew':ew,'rep':round(rep,1),'hp':[d.get('shieldCapacity',0),d.get('armorHP',0),d.get('hp',0)],'res':[res('shield'),res('armor'),hullres],
            'range':d.get('maxRange',0),'orbit':d.get('npcBehaviorMaximumCombatOrbitRange',0),'sig':d.get('signatureRadius',0),'vel':d.get('entityCruiseSpeed',0),'effs':effs}
SITES={k:{'name':{'tet':'Tetrimon Base','bra':'Crimson Gauntlet'}[k],'ships':[dict(npc(n),cnt=c) for n,c in l]} for k,l in NPC_NAMES.items()}
data={'build':meta.get('buildNumber'),'date':meta.get('releaseDate'),'A':A,'E':E,'G':G,'T':T,'SITES':SITES}
s='window.EVE='+json.dumps(data,separators=(',',':'),ensure_ascii=False)+';'
open(OUT,'w',encoding='utf-8').write(s)
print('types',len(T),'effects',len(E),'attrs',len(A),'bytes',len(s.encode()))
for k,v in SITES.items():
    for x in v['ships']: print(k,x['n'],x['c'],'x%d'%x['cnt'],'tur',round(sum(x['tur'])),'mis',round(sum(x['mis'])),x['misName'],'neut',x['neut'],x['ew'],'rep',x['rep'],'hp',x['hp'])
print(sorted({e for v in SITES.values() for x in v['ships'] for e in x['effs']}))
