from marshmallow import Schema, fields, validate


class AdminSchema(Schema):
    id = fields.Int(required=False)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, load_only=True)


class AdminLoginSchema(Schema):
    email = fields.Str(required=True)  
    password = fields.Str(required=True)