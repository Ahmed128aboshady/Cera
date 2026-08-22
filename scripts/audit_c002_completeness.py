import urllib.request
import json
import http.cookiejar

cj_live = http.cookiejar.CookieJar()
opener_live = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj_live))
auth_payload_live = {'jsonrpc': '2.0', 'params': {'db': 'cera-store', 'login': 'draboueldahab@cerastoreeg.com', 'password': 'Tito@1582020'}}
opener_live.open(urllib.request.Request('https://cera-store.odoo.com/web/session/authenticate', data=json.dumps(auth_payload_live).encode('utf-8'), headers={'Content-Type': 'application/json'}))

def call_live(model, method, args=[], kwargs={}):
    url = 'https://cera-store.odoo.com/web/dataset/call_kw'
    if 'context' not in kwargs:
        kwargs['context'] = {'allowed_company_ids': [5]}
    payload = {'jsonrpc': '2.0', 'params': {'model': model, 'method': method, 'args': args, 'kwargs': kwargs}}
    r = opener_live.open(urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'}))
    return json.loads(r.read().decode())

# 1. POS Config
pos_cfg = call_live('pos.config', 'search_read', [[['company_id', '=', 5]]], {'fields': ['name', 'journal_id', 'invoice_journal_id', 'payment_method_ids', 'warehouse_id', 'picking_type_id', 'advanced_employee_ids', 'basic_employee_ids']})
print('=== 1. POS Configuration for C002 ===')
print(json.dumps(pos_cfg.get('result'), indent=2))

# 2. Payment Methods
pms = call_live('pos.payment.method', 'search_read', [[['company_id', '=', 5]]], {'fields': ['name', 'journal_id', 'company_id']})
print('\n=== 2. Payment Methods for C002 ===')
print(json.dumps(pms.get('result'), indent=2))

# 3. Warehouse and Stock
wh = call_live('stock.warehouse', 'search_read', [[['company_id', '=', 5]]], {'fields': ['name', 'code', 'lot_stock_id']})
stock_gt0 = call_live('stock.quant', 'search_count', [[['company_id', '=', 5], ['quantity', '>', 0]]])
stock_0 = call_live('stock.quant', 'search_count', [[['company_id', '=', 5], ['quantity', '<=', 0]]])
print('\n=== 3. Warehouse & Stock ===')
print('Warehouse:', json.dumps(wh.get('result'), indent=2))
print('Items with Stock > 0:', stock_gt0.get('result'))
print('Items with Stock <= 0:', stock_0.get('result'))

# 4. Accounting Journals
journals = call_live('account.journal', 'search_read', [[['company_id', '=', 5]]], {'fields': ['name', 'type', 'code', 'default_account_id']})
print('\n=== 4. Accounting Journals ===')
for j in journals.get('result', []):
    print(f"  {j['name']} ({j['type']}) - Code: {j['code']}, Account: {j.get('default_account_id')}")

# 5. Employees in Company 5
emps = call_live('hr.employee', 'search_read', [[['company_id', '=', 5]]], {'fields': ['name', 'work_contact_id', 'user_id']})
print('\n=== 5. Employees in Company 5 ===')
print(json.dumps(emps.get('result'), indent=2))
