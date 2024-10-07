from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Train, Booking
import re

main_blueprint = Blueprint('main', __name__)

def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
    return re.match(email_regex, email)

def admin_required(fn):
    @wraps(fn)
    @jwt_required() # check for jwt token
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user and user.role == 'admin':
            return fn(*args, **kwargs)
        return jsonify({"msg": "Admin access required"})
    return wrapper


# home 
@main_blueprint.route('/')
def home():
    return "Welcome to IRCTC API"



# Register a User

'''
{
    "name":"Nitin",
    "email":"nitin@gmail.com",
    "password":"nitin123",
    "role":"user"
}
'''
@main_blueprint.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not is_valid_email(data['email']):
        return jsonify({"msg": "Invalid email format."})
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"msg": "Email already registered."})

    hashed_password = generate_password_hash(data['password'])
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        role=data.get('role', 'user')
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"msg": str(e)}), 500





# Login User

'''
{
    "email":"a@gmail.com",
    "password":"nitin123"
}
'''

@main_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not is_valid_email(data['email']):
        return jsonify({"msg": "Invalid email format."})

    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token, role=user.role)
    return jsonify({"msg": "Invalid email or password"})



# Add a New Train (admin only)

{
    "name":"Deepali Exp",
    "source":"Lonawala",
    "destination":"Bhiwadi",
    "total_seats":100
}

@main_blueprint.route('/train', methods=['POST'])
@jwt_required()
@admin_required
def add_train():
    data = request.get_json()
    new_train = Train(
        name=data['name'],
        source=data['source'],
        destination=data['destination'],
        total_seats=data['total_seats']
    )
    try:
        db.session.add(new_train)
        db.session.commit()
        return jsonify({"msg": "Train added successfully"})
    except Exception as e:
        return jsonify({"msg": str(e)})




# Get Seat Availability

'''
{
   "source":"Lonawala",
    "destination":"Bhiwadi"
}
'''
@main_blueprint.route('/availability', methods=['POST'])
def get_availability():
    data = request.get_json()
    source = data['source']
    destination = data['destination']

    if not source or not destination:
        return jsonify({"msg": "Source and destination are required."})

    trains = Train.query.filter_by(source=source, destination=destination).all()
    if not trains:
        return jsonify({"msg": "No trains found for the given source and destination."})

    result = []
    for train in trains:
        booked_seats = db.session.query(db.func.sum(Booking.seats_booked)).filter_by(train_id=train.id).scalar() or 0
        result.append({
            "id": train.id,
            "name": train.name,
            "available_seats": train.total_seats,
            "source": train.source,
            "destination": train.destination
        })
    return jsonify(result)





# Book a Seat
'''
{
    "train_id":1,
    "seats":20
}
'''
@main_blueprint.route('/book', methods=['POST'])
@jwt_required()
def book_seat():
    data = request.get_json()
    user_id = get_jwt_identity()
    train = Train.query.get(data['train_id'])

    if not train:
        return jsonify({"msg": "Train not found"})

    booked_seats = db.session.query(db.func.sum(Booking.seats_booked)).filter_by(train_id=train.id).scalar() or 0
    available_seats = train.total_seats - booked_seats

    if available_seats < data['seats']:
        return jsonify({"msg": "Not enough seats available"})

    try:
        new_booking = Booking(user_id=user_id, train_id=data['train_id'], seats_booked=data['seats'])
        db.session.add(new_booking)
        train.total_seats -= data['seats']
        db.session.commit()
        return jsonify({"msg": "Booking successful", "booking_id": new_booking.id})
    except Exception as e:
        return jsonify({"msg": str(e)})




# Get Specific Booking Details

'''
http://127.0.0.1:5000/booking/1
'''
@main_blueprint.route('/booking/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
    if not booking:
        return jsonify({"msg": "Booking not found"})
    train = Train.query.get(booking.train_id)
    return jsonify({
        "booking_id": booking.id,
        "train_name": train.name,
        "seats_booked": booking.seats_booked,
        "source": train.source,
        "destination": train.destination
    })



# @main_blueprint.route('/users',methods=['GET'])
# def get_all_users():
    
#     try:
#         results = db.session.query(User, Booking).join(Booking, User.id == Booking.user_id).all()

#     except Exception as e :
#         return {"Error":e}     
        