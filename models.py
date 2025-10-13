from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db=SQLAlchemy() 

class User(db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(120),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    password=db.Column(db.String(120),nullable=False)
    phone=db.Column(db.String(20))
    address=db.Column(db.String(200))
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

class Admin(db.Model):
    admin_id=db.Column(db.Integer,primary_key=True)
    admin_name=db.Column(db.String(120),nullable=False)
    admin_email=db.Column(db.String(120),unique=True,nullable=False)
    admin_password=db.Column(db.String(120),nullable=False)

class Product(db.Model):
    product_id=db.Column(db.Integer,primary_key=True)
    product_name=db.Column(db.String(120),nullable=False)
    description=db.Column(db.String(500))
    category=db.Column(db.String(100),nullable=False)
    price=db.Column(db.Float,nullable=False)
    stock=db.Column(db.Integer,default=0)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    product_image=db.Column(db.String(300))



class Cart(db.Model):
    cart_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    product_id=db.Column(db.Integer,db.ForeignKey('product.product_id'),nullable=False)
    quantity=db.Column(db.Integer,default=1)
    added_at=db.Column(db.DateTime,default=datetime.utcnow)
    user=db.relationship('User',backref=db.backref('carts',lazy=True))
    product=db.relationship('Product',backref=db.backref('carts',lazy=True))

class Payment(db.Model):
    payment_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    amount=db.Column(db.Float,nullable=False)
    payment_date=db.Column(db.DateTime,default=datetime.utcnow)
    payment_method=db.Column(db.String(50))
    status=db.Column(db.String(50),default='Pending')
    user=db.relationship('User',backref=db.backref('payments',lazy=True))


class Order(db.Model):
    order_id = db.Column(db.Integer,primary_key=True)
    payment_id = db.Column(db.Integer,db.ForeignKey('payment.payment_id'),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    order_date = db.Column(db.DateTime,default=datetime.utcnow)
    total_amount = db.Column(db.Float,nullable=False)
    status = db.Column(db.String(50),default='Completed')


    payment=db.relationship('Payment',backref=db.backref('order',uselist=False))
    user=db.relationship('User',backref=db.backref('orders',lazy=True))
    order_items=db.relationship('OrderItem',backref=db.backref('order',lazy=True))



class OrderItem(db.Model):
    order_item_id = db.Column(db.Integer,primary_key=True)
    order_id = db.Column(db.Integer,db.ForeignKey('order.order_id'),nullable=False)
    product_id = db.Column(db.Integer,db.ForeignKey('product.product_id'),nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    price_per_item = db.Column(db.Float,nullable=False)

    product = db.relationship('Product',backref=db.backref('order_items',lazy=True))

class DeliveryLocation(db.Model):
    location_id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    address = db.Column(db.String(200),nullable=False)
    latitude = db.Column(db.Float,nullable=False)
    longitude = db.Column(db.Float,nullable=False)
    added_at = db.Column(db.DateTime,default=datetime.utcnow)

    user = db.relationship('User',backref=db.backref('delivery_locations',lazy=True))
    