import xmlrpc.client

# Configuration
url = 'http://localhost:8069/'
db = 'sie'
username = 'zeynepcaysar2019@gmail.com'
password = '1234'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

partner_id = 46  # Assume you have verified this is a correct partner ID

order_data = {
    'partner_id': partner_id,
    'partner_invoice_id': partner_id,  # Set invoice address to the partner ID
    'partner_shipping_id': partner_id,  # Set shipping address to the partner ID
    'order_line': [
        (0, 0, {'product_id': 37, 'product_uom_qty': 1})  # Example product line
    ],
}
order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [order_data])
print(f"Created sales order with ID: {order_id}")