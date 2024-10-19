from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db=SQLAlchemy()


class Customer(db.Model):
    cust_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    cust_firstname = db.Column(db.String(255),nullable=False)
    cust_lastname = db.Column(db.String(255),nullable=False)
    cust_email = db.Column(db.String(255),nullable=False, unique=True)
    cust_password = db.Column(db.String(255),nullable=False)
    cust_phone_number = db.Column(db.String(20),nullable=False)
    cust_bill_address = db.Column(db.String(255),nullable=False)
    cust_image = db.Column(db.String(255))
    cust_status =db.Column(db.Enum('active','disabled'),nullable=False, server_default=("active"))
    cust_created_at =  db.Column(db.DateTime,default=datetime.utcnow)
    
    orders = db.relationship('Order',backref='customer')
    ratings = db.relationship('Rating',backref='customer')
    

class Product(db.Model):
    prod_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    prod_name = db.Column(db.String(255),nullable=False)
    prod_description = db.Column(db.Text(255))
    prod_price = db.Column(db.Numeric(10,2),nullable=False)
    prod_image_url = db.Column(db.String(255),nullable=False)
    prod_added_on =  db.Column(db.DateTime,default=datetime.utcnow)
    prod_updated_on = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    prod_category_id = db.Column(db.Integer,db.ForeignKey('category.cat_id'))
    prod_brand_id = db.Column(db.Integer,db.ForeignKey('brand.brand_id'))
    prod_disc_id = db.Column(db.Integer, db.ForeignKey('discount.disc_id'), unique=True)
    prod_featured_id = db.Column(db.Integer,db.ForeignKey('feature.featured_id'))
    
    
    order_items = db.relationship('Order_item',backref='product')
    ratings = db.relationship('Rating',backref='product')
    discount = db.relationship('Discount', back_populates='products', uselist=False)
   
class Feature(db.Model):
    featured_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    featured_name = db.Column(db.String(255),nullable=False)
    
    products = db.relationship('Product',backref='feature')
    
    
    
    
class Category(db.Model):
    cat_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    cat_name = db.Column(db.String(255),nullable=False)
    cat_description = db.Column(db.Text)
    
    products = db.relationship('Product',backref='category')
    
    
class Brand(db.Model):
    brand_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    brand_name = db.Column(db.String(255),nullable=False)

    
    products = db.relationship('Product',backref='brand')
    

class Order_item(db.Model):
    ord_item_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    ord_item_quant = db.Column(db.Integer)
    ord_item_total_amt = db.Column(db.Numeric(10,2))   
    ord_item_prod_id = db.Column(db.Integer,db.ForeignKey('product.prod_id'))
    ord_item_order_id = db.Column(db.Integer,db.ForeignKey('order.order_id'))
      
    
class Country(db.Model):
    count_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    count_name = db.Column(db.String(255),nullable=False)
    
    shippings = db.relationship('Shipping',backref='country')
    

class Payment(db.Model):
    pay_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    pay_date = db.Column(db.DateTime,default=datetime.utcnow)
    pay_amount = db.Column(db.Numeric(10,2))
    pay_method = db.Column(db.String(255))
    pay_status = db.Column(db.Enum('successful','pending','declined'),server_default=("pending"))
    pay_reference = db.Column(db.String(255), unique=True)
    pay_order_id = db.Column(db.Integer,db.ForeignKey('order.order_id'))


class Order(db.Model):
    order_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    order_date = db.Column(db.DateTime,default=datetime.utcnow)
    order_total_amt = db.Column(db.Numeric(10,2))
    order_status = db.Column(db.Enum('completed','pending','cancelled'),server_default=("pending"))
    # order_reference = db.Column(db.String(255), unique=True)
    order_created_at = db.Column(db.DateTime,default=datetime.utcnow)
    order_cust_id = db.Column(db.Integer,db.ForeignKey('customer.cust_id'))
    order_count_id = db.Column(db.Integer,db.ForeignKey('country.count_id'))
    order_ship_id = db.Column(db.Integer, db.ForeignKey('shipping.ship_id'))  
    
    payments = db.relationship('Payment',backref='order')
    order_items = db.relationship('Order_item',backref='order')
    
    
class Rating(db.Model):
    rate_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    rate_date = db.Column(db.DateTime,default=datetime.utcnow) 
    rate_score = db.Column(db.Numeric(10,2))
    rate_cust_id = db.Column(db.Integer,db.ForeignKey('customer.cust_id'))
    rate_prod_id = db.Column(db.Integer,db.ForeignKey('product.prod_id'))
       
    
class Shipping(db.Model):
    ship_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    ship_fees_amt = db.Column(db.Numeric(10,2)) 
    ship_count_id = db.Column(db.Integer,db.ForeignKey('country.count_id'))
    
    order = db.relationship('Order',backref='shipping')
    
        

class Administrator(db.Model):
    admin_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    admin_firstname = db.Column(db.String(255),nullable=False)
    admin_lastname = db.Column(db.String(255),nullable=False)
    admin_username = db.Column(db.String(255),nullable=False)
    admin_email = db.Column(db.String(255),nullable=False, unique=True)
    admin_phone_number = db.Column(db.String(20),nullable=False)
    admin_contact_addr = db.Column(db.Text,nullable=True)
    admin_image = db.Column(db.String(255))
    admin_password = db.Column(db.String(255),nullable=False)
    admin_login_at =  db.Column(db.DateTime,default=datetime.utcnow)
    
    
class Discount(db.Model):
    disc_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    disc_start_date = db.Column(db.DateTime,default=datetime.utcnow)
    disc_end_date = db.Column(db.DateTime,default=datetime.utcnow)
    disc_min_ord_amt = db.Column(db.Numeric(10,2))
    
    products = db.relationship('Product', back_populates='discount', uselist=False)
    

    
      