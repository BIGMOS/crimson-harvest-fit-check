"""Build wh-data.js (C3-C6 wormhole combat anomalies) for crimson-checker.html.

NPC stats come from ESI, so this needs no SDE download. Wave layouts follow the EVE University wiki.
Capital escalation waves are left out: they only spawn when a capital ship is on grid."""
import json,os,urllib.request,concurrent.futures as cf
OUT=os.path.join(os.path.dirname(__file__),'..','wh-data.js')
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

# Sleepers by name. C3/C4 and C5/C6 each share one set of hulls.
NPC={'Emergent Defender':30212,'Emergent Preserver':30214,'Emergent Upholder':30213,
     'Awakened Defender':30203,'Awakened Preserver':30205,'Awakened Upholder':30204,
     'Sleepless Defender':30192,'Sleepless Preserver':30194,'Sleepless Upholder':30193,'Sleepless Safeguard':30195,
     'Emergent Escort':30211,'Emergent Sentinel':30215,'Emergent Keeper':30216,'Emergent Warden':30217,
     'Awakened Sentinel':30206,'Awakened Keeper':30207,'Awakened Warden':30208,
     'Sleepless Sentinel':30196,'Sleepless Keeper':30197,'Sleepless Warden':30198,'Sleepless Guardian':30199}
TOWERS=('Wakeful Sentry Tower','Restless Sentry Tower')
TOWER_GROUPS=(99,383,495)
ED,EP,EU,AD,AP,AU,SD,SP,SU,SS='Emergent Defender','Emergent Preserver','Emergent Upholder','Awakened Defender','Awakened Preserver','Awakened Upholder','Sleepless Defender','Sleepless Preserver','Sleepless Upholder','Sleepless Safeguard'
EE,ES,EK,EW,AS,AK,AW,LS,LK,LW,LG='Emergent Escort','Emergent Sentinel','Emergent Keeper','Emergent Warden','Awakened Sentinel','Awakened Keeper','Awakened Warden','Sleepless Sentinel','Sleepless Keeper','Sleepless Warden','Sleepless Guardian'
WT,RT=TOWERS
# (key, class, name, waves). Spawns the wiki marks as "possible" are included: this is the worst case.
SITES=[
 ('c3ffs','C3','Fortification Frontier Stronghold',[[(ED,2),(AD,2)],[(AD,2),(AU,2)],[(AD,2),(AP,1),(AU,1),(SU,1)]]),
 ('c3ofs','C3','Outpost Frontier Stronghold',[[(WT,3),(SD,1)],[(AD,4)],[(ED,4),(SD,2)]]),
 ('c3sol','C3','Solar Cell',[[(EP,1),(AU,1),(SD,1)],[(ED,2),(EU,2),(AD,3),(AU,1)],[(AD,2),(SD,1),(SP,1)]]),
 ('c3oru','C3','The Oruze Construct',[[(WT,2),(AU,4),(AP,1)],[(ED,4),(SD,1)],[(AP,2),(SU,1)]]),
 ('c4bar','C4','Frontier Barracks',[[(SP,1),(SU,1)],[(AP,2),(SU,3)],[(EP,3),(AP,4),(SP,2)]]),
 ('c4cmd','C4','Frontier Command Post',[[(WT,5),(ED,4),(EP,4)],[(EU,4),(AD,6),(SD,2)],[(AD,2),(AP,2),(SP,3)]]),
 ('c4int','C4','Integrated Terminus',[[(WT,4),(EU,3),(AD,4)],[(EP,2),(AP,2),(AU,4)],[(ED,4),(EU,2),(SS,1)]]),
 ('c4san','C4','Sleeper Information Sanctum',[[(AU,2),(SP,2),(EU,2)],[(SD,3),(SS,1)],[(EP,2),(EU,3),(AP,2),(AU,2)]]),
 ('c5gar','C5','Core Garrison',[[(RT,3),(ES,5),(AS,5)],[(EK,6),(LS,3)],[(AS,5),(AK,3),(LS,3)],[(EW,3),(AS,2),(LK,2)]]),
 ('c5str','C5','Core Stronghold',[[(RT,6),(ES,4)],[(LK,2),(LW,2)],[(EW,6),(AS,7)],[(AW,4),(LK,2),(LW,3)]]),
 ('c5oso','C5','Oruze Osobnyk',[[(ES,4),(LK,1),(LS,3)],[(AS,6),(LG,1)],[(EK,4),(EW,2),(AW,3)]]),
 ('c5qua','C5','Quarantine Area',[[(RT,4),(EE,3),(AK,2),(LS,1)],[(AS,4),(LS,2)],[(ES,5),(AW,3),(LK,2)]]),
 ('c6cit','C6','Core Citadel',[[(LK,1),(LS,1),(LW,1)],[(EK,8),(LS,3),(LW,1)],[(EK,8),(LK,3),(LW,3)],[(EK,8),(LG,2)]]),
 ('c6bas','C6','Core Bastion',[[(RT,3),(LS,2),(AS,3),(AW,3),(AK,3),(EK,3),(ES,3)],[(AS,4),(AW,4),(LK,4)],[(EW,6),(AW,5),(LG,5)],[(LS,4),(LG,2)]]),
 ('c6ser','C6','Strange Energy Readings',[[(AW,5),(EK,5),(LK,2)],[(AK,6),(LG,3)],[(EK,6),(AW,4),(LK,5)]]),
 ('c6mir','C6','The Mirror',[[(RT,6),(LS,2),(LW,3),(AW,4),(EW,6)],[(ES,6),(LK,2),(LG,3)],[(EK,4),(EW,4),(AK,4),(AW,4),(LK,4)]]),
]

for g in many(lambda i:get('universe/groups/%d'%i),TOWER_GROUPS):
    for t in many(lambda i:get('universe/types/%d'%i),g['types']):
        if t['name'] in TOWERS: NPC.setdefault(t['name'],t['type_id'])
missing=[n for n in TOWERS if n not in NPC]
if missing: raise SystemExit('sentry tower type not found: %s'%missing)

types={t['type_id']:t for t in many(lambda i:get('universe/types/%d'%i),sorted(set(NPC.values())))}
groups={g['group_id']:g['name'] for g in many(lambda i:get('universe/groups/%d'%i),sorted({t['group_id'] for t in types.values()}))}
aid=sorted({a['attribute_id'] for t in types.values() for a in t.get('dogma_attributes',[])})
eid=sorted({e['effect_id'] for t in types.values() for e in t.get('dogma_effects',[])})
AN={a['attribute_id']:a['name'] for a in many(lambda i:get('dogma/attributes/%d'%i),aid)}
EN={e['effect_id']:e['name'] for e in many(lambda i:get('dogma/effects/%d'%i),eid)}
mcache={}
def missile(tid):
    if tid not in mcache:
        t=get('universe/types/%d'%tid);ids=[a['attribute_id'] for a in t.get('dogma_attributes',[])]
        for i in ids:
            if i not in AN: AN[i]=get('dogma/attributes/%d'%i)['name']
        mcache[tid]=(t['name'],{AN[a['attribute_id']]:a['value'] for a in t['dogma_attributes']})
    return mcache[tid]
D=('emDamage','thermalDamage','kineticDamage','explosiveDamage')
def cls(t):
    g=groups[t['group_id']]
    if 'Sentry' in g: return 'Sentry tower'
    return 'Battleship' if 'Sleepless' in g else 'Cruiser' if 'Awakened' in g else 'Frigate'
def npc(name):
    t=types[NPC[name]];d={AN[a['attribute_id']]:a['value'] for a in t.get('dogma_attributes',[])}
    effs=[EN[e['effect_id']] for e in t.get('dogma_effects',[])]
    tur=[0,0,0,0]
    if 'targetAttack' in effs and d.get('speed'):
        tur=[d.get(x,0)*d.get('damageMultiplier',1)/(d['speed']/1000) for x in D]
    mis=[0,0,0,0];mname=None
    if 'missileLaunchingForEntity' in effs and d.get('entityMissileTypeID') and d.get('missileLaunchDuration'):
        mname,md=missile(int(d['entityMissileTypeID']))
        mis=[md.get(x,0)*d.get('missileDamageMultiplier',1)/(d['missileLaunchDuration']/1000) for x in D]
    neut=0;nrange=0
    if 'entityEnergyNeutralizerFalloff' in effs:
        neut=d.get('energyNeutralizerAmount',0)/(d.get('energyNeutralizerDuration',1e9)/1000)
        nrange=d.get('energyNeutralizerRangeOptimal',0)+d.get('falloffEffectiveness',0)
    ew=[]
    if 'modifyTargetSpeed2' in effs: ew.append('web %dkm'%(d.get('modifyTargetSpeedRange',0)/1000))
    if 'warpScrambleForEntity' in effs or 'warpScrambleTargetMWDBlockActivationForEntity' in effs: ew.append('scram %dkm'%(d.get('warpScrambleRange',0)/1000))
    if neut: ew.append('neut %.1f GJ/s to ~%dkm'%(neut,nrange/1000))
    # repair on a ship being shot: its own repairer plus what its wave-mates send it is handled in the page via rrep
    rep=0
    if any(e.startswith('entityArmorRepairing') for e in effs):
        rep=d.get('entityArmorRepairAmount',0)/(d.get('entityArmorRepairDuration',1e9)/1000)
    rrep=0
    if 'NPCRemoteArmorRepair' in effs:
        rrep=d.get('npcRemoteArmorRepairAmount',0)/(d.get('npcRemoteArmorRepairDuration',1e9)/1000)
        ew.append('remote armor rep %d HP/s'%rrep)
    res=lambda p:[d.get(p+x,1) for x in ('EmDamageResonance','ThermalDamageResonance','KineticDamageResonance','ExplosiveDamageResonance')]
    hullres=[d.get(x,1) for x in ('emDamageResonance','thermalDamageResonance','kineticDamageResonance','explosiveDamageResonance')]
    return {'n':name,'c':cls(t),'tur':[round(x,2) for x in tur],'mis':[round(x,2) for x in mis],'misName':mname,
            'neut':round(neut,2),'ew':ew,'rep':round(rep,1),'rrep':round(rrep,1),
            'hp':[d.get('shieldCapacity',0),d.get('armorHP',0),d.get('hp',0)],'res':[res('shield'),res('armor'),hullres],
            'range':d.get('maxRange',0),'orbit':d.get('entityFlyRange',0),'sig':d.get('signatureRadius',0),'vel':d.get('maxVelocity',0)}
names=sorted(NPC);idx={n:i for i,n in enumerate(names)}
data={'npcs':[npc(n) for n in names],
      'sites':[{'k':k,'cls':c,'name':nm,'waves':[[[idx[n],cnt] for n,cnt in w] for w in waves]} for k,c,nm,waves in SITES]}
s='window.WH='+json.dumps(data,separators=(',',':'),ensure_ascii=False)+';'
open(OUT,'w',encoding='utf-8').write(s)
print('npcs',len(names),'sites',len(SITES),'bytes',len(s.encode()))
for x in data['npcs']: print(x['n'],'|',x['c'],'tur',round(sum(x['tur'])),'mis',round(sum(x['mis'])),x['misName'],'neut',x['neut'],x['ew'],'rep',x['rep'],'rrep',x['rrep'],'hp',x['hp'],'armres',x['res'][1])
for k,c,nm,waves in SITES:
    for i,w in enumerate(waves):
        dps=sum((sum(data['npcs'][idx[n]]['tur'])+sum(data['npcs'][idx[n]]['mis']))*cnt for n,cnt in w)
        print(c,nm,'wave',i+1,'raw dps',round(dps),'neut',round(sum(data['npcs'][idx[n]]['neut']*cnt for n,cnt in w),1))
