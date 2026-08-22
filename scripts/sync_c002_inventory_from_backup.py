import urllib.request
import json
import http.cookiejar
import os

print("=== Starting C002 Inventory Sync from Backup ===")

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

# Fetch stock quants for Asyut in old DB
old_quants = call_old('stock.quant', 'search_read', [[['company_id', '=', 1], ['quantity', '>', 0], ['location_id.usage', '=', 'internal']]], {'fields': ['product_id', 'quantity']})
print(f"Old DB: Found {len(old_quants)} stock quants in Asyut")

# Fetch old products info
old_prod_ids = [q['product_id'][0] for q in old_quants]
old_prods = call_old('product.product', 'search_read', [[['id', 'in', old_prod_ids]]], {'fields': ['id', 'barcode', 'default_code', 'name']})
old_prod_map = {p['id']: p for p in old_prods}

# 2. Connect to live database
cj_live = http.cookiejar.CookieJar()
opener_live = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_live))
auth_payload_live = {'jsonrpc': '2.0', 'params': {'db': 'cera-store', 'login': 'draboueldahab@cerastoreeg.com', 'password': 'Tito@1582020'}}
opener_live.open(urllib.request.Request('https://cera-store.odoo.com/web/session/authenticate', data=json.dumps(auth_payload_live).encode('utf-8'), headers={'Content-Type': 'application/json'}))

def call_live(model, method, args=[], kwargs={}):
    url = 'https://cera-store.odoo.com/web/dataset/call_kw'
    if 'context' not in kwargs: kwargs['context'] = {'allowed_company_ids': [1, 2, 3, 4, 5], 'inventory_mode': True}
    else:
        kwargs['context']['allowed_company_ids'] = [1, 2, 3, 4, 5]
        kwargs['context']['inventory_mode'] = True
    payload = {'jsonrpc': '2.0', 'params': {'model': model, 'method': method, 'args': args, 'kwargs': kwargs}}
    r = opener_live.open(urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}))
    return json.loads(r.read().decode())

# Fetch all live products belonging to Company 5
live_c5_prods = call_live('product.product', 'search_read', [[['company_id', '=', 5]]], {'fields': ['id', 'barcode', 'default_code', 'name']}).get('result', [])
print(f"Live DB: Found {len(live_c5_prods)} products for Company 5")

live_bc_map = {p['barcode']: p['id'] for p in live_c5_prods if p.get('barcode')}
live_code_map = {p['default_code']: p['id'] for p in live_c5_prods if p.get('default_code')}
live_name_map = {p['name']: p['id'] for p in live_c5_prods if p.get('name')}

# Existing quants in location 53 (ASY2/Stock)
existing_quants = call_live('stock.quant', 'search_read', [[['company_id', '=', 5], ['location_id', '=', 53]]], {'fields': ['id', 'product_id', 'quantity']}).get('result', [])
existing_quant_map = {q['product_id'][0]: q for q in existing_quants if q.get('product_id')}
print(f"Live DB: Found {len(existing_quant_map)} existing quants in ASY2/Stock")

# 3. Match and Prepare Updates / Inserts
to_update = []
to_create = []
unmatched = 0

for q in old_quants:
    old_pid = q['product_id'][0]
    qty = q['quantity']
    old_p = old_prod_map.get(old_pid, {})
    
    bc = old_p.get('barcode')
    code = old_p.get('default_code')
    name = old_p.get('name')
    
    live_pid = None
    if bc and bc in live_bc_map:
        live_pid = live_bc_map[bc]
    elif code and code in live_code_map:
        live_pid = live_code_map[code]
    elif name and name in live_name_map:
        live_pid = live_name_map[name]
    
    if live_pid:
        if live_pid in existing_quant_map:
            q_obj = existing_quant_map[live_pid]
            to_update.append((q_obj['id'], qty))
        else:
            to_create.append({
                'product_id': live_pid,
                'location_id': 53,
                'inventory_quantity': qty,
                'company_id': 5,
            })
    else:
        unmatched += 1

print(f"\nMatching Results:")
print(f"  Quants to Update: {len(to_update)}")
print(f"  Quants to Create: {len(to_create)}")
print(f"  Unmatched: {unmatched}")

# 4. Execute Updates
print("\nApplying updates to existing quants...")
for q_id, qty in to_update:
    call_live('stock.quant', 'write', [[q_id], {'inventory_quantity': qty, 'user_id': 7}])

# Execute Creates
print(f"Creating {len(to_create)} new quants...")
batch_size = 100
for i in range(0, len(to_create), batch_size):
    batch = to_create[i:i + batch_size]
    call_live('stock.quant', 'create', [batch])

# 5. Apply Inventory Adjustments
print("Applying inventory adjustments across all C002 quants...")
all_c5_quant_ids = call_live('stock.quant', 'search', [[['company_id', '=', 5], ['location_id', '=', 53], ['inventory_quantity_set', '=', True]]]).get('result', [])
if all_c5_quant_ids:
    print(f"Calling action_apply_inventory on {len(all_c5_quant_ids)} quants...")
    for i in range(0, len(all_c5_quant_ids), 200):
        batch = all_c5_quant_ids[i:i+200]
        call_live('stock.quant', 'action_apply_inventory', [batch])

# 6. Verification
final_gt0 = call_live('stock.quant', 'search_count', [[['company_id', '=', 5], ['location_id', '=', 53], ['quantity', '>', 0]]]).get('result')
final_quants = call_live('stock.quant', 'search_read', [[['company_id', '=', 5], ['location_id', '=', 53], ['quantity', '>', 0]]], {'fields': ['quantity']}).get('result', [])
total_final_units = sum([q['quantity'] for q in final_quants])

print("\n================ FINAL C002 INVENTORY VERIFICATION ================")
print(f"Items with positive stock in Asyut C002: {final_gt0}")
print(f"Total units in Asyut C002 Warehouse: {total_final_units}")
print("===================================================================")
