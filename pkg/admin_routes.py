import os
import json
import requests
from requests.auth import HTTPBasicAuth
from flask import render_template, make_response, redirect, request, session, flash, url_for, jsonify
from werkzeug.security import generate_password_hash,check_password_hash
from pkg import app, db
from flask_wtf.csrf import CSRFError
from pkg.forms import Admin_login_form, Admin_register_form, Admin_add_new_products, Admin_update_product, Admin_update_brand, Admin_add_new_brand, Admin_add_new_category, Admin_update_category
from pkg.models import Administrator, Customer, Category, Product, Brand, Feature, Order
import secrets




# ============================================================================================================
# Sign Up, Login and Authentication Section

def get_admin_byid(id):
    data = Administrator.query.get(id)
    return data 


"""this route is for logging out and redirects the user to the login page"""
@app.route('/admin/logout/')
def admin_logout():
    if session.get('admin_id') != None:
        session.pop('admin_id')
    flash('You are now logged out','success')
    # Create a response for the redirect and prevent page caching
    response = make_response(redirect(url_for('admin_login'))) 
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response



@app.route('/admin_login/', methods=['GET','POST'])
def admin_login():
    adform=Admin_login_form()
    admin_id = session.get('admin_id')
    
    if admin_id:
        admin_details=get_admin_byid(admin_id)
    else:
        admin_details=None
    return render_template('/admin/admin_login.html', adform=adform, admin_details=admin_details) 




@app.route('/submit/admin_login/', methods=['GET','POST'])
def submit_admin_login():
    adform = Admin_login_form() 
    if request.method == 'POST' and adform.validate_on_submit():
        username = adform.username.data
        password = adform.password.data
        
        admin = db.session.query(Administrator).filter(Administrator.admin_username == username).first()
        if admin :
            hashed_password = admin.admin_password
            check = check_password_hash(hashed_password,password)
            if check == True:
                ## save details in session and redirect to dashboard
                session['admin_id'] = admin.admin_id
                return redirect('/admin/dashboard/')
            else:
                flash('Incorrect Password','error')
                return redirect('/admin_login/')
        else:
            flash('Username and Password does not exist','error')
            return redirect('/admin_login/')
    else:
        return render_template('/admin/admin_login.html', adform=adform)
        
            
       


"""this route checks if the email a new user is about to input is taken or avaliable"""
@app.route('/admin/check_email/')
def check_admin_email():
    email = request.args.get('email')
    status = 'Email is avaliable' #email is avaliable
    data = db.session.query(Administrator).filter(Administrator.admin_email == email).first()
    if data:
        status = 'Email has been taken' #email is taken
    return status





@app.route('/admin_register/', methods=['GET', 'POST'])
def admin_register():
    adform = Admin_register_form() 

    if request.method == 'GET':
        return render_template('/admin/admin_register.html', adform=adform)

    else:  
        if adform.validate_on_submit():
            
            admin_fname = adform.fname.data 
            admin_lname = adform.lname.data
            username = adform.username.data
            admin_email = adform.email.data
            contact_no = adform.contact_no.data
            contact_addr = adform.addr.data
            password1 = adform.password.data
            picture = adform.picture.data

            # Check if the email is already in use
            existing_admin = Administrator.query.filter_by(admin_email=admin_email).first()
            if existing_admin:
                flash('The email is already in use, choose another one')
                return redirect(url_for('admin_register'))  # Redirect back to form page

            """to get the file name"""
            admin_filename = picture.filename

            if admin_filename != '':
                ext = os.path.splitext(admin_filename)
                extension = ext[-1].lower().replace('.', '')  

                allowed_ext = ['jpg', 'png', 'jpeg']

                # Generate new name
                newfilename = secrets.token_hex(16)
                if extension not in allowed_ext: 
                    flash('Extension is not allowed')
                    return redirect(url_for('admin_register'))  # Redirect back to form page
                else:
                    picture.save(f"pkg/static/uploads/{newfilename}.{extension}") 
                    hashed = generate_password_hash(password1)

                a = Administrator(
                    admin_firstname=admin_fname, 
                    admin_lastname=admin_lname,
                    admin_username=username, 
                    admin_email=admin_email, 
                    admin_phone_number=contact_no, 
                    admin_contact_addr=contact_addr, 
                    admin_password=hashed, 
                    admin_image=f"{newfilename}.{extension}" 
                )

                try:
                    db.session.add(a)
                    db.session.commit()
                    admin_id = a.admin_id
                    ## saving the id into session
                    session['admin_id'] = admin_id
                    flash('Welcome, an account has been created for you')
                    return redirect('/admin/dashboard/')
                except Exception as e:
                    print(f"Error adding to database: {e}") 
                    flash('An error occurred while creating an account. Please try again.')
                    return redirect(url_for('admin_register'))  
        else:
            flash('Form validation failed. All fields are required!.')
            return redirect(url_for('admin_register'))  # Redirect if form validation fails               


  
#================================================================================================================              

# DASHBOARD SECTION
# used to make data available in all templates or views. (in this case categories and brands data is made available in every template without needing to pass it explicitly in every view or template)
@app.context_processor
def inject_categories_brands():
    categories = db.session.query(Category).all()
    brands = db.session.query(Brand).all()
    return dict(categories=categories, brands=brands)




"""this route checks if the user is logged in and redirects them to the dashboard page"""
"""user cannot visit the page unless they are logged in"""
@app.route('/admin/dashboard/')
def center_dashboard():
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        orders = db.session.query(Order).all()
        products = db.session.query(Product).all()
        brands = db.session.query(Brand).all()
        return render_template('/admin/admin_dashboard_sec.html', admin_details=admin_details, orders=orders, products=products, brands=brands)
    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')
    
    
# Display Categories     
@app.route('/dashboard/category/')
def dashboard_category():
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        categories = db.session.query(Category).all()  
        return render_template('admin/admin_dash_category.html', admin_details=admin_details,  categories=categories)
    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')
    
    
# Display Orders     
@app.route('/dashboard/orders/')
def dashboard_orders():
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        orders = db.session.query(Order).all()  
        return render_template('admin/admin_dash_orders.html', admin_details=admin_details,  orders=orders)
    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')
    
 
#================================================================================================================================
# Display Customers 
@app.route('/dashboard/customers/')
def dashboard_customers():
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        customers = db.session.query(Customer).all()
        categories = Category.query.order_by(Category.cat_name).all()  
        return render_template('admin/admin_dash_customers.html', admin_details=admin_details,  customers=customers, categories=categories)
    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')



# #Display Search Customers template
@app.route('/dashboard/search_name/', methods=['GET', 'POST'])
def dashboard_search():
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        categories = Category.query.order_by(Category.cat_name).all()
        return render_template('admin/admin_dash_search_customers.html', admin_details=admin_details, categories=categories)
    else:
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')
    
    



    
#PRODUCT 
#===================================================================================================================  
# Display Products     
@app.route('/dashboard/products/')
def dashboard_products():
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        products = db.session.query(Product).all()  
        categories = Category.query.order_by(Category.cat_name).all()
        return render_template('admin/admin_dash_prod.html', admin_details=admin_details,  products=products, categories=categories)
    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')
        

# Insert new products
@app.route('/admin/add_new_product/', methods=['GET', 'POST'])
def add_new_products():
    admin_id = session.get('admin_id')
    adform = Admin_add_new_products() 
    brands = db.session.query(Brand).all()
    categories = db.session.query(Category).all()
    features = db.session.query(Feature).all()
    #using list comprehension to loop and get categories from category table(retrieve id and username) which the id is injected into value attr and name into innerhtml of OPTION in SELECT of flask wtf form that uses Choices to indicate it.(choices sets option with tuple values for value attr and innerhtml)
    #[(-1, 'Select a brand')] - this sets the default in the SELECT OPTION(-1 is given to value attr and 'Select a brand' for option innerhtml) (Same for the other select(brand and feature))
    adform.prod_brand_id.choices = [(-1, 'Select a brand')] + [(brand.brand_id, brand.brand_name) for brand in brands]
    adform.prod_category_id.choices = [(-1, 'Select a category')] + [(category.cat_id, category.cat_name) for category in categories] 
    adform.prod_featured_id.choices = [(-1, 'Select a Feature')] + [(feature.featured_id, feature.featured_name) for feature in features]
    
    if not admin_id:
        flash('You need to login to access to this page','error')
        return redirect(url_for('admin_login'))
    
    admin_details = get_admin_byid(admin_id)
    if request.method == 'GET':
        return render_template('/admin/admin_dash_add_new_prod.html', admin_details=admin_details, adform=adform, categories=categories)

    else:  
        if adform.validate_on_submit():
            
            prod_name = adform.prod_name.data 
            prod_brand = adform.prod_brand_id.data
            prod_category = adform.prod_category_id.data
            prod_price = adform.prod_price.data
            prod_desc = adform.prod_desc.data
            prod_img = adform.prod_img.data
            prod_feature = adform.prod_featured_id.data
            
            
            """to get the file name"""
            prod_filename = prod_img.filename

            if prod_filename != '':
                ext = os.path.splitext(prod_filename)
                extension = ext[-1].lower().replace('.', '')  

                allowed_ext = ['jpg', 'png', 'jpeg']

                # Generate new name
                newfilename = secrets.token_hex(16)
                if extension not in allowed_ext: 
                    flash('Extension is not allowed')
                    return redirect(url_for('add_new_products'))  # Redirect back to form page
                else:
                    prod_img.save(f"pkg/static/uploads/{newfilename}.{extension}") 

                b = Product(
                    prod_name=prod_name, 
                    prod_brand_id=prod_brand,
                    prod_category_id=prod_category, 
                    prod_price=prod_price, 
                    prod_description=prod_desc,
                    prod_image_url=f"{newfilename}.{extension}",
                    prod_featured_id=prod_feature
                )

                try:
                    db.session.add(b)
                    db.session.commit()
                    flash('Product added successfully')
                    return redirect('/dashboard/products/')
                except Exception as e:
                    print(f"Error adding to database: {e}") 
                    flash('An error occurred while adding product. Please check the data added and try again.')
                    return redirect(url_for('add_new_products'))  
        else:
            flash('Form validation failed. All fields are required!.')
            return redirect(url_for('add_new_products'))  # Redirect if form validation fails      




# Update Product
@app.route('/admin/update_product/<int:id>/', methods=['GET', 'POST'])
def update_product(id):
    admin_id = session.get('admin_id')
    adform = Admin_update_product()
    product = db.session.query(Product).get_or_404(id)
    brands = db.session.query(Brand).all()
    categories = db.session.query(Category).all()
    features = db.session.query(Feature).all()
    adform.prod_category_id.choices = [(-1, 'Select a category')] + [(category.cat_id, category.cat_name) for category in categories]   
    adform.prod_brand_id.choices = [(-1, 'Select a brand')] + [(brand.brand_id, brand.brand_name) for brand in brands]
    adform.prod_featured_id.choices = [(-1, 'Select a Feature')] + [(feature.featured_id, feature.featured_name) for feature in features]

    if not admin_id:  # If the user is not logged in
        flash('You need to login to access this page', 'error')
        return redirect(url_for('admin_login'))

    admin_details = get_admin_byid(admin_id)

    if request.method == 'GET':
        return render_template('admin/admin_dash_update_prod.html', admin_details=admin_details, adform=adform, product=product)
        
    # For POST method
    if adform.validate_on_submit():  # Validate form data and update details in DB
        prod_name = adform.prod_name.data 
        prod_brand = adform.prod_brand_id.data
        prod_category = adform.prod_category_id.data
        prod_price = adform.prod_price.data
        prod_desc = adform.prod_desc.data
        prod_img = request.form.get('image_url')
        prod_feature = adform.prod_featured_id.data
        print(adform)
        
        # Update other product fields even if the image is not uploaded
        product.prod_name = prod_name
        product.prod_brand_id = prod_brand
        product.prod_category_id = prod_category
        product.prod_price = prod_price
        product.prod_description = prod_desc
        product.prod_featured_id = prod_feature
        
        
        # Store the old image public ID to delete it later if a new image is uploaded
        old_image_url = product.prod_image_url
        old_image_public_id = None

        if old_image_url:
            old_image_public_id = "/".join(old_image_url.split('/')[-2:]).split('.')[0]  # Extract public ID from URL

        # Commit changes to the database
        try:
            db.session.commit()
            
            if prod_img:
                # Update product fields with the cloudinary new image
                product.prod_image_url = prod_img
                db.session.commit()  # Commit again to update the image path
                
                
                # Delete old image from Cloudinary
                cloud_name = app.config['CLOUD_NAME']
                api_key = app.config['CLOUDINARY_API_KEY']
                api_secret = app.config['CLOUDINARY_API_SECRET']
                
                if old_image_public_id:
                    delete_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/image/upload"
                    data = {
                        "public_ids": [old_image_public_id],
                        "invalidate": True
                    }
                    response = requests.delete(delete_url, auth=HTTPBasicAuth(api_key, api_secret), data=data)

                    if response.status_code == 200:
                        print("Old image deleted successfully from Cloudinary.")
                    else:
                        print("Error deleting old image:", response.json())
                        
            flash('Product updated successfully', 'success')
            return redirect(url_for('update_product', id=id))

        except Exception as e:
            db.session.rollback()  # Rollback in case of error
            print(f"Error updating the database: {e}")
            flash('An error occurred while adding product. Please check that all input box is filled and try again.', 'error')

    else:
        flash('Form validation failed. All fields are required!', 'error')
        print(adform.errors) 

    # In case of validation failure or error, re-render the form
    return render_template('admin/admin_dash_update_prod.html', admin_details=admin_details, adform=adform, product=product)
  
    
    
 
#TO delete a Product
@app.route('/admin/<int:id>/delete_product/')
def delete_product(id):
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        product = db.session.query(Product).get(id)
        
        if product:
            db.session.delete(product)
            """when deleting you have to commit the updates"""
            db.session.commit()
    
    flash('Category deleted successfully', 'success')
    return redirect('/dashboard/products/')   





@app.route('/dashboard/product_category/<int:id>/')
def product_category(id):
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        products = db.session.query(Product).filter(Product.prod_category_id==id).all() 
    return render_template('/admin/admin_prod_category.html', products=products, admin_details=admin_details) 



   
    
#BRAND  
#===================================================================================================================    
 # Display Brand     
@app.route('/dashboard/brands/')
def dashboard_brands():
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        brands = db.session.query(Brand).all()  
        categories = Category.query.order_by(Category.cat_name).all()
        return render_template('admin/admin_dash_brand.html', admin_details=admin_details,  brands=brands, categories=categories)
    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')
    
    
    
    
# Insert new brand
@app.route('/admin/add_new_brand/', methods=['GET', 'POST'])
def add_new_brand():
    admin_id = session.get('admin_id')
    adform = Admin_add_new_brand() 
    
    if not admin_id:
        flash('You need to login to access to this page', 'error')
        return redirect(url_for('admin_login'))
    
    admin_details = get_admin_byid(admin_id)
    if request.method == 'GET':
        return render_template('/admin/admin_dash_add_new_brand.html', admin_details=admin_details, adform=adform)

    else:  
        # Now proceed with form validation
        if adform.validate_on_submit():
            
            brand_name = adform.brand_name.data 
            
            b = Brand(
                brand_name = brand_name
            )

            try:
                db.session.add(b)
                db.session.commit()
                flash('Brand added successfully', 'success')
                return redirect('/dashboard/brands/')
            except Exception as e:
                print(f"Error adding to database: {e}") 
                flash('An error occurred while adding brand. Please try again.')
                return redirect(url_for('add_new_brand'))  
        else:
            flash('Form validation failed. All fields are required!.', 'error')
            return redirect(url_for('add_new_brand'))  # Redirect if form validation fails



# Update Brand
@app.route('/admin/update_brand/<int:id>/', methods=['GET','POST'])
def update_brand(id):
    admin_id = session.get('admin_id')
    adform = Admin_update_brand()
    brand = db.session.query(Brand).get_or_404(id) 
    if admin_id: #user is logged in

        if request.method == 'GET':
            admin_details = get_admin_byid(admin_id)
            return render_template('admin/admin_dash_update_brand.html', admin_details=admin_details, adform=adform, brand=brand)
        else: 
            if adform.validate_on_submit(): ## validate form data, retrive data and update details in db
                brand_name = adform.brand_name.data 
                
                ## creating an object and putting it into the database
                         
                brand.brand_name=brand_name                

                db.session.commit()

                ## upload file using flask form
                flash('File successful updated')
                return redirect (url_for('update_brand', id=id))
            else:
                admin_details = get_admin_byid(admin_id)
                return render_template('admin/admin_dash_update_brand.html', admin_details=admin_details, adform=adform, brand=brand)

    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')
    
    
    
    
#TO delete a Brand
@app.route('/admin/<int:id>/delete_brand/')
def delete_brand(id):
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        brand = db.session.query(Brand).get(id)
        
        if brand:  
            db.session.delete(brand)
            db.session.commit()  
        
    flash('Brand deleted successfully', 'success')
    return redirect('/dashboard/brands/')




@app.route('/dashboard/brand_products/<int:id>/')
def admin_brand_products(id):
    admin_id = session.get('admin_id')
    products = []  # Initialize products as an empty list

    if admin_id:
        admin_details = get_admin_byid(admin_id)
        products = db.session.query(Product).filter(Product.prod_brand_id == id).all()
        return render_template('/admin/admin_prod_category.html', products=products, admin_details=admin_details)
    
    flash('Admin not logged in', 'error')
    return redirect('/admin_login/')  



#CATEGORY  
#===================================================================================================================    
 # Display Category     
@app.route('/dashboard/categories/')
def dashboard_categories():
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        categories = db.session.query(Category).all()
        return render_template('admin/admin_dash_category.html', admin_details=admin_details,  categories=categories)
    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')
    
    
    
    
# Insert new Category
@app.route('/admin/add_new_category/', methods=['GET', 'POST'])
def add_new_category():
    admin_id = session.get('admin_id')
    adform = Admin_add_new_category() 
    
    if not admin_id:
        flash('You need to login to access to this page','error')
        return redirect(url_for('admin_login'))
    
    admin_details = get_admin_byid(admin_id)
    if request.method == 'GET':
        return render_template('/admin/admin_dash_add_new_category.html', admin_details=admin_details, adform=adform)

    else:  
        if adform.validate_on_submit():
            
            category_name = adform.category_name.data 
            category_desc = adform.category_desc.data


            c = Category(
               cat_name = category_name,
               cat_description = category_desc
            )

            try:
                db.session.add(c)
                db.session.commit()
                return redirect('/dashboard/categories/')
            except Exception as e:
                print(f"Error adding to database: {e}") 
                flash('An error occurred while adding category. Please try again.')
                return redirect(url_for('add_new_category'))  
        else:
            flash('Form validation failed. All fields are required!.')
            return redirect(url_for('add_new_category'))  # Redirect if form validation fails
        
        
        
# Update Category
@app.route('/admin/update_category/<int:id>/', methods=['GET','POST'])
def update_category(id):
    admin_id = session.get('admin_id')
    adform = Admin_update_category()
    category = db.session.query(Category).get_or_404(id)   
    if admin_id: #user is logged in

        if request.method == 'GET':
            admin_details = get_admin_byid(admin_id)
            return render_template('admin/admin_dash_update_category.html', admin_details=admin_details, adform=adform, category=category)
        else: 
            if adform.validate_on_submit(): ## validate form data, retrive data and update details in db
                category_name = adform.category_name.data 
                category_desc = adform.category_desc.data


                ## creating an object and putting it into the database          
                category.cat_name=category_name                
                category.cat_description=category_desc 
                    
                db.session.commit()

                ## upload file using flask form
                flash('Update successful')
                return redirect (url_for('update_category', id=id))
            else:
                admin_details = get_admin_byid(admin_id)
                return render_template('admin/admin_dash_update_category.html', admin_details=admin_details, adform=adform, category=category)
            
    else: #this means session is None
        flash('You need to login to access to this page','error')
        return redirect('/admin_login/')
    




#TO delete a Category
@app.route('/admin/<int:id>/delete_category/')
def delete_category(id):
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)
        category = db.session.query(Category).get(id)
        
        if category:
            db.session.delete(category)
            """when deleting you have to commit the updates"""
            db.session.commit()
    
    flash('Category deleted successfully', 'success')
    return redirect('/dashboard/categories/')



# Provides template based on category for ajax
@app.route('/dashboard/category/<int:id>/brand_products/')
def admin_ajax_brand_products(id):
    admin_id = session.get('admin_id')
    if admin_id:
        admin_details = get_admin_byid(admin_id)     
        # Used it to fetch all prod based on category to prevent the page from being empty before brand selection when a category is selected from dropdown
        products = db.session.query(Product).filter(Product.prod_category_id==id).all()
        #to fetch category by id if available 
        category = db.session.query(Category).get_or_404(id)
    return render_template('/admin/admin_ajax_brand_prods.html', products=products, admin_details=admin_details, category=category) 




# Fetch products based on brand selection using AJAX
@app.route('/category/<int:id>/filter_by_brand/', methods=['POST'])
def filter_products_by_brand(id):
    data = request.get_json()  # Get JSON data sent from AJAX
    
    brand_id = data.get('brand_id')  # Extract brand_id from JSON data
    if brand_id:  # Filter by brand if brand_id is provided
        products = db.session.query(Product).filter(Product.prod_category_id == id, Product.prod_brand_id == brand_id).all()
    else:  # If no brand selected, show all products in the category
        products = db.session.query(Product).filter(Product.prod_category_id == id).all()

    # Prepare the product data to return
    products_data = [{"prod_name": product.prod_name, "prod_price": product.prod_price, "prod_image_url": product.prod_image_url} for product in products]

    return jsonify({'products': products_data})
