import csv, zipfile
import requests
import time, os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import xml.etree.ElementTree as ET
import json
import markdown
from pdf_extractor import extract_pdf_content

# Get the current year for building URLs
current_year = datetime.now().year

zip_file_url = f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{current_year}FD.zip"
pdf_file_url = f"https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{current_year}/"

# Load environment variables from .env file
load_dotenv()

# Email and server configuration from environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_NAME = os.getenv("SENDER_NAME", "admin")  # New: set the sender name
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
EMAIL_SERVER = os.getenv("EMAIL_SERVER", "smtppro.zoho.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 465))

# Use an environment variable to set which members to monitor.
# Provide a comma-separated list if you wish to monitor more than one.
TARGET_MEMBERS = os.getenv("TARGET_MEMBERS", "Pelosi")
print("Members: ", TARGET_MEMBERS)
TARGET_MEMBERS = [member.strip() for member in TARGET_MEMBERS.split(",")]

# Set the filename for storing processed trades.
# This can be set to a persistent volume path in your Docker configuration.
PROCESSED_TRADES_FILE = os.getenv("PROCESSED_TRADES_FILE", "processed_trades.txt")

# ADDED: Boolean to control whether to send emails
sendEmail = True
print("Are we sending the email? ", sendEmail)

# Create the SMTP connection using the configurable email server and port.
server = smtplib.SMTP_SSL(EMAIL_SERVER, EMAIL_PORT)
server.login(SENDER_EMAIL, APP_PASSWORD)

def get_two_months_ago():
    """Calculate the date 2 months ago from the current date."""
    today = datetime.now()
    timeframe_days = int(os.getenv("TIMEFRAME_DAYS", 60))
    timeframe_ago = today - timedelta(days=timeframe_days)
    return timeframe_ago

def check_for_new_trades():
    # Download and extract the zip file containing trade data
    r = requests.get(zip_file_url)
    zipfile_name = f'{current_year}FD.zip'
    with open(zipfile_name, 'wb') as f:
        f.write(r.content)

    with zipfile.ZipFile(zipfile_name) as z:
        z.extractall('.')

    trades = []
    file_name = f'{current_year}FD.xml'
    tree = ET.parse(file_name)
    root = tree.getroot()

    two_months_ago = get_two_months_ago()

    for member_element in root.findall('Member'):
        try:
            first_name = member_element.find('First').text
            last_name = member_element.find('Last').text
            doc_id = member_element.find('DocID').text
            filing_date_str = member_element.find('FilingDate').text

            full_name = f"{first_name} {last_name}"
            if full_name in TARGET_MEMBERS:
                dt = datetime.strptime(filing_date_str, '%m/%d/%Y')
                # Only include trades from the past 2 months
                if dt >= two_months_ago:
                    member = full_name
                    trades.append((member, dt, doc_id))
        except Exception as e:
            print(f"Error processing member: {e}")
            continue

    # Sort trades by date (newest first)
    trades.sort(key=lambda x: x[1], reverse=True)
    print(trades)
    return trades

# Convert markdown to HTML
def markdown_to_html(markdown_text):
    html = markdown.markdown(
        markdown_text,
        extensions=['tables', 'fenced_code', 'nl2br']
    )
    return html


def send_email_notification(trades):
    if not trades:
        return

    # Build a subject with only the members present in the new trades.
    notified_members = sorted(set(trade[0] for trade in trades))
    subject = f"New Trade(s) Detected for {', '.join(notified_members)}"

    # Build the email body using all trade details.
    body = "New trades have been detected:\n\n"
    for trade in trades:
        body += f"Member: {trade[0]}\n"
        body += f"Date: {trade[1].strftime('%Y-%m-%d')}\n"
        body += f"Document ID: {trade[2]}\n"
        body += f"PDF URL: {pdf_file_url}{trade[2]}.pdf\n\n"
        # Include the AI-generated text from the PDF extractor
        pdf_extractor_enabled = os.getenv("PDF_EXRACTOR", "True").lower() == "true"
        if pdf_extractor_enabled:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if api_key:
                print(f"Extracting content from {pdf_file_url}{trade[2]}.pdf")
                extracted_content = extract_pdf_content(f"{pdf_file_url}{trade[2]}.pdf", api_key)
                print(extracted_content)
                extracted_content=markdown_to_html(extracted_content)
                body += f"\n{extracted_content}\n\n"

    # Convert markdown to HTML
    html_body = markdown_to_html(body)

    # Send a separate email for each recipient to avoid multiple To headers
    recipients = [recipient.strip() for recipient in RECIPIENT_EMAIL.split(',')]
    for recipient in recipients:
        print(f"Sending email to {recipient}")
        msg = MIMEMultipart()
        # Set the From header to include the sender name and email address.
        msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        styled_html = f"""
        <html>
        <head>
        <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.5;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 1em;
        }}
        th, td {{
            border: 1px solid #999;
            padding: 8px;
            text-align: left;
            font-size: 14px;
        }}
        thead {{
            background-color: #f2f2f2;
        }}
        </style>
        </head>
        <body>
        {html_body}
        </body>
        </html>
        """

        msg.attach(MIMEText(styled_html, 'html'))
        server.sendmail(SENDER_EMAIL, recipient, msg.as_string())

    print(f"Sent an email notification for {len(trades)} new trades.")

# --- Persistence functions to track processed trades ---

def load_processed_trades():
    """
    Load the set of processed trade document IDs from the configured file.
    If the file doesn’t exist, return an empty set.
    """
    processed = set()
    if os.path.exists(PROCESSED_TRADES_FILE):
        with open(PROCESSED_TRADES_FILE, "r") as f:
            for line in f:
                processed.add(line.strip())
    return processed

def save_processed_trades(new_doc_ids):
    """
    Append new trade document IDs to the configured file so they aren’t processed again.
    """
    with open(PROCESSED_TRADES_FILE, "a") as f:
        for doc_id in new_doc_ids:
            f.write(doc_id + "\n")




def main():
    # Load previously processed trades from the persistent storage
    processed_trades = load_processed_trades()
    last_check = datetime.now() - timedelta(minutes=10)

    while True:
        current_time = datetime.now()
        if current_time - last_check >= timedelta(minutes=5):
            print("Checking for new trades...")
            all_trades = check_for_new_trades()

            # Filter out any trades that have already been processed
            new_trades = [trade for trade in all_trades if trade[2] not in processed_trades]

            # Print all PDF URLs of new trades
            if not new_trades: print("No new trades found.")

            if new_trades:
                print("New trades have been detected:")
                pdf_links = []
                for trade in new_trades:
                    pdf_url = f"{pdf_file_url}{trade[2]}.pdf"
                    pdf_links.append(pdf_url)
                    print(f"Member: {trade[0]}")
                    print(f"Date: {trade[1].strftime('%Y-%m-%d')}")
                    print(f"Document ID: {trade[2]}")
                    print(f"PDF URL: {pdf_url}\n")

                # Analyze each PDF link
            if sendEmail==False:
                pdf_extractor_enabled = os.getenv("PDF_EXRACTOR", "True").lower() == "true"
                if pdf_extractor_enabled:
                    print("Analyzing PDFs...")
                    for pdf_url in pdf_links:
                        api_key = os.getenv("OPENROUTER_API_KEY")
                        if not api_key:
                            print("Error: OPENROUTER_API_KEY not found in environment variables. Please set it in .env file.")
                            continue  # Skip PDF extraction if API key is missing
                        extracted_content = extract_pdf_content(pdf_url, api_key)
                        print(f"Extracted Content for {pdf_url}:\n{extracted_content}\n")

            # ADDED: Conditionally send email
            if new_trades and sendEmail:
                send_email_notification(new_trades)
                # Add the new trade document IDs to our processed set and persistent storage
                new_doc_ids = [trade[2] for trade in new_trades]
                processed_trades.update(new_doc_ids)
                save_processed_trades(new_doc_ids)

            last_check = current_time
        time.sleep(60)

if __name__ == "__main__":
    main()
