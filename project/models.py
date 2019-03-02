from project import db, bcrypt
from flask_login import UserMixin
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin


# user model for application authentication and authorization.
# one to manny user to pet relationship.
# has flask_login User mixin library.
# bcrypt library to hash passwords in the init method.
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


# Using flask dance oauthconsumermixin library for oauth 2 with github.
# add provider_user_id to connect github user id with users.
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    provider_user_id = db.Column(db.Integer, unique=True)

    def __init__(self, provider, user_id, token, provider_user_id):
        self.provider = provider
        self.user_id = user_id
        self.token = token
        self.provider_user_id = provider_user_id


# category is a list  of pet types that are persisted after database creation.
# pet types are dogs, cats, birds, fish, critters, and reptiles.
# has one to many relationship with pets.
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String)
    cat_items = db.relationship('Pet', backref='category', lazy='dynamic')

    def __init__(self, cat_name):
        self.cat_name = cat_name


# pet model holds name and description of the users pets for crud operations.
# pet model also has relationship with users and category for joining.
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
