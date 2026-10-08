import zipfile,json,io,os
Z=zipfile.ZipFile(os.path.join(os.path.dirname(__file__),'..','sde-download','sde.zip'))
def rows(n):
    with Z.open(n+'.jsonl') as f:
        for line in io.TextIOWrapper(f,encoding='utf-8'): yield json.loads(line)
def en(x): return x.get('en','') if isinstance(x,dict) else (x or '')
