import urllib.request
import json
import http.cookiejar

# 1. Connect to backup database
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

old_orders = call_old('pos.order', 'search', [[['company_id', '=', 1]]])
old_sessions = call_old('pos.session', 'search', [[['company_id', '=', 1]]])
print(f"Old DB Asyut Orders: {len(old_orders)}, Sessions: {len(old_sessions)}")

# 2. Connect to live database
cj_live = http.cookiejar.CookieJar()
opener_live = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_live))
auth_payload_live = {'jsonrpc': '2.0', 'params': {'db': 'cera-store', 'login': 'draboueldahab@cerastoreeg.com', 'password': 'Tito@1582020'}}
opener_live.open(urllib.request.Request('https://cera-store.odoo.com/web/session/authenticate', data=json.dumps(auth_payload_live).encode('utf-8'), headers={'Content-Type': 'application/json'}))

def call_live(model, method, args=[], kwargs={}):
    url = 'https://cera-store.odoo.com/web/dataset/call_kw'
    if 'context' not in kwargs: kwargs['context'] = {'allowed_company_ids': [1, 2, 3, 4, 5]}
    payload = {'jsonrpc': '2.0', 'params': {'model': model, 'method': method, 'args': args, 'kwargs': kwargs}}
    r = opener_live.open(urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}))
    return json.loads(r.read().decode()).get('result', [])

recent_orders = call_live('pos.order', 'search', [[['config_id', 'in', [1, 2]], ['date_order', '>=', '2026-08-03 00:00:00'], ['date_order', '<=', '2026-08-21 23:59:59']]])
recent_sessions = call_live('pos.session', 'search', [[['config_id', 'in', [1, 2]], ['start_at', '>=', '2026-08-03 00:00:00'], ['start_at', '<=', '2026-08-21 23:59:59']]])
print(f"Live DB Recent Asyut Orders (Aug 03-21): {len(recent_orders)}, Sessions: {len(recent_sessions)}")

# Target orders for Company 5 (C002) = Old Asyut Orders + Recent Asyut Orders
c5_target_orders = list(set(old_orders + recent_orders))
c5_target_sessions = list(set(old_sessions + recent_sessions))
print(f"\nTotal Orders to set for Company 5 (C002): {len(c5_target_orders)}")
print(f"Total Sessions to set for Company 5 (C002): {len(c5_target_sessions)}")

# 3. Update orders to company_id = 5
batch_size = 500
print("Updating orders to Company 5...")
for i in range(0, len(c5_target_orders), batch_size):
    batch = c5_target_orders[i:i + batch_size]
    call_live('pos.order', 'write', [batch, {'company_id': 5}])

print("Updating sessions to Company 5...")
for i in range(0, len(c5_target_sessions), batch_size):
    batch = c5_target_sessions[i:i + batch_size]
    call_live('pos.session', 'write', [batch, {'company_id': 5}])

# 4. Final Comprehensive Verification across all companies
print("\n================ FINAL SYSTEM VERIFICATION ================")
companies = call_live('res.company', 'search_read', [[], ['id', 'name']])
for comp in companies:
    c_id = comp['id']
    c_name = comp['name']
    total_orders = call_live('pos.order', 'search_count', [[['company_id', '=', c_id]]])
    total_sessions = call_live('pos.session', 'search_count', [[['company_id', '=', c_id]]])
    print(f"Company {c_id} ({c_name}):")
    print(f"   POS Orders: {total_orders} | POS Sessions: {total_sessions}")
print("===========================================================")
