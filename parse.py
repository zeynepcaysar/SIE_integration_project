import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import spacy
from email import policy
from email.parser import BytesParser
from pathlib import Path
import xmlrpc.client
from datetime import datetime
# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

# Configuration for Odoo XML-RPC
url = 'http://localhost:8069'
db = 'sie'
username = 'zeynepcaysar2019@gmail.com'
password = '1234'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

#function to parse emails with NLP
def parse_email(file_path):
    with open(file_path, 'rb') as file:  # Read as binary to handle different encodings
        msg = BytesParser(policy=policy.default).parse(file)
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')  # decode and ignore errors in decoding
        doc = nlp(body)

        order_details = {
            'customer_email': msg['from'],
            'order_date': None,
            'delivery_date': None,
            'product_id': None,
            'quantity': None
        }

        for ent in doc.ents:
            if ent.label_ == "DATE":
                if not order_details['order_date']:
                    order_details['order_date'] = ent.text
                else:
                    order_details['delivery_date'] = ent.text
            elif ent.label_ == "CARDINAL":
                if not order_details['product_id']:
                    order_details['product_id'] = ent.text
                elif not order_details['quantity']:
                    order_details['quantity'] = ent.text

        if not all(order_details.values()):  # Check if all details are found
            print(f"Missing order details in email: {file_path}")
            return None

        return order_details

#function to check if the customer is a new or existiong one
def check_or_create_partner(email):
    # Convert email address to string if it's not already
    email_str = str(email)
    partner_ids = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['email', '=', email_str]]])
    if partner_ids:
        return partner_ids[0]
    else:
        return models.execute_kw(db, uid, password, 'res.partner', 'create', [{
            'name': email_str.split('@')[0],  # Basic name from email
            'email': email_str,
            'is_company': False,
            'customer_rank': 1
        }])


#function to fix the date format
def format_date(date_str):
    # Clean the date string to ensure no extraneous text is included
    cleaned_date_str = date_str.split('\n')[0].strip()  # Taking the first part before any newline and trimming spaces
    try:
        return datetime.strptime(cleaned_date_str, '%B %d, %Y').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        print(f"Date formatting error: {e}, with input: {cleaned_date_str}")
        return None

#function to check if the product is available and the stocks are sufficient or not. 
def check_product_availability(product_id, quantity_needed, customer_email):
    product_id = int(product_id)
    quantity_needed = int(quantity_needed)

    product = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                                [[['id', '=', product_id]]],
                                {'fields': ['name', 'qty_available']})

    if not product:
        message = f"Dear Customer,\n\nThe product with ID {product_id} is currently not available."
        send_email("Product Unavailability Notice", message, 'sales@mycompany.com', customer_email)
        return False, "Product not available"

    qty_available = product[0]['qty_available']
    if qty_available < quantity_needed:
        message = f"Dear Customer,\n\nWe do not have enough stock for the product ID {product_id}. Required: {quantity_needed}, Available: {qty_available}"
        send_email("Insufficient Stock Notice", message, 'sales@mycompany.com', customer_email)
        return False, "Insufficient stock"

    return True, "Available"

#function to send email to customer
def send_email(subject, message, from_addr, to_addr):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    # Setup the SMTP server
    server = smtplib.SMTP('localhost', 25)  # Default SMTP port
    server.send_message(msg)
    server.quit()
    print("Email sent to", to_addr)

#function to create order in odoo
def create_odoo_order(order_details):
    if order_details is None:
        return  # Exit if no order details found

    # Check product availability
    product_check, status = check_product_availability(order_details['product_id'], order_details['quantity'], order_details['customer_email'])
    if not product_check:
        print(f"Cannot create order: {status}")
        return

    # Format dates
    order_details['order_date'] = format_date(order_details['order_date'])
    order_details['delivery_date'] = format_date(order_details['delivery_date'])

    if not order_details['order_date'] or not order_details['delivery_date']:
        print("Error in date conversion, order not created.")
        return

    partner_id = check_or_create_partner(order_details['customer_email'])
    order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
        'partner_id': partner_id,
        'partner_invoice_id': partner_id,
        'partner_shipping_id': partner_id,
        'order_line': [
            (0, 0, {'product_id': int(order_details['product_id']), 'product_uom_qty': int(order_details['quantity'])})
        ],
        'date_order': order_details['order_date'],
        'validity_date': order_details['delivery_date']
    }])

    if order_id:
        print(f"Created sales order with ID: {order_id}")
        # Send confirmation email
        confirmation_message = f"Dear Customer,\n\nYour order with ID {order_id} has been successfully created. We will notify you once your order is shipped."
        send_email("Order Confirmation", confirmation_message, 'sales@mycompany.com', order_details['customer_email'])
        print("Confirmation email sent to", order_details['customer_email'])
    else:
        print("Failed to create order.")


#function to process order
def process_emails(directory):
    # Initialize variables to find the latest file
    latest_file = None
    latest_time = None

    # Walk through the directory to find the most recent email file
    for filename in Path(directory).rglob('*.eml'):
        file_path = os.path.join(directory, filename)
        file_mtime = os.path.getmtime(file_path)
        if latest_file is None or file_mtime > latest_time:
            latest_time = file_mtime
            latest_file = filename

    # Process only the latest email
    if latest_file:
        order_data = parse_email(latest_file)
        if order_data:
            create_odoo_order(order_data)
        else:
            print(f"Order details missing or incomplete in file: {latest_file}")
    else:
        print("No emails found in the directory.")


#process_emails('/Users/zeynepcaysar/Downloads/FakeSMTP-master/target/received-emails')
