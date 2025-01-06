from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_ECHO'] = True  # Enable SQLAlchemy logging

# Log absolute database path
db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace("sqlite:///", "")
absolute_path = os.path.abspath(db_path)
print(f"Absolute path to database: {absolute_path}")

db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    salaries = db.relationship('Salary', backref='owner', lazy=True)
    expenses = db.relationship('Expense', backref='owner', lazy=True)
    settings = db.relationship('Setting', backref='owner', lazy=True)


class Salary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    investment_percentage = db.Column(db.Float, nullable=False, default=20)
    entertainment_percentage = db.Column(db.Float, nullable=False, default=30)
    living_percentage = db.Column(db.Float, nullable=False, default=50)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Vault(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_investment = db.Column(db.Float, nullable=False, default=0)
    total_entertainment = db.Column(db.Float, nullable=False, default=0)
    total_living = db.Column(db.Float, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/favicon.ico')
def favicon():
    try:
        return send_file('static/favicon.ico')
    except FileNotFoundError:
        return '', 204  # No Content



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        # Create default settings for the user
        default_setting = Setting(user_id=new_user.id)
        db.session.add(default_setting)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    settings = Setting.query.filter_by(user_id=user_id).first()
    return render_template('dashboard.html', user=user, settings=settings)


@app.route('/save_salary', methods=['POST'])
def save_salary():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 401
    user_id = session['user_id']

    # Generate PDF for the past month
    export_pdf(user_id)

    # Reset expenses and salaries for the new month
    Expense.query.filter_by(user_id=user_id).delete()
    Salary.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # Save the new salary
    data = request.get_json()
    amount = float(data['salary'])
    date = datetime.now()
    salary = Salary(amount=amount, date=date, user_id=user_id)
    db.session.add(salary)
    db.session.commit()

    # Get user settings
    settings = Setting.query.filter_by(user_id=user_id).first()
    investment_percentage = settings.investment_percentage / 100
    entertainment_percentage = settings.entertainment_percentage / 100
    living_percentage = settings.living_percentage / 100

    # Calculate amounts
    total_investment = amount * investment_percentage
    total_entertainment = amount * entertainment_percentage
    total_living = amount * living_percentage

    # Save to Vault
    vault = Vault.query.filter_by(user_id=user_id).first()
    if vault:
        vault.total_investment = total_investment
        vault.total_entertainment = total_entertainment
        vault.total_living = total_living
    else:
        vault = Vault(total_investment=total_investment, total_entertainment=total_entertainment, total_living=total_living, user_id=user_id)
        db.session.add(vault)
    db.session.commit()

    return jsonify({'message': 'Salary saved successfully and report generated'})


@app.route('/vault')
def vault():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    vault = Vault.query.filter_by(user_id=user_id).first()

    # Initialize values if no vault entry is found
    if vault is None:
        total_investment = 0
        total_entertainment = 0
        total_living = 0
    else:
        total_investment = vault.total_investment
        total_entertainment = vault.total_entertainment
        total_living = vault.total_living

    expenses = Expense.query.filter_by(user_id=user_id).all()

    for expense in expenses:
        if expense.category == 'Investment':
            total_investment -= expense.amount
        elif expense.category == 'Entertainment':
            total_entertainment -= expense.amount
        elif expense.category == 'Living':
            total_living -= expense.amount

    return render_template('vault.html', total_investment=total_investment, total_entertainment=total_entertainment,
                           total_living=total_living)


@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 401
    user_id = session['user_id']
    data = request.get_json()
    amount = data['amount']
    description = data['description']
    category = data['category']
    date = datetime.now()
    expense = Expense(amount=amount, description=description, category=category, date=date, user_id=user_id)
    db.session.add(expense)
    db.session.commit()
    return jsonify({'message': 'Expense added successfully'})


@app.route('/save_settings', methods=['POST'])
def save_settings():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 401
    user_id = session['user_id']
    data = request.get_json()
    investment = data['investment']
    entertainment = data['entertainment']
    living = data['living']
    setting = Setting.query.filter_by(user_id=user_id).first()
    if setting:
        setting.investment_percentage = investment
        setting.entertainment_percentage = entertainment
        setting.living_percentage = living
    else:
        new_setting = Setting(investment_percentage=investment, entertainment_percentage=entertainment,
                              living_percentage=living, user_id=user_id)
        db.session.add(new_setting)
    db.session.commit()
    return jsonify({'message': 'Settings saved successfully'})


@app.route('/export_pdf', methods=['GET'])
def export_pdf_route():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 401
    user_id = session['user_id']
    return send_file(export_pdf(user_id), as_attachment=True)


def export_pdf(user_id):
    user = User.query.get(user_id)
    expenses = Expense.query.filter_by(user_id=user_id).all()
    salaries = Salary.query.filter_by(user_id=user_id).all()
    settings = Setting.query.filter_by(user_id=user_id).all()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Monthly Report", ln=True, align='C')

    pdf.cell(200, 10, txt=f"User: {user.username}", ln=True, align='L')
    pdf.cell(200, 10, txt="Salaries:", ln=True, align='L')
    for salary in salaries:
        pdf.cell(200, 10, txt=f"Date: {salary.date.strftime('%Y-%m-%d')} - Amount: {salary.amount}", ln=True, align='L')

    pdf.cell(200, 10, txt="Expenses:", ln=True, align='L')
    for expense in expenses:
        pdf.cell(200, 10, txt=f"Date: {expense.date.strftime('%Y-%m-%d')} - Amount: {expense.amount} - Description: {expense.description} - Category: {expense.category}", ln=True, align='L')

    reports_dir = os.path.join(os.getcwd(), 'static', 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    pdf_file_path = os.path.join(reports_dir, f'monthly_report_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf')
    pdf.output(pdf_file_path)

    return pdf_file_path




@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    reports_dir = os.path.join(os.getcwd(), 'static', 'reports')

    # Check if the directory exists, if not, create it
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    files = os.listdir(reports_dir)
    return render_template('reports.html', files=files)


@app.route('/delete_report/<filename>')
def delete_report(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    reports_dir = os.path.join(os.getcwd(), 'static', 'reports')
    file_path = os.path.join(reports_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('reports'))



@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    users = User.query.all()
    salaries = Salary.query.all()
    expenses = Expense.query.all()
    settings = Setting.query.all()
    vaults = Vault.query.all()

    return render_template('admin.html', users=users, salaries=salaries, expenses=expenses, settings=settings,vaults=vaults)


@app.route('/reset_database')
def reset_database():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if session['user_id'] != 1:  # Only allow the user with ID 1 (usually the admin) to reset the database
        return 'Unauthorized', 403

    db.drop_all()
    db.create_all()
    return 'Database reset successfully!'

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete_salary/<int:salary_id>')
def delete_salary(salary_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    salary = Salary.query.get(salary_id)
    if salary:
        db.session.delete(salary)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    expense = Expense.query.get(expense_id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('edit_user.html', user=user)

@app.route('/edit_salary/<int:salary_id>', methods=['GET', 'POST'])
def edit_salary(salary_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    salary = Salary.query.get(salary_id)
    if request.method == 'POST':
        salary.amount = request.form['amount']
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('edit_salary.html', salary=salary)

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    expense = Expense.query.get(expense_id)
    if request.method == 'POST':
        expense.amount = request.form['amount']
        expense.description = request.form['description']
        expense.category = request.form['category']
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('edit_expense.html', expense=expense)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
