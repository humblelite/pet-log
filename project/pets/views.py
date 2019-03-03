from flask import Flask, render_template, redirect, url_for, request, jsonify, Blueprint
from project import db, modus, login_manager
from project.models import *
from project.forms import PetForm
from project.api import PetSchema
from flask_login import current_user, login_required

pet_blueprint = Blueprint('pets', __name__)


@pet_blueprint.route('/home/<int:id>', methods=['GET', 'POST'])
@login_required
def user_home(id):
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
        return redirect(url_for('pets.user_home', id=id))
    return render_template('home.html', id=id, name=current_user.username, pets=category, form=form)


@pet_blueprint.route('/home/<int:id>/<pet>')
@login_required
def pet_type(id, pet):
    category = Category.query.all()
    pet_finder = Category.query.filter_by(cat_name=pet).first()
    user_pets = Pet.query.filter_by(pet_user_id=id, pet_cats=pet_finder.id).all()
    return render_template('show_pets.html', id=id, pet=pet, pets=category, user_pets=user_pets)


@pet_blueprint.route('/home/<int:id>/<pet>/<item>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@login_required
def edit(id, pet, item):
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
            return redirect(url_for('pets.user_home', id=id))
    if request.method == b'DELETE':
        db.session.delete(pet_query)
        db.session.commit()
        return redirect(url_for('pets.user_home', id=id))

    return render_template('edit.html', id=id, pet=pet, item=item, pets=category, form=form)


@pet_blueprint.route('/home/<int:id>/list')
@login_required
def pet_list_json(id):
    pet_schema = PetSchema(many=True)
    items_list = Pet.query.filter_by(pet_user_id=id).all()
    pet_dump = pet_schema.dump(items_list).data
    return jsonify({'pets': pet_dump})
