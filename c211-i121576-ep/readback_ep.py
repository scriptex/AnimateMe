#!/usr/bin/env python3
"""c211-i121576 readback: endpoints + models + Cloud Logging for the EP fill."""
import json, os, time, urllib.error, urllib.parse, urllib.request
AUD=('//iam.googleapis.com/projects/284735288225/locations/global/'
     'workloadIdentityPools/my-pool/providers/my-provider')
SA='sa-gcloud-cli@civil-epigram-370317.iam.gserviceaccount.com'
PROJ_NUM='284735288225'; TAG='C211_I121576_RB'
def cap(s,n=400):
    s=s if isinstance(s,str) else repr(s); return s[:n] if len(s)>n else s
def http(url, method='GET', data=None, headers=None, timeout=60):
    h={'User-Agent':'c211-i121576-rb'}
    if headers: h.update(headers)
    body=json.dumps(data).encode() if data is not None else None
    if body is not None: h['Content-Type']='application/json'
    req=urllib.request.Request(url, headers=h, method=method, data=body)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: return r.status, r.read().decode('utf-8','replace')
    except urllib.error.HTTPError as e: return e.code, e.read().decode('utf-8','replace')
    except Exception as e: return -1, repr(e)
def jget(t,*ks,default=''):
    try: d=json.loads(t)
    except Exception: return default
    for k in ks:
        if not isinstance(d,dict): return default
        d=d.get(k,default)
    return d
base=os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL'); tok=os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN')
print('%s_START %s'%(TAG,time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())),flush=True)
c,b=http(base+('&' if '?' in base else '?')+'audience='+urllib.parse.quote(AUD,safe=''),headers={'Authorization':'Bearer '+tok})
idt=jget(b,'value'); print('%s_MINT http=%s ok=%s %s'%(TAG,c,bool(idt),'' if idt else cap(b,200)),flush=True)
if not idt: raise SystemExit(1)
c,b=http('https://sts.googleapis.com/v1/token',method='POST',data={'audience':AUD,'grantType':'urn:ietf:params:oauth:grant-type:token-exchange','requestedTokenType':'urn:ietf:params:oauth:token-type:access_token','scope':'https://www.googleapis.com/auth/cloud-platform','subjectTokenType':'urn:ietf:params:oauth:token-type:jwt','subjectToken':idt})
fed=jget(b,'access_token'); print('%s_STS http=%s ok=%s %s'%(TAG,c,bool(fed),'' if fed else cap(b,200)),flush=True)
if not fed: raise SystemExit(1)
c,b=http('https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/'+urllib.parse.quote(SA,safe='')+':generateAccessToken',method='POST',data={'scope':['https://www.googleapis.com/auth/cloud-platform']},headers={'Authorization':'Bearer '+fed})
at=jget(b,'accessToken'); print('%s_GAT http=%s ok=%s len=%d'%(TAG,c,bool(at),len(at or '')),flush=True)
if not at: raise SystemExit(1)
AH={'Authorization':'Bearer '+at}
def g(u,m='GET',d=None,timeout=90): return http(u,method=m,data=d,headers=AH,timeout=timeout)
REGIONS=['us-central1','us-east1','us-east4','us-west1','us-west2','europe-west2','europe-west4','asia-southeast1','asia-southeast2','asia-south1','asia-east1','australia-southeast1','northamerica-northeast1','asia-northeast1','asia-northeast3']
for reg in REGIONS:
    c,b=g('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/endpoints?pageSize=100'%(reg,PROJ_NUM,reg))
    eps=[]
    try: eps=json.loads(b).get('endpoints',[])
    except Exception: pass
    ours=[e for e in eps if 'i121576' in (e.get('displayName') or '')]
    if c!=200 or ours:
        print('%s_EP %s http=%s ours=%d all=%d'%(TAG,reg,c,len(ours),len(eps)),flush=True)
    for e in ours:
        dms=[{'dn':d.get('displayName'),'model':(d.get('model') or '').rsplit('/',1)[-1]} for d in (e.get('deployedModels') or [])]
        print('%s_EP_ROW %s %s id=%s deployed=%s'%(TAG,reg,e.get('displayName'),(e.get('name') or '').rsplit('/',1)[-1],cap(json.dumps(dms),300)),flush=True)
    c2,b2=g('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/models?pageSize=200'%(reg,PROJ_NUM,reg))
    try: ms=[m.get('displayName') for m in json.loads(b2).get('models',[]) if 'i121576' in (m.get('displayName') or '')]
    except Exception: ms=[]
    if ms: print('%s_MODELS %s n=%d %s'%(TAG,reg,len(ms),cap(json.dumps(ms),400)),flush=True)
# quota re-read for the 3 serving metrics
for metric in ('custom_model_serving_nvidia_rtx_pro_6000_gpus','custom_model_serving_nvidia_l4_gpus','custom_model_serving_nvidia_t4_gpus'):
    c,b=g('https://serviceusage.googleapis.com/v1beta1/projects/%s/services/aiplatform.googleapis.com/consumerQuotaMetrics?view=FULL&pageSize=200'%(PROJ_NUM,))
    break
# Cloud Logging
c,b=g('https://logging.googleapis.com/v2/entries:list',method='POST',data={'resourceNames':['projects/%s'%PROJ_NUM],'filter':'"C211_I121576"','orderBy':'timestamp asc','pageSize':300},timeout=90)
print('%s_LOGGING http=%s'%(TAG,c),flush=True)
n=0
if c==200:
    for e in (json.loads(b).get('entries') or []):
        t=e.get('textPayload') or (e.get('jsonPayload') or {}).get('message') or ''
        if not t: continue
        n+=1
        if n<=120: print('%s_LOG %s'%(TAG,cap(t.rstrip(),300)),flush=True)
print('%s_LOGLINES %d'%(TAG,n),flush=True)
c,b=g('https://us-central1-aiplatform.googleapis.com/v1/projects/%s/locations/us-central1/operations?pageSize=50'%(PROJ_NUM,))
print('%s_OPS http=%s %s'%(TAG,c,cap(jget(b,'operations'),600)),flush=True)
print('%s_DONE'%TAG,flush=True)
