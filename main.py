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
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

# Init app, PostgreSQL Connection, and login manager
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    points = db.Column(db.Integer)
    qrcode = db.Column(db.LargeBinary)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
        

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():

        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, 
                        email=form.email.data, 
                        password=hashed_password, 
                        points=0,
                        qrcode=None)
        print(new_user.username)
        img = qrcode.make('racoon_' + str(new_user.username))
        img.save('static/qrcode.png')
        img_binary = open('static/qrcode.png', 'rb').read()
        new_user.qrcode = img_binary
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('dashboard'))
        # return '<h1>New user has been created!</h1>'
        
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('dashboard'))
        else:
            render_template('login.html', form=form)
            # return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    # load in qrcode binary info from db, then covert to digital and save as .png
    img_binary = current_user.qrcode
    open('static/qrcode2.png', 'wb').write(img_binary)
    return render_template('dashboard.html', 
                            name=current_user.username, 
                            imgpath='/static/qrcode2.png',
                            points=current_user.points
    )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)