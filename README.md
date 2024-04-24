# sie_integration_project

# needed softwares: 
Python: For scripting the automation process.

FakeSMTP: Used during development to test email capturing without needing real email traffic.

Odoo ERP: Central management software that handles CRM, sales, and inventory.

SpaCy: Natural Language Processing library to parse email content effectively.

Odoo API: RESTful API for accessing and manipulating Odoo's database, particularly for creating CRM records, checking inventory, and processing sales orders.

SMTP Protocol: Used for sending confirmation emails through the Python smtplib.

after python and fakesmtp is installed, to test the code:

# HOW TO MAKE THE CODE WORK 
to test the customer-company email interaction, first like a customer does, send an order message with send_smtp.py file. you can send multiple mails. Also, you can send multiple orders in one mail. 
try commented exemples in the send_smpty.py to see different results.


THEN, run time.py file who checks every 1 minute if there are any new email. if you run time.py file, make sure that process_emails function at the bottom of the parse.py file is commented. 
to gain 1 minute, you can simply run the parse.py. 
check the results in fakesmtp's received emails folder. 
in a successful order case, check the orders in odoo, and also check customers. 


# FILES
- parse.py file : MAIN FUNCTION THAT DOES THE WORK FOR AUTOMATIC EMAIL INTERACTION AND CREATING AN ORDER IN ODOO.
- send_smtp.py file : sends email via fakesmtp
- odoo_api.py file : access to odoo
- access_Smtp.py file : reads emails in received emails folder of fakesmtp