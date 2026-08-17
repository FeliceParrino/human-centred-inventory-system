import os
import secrets
from datetime import datetime
from datetime import timedelta
from decimal import Decimal

from dotenv import load_dotenv
from flask import Flask, Response, redirect, request, render_template, session, flash, url_for

load_dotenv()

from database import get_connection
from models.dashboard_data import get_dashboard_summary
from models.form_utils import (
    get_money_amount,
    get_optional_positive_int,
    get_positive_int,
    get_report_date_filters
)
from models.inventory_data import (
    fetch_active_product,
    fetch_categories,
    fetch_category,
    fetch_products,
    get_user_category_id
)
from models.pdf_utils import configure_pdf_native_libraries
from models.product import Product
from models.report_data import fetch_report_transactions
from models.schema import ensure_category_schema, ensure_user_privacy_schema
from models.transaction import PurchaseTransaction, SellTransaction
from models.user import User
from models.user_data import fetch_user_by_id, send_password_reset_email



app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']
PRIVACY_NOTICE_VERSION = 'UK-GDPR-2026-06'



@app.route('/')
def home():
    return redirect('/login')


@app.route('/privacy_notice')
def privacy_notice():
    return render_template(
        'privacy_notice.html',
        privacy_version=PRIVACY_NOTICE_VERSION
    )


# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    ensure_user_privacy_schema()
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        fullName = request.form.get('fullName', '').strip()
        email = request.form.get('email', '').strip().lower()
        businessName = request.form.get('businessName', '').strip()
        businessType = request.form.get('businessType', '').strip()
        password = request.form.get('password', '')
        confirmPassword = request.form.get('confirmPassword', '')
        privacyConsent = request.form.get('privacyConsent') == 'on'
        form_data = {
            'username': username,
            'fullName': fullName,
            'email': email,
            'businessName': businessName,
            'businessType': businessType,
            'privacyConsent': privacyConsent
        }

        if not username or not fullName or not email or not businessName or not password:
            return render_template(
                'register.html',
                error='All fields are required except Business type.',
                form_data=form_data
            )

        if not privacyConsent:
            return render_template(
                'register.html',
                error='You must accept the privacy notice to create an account.',
                form_data=form_data
            )

        if password != confirmPassword:
            return render_template(
                'register.html',
                error='Passwords do not match.',
                form_data=form_data
            )

        user = User(None, username, User.hash_password(password))
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''
                INSERT INTO `user`
                    (username, email, fullName, businessName, businessType, password,
                     privacyConsent, privacyConsentAt, privacyNoticeVersion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                ''',
                (
                    user.username, email, fullName, businessName, businessType,
                    user.password, 1, PRIVACY_NOTICE_VERSION
                )
            )
            conn.commit()
        except Exception:
            conn.rollback()
            return render_template(
                'register.html',
                error='Username or email already exists.',
                form_data=form_data
            )
        finally:
            cursor.close()
            conn.close()
        return redirect('/login')
    return render_template('register.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    ensure_user_privacy_schema()
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM `user` WHERE username = %s OR email = %s', (username, username.lower()))
        user_row = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_row:
            user = User(user_row['userID'], user_row['username'], user_row['password'])
        else:
            user = None

        if user and user.verify_password(password):
            session['userID'] = user.userID
            session['username'] = user.username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')


# Password Reset Request Route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    ensure_user_privacy_schema()
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT userID, email FROM `user` WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            token = secrets.token_urlsafe(32)
            tokenHash = User.hash_password(token)
            expiresAt = datetime.now() + timedelta(minutes=30)
            cursor.execute(
                'INSERT INTO password_reset (userID, tokenHash, expiresAt) VALUES (%s, %s, %s)',
                (user['userID'], tokenHash, expiresAt)
            )
            conn.commit()
            reset_url = url_for('reset_password', token=token, _external=True)
            sent = send_password_reset_email(user['email'], reset_url)
            if not sent:
                flash(f'Development reset link: {reset_url}', 'success')

        cursor.close()
        conn.close()
        flash('If that email exists, a password reset link has been sent.', 'success')
        return redirect('/login')

    return render_template('forgot_password.html')


# Password Reset Route
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    ensure_user_privacy_schema()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        '''
        SELECT resetID, userID, tokenHash, expiresAt, usedAt
        FROM password_reset
        WHERE usedAt IS NULL AND expiresAt > NOW()
        ORDER BY createdAt DESC
        '''
    )
    reset_rows = cursor.fetchall()
    reset_row = None

    for row in reset_rows:
        if User(None, None, row['tokenHash']).verify_password(token):
            reset_row = row
            break

    if not reset_row:
        cursor.close()
        conn.close()
        flash('Password reset link is invalid or expired.', 'error')
        return redirect('/forgot_password')

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirmPassword = request.form.get('confirmPassword', '')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return redirect(url_for('reset_password', token=token))

        if password != confirmPassword:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('reset_password', token=token))

        cursor.execute(
            'UPDATE `user` SET password = %s WHERE userID = %s',
            (User.hash_password(password), reset_row['userID'])
        )
        cursor.execute(
            'UPDATE password_reset SET usedAt = NOW() WHERE resetID = %s',
            (reset_row['resetID'],)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Password updated successfully. You can now sign in.', 'success')
        return redirect('/login')

    cursor.close()
    conn.close()
    return render_template('reset_password.html', token=token)


# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'userID' not in session:
        return redirect('/login')

    summary = get_dashboard_summary(session['userID'])

    return render_template(
        'dashboard.html',
        username=session['username'],
        summary=summary,
        products=summary['products']
    )


# Manage Inventory Route
@app.route('/manage_inventory')
def manage_inventory():
    if 'userID' not in session:
        return redirect('/login')

    products = fetch_products(session['userID'])
    categories = fetch_categories(session['userID'])
    autocomplete_products = [
        {'id': product['productID'], 'name': product['name']}
        for product in products
    ]

    return render_template(
        'manage_inventory.html',
        username=session['username'],
        products=products,
        categories=categories,
        autocomplete_products=autocomplete_products
    )


# Profile Route
@app.route('/profile')
def profile():
    if 'userID' not in session:
        return redirect('/login')

    user = fetch_user_by_id(session['userID'])
    summary = get_dashboard_summary(session['userID'])
    categories = fetch_categories(session['userID'])
    transactions = fetch_report_transactions(session['userID'])

    return render_template(
        'profile.html',
        username=session['username'],
        user=user,
        userID=session['userID'],
        summary=summary,
        categories=categories,
        transactions=transactions
    )


# Add Category Route
@app.route('/add_category', methods=['POST'])
def add_category():
    if 'userID' not in session:
        return redirect('/login')

    ensure_category_schema()
    name = request.form.get('name', '').strip()

    if not name:
        flash('Please enter a valid category name.', 'error')
        return redirect('/manage_inventory')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO category (name, userID) VALUES (%s, %s)",
            (name, session['userID'])
        )
        conn.commit()
        flash(f'Category "{name}" added successfully.', 'success')
    except Exception:
        conn.rollback()
        flash(f'Category "{name}" already exists.', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect('/manage_inventory')


# Edit Category Route
@app.route('/edit_category/<int:categoryID>', methods=['GET', 'POST'])
def edit_category(categoryID):
    if 'userID' not in session:
        return redirect('/login')

    category = fetch_category(categoryID, session['userID'])
    if not category:
        flash('Category not found.', 'error')
        return redirect('/manage_inventory')

    if request.method == 'POST':
        name = request.form.get('name', '').strip()

        if not name:
            flash('Please enter a valid category name.', 'error')
            return redirect(url_for('edit_category', categoryID=categoryID))

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'UPDATE category SET name = %s WHERE categoryID = %s AND userID = %s',
                (name, categoryID, session['userID'])
            )
            conn.commit()
            flash(f'Category updated to "{name}".', 'success')
            return redirect('/manage_inventory')
        except Exception:
            conn.rollback()
            flash(f'Category "{name}" already exists.', 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template(
        'edit_category.html',
        username=session['username'],
        category=category
    )


# Add Product Route
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'userID' not in session:
        return redirect('/login')

    name = request.form.get('name', '').strip()
    stock = get_positive_int('stock')
    costPrice = get_money_amount('costPrice')
    salePrice = get_money_amount('salePrice')
    categoryID = get_optional_positive_int('categoryID')
    userID = session['userID']

    if not name or stock is None or costPrice is None or salePrice is None:
        flash('Please enter valid product, stock, cost, and sale price values.', 'error')
        return redirect('/manage_inventory')

    categoryID = get_user_category_id(categoryID, userID)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Insert product
    cursor.execute(
        "INSERT INTO product (name, stock, userID, categoryID, costPrice, salePrice) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, stock, userID, categoryID, costPrice, salePrice)
    )
    productID = cursor.lastrowid
    product = Product(productID, name, 0)
    transaction = PurchaseTransaction(None, product, stock)
    transaction.execute()

    # Log purchase transaction
    cursor.execute(
        "INSERT INTO transaction (type, timestamp, productID, amount, totalValue) VALUES (%s, NOW(), %s, %s, %s)",
        ('purchase', productID, stock, stock * costPrice)
    )

    conn.commit()
    cursor.close()
    conn.close()

    flash(f'Successfully added {stock} unit(s) of {name}.', 'success')

    return redirect('/manage_inventory')


# Edit Product Route
@app.route('/edit_product/<int:productID>', methods=['GET', 'POST'])
def edit_product(productID):
    if 'userID' not in session:
        return redirect('/login')

    product = fetch_active_product(productID, session['userID'])
    if not product:
        flash('Product not found.', 'error')
        return redirect('/manage_inventory')

    categories = fetch_categories(session['userID'])

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        categoryID = get_optional_positive_int('categoryID')
        costPrice = get_money_amount('costPrice')
        salePrice = get_money_amount('salePrice')

        if not name or costPrice is None or salePrice is None:
            flash('Please enter a valid product name and price values.', 'error')
            return redirect(url_for('edit_product', productID=productID))

        categoryID = get_user_category_id(categoryID, session['userID'])

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            UPDATE product
            SET name = %s, categoryID = %s, costPrice = %s, salePrice = %s
            WHERE productID = %s AND userID = %s
            ''',
            (name, categoryID, costPrice, salePrice, productID, session['userID'])
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash(f'Product "{name}" updated successfully.', 'success')
        return redirect('/manage_inventory')

    return render_template(
        'edit_product.html',
        username=session['username'],
        product=product,
        categories=categories
    )


# Sell Product Route
@app.route('/sell_product', methods=['POST'])
def sell_product():
    if 'userID' not in session:
        return redirect('/login')

    productID = get_positive_int('productID')
    amount = get_positive_int('amount')

    if productID is None or amount is None:
        flash('Please select a product and enter a valid amount.', 'error')
        return redirect('/manage_inventory')

    # Get product and verify ownership
    row = fetch_active_product(productID, session['userID'])

    if not row:
        return redirect('/manage_inventory')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    product = Product(row['productID'], row['name'], row['stock'])
    transaction = SellTransaction(None, product, amount)

    if transaction.execute() == "Sale successful.":
        cursor.execute(
            'UPDATE product SET stock = %s WHERE productID = %s',
            (product.get_stock(), productID)
        )
        cursor.execute(
            "INSERT INTO transaction (type, timestamp, productID, amount, totalValue) VALUES (%s, NOW(), %s, %s, %s)",
            ('sell', productID, amount, Decimal(str(row.get('salePrice') or 0)) * amount)
        )
        conn.commit()
        
        flash(f'Successfully sold {amount} unit(s) of {row["name"]}. New stock: {product.get_stock()}.', 'success')
    else:
        flash(f'Not enough stock. "{row["name"]}" only has {row["stock"]} unit(s) available.', 'error')

    cursor.close()
    conn.close()
    return redirect('/manage_inventory')


# Update Product Prices Route
@app.route('/update_product_prices', methods=['POST'])
def update_product_prices():
    if 'userID' not in session:
        return redirect('/login')

    productID = get_positive_int('productID')
    costPrice = get_money_amount('costPrice')
    salePrice = get_money_amount('salePrice')

    if productID is None or costPrice is None or salePrice is None:
        flash('Please select a product and enter valid price values.', 'error')
        return redirect('/manage_inventory')

    row = fetch_active_product(productID, session['userID'])

    if not row:
        flash('Product not found.', 'error')
        return redirect('/manage_inventory')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE product SET costPrice = %s, salePrice = %s WHERE productID = %s AND userID = %s',
        (costPrice, salePrice, productID, session['userID'])
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash(f'Prices updated for "{row["name"]}".', 'success')
    return redirect('/manage_inventory')


# Restock Product Route
@app.route('/restock_product', methods=['POST'])
def restock_product():
    if 'userID' not in session:
        return redirect('/login')

    productID = get_positive_int('productID')
    amount = get_positive_int('amount')

    if productID is None or amount is None:
        flash('Please select a product and enter a valid amount.', 'error')
        return redirect('/manage_inventory')

    row = fetch_active_product(productID, session['userID'])

    if not row:
        return redirect('/manage_inventory')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    product = Product(row['productID'], row['name'], row['stock'])
    transaction = PurchaseTransaction(None, product, amount)
    transaction.execute()

    cursor.execute(
        'UPDATE product SET stock = %s WHERE productID = %s',
        (product.get_stock(), productID)
    )
    cursor.execute(
        "INSERT INTO transaction (type, timestamp, productID, amount, totalValue) VALUES (%s, NOW(), %s, %s, %s)",
        ('restock', productID, amount, Decimal(str(row.get('costPrice') or 0)) * amount)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash(f'Successfully restocked {amount} unit(s) of {row["name"]}. New stock: {product.get_stock()}.', 'success')
    return redirect('/manage_inventory')

# Delete Product route
@app.route('/delete_product', methods=['POST'])
def delete_product():
    if 'userID' not in session:
        return redirect('/login')

    productID = get_positive_int('productID')

    if productID is None:
        flash('Please select a valid product.', 'error')
        return redirect('/manage_inventory')

    row = fetch_active_product(productID, session['userID'])

    if not row:
        flash('Product not found.', 'error')
        return redirect('/manage_inventory')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'UPDATE product SET stock = %s WHERE productID = %s AND userID = %s',
        (0, productID, session['userID'])
    )
    cursor.execute(
        "INSERT INTO transaction (type, timestamp, productID, amount, totalValue) VALUES (%s, NOW(), %s, %s, %s)",
        ('delete', productID, 0, 0)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash(f'Product "{row["name"]}" deleted successfully.', 'success')
    return redirect('/manage_inventory')

# Stock Report Route — renders a page with all transactions
@app.route('/stock_report')
def stock_report():
    if 'userID' not in session:
        return redirect('/login')

    start_date, end_date, date_error = get_report_date_filters()
    if date_error:
        flash(date_error, 'error')

    if date_error:
        transactions = fetch_report_transactions(session['userID'])
    else:
        transactions = fetch_report_transactions(session['userID'], start_date, end_date)

    return render_template(
        'stock_report.html',
        transactions=transactions,
        username=session['username'],
        start_date=start_date,
        end_date=end_date
    )


@app.route('/download_report')
def download_report():
    if 'userID' not in session:
        return redirect('/login')

    start_date, end_date, date_error = get_report_date_filters()
    if date_error:
        flash(date_error, 'error')
        return redirect('/stock_report')

    transactions = fetch_report_transactions(session['userID'], start_date, end_date)
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M')
    report_range = 'All dates'

    if start_date and end_date:
        report_range = f'{start_date} to {end_date}'
    elif start_date:
        report_range = f'From {start_date}'
    elif end_date:
        report_range = f'Until {end_date}'

    html = render_template(
        'report_download.html',
        transactions=transactions,
        username=session['username'],
        start_date=start_date,
        end_date=end_date,
        report_range=report_range,
        generated_at=generated_at
    )
    filename_start = start_date or 'all'
    filename_end = end_date or 'all'
    filename = f'inventory-report-{filename_start}-to-{filename_end}.html'

    return Response(
        html,
        mimetype='text/html',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@app.route('/download_report_pdf')
def download_report_pdf():
    if 'userID' not in session:
        return redirect('/login')

    configure_pdf_native_libraries()
    try:
        from weasyprint import HTML
    except (ImportError, OSError):
        flash('PDF export requires WeasyPrint. Please install project requirements first.', 'error')
        return redirect(url_for(
            'stock_report',
            start_date=request.args.get('start_date', ''),
            end_date=request.args.get('end_date', '')
        ))

    start_date, end_date, date_error = get_report_date_filters()
    if date_error:
        flash(date_error, 'error')
        return redirect('/stock_report')

    transactions = fetch_report_transactions(session['userID'], start_date, end_date)
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M')
    report_range = 'All dates'

    if start_date and end_date:
        report_range = f'{start_date} to {end_date}'
    elif start_date:
        report_range = f'From {start_date}'
    elif end_date:
        report_range = f'Until {end_date}'

    html = render_template(
        'report_download.html',
        transactions=transactions,
        username=session['username'],
        start_date=start_date,
        end_date=end_date,
        report_range=report_range,
        generated_at=generated_at
    )
    pdf = HTML(string=html, base_url=request.url_root).write_pdf()
    filename_start = start_date or 'all'
    filename_end = end_date or 'all'
    filename = f'inventory-report-{filename_start}-to-{filename_end}.pdf'

    return Response(
        pdf,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


if __name__ == '__main__':
    app.run(debug=True, port=5001)
