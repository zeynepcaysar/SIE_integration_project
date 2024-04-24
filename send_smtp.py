import smtplib
from email.mime.text import MIMEText

def send_email(subject, message, from_addr, to_addr):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    # Connect to FakeSMTP server
    server = smtplib.SMTP('localhost', 25)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully!")


#new order mail from customer
email_subject = "New Order Confirmation"
email_body = """
Hello, this is my order below,
- address:chemin de soleil, 1223, Geneva
- Order Date: April 16, 2024
- Delivery Date: April 28, 2024
- Product ID: 21
- Quantity: 2

- Order Date: April 16, 2024
- Delivery Date: April 28, 2024
- Product ID: 5
- Quantity: 1

- Order Date: April 16, 2024
- Delivery Date: April 28, 2024
- Product ID: 1
- Quantity: 1

Thank you,
Best Regards,
"""

send_email(email_subject, email_body, 'customer1020@example.com', 'sales@mycompany.com')


#reply: insufficient stocks

#answer 1: order other available products
'''
email_subject = "reply: insufficient stocks"
email_body = """
1
- address:chemin de soleil, 1223, Geneva
- Order Date: April 16, 2024
- Delivery Date: April 28, 2024
- Product ID: 21
- Quantity: 2
"""

'''
#answer 2: wait for product replenishment
'''
email_subject = "reply: insufficient stocks"
email_body = """
2
product id: 5
quantity:2
"""
'''

