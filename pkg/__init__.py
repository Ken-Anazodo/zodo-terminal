import os
from flask import Flask, session
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
# from datetime import timedelta
from pkg.models import db

load_dotenv()
csrf= CSRFProtect()
def create_app():
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile('config.py',silent=True)
    # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) #session timeout
    app.config['UPLOAD_FOLDER'] = 'pkg/static/uploads/'
    app.config['PAYSTACK_API_KEY'] = os.getenv('PAYSTACK_API_KEY')
    app.config['CLOUDINARY_API_KEY'] = os.getenv('CLOUDINARY_API_KEY')
    app.config['CLOUDINARY_API_SECRET'] = os.getenv('CLOUDINARY_API_SECRET')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['CLOUD_NAME'] = os.getenv('CLOUD_NAME')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    
    
    # Global CSRF timeout setting
    # app.config['WTF_CSRF_TIME_LIMIT'] = 7000  # Timeout in seconds
    
    db.init_app(app)
    migrate = Migrate(app,db)
    csrf.init_app(app)
    
    #session timeout setting
    # @app.before_request
    # def make_session_permanent():
    #     session.permanent = True

    return app

app = create_app()


from pkg import admin_routes, customer_routes, forms, models, error_routes






