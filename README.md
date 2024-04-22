# sie_integration_project

# needed softwares: 
Python: For scripting the automation process.

FakeSMTP: Used during development to test email capturing without needing real email traffic.

Odoo ERP: Central management software that handles CRM, sales, and inventory.

SpaCy: Natural Language Processing library to parse email content effectively.

Odoo API: RESTful API for accessing and manipulating Odoo's database, particularly for creating CRM records, checking inventory, and processing sales orders.

SMTP Protocol: Used for sending confirmation emails through the Python smtplib.


# HOW TO MAKE THE CODE WORK 
you send an order message with send_smtp.py file.
then, run time.py file who checks every 1 minute if there is a new email. it goes to the parse.py file that shows you the result: order accepted(created order in odoo) or not regarding stock or product availability. Then, a mail sent to customer with the order information, whether accepted or not.


# FILES
- odoo_api.py file access to odoo
- access_Smtp.py file reads emails in received emails folder of fakesmtp
- parse.py file starts with function process_emails with the directory to email folder. and then it searchs for latest email. it goes to the function create_odoo_order where it checks product availability check_product_availability function. it says available or not and send confirmation email to the customer with send_email function. after, it checks if the customer is a new or existing one. after the order cretated, it the order creation, a new confirmation email sent to customer. 
- send_smtp.py file sends email via fakesmtp