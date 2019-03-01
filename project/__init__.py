from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_dance.consumer.base import oauth_authorized
from flask_dance.contrib.github import make_github_blueprint, github
from marshmallow_sqlalchemy import ModelSchema
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_caching import Cache
from flask_modus import Modus
from flask_bcrypt import Bcrypt
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, TextAreaField, \
    SelectField
from wtforms.validators import DataRequired
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


##### models####
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(70), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password = db.Column(db.String())
    pet = db.relationship('Pet', lazy='dynamic', cascade='all')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password)


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    provider_user_id = db.Column(db.Integer, unique=True)

    def __init__(self, provider, user_id, token, provider_user_id):
        self.provider = provider
        self.user_id = user_id
        self.token = token
        self.provider_user_id = provider_user_id


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String)
    cat_items = db.relationship('Pet', backref='category', lazy='dynamic')

    def __init__(self, cat_name):
            self.cat_name = cat_name



class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pet_name = db.Column(db.String)
    pet_description = db.Column(db.String)
    pet_cats = db.Column(db.Integer, db.ForeignKey('category.id'))
    pet_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, pet_name, pet_description, pet_cats, pet_user_id):
        self.pet_name = pet_name
        self.pet_description = pet_description
        self.pet_cats = pet_cats
        self.pet_user_id = pet_user_id





###########  models ############

class PetSchema(ModelSchema):
    class Meta:
        model = Pet


############  Forms #############
class UserSignup(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(),
                                             validators.Email()])
    password = PasswordField('password', validators=[DataRequired(),
                                                     validators.EqualTo('confirm',
                                                                        message='password must be the same')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('submit')


class UserLogin(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Please enter Username')])
    password = PasswordField('Password', validators=[DataRequired('please enter password')])
    remember = BooleanField('Remember Me', )
    submit = SubmitField('Submit')


class PetForm(FlaskForm):
    animal_type = SelectField('Pet Type', choices=[], coerce=int)
    pet_name = StringField("Pet Name", validators=[DataRequired()])
    pet_desc = TextAreaField("Pet Description", validators=[DataRequired()])
    submit = SubmitField('submit')


############# Foms ##################


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


github_blueprint = make_github_blueprint(client_id=os.getenv('github_id'), client_secret=os.getenv('github_secret'))
app.register_blueprint(github_blueprint, url_prefix='/github_login')

github_blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)


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


############ user routes ##########

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserSignup()
    if form.validate_on_submit():
        user = User(form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('singup is successful')
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


##################/user route############


######## user page routes ###############
@app.route('/home/<int:id>', methods=['GET', 'POST'])
@login_required
def user_home(id):
    #category = Category.query.filter_by(user_id=id).all()
    category = Category.query.all()
    form = PetForm()
    form.animal_type.choices = [(pet.id, pet.cat_name) for pet in category]
    if form.validate_on_submit():
        pet_name = form.pet_name.data
        pet_desc = form.pet_desc.data
        pet_category = form.animal_type.data
        pet_query = Pet(pet_cats=pet_category, pet_name=pet_name, pet_description=pet_desc, pet_user_id=id)
        db.session.add(pet_query)
        db.session.commit()
        return redirect(url_for('user_home', id=id))
    return render_template('home.html', id=id, name=current_user.username, pets=category, form=form)


@app.route('/home/<int:id>/<pet>')
@login_required
def pet_type(id, pet):
   #category = Category.query.filter_by(user_id=id).all()
   category = Category.query.all()
   pet_finder = Category.query.filter_by(cat_name=pet).first()
   user_pets = Pet.query.filter_by(pet_user_id=id, pet_cats=pet_finder.id).all()
   return render_template('show_pets.html', id=id, pet=pet, pets=category, user_pets=user_pets)


@app.route('/home/<int:id>/<pet>/<item>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@login_required
def edit_pet(id, pet, item):
    category = Category.query.all()
    pet_query = Pet.query.filter_by(pet_name=item, pet_user_id=id).first()
    form = PetForm(request.form)
    form.animal_type.choices = [(pet.id, pet.cat_name) for pet in category]
    if request.method == b'PATCH':
        if form.validate():
            pet_query.pet_cats = form.animal_type.data
            pet_query.pet_name = form.pet_name.data
            pet_query.pet_description = form.pet_desc.data
            db.session.add(pet_query)
            db.session.commit()
            return redirect(url_for('user_home', id=id))
    if request.method == b'DELETE':
        db.session.delete(pet_query)
        db.session.commit()
        return redirect(url_for('user_home', id=id))

    return render_template('edit.html', id=id, pet=pet, item=item, pets=category, form=form)


@app.route('/home/<int:id>/petlist')
@login_required
def pet_list_json(id):
    pet_schema = PetSchema(many=True)
    items_list = Pet.query.filter_by(pet_user_id=id).all()
    pet_dump = pet_schema.dump(items_list).data
    return jsonify({'pets': pet_dump})


########### error routes ############
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def not_found(error):
    return render_template('errors/500.html'), 500

if __name__=='__main__':
    manager.run()