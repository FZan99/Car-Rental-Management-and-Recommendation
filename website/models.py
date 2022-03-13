from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    phone_number = db.Column(db.Integer)
    password = db.Column(db.String(150))
    user_type = db.Column(db.String(150))
    bookings = db.relationship('Booking')
    cars = db.relationship('Car')
    

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    road_tax_expiry = db.Column(db.String(20))
    brand = db.Column(db.String(20))
    submodel = db.Column(db.String(20))
    num_doors = db.Column(db.Integer)
    type = db.Column(db.String(20))
    transmission = db.Column(db.String(10))
    condition = db.Column(db.String(100))
    price_per_hour = db.Column(db.String(10))
    price_per_day = db.Column(db.String(10))
    car_status = db.Column(db.String(10))
    img_name = db.Column(db.String(150))
    bookings = db.relationship('Booking')
    feedbacks = db.relationship('Feedback')

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    client_id = db.Column(db.Integer)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    start_date = db.Column(db.String(20))
    return_date = db.Column(db.String(20))
    start_time = db.Column(db.String(20))
    return_time = db.Column(db.String(20))
    pickup_location = db.Column(db.String(50))
    return_location = db.Column(db.String(50))
    pay_rate = db.Column(db.String(10))
    payment_value = db.Column(db.String(10))
    approval_status = db.Column(db.String(10))
    booking_status = db.Column(db.String(10))
    payments = db.relationship('Payment')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    payment_status = db.Column(db.String(10))
    resit_img = db.Column(db.String(150))
    bank_detail_id = db.Column(db.Integer)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    comment = db.Column(db.String(10000))

class bank_account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    account_num = db.Column(db.String(50))
    bank_name= db.Column(db.String(150))
   
