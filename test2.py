import xmlrpc.client

# Configuration
url = 'http://localhost:8069/'
db = 'sie'
username = 'zeynepcaysar2019@gmail.com'
password = '1234'

# Start the XMLRPC session
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Search for partner by email
email_to_search = "newcustomer@example.com"
partner_ids = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['email', '=', email_to_search]]])

if partner_ids:
    print(f"Customer already exists with ID: {partner_ids[0]}")
else:
    # No partner found, create new
    new_partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
        'name': "New Customer",
        'email': email_to_search,
        'is_company': False,
        'customer_rank': 1  # Indicates this is a customer
    }])
    print(f"New customer created with ID: {new_partner_id}")
