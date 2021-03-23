from config import Config
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy  import SQLAlchemy
from flask_wtf import FlaskForm
import os
import psycopg2
import qrcode
from sqlalchemy import *
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
# file_path = os.path.abspath(os.getcwd())+'\database.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
# bootstrap = Bootstrap(app)
# db = SQLAlchemy(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'


# Init app
app = Flask(__name__)
app.config.from_object(Config)
DB_URI = app.config['SQLALCHEMY_DATABASE_URI']
engine = create_engine(DB_URI)

# Init routes
CORS(app, support_credentials=True)
Base = automap_base()
Base.prepare(engine, reflect=True)
Users = Base.classes.users
session = Session(engine)
metadata = MetaData(engine)

# Init login manager
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


# @login_manager.user_loader
# def load_user(user_id):
#     return session.query(Users).get(int(user_id))
#     # return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        # points=0
        users = Table('users', metadata, autoload=True)
        engine.execute(users.insert(), 
            username=form.username.data, 
            email=form.email.data, 
            password=generate_password_hash(form.password.data, method='sha256'),
            points=0
        )

        # generate user qrcode by id
        # img = qrcode.make('racoon_' + str(new_user.id))
        # img.save('static/qrcodes/' + str(new_user.id) + '.png')

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username_entered = form.username.data
        password_entered = form.password.data
        user = session.query(Users).filter(or_(Users.username == username_entered, Users.email == username_entered)).first()
        if user is not None and check_password_hash(user.password, password_entered):
            # login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        else:
            return '<h1>Invalid username or password</h1>'
            #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)


@app.route('/dashboard')
# @login_required
def dashboard():
    return render_template('dashboard.html', 
                            # name=current_user.username, 
                            # imgpath='/static/qrcodes/' + str(current_user.id) + '.png',
                            # points=current_user.points
                            name='user',
                            imgpath='/static/qrcodes/' + str(1) + '.png',
                            points=0
    )


@app.route('/logout')
# @login_required
def logout():
    # logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)