from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, SelectField, ValidationError
from flask_wtf.file import FileField, FileAllowed,FileRequired
from wtforms.validators import DataRequired, Email, Length, EqualTo

class Login_form(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(message='Email is not in a valid format'), Email()])
    password = PasswordField('Password', validators=[DataRequired(message='Password required')])
    submit = SubmitField('Log in')
    
class Signup_form(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired(message='Firstname is required'), Length(max=50)])
    lastname = StringField('Lastname', validators=[DataRequired(message='Lastname is required'), Length(max=50)])
    email = StringField('E-mail', validators=[DataRequired(message='Email is not in a valid format'), Email()])
    contact_no = StringField('Contact Number', validators=[DataRequired(message='Contact Number is required'), Length(max=50)])
    contact_addr = TextAreaField('Contact Address', validators=[DataRequired(message='Contact Address is required')])
    cust_pict = FileField('Customer Image', validators=[DataRequired(message='Image is required'),FileAllowed(["jpg","png","jpeg"],"Invalid File Format")])
    password = PasswordField('Password', validators=[DataRequired(message='Password required')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message='Confirm Password required'), EqualTo('password', message='Passwords does not match')])
    submit = SubmitField('Sign Up')
    
    
class Update_profile(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired(message='Firstname is required'), Length(max=50)])
    lastname = StringField('Lastname', validators=[DataRequired(message='Lastname is required'), Length(max=50)])
    email = StringField('E-mail', validators=[DataRequired(message='Email is not in a valid format'), Email()])
    contact_no = StringField('Contact Number', validators=[DataRequired(message='Contact Number is required'), Length(max=50)])
    contact_addr = TextAreaField('Contact Address', validators=[DataRequired(message='Contact Address is required')])
    cust_pict = FileField('Customer Image', validators=[DataRequired(message='Image is required'),FileAllowed(["jpg","png","jpeg"],"Invalid File Format")])
    password = PasswordField('Password', validators=[DataRequired(message='Password required')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(message='Confirm Password required'), EqualTo('password', message='Passwords does not match')])
    submit = SubmitField('Update Profile')
    
class Admin_login_form(FlaskForm):
    username = StringField('username', validators=[DataRequired(message='Username is required'), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(message='Password required')])
    submit = SubmitField('Log in')
    
class Admin_register_form(FlaskForm):
    fname = StringField('Firstname', validators=[DataRequired(message='Firstname is required'), Length(max=50)])
    lname = StringField('Lastname', validators=[DataRequired(message='Lastname is required'), Length(max=50)])
    username = StringField('Username', validators=[DataRequired(message='Username is required'), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(message='Email is not in a valid format'), Email()])
    contact_no = StringField('Contact Number', validators=[DataRequired(message='Contact Number is required'), Length(max=50)])
    addr = TextAreaField('Contact Address', validators=[DataRequired(message='Contact Address is required')])
    picture = FileField('Admin Image', validators=[DataRequired(message='Image is required'),FileAllowed(["jpg","png","jpeg"],"Invalid File Format")])
    password = PasswordField('Password', validators=[DataRequired(message='Password required')])
    cpassword = PasswordField('Confirm Password', validators=[DataRequired(message='Confirm Password required'), EqualTo('password', message='Passwords does not match')])
    submit = SubmitField('Sign Up')
    
    
class Admin_add_new_products(FlaskForm):
    prod_name = StringField('Product Name', validators=[DataRequired(message='Product Name is required'), Length(max=50)])
    prod_brand_id =  SelectField('Brand', coerce=int)
    prod_category_id = SelectField('Category', coerce=int)
    prod_featured_id = SelectField('Featured In', coerce=int)
    prod_desc = TextAreaField('Product Description', validators=[DataRequired(message='Product Description is required')])
    prod_price = StringField('product_price', validators=[DataRequired(message='Product Price is required'), Length(max=50)])
    prod_img = FileField('Product Image', validators=[DataRequired(message='Image is required'),FileAllowed(["jpg","png","jpeg"],"Invalid File Format")])
    submit = SubmitField('Add Product')
    
    def validate_prod_category_and_brand_id(self, field):
        if field.data == -1:  # If the default option select a category or brand which has (-1) as value is selected
            raise ValidationError('Please select a valid category.')
    
    
class Admin_update_product(FlaskForm):
    prod_id = StringField('Product Id', validators=[DataRequired(message='Product Id is required'), Length(max=50)])
    prod_name = StringField('Product Name', validators=[DataRequired(message='Product Name is required'), Length(max=50)])
    prod_brand_id =  SelectField('Brand', coerce=int)
    prod_category_id = SelectField('Category', coerce=int)
    prod_featured_id = SelectField('Featured In', coerce=int)
    prod_desc = TextAreaField('Product Description', validators=[DataRequired(message='Product Description is required')])
    prod_price = StringField('product_price', validators=[DataRequired(message='Product Price is required'), Length(max=50)])
    prod_img = FileField('Product Image', validators=[DataRequired(message='Image is required'),FileAllowed(["jpg","png","jpeg"],"Invalid File Format")])
    submit = SubmitField('Update Product')
    
    def validate_prod_category_and_brand_id(self, field):
        if field.data == -1:  # If the default option select a category or brand which has (-1) as value is selected
            raise ValidationError('Please select a valid category.')
    
    
class Admin_add_new_brand(FlaskForm):
    brand_name = StringField('Brand Name', validators=[DataRequired(message='Brand Name is required'), Length(max=50)])
    submit = SubmitField('Add Brand')
    
    
class Admin_update_brand(FlaskForm):
    brand_name = StringField('Brand Name', validators=[DataRequired(message='Brand Name is required'), Length(max=50)])   
    submit = SubmitField('Update Brand')
    
    
class Admin_add_new_category(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired(message='Category Name is required'), Length(max=50)])
    category_desc = TextAreaField('Category Description', validators=[DataRequired(message=' Description is required')])
    submit = SubmitField('Add category')
    
    
class Admin_update_category(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired(message='category Name is required'), Length(max=50)])   
    category_desc = TextAreaField('Category Description', validators=[DataRequired(message='Category Description is required')])
    submit = SubmitField('Update category')
    
class Customer_payment(FlaskForm):
    country_name = SelectField('SHIPPING COUNTRY/REGION *', coerce=int)
    
    def validate_country_id(self, field):
        if field.data == -1:  # If the default option select a country which has (-1) as value is selected
            raise ValidationError('Please select a valid category.')