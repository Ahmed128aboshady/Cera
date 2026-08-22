import urllib.request
import json
import http.cookiejar
import os
import sys

export_dir = r"C:\Users\Video Editor\.gemini\antigravity\scratch\cera_exports_aug03_to_aug22"
os.makedirs(export_dir, exist_ok=True)

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
    if 'error' in res:
        print(f"Error in {model}.{method}:", res['error'])
    return res.get('result', [])

# 1. Back up all orders of Session 821 / Config 9
print("\n--- Step 1: Taking full backup of Session 821 and all its 8,494 orders ---")
s821_orders = []
batch_size = 500
count_821 = call_kw('pos.order', 'search_count', [[['session_id', '=', 821]]])
print(f"Total orders in Session 821: {count_821}")

offset = 0
while offset < count_821:
    print(f"Fetching session 821 orders {offset} to {min(offset + batch_size, count_821)}...")
    recs = call_kw('pos.order', 'search_read', [[['session_id', '=', 821]]], {'offset': offset, 'limit': batch_size})
    if not recs:
        break
    s821_orders.extend(recs)
    offset += batch_size

backup_path = os.path.join(export_dir, 'session_821_full_backup.json')
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(s821_orders, f, ensure_ascii=False, indent=2)

file_size = os.path.getsize(backup_path)
print(f"SUCCESS: Saved {len(s821_orders)} orders to {backup_path} ({file_size} bytes)")

# 2. Reassign POS orders for Config 1 & 2 to Company 1 (CERA Store Asyut C001)
print("\n--- Step 2: Reassigning 19,334 orders of CERA Cash 1 & 2 to Company 1 (C001) ---")
c1_orders_in_c5 = call_kw('pos.order', 'search', [[['config_id', 'in', [1, 2]], ['company_id', '=', 5]]])
print(f"Found {len(c1_orders_in_c5)} orders of Configs 1 & 2 currently set to Company 5")

batch_size_write = 500
for i in range(0, len(c1_orders_in_c5), batch_size_write):
    batch_ids = c1_orders_in_c5[i:i + batch_size_write]
    res_w = call_kw('pos.order', 'write', [batch_ids, {'company_id': 1}])
    print(f"Updated orders {i} to {min(i + batch_size_write, len(c1_orders_in_c5))}: {res_w}")

# 3. Verify orders in Company 1 vs Company 5
pos_c1_count = call_kw('pos.order', 'search_count', [[['company_id', '=', 1]]])
pos_c5_count = call_kw('pos.order', 'search_count', [[['company_id', '=', 5]]])
print(f"\nVerification after update:")
print(f"POS Orders in Company 1 (C001): {pos_c1_count}")
print(f"POS Orders in Company 5 (C002): {pos_c5_count}")

# 4. Clean Session 821 (delete duplicate orders)
print("\n--- Step 3: Cleaning Session 821 orders (already backed up in session_821_full_backup.json) ---")
order_ids_821 = [o['id'] for o in s821_orders]
print(f"Deleting {len(order_ids_821)} duplicate orders from session 821...")
for i in range(0, len(order_ids_821), batch_size_write):
    batch_del_ids = order_ids_821[i:i + batch_size_write]
    res_del = call_kw('pos.order', 'unlink', [batch_del_ids])
    print(f"Deleted orders {i} to {min(i + batch_del_ids.__len__(), len(order_ids_821))}: {res_del}")

# Check final counts
pos_c1_final = call_kw('pos.order', 'search_count', [[['company_id', '=', 1]]])
pos_c5_final = call_kw('pos.order', 'search_count', [[['company_id', '=', 5]]])
print(f"\n================ FINAL STATE ================")
print(f"POS Orders in Company 1 (CERA Store Asyut C001): {pos_c1_final}")
print(f"POS Orders in Company 5 (CERA Store Asyut C002): {pos_c5_final}")
print("=============================================")
