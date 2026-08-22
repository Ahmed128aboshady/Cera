import urllib.request
import json
import http.cookiejar

print("=== Starting Archive of Dummy Imported Products Created on Aug 21 ===")

cj_live = http.cookiejar.CookieJar()
opener_live = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_live))
auth_payload_live = {'jsonrpc': '2.0', 'params': {'db': 'cera-store', 'login': 'draboueldahab@cerastoreeg.com', 'password': 'Tito@1582020'}}
opener_live.open(urllib.request.Request('https://cera-store.odoo.com/web/session/authenticate', data=json.dumps(auth_payload_live).encode('utf-8'), headers={'Content-Type': 'application/json'}))

def call_live(model, method, args=[], kwargs={}):
    url = 'https://cera-store.odoo.com/web/dataset/call_kw'
    if 'context' not in kwargs: kwargs['context'] = {'allowed_company_ids': [1, 2, 3, 4, 5]}
    payload = {'jsonrpc': '2.0', 'params': {'model': model, 'method': method, 'args': args, 'kwargs': kwargs}}
    r = opener_live.open(urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}))
    return json.loads(r.read().decode())

# Find all dummy product templates created on 21 Aug with numeric names or company_id=5
dummy_tmpls = call_live('product.template', 'search', [[['company_id', '=', 5], ['create_date', '>=', '2026-08-21 00:00:00'], ['active', '=', True]]]).get('result', [])
print(f"Found {len(dummy_tmpls)} dummy product templates to archive")

batch_size = 500
archived_count = 0
for i in range(0, len(dummy_tmpls), batch_size):
    batch = dummy_tmpls[i:i + batch_size]
    res = call_live('product.template', 'write', [batch, {'active': False}])
    archived_count += len(batch)
    print(f"Archived batch {i//batch_size + 1}: {len(batch)} templates")

print(f"\nSuccessfully archived {archived_count} dummy products!")

# Verify active real products in DB
active_real_prods = call_live('product.template', 'search_count', [[['active', '=', True], ['available_in_pos', '=', True]]]).get('result')
print(f"Active Real Products Available in POS: {active_real_prods}")
