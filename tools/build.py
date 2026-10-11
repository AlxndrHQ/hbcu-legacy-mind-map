#!/usr/bin/env python3
"""Merge sources/*.json into data.json and embed it in index.html.

Usage:  python3 tools/build.py            # build
        python3 tools/build.py --check    # validate only, print problems

Records with the same id are merged (richest record wins, connections are unioned).
Connections to unknown ids are reported and dropped.
"""
import json, re, sys, glob, os, difflib, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'sources')
CATS = {'Founders & Owners', 'Corporate Executives', 'Finance & Investors', 'Media & Entertainment',
        'Science & Medicine', 'Public Service', 'Arts & Athletics'}
TIERS = {'Undisclosed', '$500K-$5M', '$5M-$100M', '$100M-$500M', '$500M-$1B', '$1B+'}
EDGES = {'member', 'alumni', 'ownership', 'executive', 'supply', 'capital', 'board', 'mentorship', 'civic', 'family',
         'deal', 'origin', 'lineage', 'faculty', 'parallel'}
STATUS = {'Operating', 'Closed', 'Merged'}
# the same person or school recorded under two ids: alias -> canonical
ALIASES = {'william-alexander-scott-ii': 'william-a-scott-ii'}


def gics_subs():
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    block = html[html.index('const GICS = {'):html.index('};', html.index('const GICS = {'))]
    return set(re.findall(r"^\s*'([^']+)':\[", block, re.M))


def namekey(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\b(dr|rev)\b\.?', '', s)          # keep Jr./Sr./III: they are different people
    s = re.sub(r'\b(junior)\b', 'jr', s)
    s = re.sub(r'\b[a-z]\.', '', s)              # middle initials
    return re.sub(r'[^a-z]', '', s)


def entkey(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower().replace('&', ' and ')
    s = re.sub(r'\b(of|the|at|inc|llc|corp|corporation|company|co)\b', ' ', s)
    return 'E:' + re.sub(r'[^a-z]', '', s)


def richness(r):
    return len(json.dumps(r))


def main():
    check = '--check' in sys.argv
    problems = []
    recs = {}
    files = sorted(glob.glob(os.path.join(SRC, '*.json')))
    for f in files:
        try:
            arr = json.load(open(f, encoding='utf-8'))
        except Exception as e:
            problems.append(f'{os.path.basename(f)}: invalid JSON: {e}')
            continue
        for r in arr:
            if not isinstance(r, dict) or not r.get('id'):
                continue
            r['id'] = ALIASES.get(r['id'], r['id'])
            r.setdefault('connections', [])
            r['_file'] = os.path.basename(f)
            cur = recs.get(r['id'])
            if cur is None:
                recs[r['id']] = r
                continue
            keep, other = (r, cur) if richness(r) > richness(cur) else (cur, r)
            have = {c['id'] for c in keep['connections'] if isinstance(c, dict)}
            keep['connections'] += [c for c in other['connections'] if isinstance(c, dict) and c['id'] not in have]
            if keep.get('hbcu') or other.get('hbcu'):
                keep['hbcu'] = True
            recs[r['id']] = keep

    # people listed twice under different ids (e.g. with/without a middle initial)
    alias = dict(ALIASES)
    seen = {}
    for r in list(recs.values()):
        if r['id'] not in recs:
            continue
        if r.get('type') == 'entity':   # schools/companies: same name modulo "of"/"the"/punctuation
            k = entkey(r['name'])
        else:
            k = namekey(r['name'])
        born = lambda x: (re.findall(r'\d{4}', x.get('lifespan') or '') or [None])[0]
        if k in seen and seen[k] != r['id'] and r.get('type') != 'entity' and None not in (born(r), born(recs[seen[k]])) and born(r) != born(recs[seen[k]]):
            problems.append(f'same name, different people (birth years differ): {seen[k]} / {r["id"]}')
            continue
        if k in seen and seen[k] != r['id']:
            a, b = recs[seen[k]], r
            keep, drop = (a, b) if richness(a) >= richness(b) else (b, a)
            have = {c['id'] for c in keep['connections']}
            keep['connections'] += [c for c in drop['connections'] if c['id'] not in have]
            alias[drop['id']] = keep['id']
            del recs[drop['id']]
            seen[k] = keep['id']
            problems.append(f'merged duplicate person {drop["id"]} -> {keep["id"]}')
        else:
            seen[k] = r['id']

    ids = set(recs)
    hbcu_ids = [i for i, r in recs.items() if r.get('hbcu')]
    subs = gics_subs()
    for r in recs.values():
        conns, cseen = [], set()
        for c in r['connections']:
            if isinstance(c, str):
                c = {'id': c}
            cid = alias.get(c.get('id'), c.get('id'))
            if cid not in ids:
                guess = difflib.get_close_matches(cid, hbcu_ids if c.get('type') in ('alumni', 'lineage', 'faculty') else ids, n=1, cutoff=0.82)
                if guess:
                    problems.append(f'{r["id"]}: "{cid}" -> fixed to "{guess[0]}"')
                    cid = guess[0]
                else:
                    problems.append(f'{r["id"]}: unknown connection "{cid}" dropped ({r["_file"]})')
                    continue
            if cid == r['id'] or cid in cseen:
                continue
            cseen.add(cid)
            c['id'] = cid
            if c.get('type') not in EDGES:
                c['type'] = 'civic' if c.get('type') else 'origin'
            conns.append(c)
        r['connections'] = conns
        if r.get('type') == 'entity':
            if r.get('hbcu'):
                if r.get('status') not in STATUS:
                    problems.append(f'{r["id"]}: bad status {r.get("status")!r}')
                r.setdefault('gics', {'sub': 'Non-market', 'basis': 'inferred'})
            sub = (r.get('gics') or {}).get('sub')
            if sub and sub not in subs:
                m = difflib.get_close_matches(sub, list(subs), n=1, cutoff=0.6)
                problems.append(f'{r["id"]}: gics "{sub}" -> {m[0] if m else "Non-market"}')
                r['gics']['sub'] = m[0] if m else 'Non-market'
        else:
            r['type'] = 'alumni'
            if r.get('category') not in CATS:
                problems.append(f'{r["id"]}: bad category {r.get("category")!r}')
            if r.get('netWorthTier') not in TIERS:
                problems.append(f'{r["id"]}: bad tier {r.get("netWorthTier")!r} -> Undisclosed')
                r['netWorthTier'] = 'Undisclosed'
            if not any(c['type'] == 'alumni' and recs[c['id']].get('hbcu') for c in r['connections']):
                problems.append(f'{r["id"]}: no alumni link to an HBCU')

    # drop companies nobody links to
    linked = {c['id'] for r in recs.values() for c in r['connections']}
    for i in [i for i, r in recs.items() if r.get('type') == 'entity' and not r.get('hbcu') and not r.get('network')
              and i not in linked and not r['connections']]:
        problems.append(f'dropped orphan entity {i}')
        del recs[i]

    order = {'hbcu': 0, 'net': 1, 'alumni': 2, 'entity': 3}
    kind = lambda r: 'hbcu' if r.get('hbcu') else 'net' if r.get('network') else 'alumni' if r.get('type') != 'entity' else 'entity'
    out = sorted(recs.values(), key=lambda r: (order[kind(r)], r.get('state', ''), r['name']))
    for r in out:
        r.pop('_file', None)

    for p in problems:
        print('  ' + p)
    n = {k: sum(kind(r) == k for r in out) for k in order}
    print(f'{len(out)} records: {n["hbcu"]} HBCUs, {n["net"]} networks, {n["alumni"]} alumni, {n["entity"]} companies/entities')
    if check:
        return
    data = json.dumps(out, indent=1, ensure_ascii=False)
    open(os.path.join(ROOT, 'data.json'), 'w', encoding='utf-8').write(data + '\n')
    path = os.path.join(ROOT, 'index.html')
    html = open(path, encoding='utf-8').read()
    a, b = html.index('/*DATA-START*/') + len('/*DATA-START*/'), html.index('/*DATA-END*/')
    open(path, 'w', encoding='utf-8').write(html[:a] + data.replace('</', '<\\/') + html[b:])
    print('wrote data.json and index.html')


if __name__ == '__main__':
    main()
