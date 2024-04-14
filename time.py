import schedule
import time
from parse import process_emails
def job():
    print("Checking for new emails...")
    process_emails('/Users/zeynepcaysar/Downloads/FakeSMTP-master/target/received-emails')

# Schedule the job to run every 1 minutes
schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
