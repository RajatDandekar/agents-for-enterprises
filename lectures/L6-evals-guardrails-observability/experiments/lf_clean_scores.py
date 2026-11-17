"""Delete the scores of our first, buggy online-eval pass (ids not starting with l6-) from Langfuse. Throttled: the delete
API rate-limits hard (16 Nov 2026: 429s after a few deletes). Keys from the course .env, never printed. Run from the laptop."""
import json,base64,urllib.request,time
env={}
for l in open('/Users/raj/Claude_Brain/enterprise-agents-course/.env'):
    if '=' in l: k,v=l.strip().split('=',1); env[k]=v.strip().strip('"\'')
base=(env.get('LANGFUSE_BASE_URL') or env.get('LANGFUSE_HOST')).rstrip('/')
auth=base64.b64encode(f"{env['LANGFUSE_PUBLIC_KEY']}:{env['LANGFUSE_SECRET_KEY']}".encode()).decode()
def req(p, method='GET'):
    for i in range(8):
        try:
            r=urllib.request.Request(base+p,method=method,headers={'Authorization':'Basic '+auth})
            with urllib.request.urlopen(r) as f:
                b=f.read(); return json.loads(b) if b and method=='GET' else f.status
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(3*(i+1)); continue
            raise
ids=[]
for nm in ("commit_without_yes","tool_errors","unsupported_amount","grounded_reply"):
    cursor=None
    for _ in range(50):
        d=req(f"/api/public/v3/scores?name={nm}&limit=100"+(f"&cursor={cursor}" if cursor else ""))
        data=d.get('data',[]); ids+=[s['id'] for s in data if not str(s['id']).startswith('l6-')]
        cursor=(d.get('meta') or {}).get('cursor')
        if not cursor or not data: break
        time.sleep(0.5)
ids=list(dict.fromkeys(ids)); print('old scores', len(ids), flush=True)
n=0
for i in ids:
    req(f"/api/public/scores/{i}", 'DELETE'); n+=1; time.sleep(0.4)
print('deleted', n)
