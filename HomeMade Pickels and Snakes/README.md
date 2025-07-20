# Pickle Store E-Commerce Application

## Overview

This is a Flask-based e-commerce application for a pickle store, featuring user authentication, product catalog, shopping cart, and order management with AWS integration.

## Key Features

- User authentication (login/signup) with password hashing
- Product catalog with categories:
  - Non-vegetarian pickles
  - Vegetarian pickles
  - Snacks
- Shopping cart functionality
- Order processing with confirmation emails
- AWS integrations:
  - DynamoDB for user and order data
  - SNS for order notifications
- Responsive web interface

## Technical Stack

- **Backend**: Python Flask
- **Database**: AWS DynamoDB
- **Messaging**: AWS SNS
- **Email**: SMTP
- **Frontend**: HTML, CSS, JavaScript (with Jinja2 templates)

## Setup Instructions

### Prerequisites

- Python 3.7+
- AWS account with DynamoDB and SNS access
- SMTP email service credentials

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Lavanya-959/ACHAR-HOUSE.git
   cd PROJECT
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (see [Configuration](#configuration) section)

For development:
```bash
python app.py
``````


Demo accounts available:
- Username: `demo1` / Password: `password1`
- Username: `demo2` / Password: `password2`
- Admin: `admin` / Password: `admin123`

## Deployment

For production deployment:
1. Set `FLASK_ENV=production` in `.env`
2. Configure a production WSGI server (Gunicorn, uWSGI)
3. Set up a reverse proxy (Nginx, Apache)
4. Configure proper SSL certificates

## AWS Infrastructure Requirements

- DynamoDB tables:
  - Users
  - Orders
- SNS topic for order notifications
- IAM role with permissions for:
  - DynamoDB (read/write)
  - SNS (publish)

## Troubleshooting

- **Database connection issues**: Verify AWS credentials and region
- **Email sending failures**: Check SMTP credentials and server settings
- **SNS notifications not working**: Verify topic ARN and IAM permissions


