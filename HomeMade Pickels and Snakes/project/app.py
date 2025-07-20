from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bcrypt import hashpw, gensalt, checkpw
import os
from decimal import Decimal

app = Flask(_name_)
app.secret_key = os.urandom(24)

# Context processor for current time
@app.context_processor
def inject_now():
    return {'now': datetime.now}

# AWS Resources
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
user_table = dynamodb.Table('Users')
orders_table = dynamodb.Table('Orders')

sns = boto3.client('sns', region_name='us-east-1')
SNS_TOPIC_ARN = 'YOUR_SNS_TOPIC_ARN'  # Replace this with your SNS topic ARN

# Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = 'meghanapriya794@gmail.com'
EMAIL_PASSWORD = 'ngkh yudn ljtz cizc'

# Product data
veg_pickles = [
    {'id': 1, 'name': 'Mango Pickle', 'price': 250, 'weight': '500g', 'spice_level': 5, 'description': 'Traditional raw mango chunks spiced and sun-cured.', 'image': '/static/images/mango.jpg', 'rating': 5},
    {'id': 2, 'name': 'Lemon Pickle', 'price': 220, 'weight': '500g', 'spice_level': 3, 'description': 'Zesty lemon pieces pickled with salt & spices.', 'image': '/static/images/lemon.jpg', 'rating': 4}
]

non_veg_pickles = [
    {'id': 9, 'name': 'Prawn Pickle', 'price': 599, 'weight': '500g', 'spice_level': 3, 'description': 'Spicy, tangy prawns soaked in coastal masala.', 'image': '/static/images/prawn.jpg', 'rating': 5}
]

snacks = [
    {'id': 15, 'name': 'Mixture', 'price': 99, 'weight': '250g', 'description': 'A crunchy blend of sev, nuts, spices.', 'image': '/static/images/mixture.jpg', 'rating': 5}
]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

@app.route('/veg_pickles')
def show_veg_pickles():
    return render_template('veg_pickles.html', products=veg_pickles)

@app.route('/non_veg_pickles')
def show_non_veg_pickles():
    return render_template('non_veg_pickles.html', products=non_veg_pickles)

@app.route('/snacks')
def show_snacks():
    return render_template('snacks.html', products=snacks)

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    results = []
    for item in veg_pickles + non_veg_pickles + snacks:
        if query in item['name'].lower():
            results.append({
                'name': item['name'],
                'image': item['image'],
                'link': '#'
            })
    return render_template('search_results.html', query=query, results=results)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    name = request.form['name']
    message = request.form['message']
    flash(f"Thanks for your review, {name}!")
    return redirect(url_for('home'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    name = request.form['name']
    price = float(request.form['price'])
    weight = request.form['weight']

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    for item in cart:
        if item['name'] == name and item['weight'] == weight:
            item['quantity'] += 1
            break
    else:
        cart.append({'name': name, 'price': price, 'weight': weight, 'quantity': 1})

    session['cart'] = cart
    flash(f"{name} added to cart!", "success")
    return redirect(request.referrer or url_for('home'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render_template('cart.html', cart_items=cart, total=total)

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    name = request.form['item_name']
    change = int(request.form['change'])
    cart = session.get('cart', [])
    for item in cart:
        if item['name'] == name:
            item['quantity'] += change
            if item['quantity'] <= 0:
                cart.remove(item)
            break
    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    name = request.form['item_name']
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if item['name'] != name]
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form['fullname']
        email = request.form['email']
        address = request.form['address']
        city = request.form['city']
        pincode = request.form['pincode']
        phone = request.form['phone']
        payment = request.form['payment']
        upi_id = request.form.get('upi_id')
        card_number = request.form.get('card_number')

        cart_items = session.get('cart', [])

        # ✅ Use Decimal for total and each item price
        total = Decimal(str(sum(item['price'] * item['quantity'] for item in cart_items)))
        for item in cart_items:
            item['price'] = Decimal(str(item['price']))

        order_id = str(uuid.uuid4())

        order_data = {
            'order_id': order_id,
            'name': name,
            'address': address,
            'city': city,
            'pincode': pincode,
            'phone': phone,
            'email': email,
            'payment': payment,
            'upi_id': upi_id,
            'card_number': card_number,
            'total': total,
            'items': cart_items
        }

        orders_table.put_item(Item=order_data)

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject='New Order',
            Message=f"Order ID: {order_id}\nName: {name}\nTotal: ₹{total}"
        )

        send_email(email, 'Order Confirmation - Pickle Paradise',
                   f'Thank you {name} for your order!\nOrder ID: {order_id}\nTotal: ₹{total}\nPayment: {payment}')

        session.pop('cart', None)
        return render_template('success.html', name=name, order_id=order_id)

    return render_template('checkout.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_id = str(uuid.uuid4())
        user_table.put_item(Item={'User_id': user_id, 'email': email, 'password': password})
        send_email(email, 'Welcome to Pickle Paradise', 'Thank you for signing up!')
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = user_table.get_item(Key={'email': email}).get('Item')
        if user and user['password'] == password:
            session['user'] = email
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('index'))

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Email failed:", e)

if _name_ == "_main_":
    app.run(host='0.0.0.0', port=5000, debug=True)