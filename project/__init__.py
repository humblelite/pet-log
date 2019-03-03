from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_script  import Manager
from flask_dance.contrib.github import make_github_blueprint
from flask_login import LoginManager,current_user
from flask_caching import Cache
from flask_modus import Modus
from flask_bcrypt import Bcrypt
import dotenv
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petlog.db'  #os.getenv('database')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.getenv('secret_key')
modus = Modus(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


github_blueprint = make_github_blueprint(client_id=os.getenv('github_id'), client_secret=os.getenv('github_secret'))
app.register_blueprint(github_blueprint, url_prefix='/github_login')


from project.users.views import users_blueprint
from project.pets.views import pet_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(pet_blueprint)





@app.route('/')
def index():
    if not current_user.is_anonymous:
        return render_template('index.html', id=current_user.id)
    return render_template('index.html')


@app.route('/about')
def about():
    if not current_user.is_anonymous:
        return render_template('about.html', id=current_user.id)
    return render_template('about.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def not_found(error):
    return render_template('errors/500.html'), 500

