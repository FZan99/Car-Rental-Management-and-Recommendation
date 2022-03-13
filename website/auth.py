from flask import Blueprint, render_template, request, flash, redirect, url_for,jsonify
from .models import User, Car, Booking, bank_account
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, is_human
from flask_login import login_user, login_required, logout_user, current_user
from flask import Flask, session
from werkzeug.utils import secure_filename
import json
import os
from os.path import join, dirname, realpath
from datetime import datetime



auth = Blueprint('auth', __name__)


@auth.route('/chooselogin')
def chooselogin():
    return render_template ("chooselogin.html")

@auth.route('/choosesignup')
def choosesignup():
    session.pop('_flashes', None)
    return render_template ("choosesignup.html")

@auth.route('/custlogin', methods=['GET', 'POST'])
def custlogin():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('psw')
        user_type = "customer"
        

        customer = User.query.filter_by(email=email).first()
        if customer:
            type = customer.user_type

            if type == user_type :
                if check_password_hash(customer.password, password):
                    
                    login_user(customer, remember=True)
                    session['user_name'] = customer.name
                    session['user_id'] = customer.id
                    return redirect(url_for('views.home'))

    return render_template ("custlogin.html", customer=current_user)

@auth.route('/clientlogin', methods=['GET', 'POST'])
def clientlogin():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('psw')
        user_type = "client"

        client = User.query.filter_by(email=email, user_type = user_type).first()
        if client:
           type = client.user_type

           if type == user_type:
                if check_password_hash(client.password, password):
                    
                    login_user(client, remember=True)
                    session['user_name'] = client.name
                    session['user_id'] = client.id
                    return redirect(url_for('views.home2'))
            

    return render_template ("clientlogin.html", client=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.chooselogin'))

@auth.route('/cust-sign-up', methods=['GET', 'POST'])
def cust_sign_up():
    sitekey = "6LfQaf8dAAAAAN4juczwBJ6U0-sB2fMY697bCDTs"
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phone')
        password = request.form.get('psw')
        captcha_response = request.form['g-recaptcha-response']
        
       

        customer = User.query.filter_by(email=email).first()
        
        if customer:
            flash('Email already exists. Note: Use different email for customer and client if register for both', category='error')
        
        else:
            if is_human(captcha_response):
                new_customer = User( name=name, email=email, phone_number=phone_number, password=generate_password_hash(
                    password, method='sha256'), user_type ="customer")
                db.session.add(new_customer)
                db.session.commit()
                return redirect(url_for('auth.chooselogin'))
            else:
                status = "Sorry ! Please Check Im not a robot."
                flash(status)
                

    return render_template ("custsignup.html", sitekey=sitekey)


@auth.route('/client-sign-up', methods=['GET', 'POST'])
def client_sign_up():
    sitekey = "6LfQaf8dAAAAAN4juczwBJ6U0-sB2fMY697bCDTs"
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phone')
        password = request.form.get('psw')
        bank_name = request.form.get('bank_name')
        account_num = request.form.get('account_detail')
        captcha_response = request.form['g-recaptcha-response']

        client = User.query.filter_by(email=email).first()
        
        if client:
            
            flash("Email already exist. Note: Use different email for customer and client if register for both", category='error')
        
        else:
            if is_human(captcha_response):
                new_client = User( name=name, email=email, phone_number=phone_number, password=generate_password_hash(
                    password, method='sha256'), user_type ="client")
                db.session.add(new_client)
                db.session.commit()

                latest_user = User.query.order_by(-User.id).first()
                new_client_bank = bank_account( client_id= latest_user.id, bank_name = bank_name, account_num = account_num)
                db.session.add(new_client_bank)
                db.session.commit()

                return redirect(url_for('auth.chooselogin'))
            else:
                status = "Sorry ! Please Check Im not a robot."
                flash(status)

    return render_template ("clientsignup.html", sitekey = sitekey)

