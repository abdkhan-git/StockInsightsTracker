# House Member Trades Notifier

This project monitors financial disclosures for U.S. House members, tracks stock trades, and provides notifications with detailed trade information. It can analyze PDF disclosures using AI-powered content extraction.

## Table of Contents

- [Nancy Pelosi Trades Notifier](#nancy-pelosi-trades-notifier)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)
  - [License](#license)

## Description

This Python application monitors financial disclosures for U.S. House members, tracks stock trades, and provides notifications with detailed trade information. It can analyze PDF disclosures using AI-powered content extraction to provide comprehensive trade details.

## Preview
![image](https://github.com/abdkhan-git/trade-like-nancy/assets/81310252/caf9be67-0bab-4fb8-8390-b4b4539556de)
![image](https://github.com/abdkhan-git/trade-like-nancy/assets/81310252/56b9c3b7-a864-4c4f-95b2-58a395b00ed3)

## Video Demo
[Short Video Demo](https://youtu.be/FH6rDpEqSJc)

## Features

- **Automated Disclosure Monitoring**: Downloads and processes financial disclosure data from the House Clerk's website
- **Targeted Member Tracking**: Monitors specific House members (configurable via environment variables)
- **Trade Analysis**: Extracts and formats stock trade information from PDF disclosures
- **Email Notifications**: Sends detailed email notifications for new trades
- **AI-Powered PDF Analysis**: Uses OpenRouter API to extract and format trade information from PDF documents
- **Persistent Tracking**: Maintains a record of processed trades to avoid duplicate notifications

## Prerequisites

- Python 3.x
- Required Python packages listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/house-member-trades-notifier.git
   cd house-member-trades-notifier
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project directory with the following variables:
   ```env
   # Email Configuration
   SENDER_EMAIL=your_email@example.com
   SENDER_NAME=Your Name
   APP_PASSWORD=your_app_password
   RECIPIENT_EMAIL=recipient1@example.com,recipient2@example.com
   EMAIL_SERVER=smtp.example.com
   EMAIL_PORT=465

   # Monitoring Configuration
   TARGET_MEMBERS=Pelosi,McCarthy,Schumer
   TIMEFRAME_DAYS=60

   # AI Configuration
   OPENROUTER_API_KEY=your_openrouter_api_key
   AI_MODEL=mistralai/mistral-small-3.2-24b-instruct:free
   PDF_EXRACTOR=True

   # Storage Configuration
   PROCESSED_TRADES_FILE=processed_trades.txt
   ```

2. Ensure your `.gitignore` file includes the `.env` file to avoid pushing sensitive information to GitHub:
   ```gitignore
   .env
   .venv/
   __pycache__/
   *.pyc
   ```

3. For Docker deployment, create a `.env` file with the same variables and mount it as a volume.

## Usage

1. Run the script:
   ```bash
   python nancy.py
   ```

2. The script will:
   - Continuously check for new financial disclosures
   - Monitor trades for the specified House members
   - Extract trade information from PDF documents
   - Send email notifications for new trades

3. To stop the script, use Ctrl+C in the terminal.

## Docker Deployment (Optional)

1. Build the Docker image:
   ```bash
   docker build -t house-member-trades-notifier .
   ```

2. Run the container:
   ```bash
   docker run -d --name trades-notifier \
     -v $(pwd)/.env:/app/.env \
     -v $(pwd)/processed_trades.txt:/app/processed_trades.txt \
     house-member-trades-notifier
   ```

## Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Run with debug logging:
   ```bash
   python -m debug nancy.py
   ```

## License
This project is licensed under the MIT License - see the LICENSE file for details.