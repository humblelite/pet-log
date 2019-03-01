from flask import Flask, render_template, redirect, url_for, flash, request, Blueprint
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.consumer.base import oauth_authorized
from flask_dance.contrib.github import github
from werkzeug.urls import url_parse
from project import db, bcrypt, login_manager, github_blueprint
from flask_login import login_user, login_required, current_user, logout_user
from project.models import *
from project.forms import *
import os
import dotenv

users_blueprint = Blueprint('users',__name__)
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


github_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)





@users_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserSignup()
    if form.validate_on_submit():
        user = User(form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('singup is successful')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_home', id=current_user.id))
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
                    next_page = url_for('user_home', id=user_query.id)
                return redirect(next_page)
            else:
                flash('username or password is incorrect')
                return redirect(url_for('login'))
        else:
            flash('username or password is incorrect')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/github')
def github_login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    return 'you are logged in'


@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):

    account_info = blueprint.session.get("/user")
    if not account_info.ok:
        return False

    account_json = account_info.json()
    git_user_name = account_json["login"]
    git_user_email = account_json["email"]
    git_user_id = str(account_json["id"])
    git_user_password = os.getenv('github_users_pass')

    oauth_query = OAuth.query.filter_by(provider_user_id=git_user_id)
    try:
        oauth = oauth_query.one()
        print(oauth_query, git_user_id)
    except NoResultFound:
        oauth = OAuth(provider=blueprint.name, user_id=git_user_id, token=token, provider_user_id=git_user_id)

    if oauth.user:
        user_query = User.query.filter_by(id=oauth.user_id).first()
        print(user_query)
        login_user(user_query)
        flash("logged in with github")
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('user_home', id=oauth.user_id)
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
            next_page = url_for('user_home', id=user.id)
            return redirect(next_page)


    return False


@users_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

