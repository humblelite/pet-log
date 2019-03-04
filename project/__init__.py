from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_script import Manager
from flask_dance.contrib.github import make_github_blueprint
from flask_login import LoginManager, current_user
from flask_caching import Cache
from flask_modus import Modus
from flask_bcrypt import Bcrypt
import dotenv
import os

app = Flask(__name__)

# ENVIRONMENT VARIABLES
SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
GITHUB_ID = os.getenv('GITHUB_ID')
GITHUB_SECRET = os.getenv('GITHUB_SECRET')

# Configuration for database.

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

# used modus for crud methods patch and delete.
modus = Modus(app)

# used bcrypt to encrypt passwords.
bcrypt = Bcrypt(app)

db = SQLAlchemy(app)

# used by manage.py file to create migrations scripts and database.
migrate = Migrate(app, db)
manager = Manager(app)

# caching for storing tokens in browser.
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# used flask login for  authentication system.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# used flask dance for oauth2 authentication.
github_blueprint = make_github_blueprint(client_id=GITHUB_ID,
                                         client_secret=GITHUB_SECRET)
app.register_blueprint(github_blueprint, url_prefix='/github_login')

# blue prints from user and pet views.
# import needs to be here to run.
from project.users.views import users_blueprint
from project.pets.views import pet_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(pet_blueprint)


@app.route('/')
def index():
    # if statement to allow loged in users to access
    # homepage without having to log out.
    if not current_user.is_anonymous:
        return render_template('index.html', id=current_user.id)
    return render_template('index.html')


@app.route('/about')
def about():
    # if statement allows logged in users to access about page.
    if not current_user.is_anonymous:
        return render_template('about.html', id=current_user.id)
    return render_template('about.html')


# flask error handling.
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def not_found(error):
    return render_template('errors/500.html'), 500
