import models

import os
import sys
import secrets


from flask import Blueprint, request, jsonify, url_for, send_file
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user 
from playhouse.shortcuts import model_to_dict 

user = Blueprint("users", "user", url_prefix="/user")

#rank user
@user.route('/rank', methods = ["GET"])
def rank_user():

    users=[model_to_dict(userRank) for userRank in models.User.select().order_by(models.User.profit.desc()).limit(5)]

    return jsonify(data=users, status={"code":200,"message":"success"})

#update profit
@user.route('/profit/<id>', methods = ["GET"])
def update_profit(id):
    profits=models.User.get_by_id(id).profit
    return jsonify(data=profits,status={"code":200,"message":"success"})


#register
@user.route("/register", methods=["POST"])
def register():
    # payload = request.get_json()
    payload = request.form.to_dict()

    print(payload)
    print('this is the payload')
    
    payload['email'].lower() 

    try:
        models.User.get(models.User.email == payload["email"])
        return jsonify(data={}, status={"code": 401, "message": "A user with that name or email exists"})
    except models.DoesNotExist: 
        payload["password"] = generate_password_hash(payload["password"])

        user = models.User.create(username=payload['username'], password=payload['password'], email=payload['email'], profit = 0 ) 

        login_user(user)
        user_dict = model_to_dict(user)


        del user_dict["password"]

        return jsonify(data=user_dict, status={"code": 201, "message": "Success"})


#login
@user.route('/login', methods=["POST"])
def login():
    payload = request.get_json()
    print(payload, '< --- this is playload')
    try:
        user = models.User.get(models.User.username== payload['username'])
        user_dict = model_to_dict(user)
        if(check_password_hash(user_dict['password'], payload['password'])):
            del user_dict['password']
            login_user(user)
            print(user, ' this is user')
            return jsonify(data=user_dict, status={"code": 200, "message": "Success"})
        else:
            return jsonify(data={}, status={"code": 401, "message": "Username or Password is incorrect"})
    except models.DoesNotExist:
        return jsonify(data={}, status={"code": 401, "message": "Username or Password is incorrect"})



#update password
@user.route('/pw/<id>', methods=["PUT"])
def edit_pw(id):
    print("route hit pw edit")
    payload = request.get_json()
    print(payload,"<pw payload")
    try:
        user = models.User.get(models.User.id==id)
        user_dict = model_to_dict(user)
        if(check_password_hash(user_dict['password'],payload['password']) and (payload["newPw"]==payload["confirmPw"])):
            payload["newPw"] = generate_password_hash(payload["newPw"])
            query= models.User.update(password=payload["newPw"]).where(models.User.id == id)
            query.execute()
            
            updated_user = models.User.get_by_id(id)

            return jsonify(data=model_to_dict(updated_user), status={"code":200,"message":"Success"})
        else:
            return jsonify(data={}, status={"code": 401, "message": "Invalid Input"})
    except models.DoesNotExist:
        return jsonify(data={}, status={"code": 401, "message": "Invalid Username or Password"})

#edit
@user.route('/<id>', methods=["PUT"])
def edit_user(id):
    print('hit edit route')
    payload = request.get_json()

    try:
        user = models.User.get(models.User.id==id)
        user_dict = model_to_dict(user)
        if(check_password_hash(user_dict['password'],payload['password'])):
            query= models.User.update(email=payload["email"]).where(models.User.id == id)
            query.execute()
            
            updated_user = models.User.get_by_id(id)

            return jsonify(data=model_to_dict(updated_user), status={"code":200,"message":"Success"})
        else:
            return jsonify(data={}, status={"code": 401, "message": "Wrong password"})
    except models.DoesNotExist:
        return jsonify(data={}, status={"code": 401, "message": "Wrong Input"})

            


#delete
@user.route('/<id>', methods=["DELETE"])
def delete_user(id):
    payload = request.get_json()

    try:
        user = models.User.get(models.User.id==id)
        user_dict = model_to_dict(user)
        if(check_password_hash(user_dict['password'],payload['password'])):

            query = models.User.delete().where(models.User.id == id)
            query.execute()
            

            return jsonify(data='resources successfully deleted', status={"code":200, "message":"deleted"})
        else:
            return jsonify(data={}, status={"code": 401, "message": "Wrong password"})
    except models.DoesNotExist:
        return jsonify(data={}, status={"code": 401, "message": "Wrong Input"})



@user.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify(data={}, status={"code":200, "message":"Success"})