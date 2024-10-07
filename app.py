from flask import Flask
from flask_jwt_extended import JWTManager
from models import db
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os
from routes import main_blueprint
load_dotenv()


app = Flask(__name__)
app.register_blueprint(main_blueprint)


user=os.getenv('user')
passwd=os.getenv('pwd')
host=os.getenv('host')
database=os.getenv('database')

pwd = quote_plus(passwd)

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{pwd}@{host}/{database}'  # 'sqlite:///example.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') 
app.config['ADMIN_API_KEY'] = os.getenv('ADMIN_API_KEY') 

# bound to app at the time of initialization
db.init_app(app)
jwt = JWTManager(app)


if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
