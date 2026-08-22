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

# Restore standard rule 71
std_domain = "['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]"
res_rule = call_live('ir.rule', 'write', [[71], {'domain_force': std_domain}])
print('Restored Rule 71 result:', res_rule)

# Test reading sale.order in company 5
ctx_c5 = {'allowed_company_ids': [5]}
test_sales = call_live('sale.order', 'search_read', [[]], {'context': ctx_c5, 'limit': 5})
print('Test Sales read in C002:', 'SUCCESS' if 'result' in test_sales else test_sales)

test_prods = call_live('product.product', 'search_read', [[]], {'context': ctx_c5, 'limit': 5})
print('Test Products read in C002:', 'SUCCESS' if 'result' in test_prods else test_prods)
