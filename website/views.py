from flask import Blueprint, render_template, jsonify, request,session,  redirect,url_for,flash
from flask_login import login_required, current_user
from . import db
from .models import User, Car, Booking, Payment, Feedback, bank_account
import json
from .car_recommendation import *
from werkzeug.utils import secure_filename
import json
import os
from os.path import join, dirname, realpath
from datetime import datetime, date
from sqlalchemy.sql import func
from sqlalchemy import extract 

views = Blueprint('views', __name__)

@views.route('/',methods=['GET', 'POST'])
@login_required
def home():
     cars= Car.query.order_by(-Car.id).limit(5).all()
     carscount= Car.query.count()
     last_bookings= Booking.query.filter_by(cust_id =  current_user.id).order_by(-Booking.id).first()
     if last_bookings:
        thecarid = last_bookings.car_id

        fromcar= Car.query.filter_by(id =thecarid).first()

        car_user_likes = "%" + fromcar.submodel + "%"
        block = "1"
        recommendations = contents_based_recommender(car_user_likes,3)
        # recommendations = jsonify(result)
        # random.shuffle(recommendations)
        my_list = [item for item in recommendations[:3]]
        carrecom1 = Car.query.filter(Car.id.in_(my_list)).all()
        print(carrecom1)
     else:
        thecarid = "0"
        block = "2"
        car_user_likes = "Nothing to recommend.\n Try to book a car, we will recommend the suitable car for you :)"
        carrecom1 = Car.query.filter_by(id = thecarid).all()
  
     return render_template ("base.html", customer=current_user, cars= cars, carrecom1 = carrecom1, car_user_likes =car_user_likes, block = block, carscount = carscount)

@views.route('/home2', methods=['GET', 'POST'])
@login_required
def home2():
  today = date.today()

  countbooking = Booking.query.filter(Booking.client_id == current_user.id).count()
  countcar = Car.query.filter(Car.client_id == current_user.id).count()
  totalpayment = Booking.query.with_entities(func.sum(Booking.payment_value)).filter(Booking.client_id == current_user.id, Booking.booking_status != "Cancel").scalar()
  countcancel = Booking.query.filter(Booking.client_id == current_user.id, Booking.booking_status == "Cancel").count()
  bookings2 = Booking.query.join(Car, Booking.car_id==Car.id).join(User, Booking.cust_id==User.id).add_columns(Booking.id, Booking.car_id, Booking.start_date, Booking.return_date, Booking.start_time, Booking.return_time,Booking.payment_value, Booking.approval_status, Booking.pickup_location, Booking.return_location, Car.brand, Car.submodel, User.name, User.phone_number).filter((Booking.client_id== current_user.id) & (Booking.approval_status == "Pending"))

  bookings3 = Booking.query.join(Car, Booking.car_id==Car.id).join(User, Booking.cust_id==User.id).join(Payment, Payment.booking_id==Booking.id).add_columns(Booking.id, Booking.car_id, Booking.start_date, Booking.return_date, Booking.start_time, Booking.return_time, Booking.payment_value, Booking.approval_status,  Booking.booking_status, Booking.pickup_location, Booking.return_location, Car.brand, Car.submodel, User.name, User.phone_number, Payment.id.label("payment_id"), Payment.payment_status).filter((Booking.client_id== current_user.id) & (Booking.approval_status == "Accepted") & (( Booking.booking_status =="Ongoing") |  (Booking.booking_status =="Cancel")))
  result = db.session.query(Booking).filter(extract('month', Booking.start_date)==0).all()
  
  if request.method == 'POST':
       if request.form.get('btn') == "Approve":
            booking_id = request.form.get('booking_id')
            Booking.query.filter_by(id = booking_id).update(dict(approval_status='Accepted', booking_status = 'Ongoing'))
            db.session.commit()

            bankdetail = bank_account.query.filter(bank_account.client_id == current_user.id).first()
            bankdetailid = bankdetail.id
            new_payment = Payment(booking_id = booking_id, payment_status = "Not Paid", bank_detail_id = bankdetailid)
            db.session.add(new_payment)
            db.session.commit()

            
       elif request.form.get('btn') == "reject":
            booking_id = request.form.get('booking_id')
            Booking.query.filter_by(id = booking_id).update(dict(approval_status = 'Rejected'))
            db.session.commit()

       elif request.form.get('btn') == "return":
            booking_id = request.form.get('booking_id')
            Booking.query.filter_by(id = booking_id).update(dict(booking_status = 'Completed'))
            db.session.commit()

       elif request.form.get('btn') == "submitmonth":
            monthly = request.form.get('monthly')
            yearly= request.form.get('yearly')
            
            return redirect(url_for('views.report', monthly= monthly, yearly = yearly, **request.args))
            
            


  return render_template ("clientbase.html", client=current_user, bookings2 = bookings2, bookings3 = bookings3, today = today, countbooking = countbooking, countcar = countcar, resultpayment = totalpayment, countcancel = countcancel)


@views.route('/managecar', methods=['GET', 'POST']) 
def managecar():
    
    if request.method == 'POST':
        
        if request.form.get('btn') == "addcar":
            road_tax_expiry = request.form.get('roadtax')
            brand = request.form.get('brand')
            submodel = request.form.get('submodel')
            num_doors = request.form.get('num_doors')
            type = request.form.get('type')
            transmission = request.form['transmission']
            price_per_hour = request.form.get('hourrate')
            price_per_day = request.form.get('dayrate')
            condition = request.form.get('condition')
            car_status = "Available"
            img = request.files['fileToUpload']
            img_name = secure_filename(img.filename)
            
            
            img.save(os.path.join(join(dirname(realpath(__file__)), 'static/uploads/'), img_name))
        
            new_car = Car(client_id=current_user.id, road_tax_expiry= road_tax_expiry, brand=brand, submodel=submodel,num_doors=num_doors, type=type,
            transmission=transmission, condition =condition, price_per_hour=price_per_hour,  price_per_day=price_per_day, car_status = car_status,  
            img_name=img_name)
            db.session.add(new_car)
            db.session.commit()

        elif request.form.get('btn') == "carstatus":
            car_id = request.form.get('car_id')
            current_status = request.form.get('current_status')

            if current_status == "Available":
                Car.query.filter_by(id = car_id).update(dict(car_status = 'Not Available'))
                db.session.commit()
            else:
                Car.query.filter_by(id = car_id).update(dict(car_status = 'Available'))
                db.session.commit()
 
    image_name = Car.img_name    

    registeredcar= Car.query.filter_by(client_id = session['user_id']).all()
    return render_template ("managecar.html", client=current_user, image_name =image_name, registeredcar = registeredcar )


@views.route('/car/<int:car_id>',  methods=['GET', 'POST'])
def car(car_id):
    
    car_id =car_id

    carchosen= Car.query.filter_by(id =car_id).first()
    
    client= User.query.filter_by(id = carchosen.client_id).first()

    feedbackcomment = Feedback.query.join(User, User.id == Feedback.cust_id).add_columns(User.name, Feedback.car_id, Feedback.comment).filter(Feedback.car_id == car_id).all()
    feedbackcommentcount = Feedback.query.filter_by(car_id = car_id).count()
    

    if request.method == 'POST':
        comment = request.form.get('comment')

        new_comment = Feedback(cust_id = current_user.id, car_id = car_id, comment = comment)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('views.car', car_id = car_id ))


    return render_template ("car.html",customer=current_user, carchosen=carchosen, client =client, feedbackcomment = feedbackcomment, feedbackcommentcount= feedbackcommentcount)


@views.route('/bookcar/<int:carselect_id>', methods=['GET', 'POST'])
def carbook(carselect_id):
    session.pop('_flashes', None)
    carselect_id =carselect_id

    carbook= Car.query.filter_by(id =carselect_id).first()
    client_id2 = carbook.client_id 
    carpayday= carbook.price_per_day
    carpayday2= carbook.price_per_hour
    today = date.today()
    today = str(today)

    if request.method == 'POST':
        
        startDate = request.form.get('startDate')
        returnDate = request.form.get('returnDate')
        startTime = request.form.get('startTime')
        returnTime = request.form.get('returnTime')
        pickup_location = request.form.get('pickuplocation')
        return_location = request.form.get('returnlocation')
        approval_status = "Pending"
        booking_status = "Not Aprroved"
        payment_rate = request.form['payrate']

        a = datetime.strptime(request.form['startDate'],'%Y-%m-%d')
        b = datetime.strptime(request.form['returnDate'],'%Y-%m-%d')
        c = datetime.strptime(today,'%Y-%m-%d')
        if c > a or c > b or a > b :
            flash("Wrong input")
        else:
            if payment_rate == 'hour':
                
                if(a == b):
                    time = datetime.strptime(request.form['startTime'], '%H:%M')
                    time2 = datetime.strptime(request.form['returnTime'], '%H:%M')
                    payment_value = (time2 - time)
                    payment_value = (payment_value.total_seconds()/ (60**2)) * carpayday2
                    new_booking = Booking(cust_id = current_user.id, client_id = client_id2, car_id = carselect_id, start_date = startDate, return_date = returnDate,
                    start_time = startTime, return_time = returnTime, pickup_location= pickup_location,  return_location = return_location,
                    pay_rate= payment_rate, payment_value=payment_value, approval_status =approval_status, booking_status = booking_status)
                    db.session.add(new_booking)
                    db.session.commit()
                    
                    return redirect(url_for('views.confirmation'))
                else:
                    time = datetime.strptime(request.form['startTime'], '%H:%M')
                    time2 = datetime.strptime(request.form['returnTime'], '%H:%M')
                    time3 = datetime.strptime('23:00', '%H:%M')
                    payment_value_hour = (time3 - time) 
                    payment_value_day = (b-a)
                    payment_value = ((payment_value_hour.total_seconds() / (60**2) ) * carpayday2) + ((payment_value_day.days) * carpayday)
                    new_booking = Booking(cust_id = current_user.id, client_id = client_id2, car_id = carselect_id, start_date = startDate, return_date = returnDate,
                    start_time = startTime, return_time = returnTime, pickup_location= pickup_location,  return_location = return_location,
                    pay_rate= payment_rate, payment_value=payment_value, approval_status =approval_status, booking_status = booking_status)
                    db.session.add(new_booking)
                    db.session.commit()
                    return redirect(url_for('views.confirmation'))
                    

            else:
                
                a = datetime.strptime(request.form['startDate'],'%Y-%m-%d')
                b = datetime.strptime(request.form['returnDate'],'%Y-%m-%d')
                payment_value = (b - a)
                payment_value = (payment_value.days +1) * carpayday
                new_booking = Booking(cust_id = current_user.id, client_id = client_id2, car_id = carselect_id, start_date = startDate, return_date = returnDate,
                start_time = startTime, return_time = returnTime, pickup_location= pickup_location,  return_location = return_location,
                pay_rate= payment_rate, payment_value=payment_value, approval_status =approval_status, booking_status = booking_status)
                db.session.add(new_booking)
                db.session.commit()
                return redirect(url_for('views.confirmation'))    

    return render_template ("bookcar.html",customer=current_user, carbook=carbook)


@views.route('/confirmation')
def confirmation():
    
    bookings= Booking.query.order_by(-Booking.id).first()

    return render_template ("confirmation.html",customer=current_user, bookings=bookings)


@views.route('/yourbooking', methods=['GET', 'POST'])
def yourbooking():
    
    custid= current_user.id
    
    bookings = Booking.query.join(Car, Booking.car_id==Car.id).join(User, Booking.client_id==User.id).add_columns(Booking.id, Booking.car_id, Booking.start_date, Booking.return_date, Booking.start_time, Booking.return_time, Booking.payment_value, Booking.approval_status, Booking.booking_status, Booking.pickup_location, Booking.return_location, Car.brand, Car.submodel, User.name, User.phone_number).filter(Booking.cust_id== custid).order_by(-Booking.id)
    bookings2 = Booking.query.join(Car, Booking.car_id==Car.id).join(User, User.id == Booking.client_id).join(Payment, Payment.booking_id == Booking.id).add_columns(Booking.id, Booking.car_id, Booking.start_date, Booking.return_date, Booking.start_time, Booking.return_time, Booking.payment_value, Booking.approval_status, Booking.booking_status, Booking.pickup_location, Booking.return_location, Car.brand, Car.submodel, User.name, User.phone_number, Payment.payment_status).filter(Booking.cust_id== custid, Booking.approval_status == "Accepted" ).order_by(-Booking.id)
    
    if request.method == 'POST':

        if request.form.get('btn') == "cancel":
                booking_id = request.form.get('booking_id')
                approval_updated = Booking.query.filter_by(id = booking_id).update(dict(booking_status = 'Cancel'))
                db.session.commit()
        # elif request.form.get('btn') == "return":
        #         car_id = request.form.get('car_id')
        #         startdate = request.form.get('startdate')
        #         returndate = request.form.get('returndate')
        #         return_updated = Booking.query.filter_by(car_id = car_id, start_date = startdate, return_date = returndate).update(dict(booking_status = 'Completed'))
        #         db.session.commit()

    return render_template ("yourbooking.html",customer=current_user, bookings = bookings, bookings2 = bookings2)


@views.route('/report/<monthly>/<yearly>')
def report(monthly, yearly):
    
    monthly =monthly
    yearly = yearly

    result = db.session.query(Booking).join(User, Booking.cust_id==User.id).join(Payment, Payment.booking_id==Booking.id).add_columns(Booking.id, User.name, Booking.payment_value, Payment.payment_status ).filter(extract('month', Booking.start_date)==monthly, extract('year', Booking.start_date)==yearly, Booking.client_id == current_user.id, Payment.payment_status == "Paid").all()
    countresult = Booking.query.join(Payment, Payment.booking_id==Booking.id).add_columns(Booking.id, User.name, Booking.payment_value, Payment.payment_status).filter(extract('month', Booking.start_date)==monthly, extract('year', Booking.start_date)==yearly, Booking.client_id == current_user.id,  Payment.payment_status == "Paid").count()

    return render_template ("report.html",client=current_user, result =result, countresult = countresult)

@views.route('/editcar/<car_id>', methods=['GET', 'POST'])
def editcar(car_id):
    
    cardetail= Car.query.filter_by(id =car_id).all()
    cardetail2= Car.query.filter_by(id =car_id).first()

    if request.method == 'POST':
        road_tax_expiry = request.form.get('roadtax')
        brand = request.form.get('brand')
        submodel = request.form.get('submodel')
        num_doors = request.form.get('num_doors')
        type = request.form.get('type')
        transmission = request.form.get('transmission')
        price_per_hour = request.form.get('hourrate')
        price_per_day = request.form.get('dayrate')
        condition = request.form.get('condition')

        if road_tax_expiry == '':
            road_tax_expiry = cardetail2.road_tax_expiry
        if brand == '':
            brand = cardetail2.brand
        if submodel == '':
            submodel = cardetail2.submodel
        if num_doors == '':
            num_doors = cardetail2.num_doors
        if type == '':
            type = cardetail2.type 
        if transmission == '':
            transmission = cardetail2.transmission
        if price_per_hour == '':
            price_per_hour = cardetail2.price_per_hour
        if price_per_day == '':
            price_per_day = cardetail2.price_per_day 

        Car.query.filter_by(id = car_id).update(dict( road_tax_expiry= road_tax_expiry, brand=brand, submodel=submodel,num_doors=num_doors, type=type,
            transmission=transmission, condition =condition, price_per_hour=price_per_hour,  price_per_day=price_per_day))
        db.session.commit()
        return redirect(url_for('views.managecar')) 

    return render_template ("editcar.html", cardetail=cardetail)

@views.route('/payment/<bookingid>', methods=['GET', 'POST'])
def payment(bookingid):
    bookingid = bookingid
    checkpayment = Booking.query.join(bank_account, Booking.client_id==bank_account.client_id).add_columns(Booking.id, Booking.payment_value, bank_account.account_num, bank_account.bank_name).filter(Booking.id == bookingid)

    if request.method == 'POST':
        resit = request.files['resitToUpload']
        resit_name = secure_filename(resit.filename)
     
        resit.save(os.path.join(join(dirname(realpath(__file__)), 'static/uploads/'), resit_name))

        Payment.query.filter_by(booking_id = bookingid).update(dict(resit_img  = resit_name, payment_status = "Resit Received"))
        db.session.commit()
        return redirect(url_for('views.yourbooking'))

    return render_template ("payment.html", checkpayment = checkpayment)


@views.route('/confirmresit/<payment_id>', methods=['GET', 'POST'])
def confirmresit(payment_id):

    payment_id = payment_id
    paymentdetail= Payment.query.filter_by(id = payment_id).all()
    

    if request.method == 'POST':
        Payment.query.filter_by(id = payment_id).update(dict(payment_status = "Paid"))
        db.session.commit()
        return redirect(url_for('views.home2'))
    
    return render_template ("confirmresit.html", paymentdetail = paymentdetail)

@views.route('/carlist', methods=['GET', 'POST'])
def carlist():
    cars= Car.query.order_by(-Car.id).all()
    return render_template ("carlist.html", cars =cars)
