#!/usr/bin/env python3
"""c211-i121677 lean readback for the civil-epigram-370317 Vertex mass-fill.

Fast variant of readback.py: region listing and per-job Logging queries run in
parallel, each job gets ONE immediate retry when entries:list returns empty
(fact 121656: first query for a filter is empty, immediate retry has content).

Read-only. Prints C211_I121535_DBG_JOB <json> per job (same shape cards.py parses).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

AUD = ('//iam.googleapis.com/projects/284735288225/locations/global/'
       'workloadIdentityPools/my-pool/providers/my-provider')
SA = 'sa-gcloud-cli@civil-epigram-370317.iam.gserviceaccount.com'
PROJ_NUM = '284735288225'
NONCE = 'i121377'
TAG = 'C211_I121535_DBG'
REGIONS = ['us-central1', 'us-east1', 'us-west1', 'europe-west2', 'europe-west4',
           'asia-northeast1', 'asia-northeast3', 'asia-south1', 'asia-southeast1',
           'asia-east1', 'australia-southeast1', 'northamerica-northeast1',
           'us-east4', 'us-west2']


def http(url, method='GET', data=None, headers=None, timeout=60):
    h = {'User-Agent': 'c211-i121677'}
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
        try:
            return e.code, e.read().decode('utf-8', 'replace')
        except Exception:
            return e.code, ''
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
    c, b = http('https://sts.googleapis.com/v1/token', method='POST', data={
        'audience': AUD,
        'grantType': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'requestedTokenType': 'urn:ietf:params:oauth:token-type:access_token',
        'scope': 'https://www.googleapis.com/auth/cloud-platform',
        'subjectTokenType': 'urn:ietf:params:oauth:token-type:jwt',
        'subjectToken': idt}, timeout=40)
    fed = jget(b, 'access_token')
    c, b = http('https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/'
                + urllib.parse.quote(SA, safe='') + ':generateAccessToken', method='POST',
                data={'scope': ['https://www.googleapis.com/auth/cloud-platform']},
                headers={'Authorization': 'Bearer ' + fed}, timeout=40)
    at = jget(b, 'accessToken')
    print('%s_GAT http=%s ok=%s len=%d' % (TAG, c, bool(at), len(at or '')), flush=True)
    if not at:
        print('%s_NO_TOKEN %s' % (TAG, repr(b)[:300]), flush=True)
        return
    AH = {'Authorization': 'Bearer ' + at}

    def list_region(region):
        c, b = http('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/customJobs?pageSize=100'
                    % (region, PROJ_NUM, region), headers=AH, timeout=60)
        jobs = []
        if c == 200:
            try:
                jobs = json.loads(b).get('customJobs', [])
            except Exception:
                jobs = []
        ours = [j for j in jobs if NONCE in (j.get('displayName') or '')]
        print('%s_LIST %s http=%s total=%d ours=%d' % (TAG, region, c, len(jobs), len(ours)), flush=True)
        out = []
        for j in ours:
            jn = j.get('name', '')
            out.append({'region': region, 'job': jn.rsplit('/', 1)[-1],
                        'displayName': j.get('displayName'), 'state': j.get('state')})
        return out

    t0 = time.time()
    jobs = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for res in ex.map(list_region, REGIONS):
            jobs.extend(res)
    print('%s_LISTED total_ours=%d t=%.1fs' % (TAG, len(jobs), time.time() - t0), flush=True)

    _lock = __import__('threading').Lock()
    _last = [0.0]

    def _pace():
        # Logging API quota: keep <= ~55 entries:list calls per minute
        with _lock:
            now = time.time()
            wait = 1.1 - (now - _last[0])
            _last[0] = max(now, _last[0] + 1.1)
        if wait > 0:
            time.sleep(wait)

    def read_job(row):
        jid = row['job']
        if row.get('state') != 'JOB_STATE_RUNNING':
            out = dict(row)
            out.update({'log_http': 'SKIP_NOT_RUNNING', 'n_lines': 0, 'tries': 0,
                        'device': [], 'ready': [], 'shares': [], 'hb': [],
                        'fallback': [], 'tail': []})
            return out

        def q(page=400):
            return http('https://logging.googleapis.com/v2/entries:list', method='POST',
                        data={'resourceNames': ['projects/%s' % PROJ_NUM],
                              'filter': 'resource.labels.job_id="%s"' % jid,
                              'orderBy': 'timestamp asc', 'pageSize': page},
                        headers=AH, timeout=60)

        tries = 0
        lines = []
        lc = None
        for tries in (1, 2):
            _pace()
            lc, lb = q()
            if lc == 200:
                try:
                    for e in (json.loads(lb).get('entries') or []):
                        t = e.get('textPayload') or ''
                        if t:
                            lines.append(t.rstrip())
                except Exception:
                    pass
            if lines or lc == 429:
                break
            time.sleep(0.5)
        out = dict(row)
        out['log_http'] = lc
        out['n_lines'] = len(lines)
        out['tries'] = tries
        out['device'] = [x for x in lines if '_DEVICE ' in x or '_NO_GPU' in x]
        out['ready'] = [x for x in lines if '_WR_READY' in x or '_WR_TGZ_BAD' in x or '_WR_DL_FAIL' in x]
        out['shares'] = [x for x in lines if 'accepted' in x.lower()]
        out['hb'] = [x for x in lines if '_HB ' in x][-3:]
        out['fallback'] = [x for x in lines if '_FALLBACK' in x or '_SRB_START' in x or '_PH_START' in x]
        out['tail'] = lines[-4:]
        return out

    rows = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(read_job, jobs):
            rows.append(r)
            print('%s_JOB %s' % (TAG, json.dumps(r, separators=(',', ':'))), flush=True)
    dev = [r for r in rows if r.get('device')]
    print('%s_TOTAL jobs=%d with_device=%d with_shares=%d t=%.1fs'
          % (TAG, len(rows), len(dev), len([r for r in rows if r.get('shares')]), time.time() - t0), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('%s_FATAL %r' % (TAG, e), flush=True)
        raise
