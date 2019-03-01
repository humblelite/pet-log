from marshmallow_sqlalchemy import ModelSchema


# Schema for json objet in application
# json object for pets will be under allpets inside application
class PetSchema(ModelSchema):
    class Meta:
        model = Pet
