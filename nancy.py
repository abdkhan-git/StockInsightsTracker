import csv, zipfile
import requests
import time, os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get the current year for building URLs
current_year = datetime.now().year

zip_file_url = f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{current_year}FD.zip"
pdf_file_url = f"https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{current_year}/"

load_dotenv()

# Email and server configuration from environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
EMAIL_SERVER = os.getenv("EMAIL_SERVER", "smtppro.zoho.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))

# Use an environment variable to set which members to monitor.
# Provide a comma-separated list if you wish to monitor more than one.
TARGET_MEMBERS = os.getenv("TARGET_MEMBERS", "Pelosi")
TARGET_MEMBERS = [member.strip() for member in TARGET_MEMBERS.split(",")]

# Create the SMTP connection using the configurable email server and port.
server = smtplib.SMTP_SSL(EMAIL_SERVER, EMAIL_PORT)
server.login(SENDER_EMAIL, APP_PASSWORD)

def check_for_new_trades():
    # Download and extract the zip file containing trade data
    r = requests.get(zip_file_url)
    zipfile_name = f'{current_year}FD.zip'
    with open(zipfile_name, 'wb') as f:
        f.write(r.content)
    
    with zipfile.ZipFile(zipfile_name) as z:
        z.extractall('.')
    
    trades = []
    file_name = f'{current_year}FD.txt'
    with open(file_name) as f:
        for line in csv.reader(f, delimiter='\t'):
            # Check if the trade belongs to one of our target members
            if line[1] in TARGET_MEMBERS:
                member = line[1]
                dt = datetime.strptime(line[7], '%m/%d/%Y')
                doc_id = line[8]
                # Store member name, date, and document id
                trades.append((member, dt, doc_id))
    
    # Sort trades by date (newest first)
    trades.sort(key=lambda x: x[1], reverse=True)
    return trades

def send_email_notification(trades):
    if not trades:
        return

    # Build a subject with only the members present in the new trades.
    notified_members = sorted(set(trade[0] for trade in trades))
    subject = f"New Trade(s) Detected for {', '.join(notified_members)}"
    body = "New trades have been detected:\n\n"
    recipients = RECIPIENT_EMAIL.split(',')

    for trade in trades:
        # trade[0]: member name, trade[1]: date, trade[2]: document ID
        body += f"Member: {trade[0]}\n"
        body += f"Date: {trade[1].strftime('%Y-%m-%d')}\n"
        body += f"Document ID: {trade[2]}\n"
        body += f"PDF URL: {pdf_file_url}{trade[2]}.pdf\n\n"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    for recipient in recipients:
        print(f"Sending email to {recipient}")
        msg['To'] = recipient
        server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        
    print(f"Sent an email notification for {len(trades)} new trades.")

# --- Persistence functions to track processed trades ---

def load_processed_trades(file_name="processed_trades.txt"):
    """
    Load the set of processed trade document IDs from a file.
    If the file doesn’t exist, return an empty set.
    """
    processed = set()
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            for line in f:
                processed.add(line.strip())
    return processed

def save_processed_trades(new_doc_ids, file_name="processed_trades.txt"):
    """
    Append new trade document IDs to the file so they aren’t processed again.
    """
    with open(file_name, "a") as f:
        for doc_id in new_doc_ids:
            f.write(doc_id + "\n")

# --- Main loop ---

def main():
    # Load previously processed trades from file
    processed_trades = load_processed_trades()
    last_check = datetime.now() - timedelta(minutes=10)
    
    while True:
        current_time = datetime.now()
        if current_time - last_check >= timedelta(minutes=5):
            print("Checking for new trades...")
            all_trades = check_for_new_trades()
            
            # Filter out any trades that have already been processed
            new_trades = [trade for trade in all_trades if trade[2] not in processed_trades]
            
            if new_trades:
                send_email_notification(new_trades)
                # Add the new trade document IDs to our processed set and file
                new_doc_ids = [trade[2] for trade in new_trades]
                processed_trades.update(new_doc_ids)
                save_processed_trades(new_doc_ids)
            
            last_check = current_time
        time.sleep(60)

if __name__ == "__main__":
    main()
