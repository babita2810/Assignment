from flask_sqlalchemy import SQLAlchemy
from test import app
from urllib.parse import quote_plus

# pwd = quote_plus('nitin@123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db' #f'mysql+pymysql://root:{pwd}@localhost/irctc' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'user'), default='user')

class Train(db.Model):
    __tablename__ = 'trains'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('trains.id'), nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()  