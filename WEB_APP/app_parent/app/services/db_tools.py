import json
from flask_jwt_extended import create_refresh_token
import uuid
from flask import request, abort

import sys
from app import db
from app.models.user import User
from app.models.user import RoleEnum
from app.services.jwt_tools import generate_token
RoleEnum = RoleEnum
def transact_and_record(operation, entity, **kwargs):
    try:
        operation(entity)
        db.session.commit()
        
        # Record the transaction
        try:
            with open('transactions.json', 'a') as file:
                file.write(json.dumps({
                    "operation": operation.__name__,
                    "entity": str(entity),
                    "parameters": kwargs
                }) + "\n")
        except IOError:
            print("Error recording transaction to file.")
        
    except Exception as e:
        db.session.rollback()
        print("Error during transaction: ", e)



def create_user(phone, password=None, role=RoleEnum.admin):
    user = User(phone=phone, password=password, role=role)
    user.refresh_token = create_refresh_token(identity=user.id)
    user.long_term_token = generate_token()
    transact_and_record(db.session.add, user)
    return user

def update_user(user, **kwargs):
    for key, value in kwargs.items():
        setattr(user, key, value)
    refresh_token = kwargs.get('refresh_token')
    if refresh_token:
        user.refresh_token = refresh_token
    transact_and_record(db.session.commit, user, **kwargs)
    return user
def get_user_by_id(id):
    return User.query.get(id)



def delete_user(user):
    transact_and_record(db.session.delete, user)



def get_user_by_phone(phone):
    return User.query.filter_by(phone=phone).first()

