from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_dance.consumer.base import oauth_authorized
from flask_dance.contrib.github import make_github_blueprint, github
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_caching import Cache
from flask_modus import Modus
from flask_bcrypt import Bcrypt
from werkzeug.urls import url_parse
import dotenv
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =os.getenv('database')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] =os.getenv('secret_key')
modus = Modus(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)



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

if __name__=='__main__':
    manager.run()