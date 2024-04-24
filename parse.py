import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import policy
from email.parser import BytesParser
from pathlib import Path
import xmlrpc.client
from datetime import datetime

# Configuration for Odoo XML-RPC
url = 'http://localhost:8069'
db = 'sie'
username = 'zeynepcaysar2019@gmail.com'
password = '1234'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')


def extract_order_details(order_text, customer_email):
    order_details = {
        'customer_email': customer_email,
        'order_date': None,
        'delivery_date': None,
        'product_id': None,
        'quantity': None,
        'address': None
    }
    for line in order_text.split('\n'):
        line = line.strip()
        if line.startswith('-'):
            line = line[1:].strip()

        key, sep, value = line.partition(':')
        if sep:
            key = key.strip().lower()
            value = value.strip()

            mapping = {
                'order date': 'order_date',
                'delivery date': 'delivery_date',
                'product id': 'product_id',
                'quantity': 'quantity',
                'address': 'address'
            }
            normalized_key = mapping.get(key, None)
            if normalized_key:
                order_details[normalized_key] = value

    if all(order_details[key] for key in ['order_date', 'delivery_date', 'product_id', 'quantity'] if key in order_details):
        return order_details
    else:
        #print("Incomplete Order Details:", order_details)
        return None


def extract_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain' and not part.get('Content-Disposition'):
                return part.get_payload(decode=True).decode('utf-8', errors='ignore')
    else:
        return msg.get_payload(decode=True).decode('utf-8', errors='ignore')

    return ""


def parse_email(msg, file_path):
    from_email = str(msg.get('From')).lower()
    subject = str(msg.get('Subject', '')).lower()

    if "noreply@mycompany.com" in from_email or "sales@mycompany.com" in from_email:
        return []  # skip processing for these addresses

    body = extract_body(msg)
    if not body:
        print("No text content could be extracted from:", file_path)
        return []

    if 'reply: insufficient stocks' in subject:
        return handle_stock_reply(body, from_email)

    orders = []
    order_texts = body.split("\n\n")
    for order_text in order_texts:
        order_details = extract_order_details(order_text, from_email)
        if order_details:
            process_order(order_details, from_email)
        else:
            continue

    return orders


def handle_stock_reply(body, from_email):
    lines = body.strip().split('\n')
    if not lines:
        send_email("Error in Stock Reply", "No response detected.", "sales@mycompany.com", from_email)
        return
    response = lines[0].strip()
    try:
        if response == '2':
            product_id = int(lines[1].split(':')[1].strip())
            quantity = int(lines[2].split(':')[1].strip())
            notify_supplier(product_id, quantity, from_email)
            send_email("Request for Product Replenishment Confirmed",
                       f"Thank you for your patience. We have requested more stock for Product ID {product_id} in the quantity of {quantity}. We will notify you as soon as it is available.",
                       "sales@mycompany.com", from_email)
        elif response == '3':
            send_email("Order Cancellation Confirmed",
                       "We have canceled your order as per your request.",
                       "sales@mycompany.com", from_email)
        elif response == '1':
            order_details = extract_order_details_from_response(lines[1:], from_email)
            if order_details and create_odoo_order(order_details):
                send_email("Order Processing Confirmed",
                           "We will proceed with your order with the available stock.",
                           "sales@mycompany.com", from_email)
            else:
                send_email("Order Processing Error",
                           "There was an error processing your order. Please check the order details and try again.",
                           "sales@mycompany.com", from_email)
        else:
            raise ValueError("Invalid response received.")
    except (IndexError, ValueError) as e:
        print(f"Error parsing response: {e}")
        send_email("Error in Stock Reply",
                   "We could not process your response. Please ensure your reply is formatted correctly.",
                   "sales@mycompany.com", from_email)


def extract_order_details_from_response(lines, customer_email):
    order_details = {'customer_email': customer_email}
    for line in lines:
        clean_line = line.strip().lstrip('-').strip()
        key, _, value = clean_line.partition(':')
        normalized_key = key.strip().lower().replace(' ', '_')
        if normalized_key in ['address', 'order_date', 'delivery_date', 'product_id', 'quantity']:
            order_details[normalized_key] = value.strip()

    required_fields = ['order_date', 'delivery_date', 'product_id', 'quantity', 'address']
    if all(order_details.get(field) for field in required_fields):
        try:
            order_details['order_date'] = format_date(order_details['order_date'])
            order_details['delivery_date'] = format_date(order_details['delivery_date'])
            if order_details['order_date'] and order_details['delivery_date']:
                return order_details
        except ValueError as e:
            print(f"Date formatting error: {e}")

    return None


def notify_supplier(product_id, quantity, from_email):
    message = f"We need more stock for Product ID {product_id}, Quantity Required: {quantity}. Please confirm availability."
    send_email("Request for Product Replenishment", message, "sales@mycompany.com", "supplier@example.com")


def process_order(order_details, from_email):
    order_date = format_date(order_details['order_date'])
    delivery_date = format_date(order_details['delivery_date'])
    if not order_date or not delivery_date:
        send_email("Order Format Error", "Invalid date format. Please check the order and delivery dates and try again.", "noreply@mycompany.com", from_email)
        print("Failed to format one or more dates.")
        return

    order_details['order_date'] = order_date
    order_details['delivery_date'] = delivery_date
    if create_odoo_order(order_details):
        send_email("Order Confirmation", f"Dear Customer,\n\nYour order with product ID {order_details['product_id']} was successfully processed.\n\nBest Regards.", "sales@mycompany.com", from_email)


def send_email(subject, message, from_addr, to_addr):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('localhost', 25)
    server.send_message(msg)
    server.quit()


def create_odoo_order(order_details):
    # First check if the product is available and there is sufficient stock
    product_available, availability_message = check_product_availability(order_details['product_id'],
                                                                         order_details['quantity'],
                                                                         order_details['customer_email'])

    if not product_available:
        print(availability_message)
        return False  # Stop further processing since the product isn't available

    partner_id = check_or_create_partner(order_details['customer_email'],order_details['address'])
    if not partner_id:
        print("Failed to find or create a partner with the email:", order_details['customer_email'])
        return False

    # Creating the order in Odoo
    order_id = models.execute_kw(db, uid, password, 'sale.order', 'create', [{
        'partner_id': partner_id,
        'partner_invoice_id': partner_id,
        'partner_shipping_id': partner_id,
        'order_line': [(0, 0, {'product_id': int(order_details['product_id']),
                               'product_uom_qty': int(order_details['quantity'])})],
        'date_order': order_details['order_date'],
        'validity_date': order_details['delivery_date']
    }])

    if order_id:
        print(f"Created sales order with ID: {order_id}")
        return order_id
    else:
        print("Failed to create the order in Odoo.")
        return False


def check_or_create_partner(email, address=None):
    try:
        if not email:
            raise ValueError("Email address is required for creating or finding a partner.")

        email_str = str(email)
        partner_search = models.execute_kw(db, uid, password, 'res.partner', 'search', [[['email', '=', email_str]]])
        if partner_search:
            partner_id = partner_search[0]
            # Update address if provided and not None
            if address:
                models.execute_kw(db, uid, password, 'res.partner', 'write', [partner_id, {'street': address}])
            return partner_id
        else:
            partner_data = {
                'name': email_str.split('@')[0],
                'email': email_str,
                'is_company': False,
                'customer_rank': 1
            }
            # Ensure address is not None when creating a new partner
            if address:
                partner_data['street'] = address
            return models.execute_kw(db, uid, password, 'res.partner', 'create', [partner_data])
    except Exception as e:
        print(f"Error in partner creation or retrieval: {e}")
        return None


def format_date(date_str):
    cleaned_date_str = date_str.split('\n')[0].strip()
    try:
        return datetime.strptime(cleaned_date_str, '%B %d, %Y').strftime('%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        print(f"Date formatting error: {e}, with input: {cleaned_date_str}")
        return None


def check_product_availability(product_id, quantity_needed, customer_email):
    product_id = int(product_id)
    quantity_needed = int(quantity_needed)

    product = models.execute_kw(db, uid, password, 'product.product', 'search_read',
                                [[['id', '=', product_id]]],
                                {'fields': ['name', 'qty_available']})

    if not product:
        message = f"Dear Customer,\n\nThe product with ID {product_id} is currently not available. We don't produce this product. Please have a look at our products and services again.\n\nBest Regards."
        send_email("Product Unavailability Notice", message, 'sales@mycompany.com', customer_email)
        return False, "Product not available"

    qty_available = product[0]['qty_available']
    if qty_available < quantity_needed:
        # Fetch product information
        products = models.execute_kw(db, uid, password,
                                     'product.product', 'search_read',
                                     [[]],  # You can modify this to filter products if necessary
                                     {'fields': ['name', 'list_price', 'qty_available', 'id']})

        # Building the product availability section for the email
        product_list = "\n".join(
            f"- Name: {p['name']}, ID: {p['id']}, Price: ${p['list_price']:.2f}, Available: {p['qty_available']}"
            for p in products if p['qty_available'] > 0)  # Optional: filter out products with no available stock

        message = f"""Dear Customer,

        We regret to inform you that we currently do not have enough stock for the product ID {product_id}. Required: {quantity_needed}, Available: {qty_available}.

        Here are some other available products:
        {product_list}

        Would you like to:
        1. Order the available items.
        2. Wait until the full quantity is available.
        3. Cancel the item from your order.

        Please reply to this email with your choice.

        Best Regards,
        Your Sales Team
        """
        send_email("Insufficient Stock Notice", message, 'sales@mycompany.com', customer_email)
        return False, "Insufficient stock"

    return True, "Available"


def process_emails(directory, last_run_file):
    last_run_time = get_last_run_time(last_run_file)
    current_time = datetime.now()

    for file_path in Path(directory).rglob('*.eml'):
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        if file_mtime > last_run_time:
            with open(file_path, 'rb') as file:
                msg = BytesParser(policy=policy.default).parse(file)
                parse_email(msg, file_path)
                #print(f"Processed {file_path}")

    update_last_run_time(last_run_file, current_time)


def get_last_run_time(file_path):
    try:
        with open(file_path, 'r') as file:
            last_run_str = file.read().strip()
            if last_run_str:
                return datetime.fromisoformat(last_run_str)
            else:
                return datetime.min  # Return the earliest possible date if the file is empty
    except FileNotFoundError:
        return datetime.min  # Return the earliest possible date if the file does not exist
    except ValueError:
        print(f"Invalid isoformat string in file: {file_path}")
        return datetime.min  # Return the earliest possible date if the content is invalid


def update_last_run_time(file_path, current_time):
    with open(file_path, 'w') as file:
        file.write(current_time.isoformat())

#when time.py is used, comment the bottom line
process_emails('/Users/zeynepcaysar/Downloads/FakeSMTP-master/target/received-emails', '/Users/zeynepcaysar/PycharmProjects/SIE2024/last_run_time.txt')


