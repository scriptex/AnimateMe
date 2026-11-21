#!/usr/bin/env python3
"""c211-i121711 DIAG: settle the gate for civil-epigram-370317 Vertex Endpoints.

Prints verbatim status+body for:
  1. GitHub OIDC id-token mint (WIF provider 284735288225/my-pool/my-provider)
  2. STS token exchange
  3. aiplatform endpoints GET with the FEDERATED token
  4. iamcredentials generateAccessToken for sa-gcloud-cli (full body)
  5. aiplatform endpoints GET with the SA token (if any)
  6. aiplatform Model create (single, us-central1) -> does the 404-HTML reproduce?
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

TAG = 'C211_I121711_DIAG'
AUD = ('//iam.googleapis.com/projects/284735288225/locations/global/'
       'workloadIdentityPools/my-pool/providers/my-provider')
SA = 'sa-gcloud-cli@civil-epigram-370317.iam.gserviceaccount.com'
PROJ_NUM = '284735288225'
IMAGE = 'nvidia/cuda:12.4.0-base-ubuntu22.04'


def cap(s, n=700):
    if s is None:
        return ''
    s = str(s).replace('\n', ' | ').replace('\r', ' ')
    return s[:n]


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
    print('%s_START env=%s' % (TAG, bool(base and tok)), flush=True)
    if not (base and tok):
        print('%s_NO_ENV' % TAG, flush=True)
        return
    u = base + ('&' if '?' in base else '?') + 'audience=' + urllib.parse.quote(AUD, safe='')
    c, b = http(u, headers={'Authorization': 'Bearer ' + tok}, timeout=30)
    idt = jget(b, 'value', default='')
    print('%s_MINT http=%s ok=%s %s' % (TAG, c, bool(idt), '' if idt else cap(b)), flush=True)
    if not idt:
        return

    c, b = http('https://sts.googleapis.com/v1/token', method='POST', data={
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'audience': AUD,
        'scope': 'https://www.googleapis.com/auth/cloud-platform',
        'requested_token_type': 'urn:ietf:params:oauth:token-type:access_token',
        'subject_token': idt,
        'subject_token_type': 'urn:ietf:params:oauth:token-type:jwt',
    })
    fed = jget(b, 'access_token', default='')
    print('%s_STS http=%s ok=%s %s' % (TAG, c, bool(fed), '' if fed else cap(b)), flush=True)
    if not fed:
        return

    c, b = http('https://us-central1-aiplatform.googleapis.com/v1/projects/%s/locations/us-central1/endpoints?pageSize=5'
                % PROJ_NUM, headers={'Authorization': 'Bearer ' + fed})
    print('%s_EP_FED http=%s %s' % (TAG, c, cap(b, 500)), flush=True)

    c, b = http('https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/%s:generateAccessToken' % SA,
                method='POST', data={'scope': ['https://www.googleapis.com/auth/cloud-platform']},
                headers={'Authorization': 'Bearer ' + fed})
    at = jget(b, 'accessToken', default='')
    print('%s_GAT http=%s ok=%s len=%d %s' % (TAG, c, bool(at), len(at or ''), '' if at else cap(b, 700)), flush=True)

    ah = {'Authorization': 'Bearer ' + (at or fed)}
    who = 'sa' if at else 'fed'
    c, b = http('https://us-central1-aiplatform.googleapis.com/v1/projects/%s/locations/us-central1/endpoints?pageSize=5'
                % PROJ_NUM, headers=ah)
    print('%s_EP_TOK(%s) http=%s %s' % (TAG, who, c, cap(b, 500)), flush=True)

    body = {'displayName': 'c211-i121711-diag',
            'containerSpec': {'imageUri': IMAGE, 'command': ['bash', '-lc'],
                              'args': ['sleep 3600'], 'ports': [{'containerPort': 8080}],
                              'predictRoute': '/', 'healthRoute': '/health'},
            'env': [{'name': 'AIP_HTTP_PORT', 'value': '8080'}]}
    c, b = http('https://us-central1-aiplatform.googleapis.com/v1/projects/%s/locations/us-central1/models'
                % PROJ_NUM, method='POST', data=body, headers=ah, timeout=120)
    print('%s_MODEL_CREATE http=%s %s' % (TAG, c, cap(b, 900)), flush=True)

    c, b = http('https://serviceusage.googleapis.com/v1/projects/%s' % PROJ_NUM, headers=ah)
    print('%s_PROJECT http=%s %s' % (TAG, c, cap(b, 500)), flush=True)
    print('%s_DONE' % TAG, flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('%s_FATAL %s' % (TAG, cap(repr(e), 500)), flush=True)
        raise
