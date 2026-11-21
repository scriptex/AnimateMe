#!/usr/bin/env python3
"""c211-i121677 lean readback v3 for the civil-epigram-370317 Vertex mass-fill.

Bulk read: ONE paged entries:list query over resource.type=CustomJob with a
timestamp window, grouped locally by resource.labels.job_id. Far fewer API calls
than per-job queries (which intermittently return 401/429). Re-mints the access
token once on 401.

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
WINDOW_MIN = int(os.environ.get('C211_WINDOW_MIN', '25'))
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


def mint():
    base = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL')
    tok = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN')
    if not base or not tok:
        return None, 'NO_ACTIONS_ENV'
    u = base + ('&' if '?' in base else '?') + 'audience=' + urllib.parse.quote(AUD, safe='')
    last = ''
    for attempt in (1, 2, 3):
        c, b = http(u, headers={'Authorization': 'Bearer ' + tok}, timeout=30)
        idt = jget(b, 'value')
        print('%s_MINT_OIDC attempt=%d http=%s ok=%s' % (TAG, attempt, c, bool(idt)), flush=True)
        if not idt:
            print('%s_MINT_OIDC_BODY %s' % (TAG, repr(b)[:240]), flush=True)
            last = b
            time.sleep(3)
            continue
        c, b = http('https://sts.googleapis.com/v1/token', method='POST', data={
            'audience': AUD,
            'grantType': 'urn:ietf:params:oauth:grant-type:token-exchange',
            'requestedTokenType': 'urn:ietf:params:oauth:token-type:access_token',
            'scope': 'https://www.googleapis.com/auth/cloud-platform',
            'subjectTokenType': 'urn:ietf:params:oauth:token-type:jwt',
            'subjectToken': idt}, timeout=40)
        fed = jget(b, 'access_token')
        print('%s_MINT_STS attempt=%d http=%s ok=%s' % (TAG, attempt, c, bool(fed)), flush=True)
        if not fed:
            print('%s_MINT_STS_BODY %s' % (TAG, repr(b)[:240]), flush=True)
            last = b
            time.sleep(3)
            continue
        c, b = http('https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/'
                    + urllib.parse.quote(SA, safe='') + ':generateAccessToken', method='POST',
                    data={'scope': ['https://www.googleapis.com/auth/cloud-platform']},
                    headers={'Authorization': 'Bearer ' + fed}, timeout=40)
        at = jget(b, 'accessToken')
        print('%s_GAT attempt=%d http=%s ok=%s len=%d expire=%s'
              % (TAG, attempt, c, bool(at), len(at or ''), jget(b, 'expireTime')), flush=True)
        if at:
            return at, b
        print('%s_GAT_BODY %s' % (TAG, repr(b)[:240]), flush=True)
        last = b
        time.sleep(3)
    return None, last


def main():
    at, raw = mint()
    if not at:
        print('%s_NO_TOKEN %s' % (TAG, repr(raw)[:300]), flush=True)
        return

    def q(body):
        nonlocal at
        for attempt in (1, 2, 3):
            c, b = http('https://logging.googleapis.com/v2/entries:list', method='POST',
                        data=body, headers={'Authorization': 'Bearer ' + at}, timeout=90)
            if c == 200:
                return c, b
            print('%s_QHTTP http=%s attempt=%d body=%s' % (TAG, c, attempt, repr(b)[:220]), flush=True)
            if c == 401 and attempt < 3:
                n_at, _ = mint()
                if n_at:
                    at = n_at
                    continue
            time.sleep(2)
        return c, b

    # 1) list jobs per region (cheap, parallel)
    def list_region(region):
        c, b = http('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/customJobs?pageSize=100'
                    % (region, PROJ_NUM, region), headers={'Authorization': 'Bearer ' + at}, timeout=60)
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

    # 2) accumulate all running jobs onto the map keyed by (region, job)
    rowmap = {}
    for j in jobs:
        j['device'] = []
        j['ready'] = []
        j['shares'] = []
        j['hb'] = []
        j['fallback'] = []
        j['tail'] = []
        j['n_lines'] = 0
        j['log_http'] = 'BULK'
        rowmap[(j['region'], j['job'])] = j
    by_id = {j['job']: j for j in jobs}

    # 3) one paged bulk query over the CustomJob log stream
    cutoff = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() - WINDOW_MIN * 60))
    body = {'resourceNames': ['projects/%s' % PROJ_NUM],
            'filter': ('resource.type="aiplatform.googleapis.com/CustomJob" AND timestamp>="%s"' % cutoff),
            'orderBy': 'timestamp desc', 'pageSize': 1000}
    entries = []
    pages = 0
    while True:
        c, b = q(body)
        pages += 1
        if c != 200:
            print('%s_BULK_FAIL http=%s body=%s' % (TAG, c, repr(b)[:300]), flush=True)
            break
        d = json.loads(b)
        es = d.get('entries') or []
        entries.extend(es)
        print('%s_BULK page=%d http=%s entries=%d cutoff=%s' % (TAG, pages, c, len(es), cutoff), flush=True)
        tok = d.get('nextPageToken')
        if not tok or pages >= 6:
            break
        body['pageToken'] = tok

    # 4) group locally
    for e in entries:
        lbl = ((e.get('resource') or {}).get('labels') or {})
        jid = lbl.get('job_id') or ''
        region = lbl.get('location') or ''
        t = e.get('textPayload') or ''
        row = by_id.get(jid)
        if row is None or not t:
            continue
        t = t.rstrip()
        row['n_lines'] += 1
        if '_DEVICE ' in t or '_NO_GPU' in t:
            row['device'].append(t)
        if '_WR_READY' in t or '_WR_TGZ_BAD' in t or '_WR_DL_FAIL' in t:
            row['ready'].append(t)
        if 'accepted' in t.lower():
            row['shares'].append(t)
        if '_HB ' in t:
            row['hb'].append(t)
        if '_FALLBACK' in t or '_SRB_START' in t or '_PH_START' in t:
            row['fallback'].append(t)
        row['tail'].append(t)

    for j in jobs:
        j['hb'] = j['hb'][-3:]
        j['tail'] = j['tail'][-4:]
        print('%s_JOB %s' % (TAG, json.dumps(j, separators=(',', ':'))), flush=True)
    dev = [j for j in jobs if j.get('device')]
    print('%s_TOTAL jobs=%d with_device=%d with_shares=%d entries=%d pages=%d t=%.1fs'
          % (TAG, len(jobs), len(dev), len([j for j in jobs if j.get('shares')]), len(entries), pages,
             time.time() - t0), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('%s_FATAL %r' % (TAG, e), flush=True)
        raise
