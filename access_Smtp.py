import os
import email
from email import policy

def read_emails(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.eml'):
            path = os.path.join(directory, filename)
            with open(path, 'r', encoding='utf-8') as file:
                msg = email.message_from_file(file, policy=policy.default)
                print('Subject:', msg['subject'])
                print('From:', msg['from'])
                print('To:', msg['to'])
                print('Body:', msg.get_body(preferencelist=('plain', 'html')).get_content())
                print('----')

# Example usage
read_emails('/Users/zeynepcaysar/Downloads/FakeSMTP-master/target/received-emails')
