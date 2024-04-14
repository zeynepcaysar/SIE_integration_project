import xmlrpc.client

url = 'http://localhost:8069/'
db = 'sie'
username = 'zeynepcaysar2019@gmail.com'
password = '1234'

# Setup common and models server proxy
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Authenticate
uid = common.authenticate(db, username, password, {})
if uid:
    print("Authentication success.")

    # Execute operation after successful authentication
    try:
        # Fetch product information
        products = models.execute_kw(db, uid, password,
                                     'product.product', 'search_read',
                                     [[]],
                                     {'fields': ['name', 'list_price', 'qty_available']})
        print("---> Products and their quantities:")
        for product in products:
            print(f"Name: {product['name']}, ID: {product['id']}, Price: {product['list_price']}, Quantity Available: {product['qty_available']}")

        # Fetch all customers (partners)
        customers = models.execute_kw(db, uid, password,
                                      'res.partner', 'search_read',
                                      [[['customer_rank', '>', 0]]],  # customers have customer_rank greater than 0
                                      {'fields': ['name', 'id']})
        print("---> Customers:")
        for customer in customers:
            print(f"Customer Name: {customer['name']}, ID: {customer['id']}")

            # Fetch orders for each customer
            orders = models.execute_kw(db, uid, password,
                                       'sale.order', 'search_read',
                                       [[['partner_id', '=', customer['id']]]],
                                       {'fields': ['name', 'state', 'date_order']})
            if orders:
                print("Orders for Customer ID", customer['id'], ":")
                for order in orders:
                    print(f"Order ID: {order['id']}, Name: {order['name']}, State: {order['state']}, Date: {order['date_order']}")

    except xmlrpc.client.Fault as e:
        print(f"An error occurred: {e}")
else:
    print("Authentication failed. Please check your credentials.")
