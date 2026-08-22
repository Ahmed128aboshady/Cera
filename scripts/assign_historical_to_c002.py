import urllib.request
import json
import http.cookiejar
import os

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

auth_url = 'https://cera-store.odoo.com/web/session/authenticate'
auth_payload = {
    'jsonrpc': '2.0',
    'params': {
        'db': 'cera-store',
        'login': 'draboueldahab@cerastoreeg.com',
        'password': 'Tito@1582020'
    }
}

req = urllib.request.Request(auth_url, data=json.dumps(auth_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
resp = opener.open(req)
auth_data = json.loads(resp.read().decode())
print("Authenticated successfully as:", auth_data['result']['name'])

all_company_ids = [1, 2, 3, 4, 5]

def call_kw(model, method, args=[], kwargs={}):
    url = 'https://cera-store.odoo.com/web/dataset/call_kw'
    if 'context' not in kwargs:
        kwargs['context'] = {'allowed_company_ids': all_company_ids}
    else:
        kwargs['context']['allowed_company_ids'] = all_company_ids
    payload = {
        'jsonrpc': '2.0',
        'params': {
            'model': model,
            'method': method,
            'args': args,
            'kwargs': kwargs
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    r = opener.open(req)
    res = json.loads(r.read().decode())
    return res.get('result', [])

cutoff_date = '2026-08-03 00:00:00'

# 1. Asyut POS Orders before Aug 3 -> set company_id = 5 (C002)
print("\n--- Assigning Asyut POS orders before 2026-08-03 to Company 5 (C002) ---")
asyut_orders_hist = call_kw('pos.order', 'search', [[['config_id', 'in', [1, 2, 9]], ['date_order', '<', cutoff_date]]])
print(f"Total historical Asyut orders before {cutoff_date}: {len(asyut_orders_hist)}")

batch_size = 500
for i in range(0, len(asyut_orders_hist), batch_size):
    batch = asyut_orders_hist[i:i + batch_size]
    res = call_kw('pos.order', 'write', [batch, {'company_id': 5}])
    print(f"Updated orders {i} to {min(i + batch_size, len(asyut_orders_hist))}: {res}")

# 2. Asyut POS Sessions before Aug 3 -> set company_id = 5 (C002)
print("\n--- Assigning Asyut POS sessions before 2026-08-03 to Company 5 (C002) ---")
asyut_sessions_hist = call_kw('pos.session', 'search', [[['config_id', 'in', [1, 2, 9]], ['start_at', '<', cutoff_date]]])
print(f"Total historical Asyut sessions before {cutoff_date}: {len(asyut_sessions_hist)}")

for i in range(0, len(asyut_sessions_hist), batch_size):
    batch = asyut_sessions_hist[i:i + batch_size]
    res = call_kw('pos.session', 'write', [batch, {'company_id': 5}])
    print(f"Updated sessions {i} to {min(i + batch_size, len(asyut_sessions_hist))}: {res}")

# 3. Verify ALL companies POS order counts
print("\n================ COMPREHENSIVE VERIFICATION ================")
companies = call_kw('res.company', 'search_read', [[], ['id', 'name']])
for comp in companies:
    c_id = comp['id']
    c_name = comp['name']
    total_orders = call_kw('pos.order', 'search_count', [[['company_id', '=', c_id]]])
    orders_pre = call_kw('pos.order', 'search_count', [[['company_id', '=', c_id], ['date_order', '<', cutoff_date]]])
    orders_post = call_kw('pos.order', 'search_count', [[['company_id', '=', c_id], ['date_order', '>=', cutoff_date]]])
    print(f"Company {c_id} ({c_name}):")
    print(f"   Total Orders: {total_orders} | Pre-Aug03: {orders_pre} | Post-Aug03: {orders_post}")
print("============================================================")
