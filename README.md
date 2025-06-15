# Nancy Pelosi Trades Notifier

This project checks for new financial disclosures related to Nancy Pelosi and sends email notifications when new trades are detected.

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

This script downloads financial disclosure data, checks for new trades involving Nancy Pelosi, and sends email notifications with details of the trades.

## Preview
![image](https://github.com/abdkhan-git/trade-like-nancy/assets/81310252/caf9be67-0bab-4fb8-8390-b4b4539556de)
![image](https://github.com/abdkhan-git/trade-like-nancy/assets/81310252/56b9c3b7-a864-4c4f-95b2-58a395b00ed3)

## Video Demo
[Short Video Demo](https://youtu.be/FH6rDpEqSJc)

## Features

- Downloads financial disclosure data.
- Checks for new trades related to House Members.
- Sends email notifications with trade details.

## Prerequisites

- Python 3.x
- Required Python packages listed in `requirements.txt`

## Installation

1. Clone the repository:
 
2. Install the required Python packages:
pip install -r requirements.txt

## Configuration
1. Create a .env file in the project directory and add your email configuration:
- SENDER_EMAIL=your_email@example.com
- APP_PASSWORD=your_app_password
- RECIPIENT_EMAIL=recipient@example.com,email2@example.com
- EMAIL_SERVER=your.smtp.server.com
- EMAIL_PORT=465
- TARGET_MEMBERS=Pelosi,McCarthy,Schumer

2. Ensure your .gitignore file includes the .env file to avoid pushing sensitive information to GitHub:

## Usage
Run the script:
python your_script.py

## License
This project is licensed under the MIT License - see the LICENSE file for details.
