# sie_integration_project

# HOW TO MAKE IT WORK
you send an order message with send_smtp.py file.
and then time.py function checks every 1 minute if there is a new email. it goes to the parse.py file that shows you the result: order accepted or not regarding stock or product availability. 


# FILES
- odoo_api.py file does access to odoo's api
- access_Smtp.py file reads emails in received emails folder of fakesmtp
- parse.py file starts with function process_emails with the directory to email folder. and then it searchs for latest email. it goes to the function create_odoo_order where it checks product availability check_product_availability function. it says available or not and send confirmation email to the customer with send_email function. after, it checks if the customer is a new or existing one. after the order cretated, it the order creation, a new confirmation email sent to customer. 
- send_smtp.py file sends email via fakesmtp