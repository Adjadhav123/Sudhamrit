from flask import Flask,render_template,request,redirect,url_for,flash,session,jsonify
from models import db,User,Admin,Product,Cart,Payment,Order,OrderItem
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
import os 
from flask_mail import Mail,Message
import os 
import razorpay
from dotenv import load_dotenv 
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='your_secret_key'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL']=False
app.config['MAIL_USERNAME']=os.getenv("EMAIL")  
app.config['MAIL_PASSWORD']=os.getenv("PASSWORD")  
app.config['MAIL_DEFAULT_SENDER']=os.getenv("EMAIL")
app.config['MAIL_DEBUG']=True

load_dotenv() 

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Validate Razorpay credentials
if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    logger.warning("Razorpay credentials not found in environment variables")
    RAZORPAY_KEY_ID = "dummy_key"
    RAZORPAY_KEY_SECRET = "dummy_secret"

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

mail=Mail(app)



db.init_app(app)


@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/register',methods=['GET','POST'])
def register():
    register_message=""
    if request.method=='POST':
        username=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')
        phone=request.form.get('phone')
        address=request.form.get('address')

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            register_message = "Email already registered. Please use a different email or log in."
            flash(register_message, 'warning')
            return render_template('register.html', register_message=register_message)
        
        
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            register_message = "Username already taken. Please choose a different username."
            flash(register_message, 'warning')
            return render_template('register.html', register_message=register_message)

        try:
            hashed_password=generate_password_hash(password=password,method="pbkdf2:sha256",salt_length=16)

            new_user=User(
                username=username,
                email=email,
                password=hashed_password,
                phone=phone,
                address=address
            )
            
            db.session.add(new_user)
            db.session.commit()
            register_message="Registration successful! Please log in."
            flash(register_message,'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            register_message = "Registration failed. Please try again with different details."
            flash(register_message, 'danger')
            return render_template('register.html', register_message=register_message)
    
    return render_template('register.html',register_message=register_message)

@app.route('/login',methods=['GET','POST'])
def login():
    login_message=""
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')

        user=User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            login_message="Login successful!"
            flash(login_message,'success')
            return redirect(url_for('home',user_id=user.user_id))
        else:
            login_message="Invalid email or password."
            flash(login_message,'danger')
    return render_template('login.html',login_message=login_message)


@app.route('/home/<int:user_id>')
def home(user_id):
    user = db.session.get(User, user_id)
    if user:
        return render_template('home.html', user=user)
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

@app.route('/products')
def products():
    user_id = session.get('user_id')
    user = None
    if user_id:
        user = db.session.get(User, user_id)
    
    try:
        products = Product.query.all()
    except Exception as e:
        print(f"Database error: {e}")
        products = []
        flash('Unable to load products. Please try again later.', 'warning')
    
    return render_template('products.html', user=user, products=products)

@app.route('/admin_register',methods=['GET','POST'])
def admin_register():
    admin_register_message=""
    if request.method=='POST':
        admin_name=request.form.get('admin_name')
        admin_email=request.form.get('admin_email')
        admin_password=request.form.get('admin_password')

        existing_admin_email=Admin.query.filter_by(admin_email=admin_email).first()
        existing_admin_name=Admin.query.filter_by(admin_name=admin_name).first()
        if existing_admin_email or existing_admin_name:
            admin_register_message="Email or Name already exists. Please use a different email or name."
            flash(admin_register_message,'warning')
            return render_template('admin_register.html',admin_register_message=admin_register_message)
        
        try:
            hashed_password=generate_password_hash(password=admin_password,method="pbkdf2:sha256",salt_length=16)

            new_admin=Admin(
                admin_name=admin_name,
                admin_email=admin_email,
                admin_password=hashed_password
            )

            db.session.add(new_admin)
            db.session.commit() 
            admin_register_message="Admin Registration successful! Please log in."
            flash(admin_register_message,'success')
            return redirect(url_for('admin_login'))
        except Exception as e:
            db.session.rollback()
            admin_register_message="Admin Registration failed. Please try again with different details."
            flash(admin_register_message,'danger')

    return render_template('admin_register.html',admin_register_message=admin_register_message)
        

@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    admin_login_message=""
    if request.method=='POST':
        admin_email=request.form.get('admin_email')
        admin_password=request.form.get('admin_password')
        admin=Admin.query.filter_by(admin_email=admin_email).first()
        if admin_email and check_password_hash(admin.admin_password,admin_password):
            session['admin_id']=admin.admin_id
            session['admin_name']=admin.admin_name
            admin_login_message="Admin Login successful!"
            flash(admin_login_message,'success')
            return redirect(url_for('admin_dashboard',admin_id=admin.admin_id))
        else:
            admin_login_message="Invalid email or password."
            flash(admin_login_message,'danger')
    return render_template('admin_login.html',admin_login_message=admin_login_message)
        
@app.route('/admin_dashboard/<int:admin_id>')
def admin_dashboard(admin_id):
    admin=db.session.get(Admin, admin_id)
    if admin:
        try:
            products = Product.query.all()
            total_products = len(products)
            customers=User.query.all()
            total_customers = len(customers)

            orders = Order.query.order_by(Order.order_date.desc()).all()
            total_orders = Order.query.count()
            total_revenue = sum(order.total_amount for order in orders)

            return render_template('admin_dashboard.html',
                                 admin=admin, 
                                 products=products, 
                                 total_products=total_products,
                                 total_customers=total_customers,
                                 total_orders=total_orders,
                                 total_revenue=total_revenue,
                                 orders=orders)
        except Exception as e:
            flash(f'Database error: {str(e)}. Please refresh the page.', 'danger')
            return render_template('admin_dashboard.html',
                                 admin=admin, 
                                 products=[], 
                                 total_products=0,
                                 total_customers=0,
                                 total_orders=0,
                                 total_revenue=0,
                                 orders=[])
    else:
        flash('Admin not found. Please log in.','danger')
        return redirect(url_for('admin_login'))
    
@app.route('/admin_logout')
def admin_logout():
    session.clear()
    flash('Admin has been logged out.','info')
    return redirect(url_for('landing'))

@app.route('/add_product',methods=['GET','POST'])
def add_product():
    admin=db.session.get(Admin, session.get('admin_id'))
    if not admin:
        flash('Admin not found. Please log in.','danger')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        product_name=request.form.get('product_name')
        description=request.form.get('description')
        category=request.form.get('category')
        price=request.form.get('product_price')
        stock=request.form.get('stock')
        product_image=request.files.get('product_image')

        if not all([product_name,category,price,stock,product_image]):
            flash('Please fill in all required fields.','warning')
            return redirect(url_for('admin_dashboard',admin_id=admin.admin_id))
        
        if product_image and product_image.filename:
            image_filename=product_image.filename
            image_path=os.path.join('static/images',image_filename)
            product_image.save(image_path)
            image_db_path = image_filename
        else:
            image_db_path = None

        try:
            new_product=Product(
                product_name=product_name,
                description=description,
                category=category,
                price=float(price),
                stock=int(stock),
                product_image=image_db_path
            )
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!','success')
            return redirect(url_for('admin_dashboard',admin_id=admin.admin_id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to add product. Please try again.','danger')

    return redirect(url_for('admin_dashboard',admin_id=admin.admin_id))

@app.route('/delete_product/<int:product_id>', methods=['POST', 'GET'])
def delete_product(product_id):
    admin=db.session.get(Admin, session.get('admin_id'))
    if not admin:
        flash('Admin not found. Please log in.','danger')
        return redirect(url_for('admin_login'))
    product = db.session.get(Product, product_id)
    if not product:
        flash('Product not found.','danger')
        return redirect(url_for('admin_dashboard', admin_id=admin.admin_id))
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!','success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to delete product. Please try again.','danger')
        return redirect(url_for('admin_dashboard', admin_id=admin.admin_id))
    return redirect(url_for('admin_dashboard', admin_id=admin.admin_id))     

@app.route('/update_product/<int:product_id>',methods=['GET','POST'])
def update_product(product_id):
    admin=db.session.get(Admin, session.get('admin_id'))
    if not admin:
        flash('Admin not found. Please log in.','danger')
        return redirect(url_for('admin_login'))
    product=db.session.get(Product, product_id)
    if not product:
        flash('Product not found.','danger')
        return redirect(url_for('admin_dashboard', admin_id=admin.admin_id))
    if request.method=='POST':
        product_name=request.form.get('product_name')
        description=request.form.get('description')
        category=request.form.get('category')
        price=request.form.get('product_price')
        stock=request.form.get('stock')
        product_image=request.files.get('product_image')

        if not all([product_name,category,price,stock]):
            flash('Please fill in all required fields.','warning')
            return redirect(url_for('admin_dashboard',admin_id=admin.admin_id))
        if product_image and product_image.filename:
            image_filename=product_image.filename
            image_path=os.path.join('static/images',image_filename)
            product_image.save(image_path)
            product.product_image=image_filename
        
        product.product_name=product_name
        product.description=description
        product.category=category
        product.price=float(price)
        product.stock=int(stock)

        try:
            db.session.commit() 
            flash("Product Update Successfully!", "success")
            return redirect(url_for('admin_dashboard',admin_id=admin.admin_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating product {str(e)}","danger")
            return redirect(url_for('admin_dashboard'),admin_id=admin.admin_id)
        
    return render_template('admin_dashboard.html',product=product,admin=admin)
    
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    user_id = session.get('user_id')
    
    if not user_id:
        flash('Please log in to add items to cart.', 'warning')
        return redirect(url_for('login'))
    
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login'))
    
    product = db.session.get(Product, product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products'))
    
    existing_cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    try:
        if existing_cart_item:
            existing_cart_item.quantity += 1
        else:
            new_cart_item = Cart(
                user_id=user_id,
                product_id=product_id,
                quantity=1
            )
            db.session.add(new_cart_item)
        
        db.session.commit()
        flash(f'{product.product_name} added to cart successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to add item to cart: {str(e)}', 'danger')
    
    return redirect(url_for('cart'))


@app.route('/cart',methods=['GET','POST'])
def cart():
    user_id=session.get('user_id')
    
    if not user_id:
        flash('Please log in to view your cart.','warning')
        return redirect(url_for('login'))
    
    user=db.session.get(User, user_id)
    if not user:
        flash('User not found. Please log in again.','danger')
        return redirect(url_for('login'))
    
    try:
        cart_items=Cart.query.filter_by(user_id=user.user_id).all()
        total_amount=sum(item.product.price * item.quantity for item in cart_items)
        return render_template('cart.html',user=user,cart_items=cart_items,total_amount=total_amount)
    except Exception as e:
        flash(f'Database error: {str(e)}. Please refresh the page.','danger')
        return render_template('cart.html',user=user,cart_items=[],total_amount=0)

    return render_template('cart.html',user=user,cart_items=cart_items,total_amount=total_amount)

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to modify your cart.', 'warning')
        return redirect(url_for('login'))
    
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    
    if cart_item:
        try:
            db.session.delete(cart_item)
            db.session.commit()
            flash('Item removed from cart successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to remove item from cart. Please try again.', 'danger')
    else:
        flash('Item not found in cart.', 'warning')
    
    return redirect(url_for('cart'))


@app.route('/update_cart', methods=['POST'])
def update_cart():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not_logged_in'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'invalid_payload'}), 400

    product_id = data.get('product_id')
    quantity = data.get('quantity')

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({'error': 'invalid_quantity'}), 400

    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not cart_item:
        return jsonify({'error': 'item_not_found'}), 404

    try:
        if quantity <= 0:
            db.session.delete(cart_item)
            db.session.commit()
            remaining = Cart.query.filter_by(user_id=user_id).all()
            grand_total = sum(i.product.price * i.quantity for i in remaining)
            return jsonify({'item_total': 0, 'grand_total': grand_total})

        cart_item.quantity = quantity
        db.session.commit()

        # compute totals
        item_total = cart_item.product.price * cart_item.quantity
        grand_total = sum(i.product.price * i.quantity for i in Cart.query.filter_by(user_id=user_id).all())
        return jsonify({'item_total': item_total, 'grand_total': grand_total})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/payment')
def payment():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to proceed with payment.', 'warning')
        return redirect(url_for('login'))
    
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login'))
    
    try:
        cart_items = Cart.query.filter_by(user_id=user.user_id).all()
        if not cart_items:
            flash('Your cart is empty.', 'warning')
            return redirect(url_for('products'))
        
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        amount_paise = int(total_amount * 100)  # Convert to paise and ensure it's an integer

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': '1'  # Auto capture payment
        })

        # Store order ID in session for verification later
        session['razorpay_order_id'] = razorpay_order['id']
        session['payment_amount'] = total_amount
        
        return render_template('payment.html', 
                             user=user, 
                             cart_items=cart_items, 
                             total=total_amount,
                             razorpay_order_id=razorpay_order['id'], 
                             razorpay_key_id=RAZORPAY_KEY_ID)
    except Exception as e:
        flash(f'Error processing payment: {str(e)}', 'danger')
        return redirect(url_for('cart'))

@app.route('/payment_success', methods=['POST'])
def payment_success():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in again.', 'warning')
        return redirect(url_for('login'))

    user = db.session.get(User, user_id)
    data = request.form

    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })

    
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        total_amount = session.get('payment_amount', 0)  # Get amount from session
        
        if not cart_items:
            flash('Cart is empty or order already processed.', 'warning')
            return redirect(url_for('products'))

        # Save Payment in DB with Razorpay details
        new_payment = Payment(
            user_id=user_id,
            amount=total_amount,
            payment_method='Razorpay',
            status='Completed',
            razorpay_order_id=data['razorpay_order_id'],
            razorpay_payment_id=data['razorpay_payment_id'],
            razorpay_signature=data['razorpay_signature']
        )
        db.session.add(new_payment)
        db.session.flush()

        # Create Order
        new_order = Order(
            payment_id=new_payment.payment_id,
            user_id=user_id,
            total_amount=total_amount,
            status='Confirmed'
        )
        db.session.add(new_order)
        db.session.flush()

        # Create Order Items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=new_order.order_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price_per_item=cart_item.product.price
            )
            db.session.add(order_item)

        # Clear cart after successful order
        Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()

        # Clear session data
        session.pop('razorpay_order_id', None)
        session.pop('payment_amount', None)

        flash("Payment verified and order placed successfully!", "success")

        # Send confirmation email
        try:
            msg = Message(
                subject="Order Confirmation - Sudhamrit Dairy Farm",
                recipients=[user.email],
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            msg.body = f"""
Hello {user.username},

Your payment of ₹{total_amount} has been received successfully!

Order Details:
- Order ID: {new_order.order_id}
- Payment ID: {data['razorpay_payment_id']}
- Amount: ₹{total_amount}
- Payment Method: Razorpay

Your products will be delivered soon to:
{user.address}

Thank you for shopping with Sudhamrit Dairy Farm!

Best Regards,
Sudhamrit Dairy Farm Team
            """
            mail.send(msg)
        except Exception as mail_error:
            print(f"Email sending failed: {mail_error}")

        return render_template('confirm_order.html', 
                             user=user, 
                             total=total_amount, 
                             payment_method='Razorpay', 
                             order_id=new_order.order_id,
                             razorpay_payment_id=data['razorpay_payment_id'])
                             
    except razorpay.errors.SignatureVerificationError:
        db.session.rollback()
        flash("Payment verification failed! This may be a fraudulent transaction.", "danger")
        return redirect(url_for('payment'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error processing payment: {str(e)}", "danger")
        return redirect(url_for('payment'))

@app.route('/payment_failed', methods=['GET'])
def payment_failed():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in again.', 'warning')
        return redirect(url_for('login'))
    
    flash('Payment was cancelled or failed. Please try again.', 'warning')
    return redirect(url_for('cart'))

@app.route('/razorpay_webhook', methods=['POST'])
def razorpay_webhook():
    """
    Handle Razorpay webhooks for payment notifications
    This is useful for server-to-server payment confirmations
    """
    try:
        # Get the request data
        webhook_data = request.get_json()
        
        # Verify webhook signature (recommended for production)
        # webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET")
        # received_signature = request.headers.get('X-Razorpay-Signature')
        
        # Process different event types
        event = webhook_data.get('event')
        
        if event == 'payment.captured':
            # Payment was successful
            payment_data = webhook_data.get('payload', {}).get('payment', {}).get('entity', {})
            payment_id = payment_data.get('id')
            order_id = payment_data.get('order_id')
            amount = payment_data.get('amount', 0) / 100  # Convert from paise to rupees
            
            logger.info(f"Payment captured: {payment_id} for order: {order_id}")
            
            # Update payment status in database if needed
            payment_record = Payment.query.filter_by(razorpay_payment_id=payment_id).first()
            if payment_record:
                payment_record.status = 'Completed'
                db.session.commit()
                logger.info(f"Updated payment status for payment_id: {payment_id}")
        
        elif event == 'payment.failed':
            # Payment failed
            payment_data = webhook_data.get('payload', {}).get('payment', {}).get('entity', {})
            payment_id = payment_data.get('id')
            logger.warning(f"Payment failed: {payment_id}")
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to complete payment.', 'warning')
        return redirect(url_for('login'))
    
    payment_method = request.form.get('payment_method')
    card_name = request.form.get('cardName')
    
    try:
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        if not cart_items:
            flash('Your cart is empty.', 'warning')
            return redirect(url_for('products'))

        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        new_payment = Payment(
            user_id=user_id,
            amount=total_amount,
            payment_method=payment_method,
            status='Completed'
        )
        db.session.add(new_payment)
        db.session.flush() 

        new_order = Order(
            payment_id=new_payment.payment_id,
            user_id=user_id,
            total_amount=total_amount,
            status='Completed'
        )
        db.session.add(new_order)
        db.session.flush()  

        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=new_order.order_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price_per_item=cart_item.product.price
            )
            db.session.add(order_item)

        db.session.commit()

        flash(f'Payment successful! ₹{total_amount} paid via {payment_method}', 'success')
        user = db.session.get(User, user_id)

        try:
            msg=Message(
                subject="Order Confirmation - Sudhamrit Dairy Farm",
                recipients=[user.email],
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            msg.body=f"""
            Hello {user.username},

            Thank You for your order with Sudhamrit Dairy Farm!

            Your Order #{new_order.order_id} has been successfully placed and will be processed soon.

            Order Details:
            - Order ID: {new_order.order_id}
            - Total Amount: ₹{total_amount}
            - Payment Method: {payment_method}
            - Order Date: {new_order.order_date.strftime('%Y-%m-%d %H:%M')}

            Your fresh dairy products will be delivered to:
            {user.address}

            Thank You for shopping with us!

            Best Regards,
            Sudhamrit Dairy Farm Team
            Phone: +91-XXXXXXXXXX
            Email: sudhamritdairy@gmail.com
            """

            mail.send(msg)
            print(f"Email sent successfully to {user.email}")  # Debug log
            flash(f'Payment successful! ₹{total_amount} paid via {payment_method}. Confirmation email sent.', 'success')
        except Exception as mail_error:
            print(f"Email sending failed: {mail_error}")  # Debug log
            flash(f'Order confirmed but email failed to send: {mail_error}', 'warning')
        return render_template('confirm_order.html', 
                             user=user, 
                             total=total_amount, 
                             payment_method=payment_method,
                             order_id=new_order.order_id)
    except Exception as e:
        db.session.rollback()
        flash(f'Payment failed: {str(e)}', 'danger')
        return redirect(url_for('payment'))

@app.route('/test_email')
def test_email():
    try:
        msg = Message(
            subject="Test Email - Sudhamrit Dairy Farm",
            recipients=["aditya29jadhav@gmail.com"], 
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        msg.body = """
        This is a test email from Sudhamrit Dairy Farm.
        
        If you receive this email, your email configuration is working correctly!
        
        Best Regards,
        Sudhamrit Team
        """    
        mail.send(msg)
        return "Test email sent successfully! Check your inbox."
    except Exception as e:
        return f"Email sending failed: {str(e)}"
    
@app.route('/orders',methods=['GET','POST'])
def orders():
    admin_id = session.get('admin_id')
    if not admin_id:
        return redirect(url_for('admin_login'))
    all_orders=Order.query.all()
    return render_template('orders.html',orders=all_orders,admin_id=admin_id)

@app.route('/marked_delivery<int:order_id>',methods=['GET','POST'])
def marked_delivery(order_id):
    order=Order.query.get(order_id)
    if order:
        order.status='Delivered'
        try:
            db.session.commit()
            flash(f"Order {order_id} marked as Delivered.",'Success')
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating order status: {str(e)}",'danger')
        return redirect(url_for('orders'))
    return redirect(url_for('orders'))
@app.route('/test_db')
def test_db():
    try:
        users = User.query.all()
        products = Product.query.all()
        carts = Cart.query.all()
        
        return f"""
        <h2>Database Test Results:</h2>
        <p>Users: {len(users)}</p>
        <p>Products: {len(products)}</p>
        <p>Cart Items: {len(carts)}</p>
        <p>Current Session: {dict(session)}</p>
        """
    except Exception as e:
        return f"Database Error: {str(e)}"
        
if __name__=='__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)