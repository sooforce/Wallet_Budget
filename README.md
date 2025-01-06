Personal Finance Management Application

Introduction
This Personal Finance Management Application is a web-based tool designed to help users manage their income, expenses, and savings effectively. It enables users to track their financial habits, generate reports, and make better financial decisions. The application is built using Flask and SQLite with a user-friendly interface for seamless financial management.

Features
User Authentication

Secure user registration and login with password hashing.
Session management for user-specific data security.
Expense Management

Add, edit, and categorize expenses (Investment, Entertainment, Living).
View expense summaries directly on the dashboard.
Salary Tracking

Record monthly income and split it across financial goals (Investment, Entertainment, Living).
Automatically reset expenses and salaries at the start of a new month.
Dynamic Dashboard

Interactive forms for adding expenses, updating financial settings, and entering salary details.
PDF Report Generation

Export monthly financial reports in PDF format for offline use.
Vault Summary

Overview of savings across financial categories after deducting expenses.
Administrative Features

Admin tools for managing users, expenses, salaries, and resetting the database.
Responsive Design

Optimized for all devices with clean and intuitive navigation.
Installation


Clone the Repository

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
Set Up Virtual Environment

python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate     # For Windows

```
Install Dependencies

```bash
pip install -r requirements.txt

```
Set Up the Database

The application uses SQLite as the database.
Run the following command to initialize the database:

```bash
flask db init
flask db migrate
flask db upgrade

```
Run the Application

```bash
flask run
```
The application will be available at http://127.0.0.1:5000/.

Usage

Navigate to the registration page to create a new account.
Log in with your credentials to access the dashboard.
Use the dashboard to:
Add and categorize expenses.
Update financial settings.
Enter your monthly salary.
Export monthly financial reports in PDF format via the "Reports" section.
View savings breakdown in the "Vault" section.
Admin users can manage users, expenses, and reset the database via the "Analytics" section.


![image](https://github.com/user-attachments/assets/8807b0be-b58d-4386-a7aa-4099b6ecaf81)


Technologies Used

Backend: Flask, SQLite
Frontend: HTML, CSS, JavaScript
PDF Generation: FPDF
Security: Werkzeug (Password Hashing)
Development Tools: Python, Virtual Environment

Future Enhancements

Add multi-user roles for advanced admin functionalities.
Implement visualization tools for financial data (e.g., charts).
Enable email notifications for financial updates and reports.
Introduce AI-based financial insights.

Contributing

Contributions are welcome! Please fork this repository and create a pull request with detailed descriptions of your changes.
