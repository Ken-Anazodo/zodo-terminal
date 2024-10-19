import os
import random
import json
import requests
from flask import render_template, make_response, redirect, request, session, flash, url_for, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app,db
from flask_wtf.csrf import CSRFError
from pkg.forms import Login_form, Signup_form, Customer_payment, Update_profile
from pkg.models import Customer, Product, Brand, Category, Country, Order, Order_item, Payment, Shipping
import secrets






def get_cust_byid(id):
    data = Customer.query.get(id)
    return data 


"""this route is for logging out and redirects the user to the login page"""
@app.route('/customer/logout/')
def customer_logout():
    if session.get('cust_id') != None:
        session.pop('cust_id')
    flash('You are now logged out','success')
    # Create a response for the redirect and prevent page caching (or having access to previous page after logout)
    response = make_response(redirect(url_for('index'))) 
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response



@app.route('/logIn/', methods=['GET','POST'])
def login():
    custform=Login_form()
    brands = Brand.query.order_by(Brand.brand_name).all() 
    cust_id = session.get('cust_id')
    
    if cust_id:
        cust_details=get_cust_byid(cust_id)
    else:
        cust_details=None
    return render_template('/customer/logIn.html', custform=custform, cust_details=cust_details, brands=brands) 





@app.route('/submit/cust_login/', methods=['GET','POST'])
def submit_cust_login():
    custform = Login_form() 
    brands = Brand.query.order_by(Brand.brand_name).all() 
    if request.method == 'POST' and custform.validate_on_submit():
        email = custform.email.data
        password = custform.password.data
        
        cust = db.session.query(Customer).filter(Customer.cust_email == email).first()
        if cust :
            hashed_password = cust.cust_password
            check = check_password_hash(hashed_password,password)
            if check == True:
                ## save details in session and redirect to dashboard
                session['cust_id'] = cust.cust_id
                return redirect('/')
            else:
                flash('Incorrect Password','error')
                return redirect('/logIn/')
        else:
            flash('Username and Password does not exist','error')
            return redirect('/logIn/')
    else:
        return render_template('/customer/logIn.html', custform=custform, brands=brands)
        
            
       


"""this route checks if the email a new user is about to input is taken or avaliable"""
@app.route('/customer/check_email/')
def check_email():
    email = request.args.get('email')
    status = 'Email is avaliable' 
    data = db.session.query(Customer).filter(Customer.cust_email == email).first()
    if data:
        status = 'Email has been taken'
    return status





@app.route('/signUp/', methods=['GET', 'POST'])
def sign_up():
    brands = Brand.query.order_by(Brand.brand_name).all() 
    custform = Signup_form() 

    if request.method == 'GET':
        return render_template('/customer/signUp.html', custform=custform, brands=brands)

    else:  
        if custform.validate_on_submit():
            
            cust_fname = custform.firstname.data 
            cust_lname = custform.lastname.data
            cust_email = custform.email.data
            contact_no = custform.contact_no.data
            contact_addr = custform.contact_addr.data
            password1 = custform.password.data
            picture = custform.cust_pict.data

            # Check if the email is already in use
            existing_customer = Customer.query.filter_by(cust_email=cust_email).first()
            if existing_customer:
                flash('The email is already in use, choose another one')
                return redirect(url_for('admin_register'))  # Redirect back to form page

            """to get the file name"""
            cust_filename = picture.filename

            if cust_filename != '':
                ext = os.path.splitext(cust_filename)
                extension = ext[-1].lower().replace('.', '')  

                allowed_ext = ['jpg', 'png', 'jpeg']

                # Generate new name
                newfilename = secrets.token_hex(16)
                if extension not in allowed_ext: 
                    flash('Extension is not allowed')
                    return redirect(url_for('sign_up'))  # Redirect back to form page
                else:
                    picture.save(f"pkg/static/uploads/{newfilename}.{extension}") 
                    hashed = generate_password_hash(password1)

                new_cust = Customer(
                    cust_firstname=cust_fname, 
                    cust_lastname=cust_lname,
                    cust_email=cust_email, 
                    cust_phone_number=contact_no, 
                    cust_bill_address=contact_addr, 
                    cust_password=hashed, 
                    cust_image=f"{newfilename}.{extension}" 
                )

                try:
                    db.session.add(new_cust)
                    db.session.commit()
                    cust_id = new_cust.cust_id
                    ## saving the id into session
                    session['cust_id'] = cust_id
                    flash('Welcome, an account has been created for you')
                    return redirect('/')
                except Exception as e:
                    print(f"Error adding to database: {e}") 
                    flash('An error occurred while creating an account. Please try again.')
                    return redirect(url_for('sign_up'))  
        else:
            print(f"Form validation errors: {custform.errors}")

            flash('Form validation failed. Please check your input.')
            return redirect(url_for('sign_up'))  # Redirect if form validation fails  








# UPDATE PROFILE
@app.route('/update_profile/<int:id>/', methods=['GET', 'POST'])
def update_profile(id):
    cust_id = session.get('cust_id')
    brands = Brand.query.order_by(Brand.brand_name).all() 
    custform = Update_profile() 
    customer = Customer.query.get_or_404(id)

    if not cust_id:  # If the user is not logged in
        flash('You need to login to access this page', 'error')
        return redirect(url_for('login'))

    cust_details = get_cust_byid(cust_id)
    
    
    if request.method == 'GET':
        return render_template('/customer/update_profile.html', customer=customer, cust_details=cust_details, custform=custform, brands=brands)

    else:  
        if custform.validate_on_submit():
            
            cust_fname = custform.firstname.data 
            cust_lname = custform.lastname.data
            cust_email = custform.email.data
            contact_no = custform.contact_no.data
            contact_addr = custform.contact_addr.data
            password1 = custform.password.data
            picture = custform.cust_pict.data

            # Check if the email is already in use, and exclude the current customer
            existing_customer = Customer.query.filter(Customer.cust_email==cust_email, Customer.cust_id!=id).first()
            if existing_customer:
                flash('The email is already in use, Please choose another one', 'error')
                return redirect(url_for('update_profile', id=id))  

            """to get the file name"""
            cust_filename = picture.filename

            if cust_filename != '':
                ext = os.path.splitext(cust_filename)
                extension = ext[-1].lower().replace('.', '')  

                allowed_ext = ['jpg', 'png', 'jpeg']

                # Generate new name
                newfilename = secrets.token_hex(16)
                if extension not in allowed_ext: 
                    flash('Extension is not allowed')
                    return redirect(url_for('sign_up'))  
                else:
                    picture.save(f"pkg/static/uploads/{newfilename}.{extension}") 
                    hashed = generate_password_hash(password1)

                
                customer.cust_firstname=cust_fname 
                customer.cust_lastname=cust_lname
                customer.cust_email=cust_email 
                customer.cust_phone_number=contact_no 
                customer.cust_bill_address=contact_addr 
                customer.cust_password=hashed 
                customer.cust_image=f"{newfilename}.{extension}" 
                

                try:
                    db.session.commit()
                    flash('Profile successfully updated', 'success')
                    return redirect('/')
                except Exception as e:
                    db.session.rollback()  
                    print(f"Error Updating Profile: {e}") 
                    flash('An error occurred while updating your profile. Please try again.', 'error')
        else:
            print(f"Form validation errors: {custform.errors}")

            flash('Form validation failed, All fields are required! Please check your input.', 'error')
            return redirect(url_for('update_profile', id=id))  # Redirect if form validation fails  
    return render_template('/customer/update_profile.html', customer=customer,  cust_details=cust_details, custform=custform, brands=brands)
















@app.route('/')
def index():
    countries = db.session.query(Country).all()
    products = db.session.query(Product).all() 
    onsales = db.session.query(Product).filter(Product.prod_featured_id == 1).all()
    featured = db.session.query(Product).filter(Product.prod_featured_id == 2).all()
    categories = Category.query.order_by(Category.cat_name).all()
    brands = Brand.query.order_by(Brand.brand_name).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('index.html', countries=countries, products=products,  categories=categories, brands=brands, cust_details=cust_details, onsales=onsales, featured=featured) 



@app.route('/men_section/')
def men_section():
    countries = db.session.query(Country).all()
    brands = Brand.query.order_by(Brand.brand_name).all()
    categories = Category.query.order_by(Category.cat_name).all()
    men_prods = db.session.query(Product).filter(Product.prod_category_id==1).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('menSection.html', countries=countries, brands=brands, men_prods=men_prods, categories=categories, cust_details=cust_details)


@app.route('/women_section/')
def women_section():
    countries = db.session.query(Country).all()
    brands = Brand.query.order_by(Brand.brand_name).all()
    categories = Category.query.order_by(Category.cat_name).all()
    women_prods = db.session.query(Product).filter(Product.prod_category_id==3).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('womenSection.html', countries=countries, brands=brands, women_prods=women_prods, categories=categories, cust_details=cust_details) 



@app.route('/products/')
def products():
    countries = db.session.query(Country).all()
    products = db.session.query(Product).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('products.html', countries=countries, products=products, cust_details=cust_details) 



@app.route('/about/company/')
def about_company():
    countries = db.session.query(Country).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('about.html', countries=countries, cust_details=cust_details) 



@app.route('/information/client_support/')
def client_support():
    countries = db.session.query(Country).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('customer/client_support.html', countries=countries, cust_details=cust_details) 




@app.route('/policies/cookie_notice/')
def cookie_notice():
    countries = db.session.query(Country).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('cookie_notice.html', countries=countries, cust_details=cust_details)



@app.route('/policies/legal_notice/')
def legal():
    countries = db.session.query(Country).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('legal.html', countries=countries, cust_details=cust_details) 




@app.route('/pages/return_policy/')
def return_policy():
    countries = db.session.query(Country).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('customer/return_policy.html', countries=countries, cust_details=cust_details) 




@app.route('/pages/faq/')
def faq():
    countries = db.session.query(Country).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('customer/faq.html', countries=countries, cust_details=cust_details) 




@app.route('/policies/shipping_policy/')
def shipping_policy():
    countries = db.session.query(Country).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('customer/shipping.html', countries=countries, cust_details=cust_details) 


@app.route('/career/')
def career():
    countries = db.session.query(Country).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('career.html', countries=countries, cust_details=cust_details) 


@app.route('/collection/summer/')
def summer_collection():
    countries = db.session.query(Country).all()
    product1 = db.session.query(Product).filter(Product.prod_id == 24).first()
    product2 = db.session.query(Product).filter(Product.prod_id == 22).first()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('summer.html', countries=countries, cust_details=cust_details, product1=product1, product2=product2) 



@app.route('/shop/category/<int:id>/')
def shop_category(id):
    countries = db.session.query(Country).all()
    prod_category = db.session.query(Product).filter(Product.prod_category_id==id).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('product_category.html', countries=countries, prod_category=prod_category, cust_details=cust_details) 



@app.route('/brand_products/<int:brand_id>/<int:category_id>/')
def brand_products(brand_id, category_id):
    countries = db.session.query(Country).all()
    # Get all brands and categories for dropdowns
    brands = Brand.query.order_by(Brand.brand_name).all()
    categories = Category.query.order_by(Category.cat_name).all()
    brand = Brand.query.get_or_404(brand_id)

    # Filter products by selected brand and category
    filtered_products = db.session.query(Product).filter(Product.prod_brand_id == brand_id,Product.prod_category_id == category_id).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None

    return render_template('brandproducts.html',countries=countries,brand=brand,brands=brands,categories=categories,products=filtered_products, cust_details=cust_details)




@app.route('/collection/ada_ajuronu/')
def latest_feat_one():
    countries = db.session.query(Country).all()
    brand_products = db.session.query(Product).filter(Product.prod_brand_id==1).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('latest_one.html', countries=countries, brand_products=brand_products, cust_details=cust_details) 


@app.route('/collection/mikeal_mbatha/')
def latest_feat_two():
    countries = db.session.query(Country).all()
    brand_products = db.session.query(Product).filter(Product.prod_brand_id==3).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('latest_two.html', countries=countries, brand_products=brand_products, cust_details=cust_details) 


@app.route('/collection/valentina_dermaco/')
def latest_feat_three():
    countries = db.session.query(Country).all()
    brand_products = db.session.query(Product).filter(Product.prod_brand_id==9).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None 
    return render_template('latest_three.html', countries=countries, brand_products=brand_products, cust_details=cust_details) 





#===================================================================================================================
#==============================  SEARCH  ==============================================================

@app.route('/search/', methods=['POST', 'GET'])
def search():
    search_val = request.form.get('search_val')

    if not search_val or search_val.strip() == '':
        return ''

    # Perform queries for categories, brands, and products
    categories = db.session.query(Category).filter(Category.cat_name.like(f'%{search_val}%')).all()
    brands = db.session.query(Brand).filter(Brand.brand_name.like(f'%{search_val}%')).all()
    products = db.session.query(Product).filter(Product.prod_name.like(f'%{search_val}%')).all()

    # If no results, return an early response
    if not categories and not brands and not products:
        return f"<p class='mt-3'>No items found for '{search_val}'</p>"
    
    rows = []

    # Add rows for categories with links
    for cat in categories:
        rows.append(f'<tr><td>Category</td><td><a href="/category/{cat.cat_id}/">{cat.cat_name}</a></td></tr>')
    
    # Add rows for brands with links
    for brand in brands:
        rows.append(f'<tr><td>Brand</td><td><a href="/brand/{brand.brand_id}/">{brand.brand_name}</a></td></tr>')
    
    # Add rows for products with links
    for product in products:
        rows.append(f'<tr><td>Product</td><td><a href="/product/{product.prod_id}/">{product.prod_name}</a></td></tr>')

    # Join rows to form the table body
    rows_html = ''.join(rows)
    
    # Create the final HTML table
    table_html = f'''
    <table cellpadding="10" cellspacing="0" class='mt-1 table-custom'>
      <thead>
        <tr>
          <th>Type</th>
          <th>Name</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
    ''' 
    
    # Return the final HTML table
    return table_html


    
#==========================================================================================================
#=========================== DISPLAYING SELECTED SEARCH RESULTS===========================================

@app.route('/brand/<int:brand_id>/', methods=['GET'])
def search_brand(brand_id):
    # Fetch all products related to the brand
    products = db.session.query(Product).filter_by(prod_brand_id=brand_id).all()
    brand = Brand.query.get_or_404(brand_id)
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None
    return render_template('search_brand.html', brand=brand, products=products, cust_details=cust_details)
    
    
    
@app.route('/category/<int:category_id>/', methods=['GET'])
def search_category(category_id):
    category = Category.query.get_or_404(category_id)
    # Fetch all products in the category
    products = db.session.query(Product).filter_by(prod_category_id=category_id).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None
    return render_template('search_category.html',category=category, products=products, cust_details=cust_details)
    
    
    
@app.route('/product/<int:product_id>/', methods=['GET'])
def search_product(product_id):
    product = Product.query.get_or_404(product_id)
    # Fetch product details
    product = db.session.query(Product).get(product_id)
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None
    return render_template('search_product.html', product=product, cust_details=cust_details)
    
   


#===================================================================================================================
#==============================  CART  ==============================================================

def initialize_cart():
    if 'cart' not in session:
        session['cart'] = []



# FUNCTION TO GET THE TOTAL NUMBER OF ITEMS IN THE CART 
def cart_item_count():
    return sum(item['quantity'] for item in session['cart'])


#ADD TO CART (OFF CANVAS) 
@app.route('/choose_to_add_to_cart/<int:id>/')
def add_to_cart(id):
    selected_product = db.session.query(Product).get_or_404(id)
    categories = Category.query.order_by(Category.cat_name).all()
    brands = Brand.query.order_by(Brand.brand_name).all()
    cust_id = session.get('cust_id')
    if  cust_id:
        cust_details = get_cust_byid(cust_id)
    else:
        cust_details = None
    
    return render_template('/customer/add_to_cart.html', product=selected_product, cust_details=cust_details, categories=categories, brands=brands)


#======================================================================================================
#===============================DISPLAY AND VIEW CART IN OFF CANVAS OR ORDER PAGE======================================================
@app.route('/get_cart_items')
def get_cart_items():
    
    # Initialize variables for cart
    cart_items = []
    total_price = 0
    cart_count = cart_item_count()
    session['cart_count'] = cart_count
    session['total_price'] = total_price

    #To Initialize cart in session
    initialize_cart()

    # Fetch item(products) in the cart
    for item in session['cart']:
        # Use the product_id(it was passed from ajax and used to create a key for item(a dictionary) to store the id of item clicked) from the cart to get the product details from database
        product = db.session.query(Product).get(item['product_id'])  
        total = product.prod_price * item['quantity'] #quantity was passed from ajax and used to create a key for item that's a dict(key:value) to store value of quantity and multiply with price in database
        item['total_amt'] = total
        total_price += total
        session['total_price'] = total_price
        cart_items.append({
            'product': {
                'prod_id': product.prod_id,
                'prod_image_url': product.prod_image_url,
                'prod_name': product.prod_name,
                'prod_description': product.prod_description,
                'prod_price': product.prod_price
            },
            'quantity': item['quantity'],
            'total': total
        })
        
    if request.args.get('my_display') == 'my_order_page':
        
        return render_template('customer/cart_items_for_order.html', 
                           cart_items=cart_items,   # Pass the current cart items
                           total_price=total_price,  # Pass the total price of cart items
                           cart_count=cart_count
                           )
    else:
        return render_template('customer/cart_items.html', 
                           cart_items=cart_items,   # Pass the current cart items
                           total_price=total_price,  # Pass the total price of cart items
                           cart_count=cart_count
                           )


#==============================================================================================
#================================ADDING ITEMS TO CART=============================================

@app.route('/add_to_cart/selected/', methods=['POST'])
def add_to_cart_selected():
    product_id = int(request.form.get('product_id'))  # Convert to int to ensure consistency
    quantity = int(request.form.get('quantity', 1))
   
    # Initialize the cart if it doesn't exist
    initialize_cart()

    # Check if product is already in the cart, if so update quantity
    for item in session['cart']:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        # Add new product to the cart if its not in cart
        session['cart'].append({'product_id': product_id, 'quantity': quantity})

    session.modified = True  # Mark session as modified so that Flask saves the changes
    return jsonify({'status': 'success', 'cart_count': cart_item_count()})



#=========================================================================================================
#========================== ROUTE TO UPDATE OR REMOVE ITEM FROM THE CART=====================================

@app.route('/update_cart/', methods=['POST']) 
def update_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', '1'))  # Default to '1' if no quantity provided
    
    product_id = int(product_id)
    quantity = int(quantity)

    initialize_cart()

    # Update the cart
    for item in session['cart']:
        if item['product_id'] == product_id:  # Compare as int
            if quantity <= 0:
                # Remove item from cart if quantity is 0 or less
                session['cart'].remove(item)
            else:
                # Update the quantity if valid
                item['quantity'] = quantity
            break

    session.modified = True  # Mark session as modified so changes are saved
    return jsonify({'status': 'success', 'cart_count': cart_item_count()})






#====================================================================================================================
#=============================== Get the shipping fee based on the selected country==================================

@app.route('/get_shipping_fee', methods=['POST'])
def get_shipping_fee():
    country_id = request.json.get('country_id')
    
    if country_id:
        # Fetch the shipping fee from the database based on the country ID
        shipping = db.session.query(Shipping).filter(Shipping.ship_count_id == country_id).first()
        
        if shipping:
            return jsonify({
                'status': 'success',
                'ship_fee': shipping.ship_fees_amt
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Shipping fee not found for this country'
            }), 404
    return jsonify({
        'status': 'error',
        'message': 'Invalid country ID'
    }), 400






#=============================================================================================
#================================ORDER AND PAYMENT ROUTE========================================

@app.route('/order/', methods=['POST','GET'])
def order():
    cust_id = session.get('cust_id')
    cust_details = get_cust_byid(cust_id)
    custform = Customer_payment()
    countries = db.session.query(Country).all()
    custform.country_name.choices = [(-1, 'SELECT A COUNTRY')] + [(country.count_id, country.count_name) for country in countries]  
    
    customer_id = session.get("cust_id")
    total_price = session.get('total_price')
    cart = session.get('cart')
    ship_fees = 0
    
    if customer_id:
        customer = db.session.query(Customer).get_or_404(customer_id)
        
    if request.method == 'POST':
        country_id = custform.country_name.data
        
        # Get shipping details from database
        shipping = db.session.query(Shipping).filter(Shipping.ship_count_id == country_id).first()
        if shipping:
            ship_fees = shipping.ship_fees_amt
            shipping_id  = shipping.ship_id
            session['ship_fees'] = ship_fees
            
            ship_fees = float(ship_fees) #convert to decimal
        else:
            flash('Shipping fee could not be determined.', 'danger')
            return redirect('/order/') 
        
         # Calculate total price with shipping fee
        total_price = float(total_price) + ship_fees
        
        ref = random.randint(10000000000000,9000000000000000000)
        ref_no = f"CP{ref}"
        session['ref'] = ref_no
        
        # Create a new order
        order = Order(order_count_id=country_id,order_total_amt=total_price,order_cust_id=customer_id,order_ship_id=shipping_id,order_status='pending')
        db.session.add(order)
        db.session.commit()
        
        #Get the newly created order's order_id to assign to ord_item_order_id for order items
        order_id = order.order_id
        
        #Inserting all order_items
        for item in cart:
            order_item = Order_item(ord_item_quant=item['quantity'], ord_item_prod_id=item['product_id'], ord_item_total_amt=item['total_amt'], ord_item_order_id=order_id)
            db.session.add(order_item)
        
        db.session.commit()  # Commit all the order items

        #Create payment entry
        payment = Payment(pay_order_id=order_id,pay_amount=total_price,pay_reference=ref_no,pay_status='pending')
        db.session.add(payment)
        db.session.commit()

        if payment.pay_id:
            if cust_id:
                flash('Please confirm payment','warning')
            return redirect('/customer/proceed_to_payment/')
        else:
            flash('Please start the order again','warning')
            return redirect('/order/')

    
    return render_template('/customer/order.html', custform=custform, total_price=total_price, cust_details=cust_details)  



#=============================================================================================================
#===================================PROCEED TO PAYMENT=========================================================

@app.route('/customer/proceed_to_payment/', methods=['POST', 'GET'])
def proceed_to_payment():
    cust_id = session.get('cust_id')
    
    # If customer ID is not present in session, redirect to login
    if not cust_id:
        flash('Please login or sign up to proceed to payment', 'warning')
        return redirect('/logIn/')

    cust_details = get_cust_byid(cust_id)
    ref = session.get('ref')
    
    print(f"Reference from session: {ref}")

    # If reference is not found, redirect to start a new order
    if not ref:
        flash('Please start the order again', 'warning')
        return redirect('/order/')
    
    # Getting cart data from session
    cart = session.get('cart', [])
    cart_items = []

    total_price = float(session.get('total_price', 0))
    ship_fees = float(session.get('ship_fees', 0))

    # Calculate subtotal
    sub_total = total_price - ship_fees

    # Fetch product details for each item in the cart
    for item in cart:
        product = db.session.query(Product).get(item['product_id'])
        cart_items.append({
            'product': product,
            'quantity': item['quantity']
        })

    # Render the payment page
    return render_template("/customer/proceed_to_payment.html",cust_details=cust_details,total_price=total_price,ship_fees=ship_fees,sub_total=sub_total,cart=cart_items)

    
        

    
    
"""route that communicates with paystack api to accept payment"""
@app.route('/payment/paystack/',methods=['POST'])
def pay_with_paystack():
    cust_id = session.get('cust_id')
    if cust_id:
        ref = session.get('ref')
        api_key = app.config['API_KEY']
        if ref:
            url = "https://api.paystack.co/transaction/initialize"
            headers = {"Content-Type":"application/json", "Authorization":f"Bearer {api_key}"}

            payment_details = Payment.query.filter(Payment.pay_reference == ref).first()  

            # Fetch the actual customer object using the customer ID
            customer = db.session.query(Customer).filter_by(cust_id=cust_id).first()
            customer_email = customer.cust_email

            # Converting the Decimal pay_amount to a float
            pay_amount_float = float(payment_details.pay_amount)

            # Prepare the data for Paystack
            data = {
                "email": customer_email,
                "amount": pay_amount_float * 100,  # Paystack expects amount in kobo (i.e., *100 for cents)
                "reference": ref,
                "callback_url": "http://127.0.0.1:5900/payment/landing/"
            }

            # Send the request to Paystack
            rspjson = requests.post(url, headers=headers, data=json.dumps(data))

            # Parse the JSON response (convert to Python)
            resp_dict = rspjson.json()

            # Redirect to Paystack authorization URL if successful
            if resp_dict and resp_dict.get('status') == True:
                auth_url = resp_dict['data']['authorization_url']
                return redirect(auth_url)
            else:
                flash('Please start the order again', 'warning')
                return redirect('/order/')
        else:
            flash('Please start the order again','warning')       
    else:
        flash('Please login or sign up to proceed')
        return redirect('/login/')





"""confirm successful transaction and update our database"""
@app.route('/payment/landing/')
def payment_success():
    cust_id = session.get('cust_id')
    if cust_id:
        ref = session.get('ref')
        trxref = request.args.get('trxref')
        api_key = app.config['API_KEY']

        ## checking if our reference matches the reference from paystack
        if (ref != None) and (ref == trxref):
            url = f"https://api.paystack.co/transaction/verify/{ref}"
            headers = {"Authorization":f"Bearer {api_key}"} 
            rsp_json = requests.get(url,headers=headers)
            resp_dict = rsp_json.json()
            print(resp_dict)

            """checking if the transcation was successfull"""
            payment = Payment.query.filter(Payment.pay_reference == ref).first()
            order = Order.query.filter(Order.order_cust_id == cust_id).first()
            if resp_dict['data']['status'] == "success":
                flash("Your payment was successful","success")
                payment.pay_status = "successful"
                order.order_status = "completed"
                db.session.commit()
                session['cart'] = []
                return redirect('/payment/confirmation/')
            
            else:
                flash("Payment was not successful")
                payment.pay_status = "declined"
                order.order_status = "cancelled"
                db.session.commit()
                return redirect('/order/')
        else:
            flash('Please start the order again','warning')
            return redirect('/order/')
    else:
        flash('Please login or sign up to proceed')
        return redirect('/login/')



   
@app.route("/payment/confirmation/")
def pay_confirmation():
    cust_id = session.get('cust_id')
    if cust_id:
        cust_details = get_cust_byid(cust_id)
        ref = session.get('ref')
        
        if ref:
            # Getting cart data from session
            cart = session.get('cart', [])
            cart_items = []

            total_price = float(session.get('total_price', 0))
            ship_fees = float(session.get('ship_fees', 0))

            # Calculate subtotal
            sub_total = total_price - ship_fees

            # Fetch product details for each item in the cart
            for item in cart:
                product = db.session.query(Product).get(item['product_id'])
                cart_items.append({
                    'product': product,
                    'quantity': item['quantity']
                })
            return render_template("/customer/payment_confirmation.html",
                                cust_details=cust_details, 
                                total_price=total_price, 
                                ship_fees=ship_fees, 
                                sub_total=sub_total, 
                                cart=cart_items)
        else:
            flash('Please start the order again','warning')
            return redirect('/order/') 
    else:
        flash('Please login or sign up to proceed')
        return redirect('/login/')  
    

