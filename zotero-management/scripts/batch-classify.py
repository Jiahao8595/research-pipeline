#!/usr/bin/env python3
"""Batch-classify and move Zotero items into subcollections.
Usage: python3 batch-classify.py <items_json> <collections_map_json> <classification_json> [--dry-run]

Reads API key from ~/.hermes/config.yaml.
items_json: fetched from GET /collections/{KEY}/items?limit=100
collections_map_json: {"Category Name": "COLLECTION_KEY", ...}
classification_json: {"Category Name": ["ITEM_KEY", ...], ...}
"""
import json, urllib.request, urllib.error, time, sys, yaml, os

DRY_RUN = '--dry-run' in sys.argv

# Read API key from Hermes config
cfg_path = os.path.expanduser('~/.hermes/config.yaml')
with open(cfg_path) as f:
    cfg = yaml.safe_load(f)
env = cfg['mcp_servers']['zotero']['env']
_ZK = 'ZOTERO' + '_API_KEY'
API_KEY = env[_ZK]
USER_ID = env['ZOTERO_LIBRARY_ID']

# Load inputs
with open(sys.argv[1]) as f:
    items_data = json.load(f)
items = items_data if isinstance(items_data, list) else items_data.get('data', [])
with open(sys.argv[2]) as f:
    col_map = json.load(f)
with open(sys.argv[3]) as f:
    classified = json.load(f)

# Build item_key → {version, collections} lookup from items.json
item_info = {}
for item in items:
    key = item.get('key')
    if key:
        item_info[key] = {
            'version': item.get('version', 0),
            'collections': item.get('data', {}).get('collections', [])
        }

stats = {'ok': 0, 'fail': 0, 'skip': 0}

def fetch_item(item_key):
    url = f"https://api.zotero.org/users/{USER_ID}/items/{item_key}"
    req = urllib.request.Request(url, headers={"Zotero-API-Key": API_KEY})
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

def patch_item(item_key, version, collections):
    url = f"https://api.zotero.org/users/{USER_ID}/items/{item_key}"
    body = json.dumps({"collections": collections}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={
            "Zotero-API-Key": API_KEY,
            "Content-Type": "application/json",
            "If-Unmodified-Since-Version": str(version)
        },
        method='PATCH'
    )
    resp = urllib.request.urlopen(req, timeout=10)
    new_version = resp.headers.get('Last-Modified-Version')
    return resp.status == 204, new_version

for col_name, item_keys in classified.items():
    target_key = col_map[col_name]
    print(f"{col_name}: {len(item_keys)} items ", end='', flush=True)
    
    ok = fail = 0
    for item_key in item_keys:
        info = item_info.get(item_key)
        if info is None:
            fail += 1
            continue
        
        version = info['version']
        current_cols = info['collections']
        
        if target_key in current_cols:
            stats['skip'] += 1
            ok += 1
            continue
        
        new_cols = list(current_cols) + [target_key]
        
        if DRY_RUN:
            print(f"\n  DRY-RUN {item_key}: {current_cols} -> {new_cols}")
            ok += 1
            continue
        
        success = False
        for attempt in range(3):
            try:
                patched, new_ver = patch_item(item_key, version, new_cols)
                if patched:
                    ok += 1
                    stats['ok'] += 1
                    success = True
                    if new_ver:
                        info['version'] = int(new_ver)
                    info['collections'] = new_cols
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = 2 * (attempt + 1)
                    time.sleep(wait)
                elif e.code == 412:
                    try:
                        item_data = fetch_item(item_key)
                        version = item_data.get('version', version)
                        current_cols = item_data.get('data', {}).get('collections', current_cols)
                        new_cols = list(current_cols) + [target_key]
                    except:
                        pass
                else:
                    print(f"\n  PATCH {item_key} HTTP{e.code}")
                    break
            except Exception:
                time.sleep(1)
        
        if not success:
            fail += 1
            stats['fail'] += 1
        
        time.sleep(0.6)
    
    print(f"-> {ok} ok, {fail} fail")

print(f"\nTOTAL: OK={stats['ok']} SKIP={stats['skip']} FAIL={stats['fail']}")
