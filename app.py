from flask import Flask,render_template,request,redirect,url_for,flash,session,jsonify
from models import db,User,Admin,Product,Cart,Payment,Order,OrderItem,DeliveryLocation
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
import os 
from flask_mail import Mail,Message
import os 
from dotenv import load_dotenv 
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='your_secret_key'

# Email configuration with timeout settings
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL']=False
app.config['MAIL_USERNAME']=os.getenv("EMAIL")  
app.config['MAIL_PASSWORD']=os.getenv("PASSWORD")  
app.config['MAIL_DEFAULT_SENDER']=os.getenv("EMAIL")
app.config['MAIL_DEBUG']=False  # Disable debug in production
app.config['MAIL_SUPPRESS_SEND']=os.getenv('FLASK_ENV') == 'production'  # Suppress email in production

load_dotenv() 

mail=Mail(app)



db.init_app(app)

# Create tables before first request
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

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

        try:
            user=User.query.filter_by(email=email).first()
        except Exception as e:
            logger.error(f"Database error during login: {e}")
            # Try to initialize database if tables don't exist
            try:
                db.create_all()
                user=User.query.filter_by(email=email).first()
            except Exception as init_error:
                logger.error(f"Failed to initialize database: {init_error}")
                login_message="Database error. Please try again later."
                flash(login_message,'danger')
                return render_template('login.html',login_message=login_message)

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
        
        session['payment_amount'] = total_amount
        
        return render_template('payment.html', 
                             user=user, 
                             cart_items=cart_items, 
                             total=total_amount)
    except Exception as e:
        flash(f'Error processing payment: {str(e)}', 'danger')
        return redirect(url_for('cart'))

@app.route('/payment_success',methods=['GET','POST'])
def payment_success():
    """
    Process payment and create order - Fixed for production deployment
    """
    print("🚀 Starting payment processing...")
    
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to proceed with payment.', 'warning')
        return redirect(url_for('login'))
    
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found. Please log in again.', 'danger')
        return redirect(url_for('login'))
    
    payment_method = request.form.get('payment_method')
    print(f"Processing payment for user {user.username} (ID: {user_id})")
    print(f"Payment method: {payment_method}")

    try:
        cart_items = Cart.query.filter_by(user_id=user.user_id).all()
        total_amount = session.get('payment_amount', 0)
        
        print(f"Found {len(cart_items)} items in cart")
        print(f"Total amount: ₹{total_amount}")

        if not cart_items:
            print("Cart is empty")
            flash('Your cart is empty.', 'warning')
            return redirect(url_for('products'))
        
        if total_amount <= 0:
            print("Invalid payment amount")
            flash('Invalid payment amount.', 'danger')
            return redirect(url_for('cart'))
        
        # Step 1: Create Payment Record
        print("Creating payment record...")
        new_payment = Payment(
            user_id=user.user_id,
            amount=total_amount,
            payment_method=payment_method,
            status='Completed'
        )
        db.session.add(new_payment)
        db.session.flush()
        print(f"Payment record created with ID: {new_payment.payment_id}")

        print("Creating order record...")
        new_order = Order(
            payment_id=new_payment.payment_id,
            user_id=user.user_id,
            total_amount=total_amount,
            status='Completed'
        )
        db.session.add(new_order)
        db.session.flush()
        print(f"Order record created with ID: {new_order.order_id}")

        print("Creating order items...")
        for item in cart_items:
            order_item = OrderItem(
                order_id=new_order.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_per_item=item.product.price
            )
            db.session.add(order_item)
            print(f"  - Added {item.product.product_name} x {item.quantity}")
        
        print("Clearing cart...")
        Cart.query.filter_by(user_id=user.user_id).delete()
        
        db.session.commit()
        print("All database changes committed successfully!")
        session.pop('payment_amount', None)
        print("Session data cleared")

        
        flash("Order placed successfully!", "success")

       
        email_sent = False
        
        if os.getenv('FLASK_ENV') == 'production':
            print("Skipping email in production environment")
            flash("Order placed successfully! You will receive confirmation via SMS/WhatsApp.", "warning")
        else:
            try:
                print("Attempting to send confirmation email...")
                
                msg = Message(
                    subject="Order Confirmation - Sudhamrit Dairy Farm",
                    recipients=[user.email],
                    sender=app.config['MAIL_DEFAULT_SENDER']
                )
                msg.body = f"""Hello {user.username},

Your order has been placed successfully! 🎉

📋 ORDER DETAILS:
• Order ID: #{new_order.order_id}
• Amount: ₹{total_amount}
• Payment Method: {payment_method}
• Order Date: {new_order.order_date.strftime('%d/%m/%Y at %I:%M %p')}

🚚 DELIVERY ADDRESS:
{user.address}

📞 CONTACT: {user.phone}

Your fresh dairy products will be delivered soon!

Thank you for choosing Sudhamrit Dairy Farm! 🥛

Best Regards,
Sudhamrit Dairy Farm Team
Email: support@sudhamritdairy.com
Phone: +91-XXXXXXXXXX
"""
                
                mail.send(msg)
                email_sent = True
                print("Confirmation email sent successfully!")
                flash("Order confirmation email sent!", "info")
                
            except Exception as mail_error:
                print(f"Email sending failed: {mail_error}")
                flash("Order placed successfully! Email notification will be sent separately.", "warning")

        print("Redirecting to confirmation page...")

        # Get order items with product details for the confirmation page
        order_items = OrderItem.query.filter_by(order_id=new_order.order_id).all()
        
        return render_template('confirm_order.html', 
                             user=user, 
                             total=total_amount, 
                             payment_method=payment_method, 
                             order_id=new_order.order_id,
                             order_items=order_items,
                             email_sent=email_sent) 
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR processing payment: {str(e)}")
        flash(f"Error processing payment: {str(e)}", "danger")
        return redirect(url_for('cart'))

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

@app.route('/test_order_flow')
def test_order_flow():
    """Test route to check order processing without email"""
    user_id = session.get('user_id')
    if not user_id:
        return "Please log in first"
    
    try:
        # Check if user has cart items
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        total_amount = session.get('payment_amount', 0)
        
        orders = Order.query.filter_by(user_id=user_id).all()
        payments = Payment.query.filter_by(user_id=user_id).all()
        
        return f"""
        <h3>Order Flow Test for User ID: {user_id}</h3>
        <p><strong>Cart Items:</strong> {len(cart_items)}</p>
        <p><strong>Total Amount in Session:</strong> ₹{total_amount}</p>
        <p><strong>Previous Orders:</strong> {len(orders)}</p>
        <p><strong>Previous Payments:</strong> {len(payments)}</p>
        <br>
        <h4>Recent Orders:</h4>
        {'<br>'.join([f"Order #{order.order_id}: ₹{order.total_amount} - {order.status}" for order in orders[-5:]])}
        <br><br>
        <a href="/cart">Back to Cart</a> | <a href="/payment">Go to Payment</a>
        """
    except Exception as e:
        return f"Error: {str(e)}"
    
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
# @app.route('/test_db')
# def test_db():
#     try:
#         users = User.query.all()
#         products = Product.query.all()
#         carts = Cart.query.all()
        
#         return f"""
#         <h2>Database Test Results:</h2>
#         <p>Users: {len(users)}</p>
#         <p>Products: {len(products)}</p>
#         <p>Cart Items: {len(carts)}</p>
#         <p>Current Session: {dict(session)}</p>
#         """
#     except Exception as e:
#         return f"Database Error: {str(e)}"
    
@app.route('/save_location',methods=['GET','POST'])
def save_location():
     data = request.get_json()
     address = data.get('address')
     latitude = data.get('latitude')
     longitude = data.get('longitude')
     session['address'] = address
     session['latitude'] = latitude
     session['longitude'] = longitude

     if not all([address, latitude, longitude]):
         return jsonify({'error': 'Incomplete location data'}), 400
     
     user_id = session.get('user_id')
     if not user_id:
         return jsonify({'error': 'User not logged in'}), 401   
     
     new_location=DeliveryLocation(
         user_id=user_id,
         address=address,
         latitude=latitude,
         longitude=longitude
     )
     db.session.add(new_location)
     db.session.commit()

     return jsonify({'message': 'Location saved successfully!'}), 200
     return render_template('payment.html',user=user,cart_items=cart_items,total=total_amount,google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY"))

        
if __name__=='__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {e}")
    app.run(debug=True)