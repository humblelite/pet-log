from marshmallow_sqlalchemy import ModelSchema
from project.models import Pet


# Schema for json object in application
# json object for pets will be under all pets inside application
class PetSchema(ModelSchema):
    class Meta:
        model = Pet
