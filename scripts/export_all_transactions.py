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

def export_model(model_name, domain, output_filename, batch_size=500):
    print(f"\n--- Exporting {model_name} with domain {domain} ---")
    count = call_kw(model_name, 'search_count', [domain])
    print(f"Total records to export for {model_name}: {count}")
    if count == 0:
        with open(os.path.join(export_dir, output_filename), 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []
    
    all_records = []
    offset = 0
    while offset < count:
        print(f"Fetching {model_name} records {offset} to {min(offset + batch_size, count)}...")
        records = call_kw(model_name, 'search_read', [domain], {'offset': offset, 'limit': batch_size})
        if not records:
            break
        all_records.extend(records)
        offset += batch_size
    
    file_path = os.path.join(export_dir, output_filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(all_records)} records to {file_path}")
    return all_records

# 1. Companies metadata
export_model('res.company', [], 'res_company.json')

# 2. POS Sessions
export_model('pos.session', ['|', ['create_date', '>=', '2026-08-03 00:00:00'], ['stop_at', '>=', '2026-08-03 00:00:00']], 'pos_session_aug03_aug22.json')

# 3. POS Orders
pos_orders = export_model('pos.order', [['date_order', '>=', '2026-08-03 00:00:00']], 'pos_order_aug03_aug22.json')

# 4. POS Order Lines
pos_order_ids = [o['id'] for o in pos_orders]
if pos_order_ids:
    export_model('pos.order.line', [['order_id', 'in', pos_order_ids]], 'pos_order_line_aug03_aug22.json')
else:
    export_model('pos.order.line', [['create_date', '>=', '2026-08-03 00:00:00']], 'pos_order_line_aug03_aug22.json')

# 5. POS Payments
if pos_order_ids:
    export_model('pos.payment', [['pos_order_id', 'in', pos_order_ids]], 'pos_payment_aug03_aug22.json')
else:
    export_model('pos.payment', [['create_date', '>=', '2026-08-03 00:00:00']], 'pos_payment_aug03_aug22.json')

# 6. Account Moves (Invoices, Bills, Journal Entries)
account_moves = export_model('account.move', ['|', ['date', '>=', '2026-08-03'], ['create_date', '>=', '2026-08-03 00:00:00']], 'account_move_aug03_aug22.json')

# 7. Account Move Lines
move_ids = [m['id'] for m in account_moves]
if move_ids:
    export_model('account.move.line', [['move_id', 'in', move_ids]], 'account_move_line_aug03_aug22.json')
else:
    export_model('account.move.line', [['date', '>=', '2026-08-03']], 'account_move_line_aug03_aug22.json')

# 8. Account Payments
export_model('account.payment', ['|', ['date', '>=', '2026-08-03'], ['create_date', '>=', '2026-08-03 00:00:00']], 'account_payment_aug03_aug22.json')

# 9. Stock Pickings (Deliveries, Receipts, Internal Transfers)
export_model('stock.picking', ['|', ['scheduled_date', '>=', '2026-08-03 00:00:00'], ['create_date', '>=', '2026-08-03 00:00:00']], 'stock_picking_aug03_aug22.json')

# 10. Stock Moves & Move Lines
export_model('stock.move', ['|', ['date', '>=', '2026-08-03 00:00:00'], ['create_date', '>=', '2026-08-03 00:00:00']], 'stock_move_aug03_aug22.json')
export_model('stock.move.line', ['|', ['date', '>=', '2026-08-03 00:00:00'], ['create_date', '>=', '2026-08-03 00:00:00']], 'stock_move_line_aug03_aug22.json')

# 11. Current Stock Quants Snapshot
export_model('stock.quant', [['quantity', '!=', 0]], 'stock_quant_snapshot_aug22.json')

# 12. Sale Orders
export_model('sale.order', ['|', ['date_order', '>=', '2026-08-03 00:00:00'], ['create_date', '>=', '2026-08-03 00:00:00']], 'sale_order_aug03_aug22.json')

# 13. Purchase Orders
export_model('purchase.order', ['|', ['date_order', '>=', '2026-08-03 00:00:00'], ['create_date', '>=', '2026-08-03 00:00:00']], 'purchase_order_aug03_aug22.json')

print("\n==========================================")
print("ALL TRANSACTIONS SUCCESSFULLY EXPORTED & BACKED UP!")
print("Location:", export_dir)
print("==========================================")
