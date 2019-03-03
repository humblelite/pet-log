from flask import render_template, redirect, url_for, flash, request, Blueprint
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.consumer.base import oauth_authorized
from flask_dance.contrib.github import github

from werkzeug.urls import url_parse
from project import db, bcrypt, login_manager, github_blueprint
from flask_login import login_user, login_required, current_user, logout_user
from project.models import User, OAuth
from project.forms import UserSignup, UserLogin
import os
import dotenv

users_blueprint = Blueprint('users', __name__)


# allows users who are authenticated to access login requiered pages.
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


# github oauth2 authentication allows users oauth model to be stored in database and accessed by flask dance.
github_blueprint.backend = SQLAlchemyStorage(OAuth, db.session, user=current_user, user_required=False)


# form validates users, adds them to database and redircts to login page.
@users_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserSignup()
    if form.validate_on_submit():
        try:
            user = User(form.username.data, form.email.data, form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('singup is successful')
        except IntegrityError:
            db.session.rollback()
            flash('username or email already exist')
            return redirect (url_for('users.signup'))
        return redirect(url_for('users.login'))
    return render_template('users/signup.html', form=form)


# login  authentication verifys  users information in database and directs them to there dashboard.
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('pets.user_home', id=current_user.id))
    form = UserLogin()
    if form.validate_on_submit():
        user = form.username.data
        password = form.password.data
        user_query = User.query.filter_by(username=user).first()

        if not user_query is None:
            pw = bcrypt.check_password_hash(user_query.password, password)
            if pw is True:
                login_user(user_query, remember=form.remember.data)
                flash('you are logged in')
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('pets.user_home', id=user_query.id)
                return redirect(next_page)
            else:
                flash('username or password is incorrect')
                return redirect(url_for('users.login'))
        else:
            flash('username or password is incorrect')
            return redirect(url_for('users.login'))
    return render_template('users/login.html', form=form)


# allows user to use github to login into system useing flask dance.
@users_blueprint.route('/github')
def github_login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    return 'you are logged in'


@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    account_info = blueprint.session.get("/user")
    if not account_info.ok:
        return False

    # gets json info from github
    account_json = account_info.json()
    git_user_name = account_json["login"]
    git_user_email = account_json["email"]
    git_user_id = str(account_json["id"])
    git_user_password = os.getenv('github_users_pass')

    # querys for user git hub id.
    oauth_query = OAuth.query.filter_by(provider_user_id=git_user_id)

    # try and except statemment checks if user is registered and logs them in, if not registers
    # users and then logs them in and redirects to dashboard.
    try:
        oauth = oauth_query.one()
        print(oauth_query, git_user_id)
    except NoResultFound:
        oauth = OAuth(provider=blueprint.name, user_id=git_user_id, token=token, provider_user_id=git_user_id)

    if oauth.user:
        user_query = User.query.filter_by(id=oauth.user_id).first()
        login_user(user_query)
        flash("logged in with github")
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('pets.user_home', id=oauth.user_id)
            return redirect(next_page)

    else:
        user = User(username=git_user_name, email=git_user_email, password=git_user_password)
        oauth.user = user
        db.session.add(user)
        db.session.commit()
        db.session.add(oauth)
        db.session.commit()
        login_user(user)
        flash('account created')
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('pets.user_home', id=user.id)
            return redirect(next_page)

    return False


# flask login logout function to logout users and redirct to homepage.
@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
