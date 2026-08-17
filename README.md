# Human-Centred Inventory Management System

A web-based inventory management system designed for small businesses, built with Flask and MySQL.

The project focuses on making everyday stock management simpler, clearer, and more efficient while keeping people at the centre of the decision-making process.

🏆 **Best Poster Award – First Place**
Presented at the Human Work Interaction Design (HWID) Conference, University of West London.

---

## Overview

This project was originally developed as a university software development project and later expanded into a more complete human-centred inventory platform for small businesses.

The system supports secure account access, product management, category management, stock movements, transaction reporting, pricing, business summaries, and downloadable reports.

The current version also introduces a clearer business dashboard with stock values, potential margin, low-stock monitoring, category-based information, and transaction activity.

---

## Features

* User registration and authentication
* Password reset by email
* User and business profiles
* Privacy consent and UK GDPR notice
* Product creation and editing
* Custom product categories
* Stock purchase and restock management
* Product sales
* Low-stock indicators
* Cost price and sale price management
* Current stock cost and sale value
* Potential margin calculation
* Sales and restock value summaries
* Transaction history
* Date-based transaction filtering
* Downloadable PDF stock reports
* Responsive dashboard interface
* Unit testing for core models

---

## Business Dashboard

The dashboard provides a quick overview of:

* Total products
* Total stock
* Product categories
* Low-stock products
* Stock movements
* Current stock cost
* Current sale value
* Potential margin
* Sales revenue
* Restock spending

It also includes visual summaries of stock movements and stock distribution by category.

---

## Technology Stack

**Backend**

* Python
* Flask
* Object-Oriented Programming

**Database**

* MySQL
* MySQL Connector for Python

**Frontend**

* HTML
* CSS
* JavaScript
* Jinja2 templates

**Other Tools**

* Werkzeug
* WeasyPrint
* python-dotenv
* unittest

---

## Project Structure

```text
human-centred-inventory-system/
│
├── app.py
├── database.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── models/
│   ├── product.py
│   ├── transaction.py
│   ├── user.py
│   ├── dashboard_data.py
│   ├── inventory_data.py
│   ├── report_data.py
│   ├── user_data.py
│   ├── form_utils.py
│   ├── schema.py
│   └── pdf_utils.py
│
├── templates/
│   ├── dashboard.html
│   ├── manage_inventory.html
│   ├── stock_report.html
│   ├── profile.html
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── edit_product.html
│   ├── edit_category.html
│   ├── privacy_notice.html
│   └── report_download.html
│
├── static/
│   ├── CSS/
│   └── js/
│
├── database/
│   └── retail_inventory_db.sql
│
└── tests/
    └── test_models.py
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/FeliceParrino/human-centred-inventory-system.git
cd human-centred-inventory-system
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template.

Example:

```env
SECRET_KEY=your-secret-key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-database-password
DB_PORT=3306
DB_NAME=retail_inventory_2

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
SMTP_FROM=your-email@example.com
```

### 5. Set up the database

Import the SQL file located in:

```text
database/retail_inventory_db.sql
```

into MySQL.

### 6. Run the application

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

---

## Testing

The project includes unit tests for the main object-oriented components, including:

* Product stock management
* Purchase transactions
* Sale transactions
* Password hashing
* Password verification

Run the tests with:

```bash
python -m unittest tests/test_models.py
```

---

## Human-Centred Design

The project follows a human-centred approach inspired by Industry 5.0 and Human Work Interaction Design.

The purpose of the system is not to remove people from inventory decisions, but to reduce repetitive work and provide clearer information that helps small business workers make better decisions.

The interface therefore focuses on:

* Clear navigation
* Simple forms
* Visible feedback
* Low-stock warnings
* Accessible business information
* Reduced manual inventory work

---

## Future Development

A major planned development is the integration of **AI-supported demand forecasting and decision support**.

Future functionality could use historical sales and stock data to:

* Forecast future product demand
* Identify potential stockout risks
* Suggest reorder quantities
* Detect unusual stock patterns
* Support inventory planning

The intended approach remains human-centred:

> **AI should support the decision, not replace the person making it.**

AI-generated recommendations would therefore be presented as decision support, with the final decision remaining with the business user.

Other possible future developments include:

* Barcode scanning
* Cloud deployment
* More advanced analytics
* Role-based user access
* Automated low-stock notifications
* Supplier management
* Improved reporting and forecasting

---

## Award

This project was presented as:

**Human-Centred Retail Inventory Management System for Small Businesses**

at the **Human Work Interaction Design (HWID) Conference** at the University of West London.

The project received:

**Best Poster Award – First Place**

---

## License

Copyright © 2026 Felice Parrino. All rights reserved.

This project is publicly available for portfolio and demonstration purposes only.

No permission is granted to copy, modify, distribute, sublicense, sell, or use this software for commercial purposes without prior written permission from the author.

---

## Author

**Felice Parrino**

Computer Science Student
London, United Kingdom

GitHub: FeliceParrino
LinkedIn: [in/felice-parrino-b43940259](https://www.linkedin.com/in/felice-parrino-b43940259/)
