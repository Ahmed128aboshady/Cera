import urllib.request
import json
import http.cookiejar

cj_old = http.cookiejar.CookieJar()
opener_old = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_old))
auth_payload_old = {'jsonrpc': '2.0', 'params': {'db': 'cera-store-20260803', 'login': 'draboueldahab@cerastoreeg.com', 'password': 'Tito@1582020'}}
opener_old.open(urllib.request.Request('https://cera-store-20260803.odoo.com/web/session/authenticate', data=json.dumps(auth_payload_old).encode('utf-8'), headers={'Content-Type': 'application/json'}))

def call_old(model, method, args=[], kwargs={}):
    url = 'https://cera-store-20260803.odoo.com/web/dataset/call_kw'
    if 'context' not in kwargs: kwargs['context'] = {'allowed_company_ids': [1, 2, 3]}
    payload = {'jsonrpc': '2.0', 'params': {'model': model, 'method': method, 'args': args, 'kwargs': kwargs}}
    r = opener_old.open(urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}))
    return json.loads(r.read().decode()).get('result', [])

old_tmpls = call_old('product.template', 'search_read', [[]], {'fields': ['id', 'name', 'barcode', 'company_id']})
old_cairo_bcs = set([p['barcode'] for p in old_tmpls if p.get('barcode') and p.get('company_id') and p['company_id'][0] == 3])
old_wh_bcs = set([p['barcode'] for p in old_tmpls if p.get('barcode') and p.get('company_id') and p['company_id'][0] == 2])
print(f"Old DB: Cairo Barcodes = {len(old_cairo_bcs)}, Warehouse Barcodes = {len(old_wh_bcs)}")

cj_live = http.cookiejar.CookieJar()
opener_live = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_live))
auth_payload_live = {'jsonrpc': '2.0', 'params': {'db': 'cera-store', 'login': 'draboueldahab@cerastoreeg.com', 'password': 'Tito@1582020'}}
opener_live.open(urllib.request.Request('https://cera-store.odoo.com/web/session/authenticate', data=json.dumps(auth_payload_live).encode('utf-8'), headers={'Content-Type': 'application/json'}))

def call_live(model, method, args=[], kwargs={}):
    url = 'https://cera-store.odoo.com/web/dataset/call_kw'
    if 'context' not in kwargs: kwargs['context'] = {'allowed_company_ids': [1, 2, 3, 4, 5]}
    payload = {'jsonrpc': '2.0', 'params': {'model': model, 'method': method, 'args': args, 'kwargs': kwargs}}
    r = opener_live.open(urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}))
    res = json.loads(r.read().decode())
    return res.get('result', [])

live_prods = call_live('product.template', 'search_read', [[['company_id', '=', False]]], {'fields': ['id', 'barcode']})
print(f"Found {len(live_prods)} open products in Live DB")

cairo_update_ids = [p['id'] for p in live_prods if p.get('barcode') and p['barcode'] in old_cairo_bcs]
wh_update_ids = [p['id'] for p in live_prods if p.get('barcode') and p['barcode'] in old_wh_bcs]

print(f"Assigning {len(cairo_update_ids)} products to Cairo (C3)...")
for i in range(0, len(cairo_update_ids), 100):
    call_live('product.template', 'write', [cairo_update_ids[i:i+100], {'company_id': 3}])

print(f"Assigning {len(wh_update_ids)} products to Warehouse (C2)...")
for i in range(0, len(wh_update_ids), 100):
    call_live('product.template', 'write', [wh_update_ids[i:i+100], {'company_id': 2}])

print('\n=== Final Counts per Company ===')
for c_id, c_name in [(5, 'CERA Store Asyut C002'), (4, 'CERA Store Minya C003'), (3, 'First Store Cairo'), (2, 'Cerameda Warehouse'), (1, 'CERA Store Asyut C001')]:
    ctx = {'allowed_company_ids': [c_id]}
    res = call_live('product.template', 'search_count', [[]], {'context': ctx})
    res_s = call_live('product.template', 'search_count', [[['sale_ok', '=', True]]], {'context': ctx})
    print(f"{c_name} (ID {c_id}): Total = {res}, [Sales] = {res_s}")
