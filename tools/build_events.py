"""Build event-data.js: event combat sites beyond the two in eve-data.js.

To add a future event, add its NPC type ids to NPC (ESI type ids; names are looked up from ESI) and
its sites to SITES. An NPC already in eve-data.js (the Crimson Harvest Blood Raiders and Tetrimon
ships) can be used by name without an id. Wave layouts follow the EVE University wiki; where the
wiki gives a range ("0-4"), the top of the range is used.

NPC stats come from ESI, so this needs no SDE download."""
import json,os,urllib.request,concurrent.futures as cf
OUT=os.path.join(os.path.dirname(__file__),'..','event-data.js')
ESI='https://esi.evetech.net/latest/'
def get(p):
    err=None
    for _ in range(4):
        try:
            rq=urllib.request.Request(ESI+p+'/?datasource=tranquility',headers={'User-Agent':'crimson-harvest-fit-check'})
            return json.load(urllib.request.urlopen(rq,timeout=30))
        except Exception as e: err=e
    raise err
def many(f,ids):
    with cf.ThreadPoolExecutor(16) as ex: return list(ex.map(f,ids))

# Triglavian NPCs of the Criterion of Fitness site (Crimson Harvest 2026). The plain Raznaborg hulls are
# used; the wiki also lists Hospodar and specialised variants (Blinding, Starving...) that can spawn instead.
NPC=[52645,52649,54132,54131,54133,54134,97288,97290,97310]
BR=['Harvest Savior','Harvest Shepherd','Harvest Exsanguinator','Harvest Follower','Harvest Cleric','Harvest Prophet','Harvest Sage','Harvest Diviner']
ROOM=[(n,{'Harvest Savior':2,'Harvest Shepherd':2,'Harvest Cleric':2,'Harvest Diviner':2}.get(n,4)) for n in BR]
# (key, group in the Site dropdown, name, share of the room shooting you by default, note, waves)
SITES=[
 ('chsan','Crimson Harvest','Crimson Harvest Sanctuary',60,'Level 5 escalation from a Crimson Gauntlet run. One room, four waves, then the Harvest Overseer.',
  [ROOM,ROOM,ROOM,ROOM,[('Harvest Overseer',1)]]),
 ('chcof','Crimson Harvest','Criterion of Fitness',100,'Solo site: the gate lets one ship through. Triglavian damage spools up over time and that ramp is not modelled. The boss shown is the Fitness 15 one; lower Fitness gives a Superior Leshak or Superior Drekavac.',
  [[('Raznaborg Damavik',2),('Raznaborg Kikimora',2),('Raznaborg Rodiva',1),('Raznaborg Drekavac',1)],
   [('Raznaborg Damavik',2),('Raznaborg Kikimora',2),('Raznaborg Rodiva',1),('Raznaborg Vedmak',3),('Raznaborg Drekavac',3),('Raznaborg Leshak',1)],
   [('Raznaborg Damavik',3),('Raznaborg Kikimora',2),('Raznaborg Rodiva',2),('Raznaborg Vedmak',1),('Raznaborg Drekavac',3),('Raznaborg Leshak',4)],
   [("Zorya's Babaroga",1)]]),
]

types={t['type_id']:t for t in many(lambda i:get('universe/types/%d'%i),NPC)}
groups={g['group_id']:g['name'] for g in many(lambda i:get('universe/groups/%d'%i),sorted({t['group_id'] for t in types.values()}))}
aid=sorted({a['attribute_id'] for t in types.values() for a in t.get('dogma_attributes',[])})
eid=sorted({e['effect_id'] for t in types.values() for e in t.get('dogma_effects',[])})
AN={a['attribute_id']:a['name'] for a in many(lambda i:get('dogma/attributes/%d'%i),aid)}
EN={e['effect_id']:e['name'] for e in many(lambda i:get('dogma/effects/%d'%i),eid)}
mcache={}
def missile(tid):
    if tid not in mcache:
        t=get('universe/types/%d'%tid)
        for a in t.get('dogma_attributes',[]):
            if a['attribute_id'] not in AN: AN[a['attribute_id']]=get('dogma/attributes/%d'%a['attribute_id'])['name']
        mcache[tid]=(t['name'],{AN[a['attribute_id']]:a['value'] for a in t['dogma_attributes']})
    return mcache[tid]
D=('emDamage','thermalDamage','kineticDamage','explosiveDamage')
CLASS=(('Babaroga','Battleship'),('Leshak','Battleship'),('Drekavac','Battlecruiser'),('Vedmak','Cruiser'),('Rodiva','Cruiser'),('Kikimora','Destroyer'),('Damavik','Frigate'))
def npc(tid):
    t=types[tid];d={AN[a['attribute_id']]:a['value'] for a in t.get('dogma_attributes',[])}
    effs=[EN[e['effect_id']] for e in t.get('dogma_effects',[])]
    tur=[0,0,0,0]
    if d.get('speed') and any(e in effs for e in ('targetAttack','targetDisintegratorAttack','npcBehaviorTargetDisintegratorAttack')):
        tur=[d.get(x,0)*d.get('damageMultiplier',1)/(d['speed']/1000) for x in D]
    mis=[0,0,0,0];mname=None
    if 'missileLaunchingForEntity' in effs and d.get('entityMissileTypeID') and d.get('missileLaunchDuration'):
        mname,md=missile(int(d['entityMissileTypeID']))
        mis=[md.get(x,0)*d.get('missileDamageMultiplier',1)/(d['missileLaunchDuration']/1000) for x in D]
    neut=0;nrange=0
    if 'npcBehaviorEnergyNeutralizer' in effs:
        neut=d.get('energyNeutralizerAmount',0)/(d.get('behaviorEnergyNeutralizerDuration',1e9)/1000);nrange=d.get('behaviorEnergyNeutralizerRange',0)+d.get('behaviorEnergyNeutralizerFalloff',0)
    elif 'entityEnergyNeutralizerFalloff' in effs:
        neut=d.get('energyNeutralizerAmount',0)/(d.get('energyNeutralizerDuration',1e9)/1000);nrange=d.get('energyNeutralizerRangeOptimal',0)
    ew=[]
    if 'npcBehaviorWebifier' in effs: ew.append('web %dkm'%(d.get('behaviorWebifierRange',0)/1000))
    if 'behaviorWarpDisrupt' in effs: ew.append('point %dkm'%(d.get('behaviorWarpDisruptRange',0)/1000))
    if 'behaviorWarpScramble' in effs or 'npcBehaviorWarpScrambler' in effs: ew.append('scram')
    if neut: ew.append('neut %.1f GJ/s to ~%dkm'%(neut,nrange/1000))
    rep=0;rrep=0
    if 'npcBehaviorArmorRepairer' in effs: rep=d.get('behaviorArmorRepairerAmount',0)/(d.get('behaviorArmorRepairerDuration',1e9)/1000)
    if 'npcBehaviorRemoteArmorRepairer' in effs:
        rrep=d.get('armorDamageAmount',0)/(d.get('behaviorRemoteArmorRepairDuration',1e9)/1000);ew.append('remote armor rep %d HP/s'%rrep)
    res=lambda p:[d.get(p+x,1) for x in ('EmDamageResonance','ThermalDamageResonance','KineticDamageResonance','ExplosiveDamageResonance')]
    hullres=[d.get(x,1) for x in ('emDamageResonance','thermalDamageResonance','kineticDamageResonance','explosiveDamageResonance')]
    c=next((v for k,v in CLASS if k in t['name']),groups[t['group_id']])
    return {'n':t['name'],'c':c,'tur':[round(x,2) for x in tur],'mis':[round(x,2) for x in mis],'misName':mname,
            'neut':round(neut,2),'ew':ew,'rep':round(rep,1),'rrep':round(rrep,1),
            'hp':[d.get('shieldCapacity',0),d.get('armorHP',0),d.get('hp',0)],'res':[res('shield'),res('armor'),hullres],
            'range':d.get('maxRange',0),'sig':d.get('signatureRadius',0),'vel':d.get('maxVelocity',0),'effs':effs}
npcs=[npc(i) for i in NPC]
for x in npcs: x.pop('effs')
data={'npcs':npcs,'sites':[{'k':k,'grp':g,'name':n,'scale':sc,'note':note,'waves':[[[a,b] for a,b in w] for w in waves]} for k,g,n,sc,note,waves in SITES]}
s='window.EVENTS='+json.dumps(data,separators=(',',':'),ensure_ascii=False)+';'
open(OUT,'w',encoding='utf-8').write(s)
print('npcs',len(npcs),'sites',len(SITES),'bytes',len(s.encode()))
for i,x in zip(NPC,[npc(i) for i in NPC]): print(x['n'],'|',x['c'],'tur',round(sum(x['tur'])),'mis',round(sum(x['mis'])),'neut',x['neut'],x['ew'],'rep',x['rep'],'hp',[round(h) for h in x['hp']],'effs',x['effs'])
