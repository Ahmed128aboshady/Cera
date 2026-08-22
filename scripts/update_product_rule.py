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

# Update Rule 71 (Product multi-company)
domain_str = "[('company_id', 'in', company_ids)]"
res_rule = call_live('ir.rule', 'write', [[71], {'domain_force': domain_str}])
print('Update Rule 71 result:', res_rule)

count_all = call_live('product.template', 'search_count', [[]])
count_sales = call_live('product.template', 'search_count', [[['sale_ok', '=', True]]])

print('\n================ C002 PRODUCT CATALOG COUNT ================')
print('Total Products visible in C002 now:', count_all.get('result'))
print('Products with [Sales] filter in C002 now:', count_sales.get('result'))
print('===========================================================')
