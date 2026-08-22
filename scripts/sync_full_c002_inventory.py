import urllib.request
import json
import http.cookiejar
import os

print("=== Starting Full C002 Inventory Sync via Stock Pickings ===")

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

old_prod_ids = [q['product_id'][0] for q in old_quants]
old_prods = call_old('product.product', 'search_read', [[['id', 'in', old_prod_ids]]], {'fields': ['id', 'barcode', 'default_code', 'name']})
old_prod_map = {p['id']: p for p in old_prods}

# Aggregate target quantity per barcode / code / name
target_quantities = {}
for q in old_quants:
    old_pid = q['product_id'][0]
    qty = q['quantity']
    old_p = old_prod_map.get(old_pid, {})
    bc = old_p.get('barcode')
    code = old_p.get('default_code')
    name = old_p.get('name')
    
    key = None
    if bc: key = ('barcode', bc)
    elif code: key = ('code', code)
    elif name: key = ('name', name)
    
    if key:
        target_quantities[key] = target_quantities.get(key, 0.0) + qty

print(f"Target unique products with stock: {len(target_quantities)}")

# 2. Connect to live database
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
live_c5_prods = call_live('product.product', 'search_read', [[['company_id', '=', 5]]], {'fields': ['id', 'barcode', 'default_code', 'name', 'uom_id']}).get('result', [])
print(f"Live DB: Found {len(live_c5_prods)} products for Company 5")

# Existing stock in ASY2/Stock (Location 53)
existing_quants = call_live('stock.quant', 'search_read', [[['company_id', '=', 5], ['location_id', '=', 53]]], {'fields': ['product_id', 'quantity']}).get('result', [])
current_stock_map = {q['product_id'][0]: q['quantity'] for q in existing_quants if q.get('product_id')}
print(f"Live DB: Found {len(current_stock_map)} existing quants in ASY2/Stock")

# Calculate moves needed
moves_to_create = []
for p in live_c5_prods:
    pid = p['id']
    bc = p.get('barcode')
    code = p.get('default_code')
    name = p.get('name')
    uom_id = p.get('uom_id', [1])[0]
    
    target_qty = 0.0
    if bc and ('barcode', bc) in target_quantities:
        target_qty = target_quantities[('barcode', bc)]
    elif code and ('code', code) in target_quantities:
        target_qty = target_quantities[('code', code)]
    elif name and ('name', name) in target_quantities:
        target_qty = target_quantities[('name', name)]
    
    curr_qty = current_stock_map.get(pid, 0.0)
    diff = target_qty - curr_qty
    
    if diff > 0:
        moves_to_create.append({
            'product_id': pid,
            'product_uom_qty': diff,
            'quantity': diff,
            'product_uom': uom_id,
            'location_id': 49, # Inventory adjustment location
            'location_dest_id': 53, # ASY2/Stock
            'company_id': 5,
        })

print(f"\nTotal moves to create to achieve exact backup inventory: {len(moves_to_create)}")

# Create Pickings in batches of 300 moves
batch_size = 300
total_pickings = 0

for i in range(0, len(moves_to_create), batch_size):
    batch_moves = moves_to_create[i:i + batch_size]
    picking_vals = {
        'picking_type_id': 37,
        'location_id': 49,
        'location_dest_id': 53,
        'company_id': 5,
        'origin': f'Asyut Backup Inventory Sync Batch {i//batch_size + 1}',
        'move_ids': [(0, 0, m) for m in batch_moves]
    }
    
    res_pick = call_live('stock.picking', 'create', [[picking_vals]])
    if res_pick.get('result'):
        pick_id = res_pick['result']
        if isinstance(pick_id, list): pick_id = pick_id[0]
        res_val = call_live('stock.picking', 'button_validate', [[pick_id]])
        total_pickings += 1
        print(f"Validated Picking Batch {i//batch_size + 1} ({len(batch_moves)} items): Picking ID {pick_id}")

# 3. Final Stock Verification
final_gt0 = call_live('stock.quant', 'search_count', [[['company_id', '=', 5], ['location_id', '=', 53], ['quantity', '>', 0]]]).get('result')
final_quants = call_live('stock.quant', 'search_read', [[['company_id', '=', 5], ['location_id', '=', 53], ['quantity', '>', 0]]], {'fields': ['quantity']}).get('result', [])
total_final_units = sum([q['quantity'] for q in final_quants])

print("\n================ FINAL C002 INVENTORY VERIFICATION ================")
print(f"Items with positive stock in Asyut C002: {final_gt0}")
print(f"Total units in Asyut C002 Warehouse: {total_final_units}")
print("===================================================================")
