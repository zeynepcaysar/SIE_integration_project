import smtplib
from email.mime.text import MIMEText

def send_email(subject, message, from_addr, to_addr):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    # Connect to your local FakeSMTP server
    server = smtplib.SMTP('localhost', 25)  # Default SMTP port is 25
    server.send_message(msg)
    server.quit()
    print("Email sent successfully!")


email_subject = "New Order Confirmation"
email_body = """
- Order Date: April 16, 2024
- Delivery Date: April 28, 2024
- Product ID: 31
- Quantity: 2
"""

send_email(email_subject, email_body, 'customer6@example.com', 'sales@mycompany.com')
