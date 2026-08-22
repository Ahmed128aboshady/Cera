import urllib.request
import json
import http.cookiejar
from collections import Counter

cj_live = http.cookiejar.CookieJar()
opener_live = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_live))
auth_payload_live = {'jsonrpc': '2.0', 'params': {'db': 'cera-store', 'login': 'draboueldahab@cerastoreeg.com', 'password': 'Tito@1582020'}}
opener_live.open(urllib.request.Request('https://cera-store.odoo.com/web/session/authenticate', data=json.dumps(auth_payload_live).encode('utf-8'), headers={'Content-Type': 'application/json'}))

def call_live(model, method, args=[], kwargs={}):
    url = 'https://cera-store.odoo.com/web/dataset/call_kw'
    if 'context' not in kwargs: kwargs['context'] = {'allowed_company_ids': [5]}
    payload = {'jsonrpc': '2.0', 'params': {'model': model, 'method': method, 'args': args, 'kwargs': kwargs}}
    r = opener_live.open(urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}))
    return json.loads(r.read().decode())

# Fetch all products in Company 5
prods = call_live('product.product', 'search_read', [[['company_id', '=', 5]]], {'fields': ['id', 'barcode', 'default_code', 'name', 'list_price']}).get('result', [])
print(f"Total Products in C002: {len(prods)}")

# 1. Duplicate Barcodes
barcodes = [p['barcode'] for p in prods if p.get('barcode')]
bc_counts = Counter(barcodes)
dup_bcs = {bc: count for bc, count in bc_counts.items() if count > 1}

# 2. Duplicate Internal References (default_code)
codes = [p['default_code'] for p in prods if p.get('default_code')]
code_counts = Counter(codes)
dup_codes = {code: count for code, count in code_counts.items() if count > 1}

# 3. Duplicate Names
names = [p['name'] for p in prods if p.get('name')]
name_counts = Counter(names)
dup_names = {name: count for name, count in name_counts.items() if count > 1}

print(f"\n1. Duplicate Barcodes in C002: {len(dup_bcs)}")
for bc, count in list(dup_bcs.items())[:10]:
    sample_prods = [p for p in prods if p.get('barcode') == bc]
    print(f"   Barcode '{bc}' repeated {count} times -> IDs: {[p['id'] for p in sample_prods]}")

print(f"\n2. Duplicate Internal Codes in C002: {len(dup_codes)}")
for code, count in list(dup_codes.items())[:10]:
    sample_prods = [p for p in prods if p.get('default_code') == code]
    print(f"   Code '{code}' repeated {count} times -> IDs: {[p['id'] for p in sample_prods]}")

print(f"\n3. Duplicate Names in C002: {len(dup_names)}")
for name, count in list(dup_names.items())[:10]:
    sample_prods = [p for p in prods if p.get('name') == name]
    print(f"   Name '{name}' repeated {count} times -> IDs: {[p['id'] for p in sample_prods]}")
