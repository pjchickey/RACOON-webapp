from config import Config
from flask import Flask, flash, render_template, redirect, url_for, request, jsonify
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
    giveaway_entries = db.Column(db.Integer)
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
                        giveaway_entries=0,
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
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
            else:
                flash('incorrect password')
        else:  
            flash('incorrect username')
        render_template('login.html', form=form)
        # return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)


@app.route('/info')
def info():
    return render_template('info.html')


def enter_giveaway(conn, task):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE users
              SET points = points - 5
              ,giveaway_entries = giveaway_entries + 1
              WHERE username = %s;'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # load in qrcode binary info from db, then covert to digital and save as .png
    img_binary = current_user.qrcode
    imgpath = 'static/' + str(current_user.username) + '.png'
    open(imgpath, 'wb').write(img_binary)

    # user attempts to enter gift card giveaway
    if request.method == 'POST':
        if current_user.points < 5:
            flash('insufficient points')
        else:
            conn = psycopg2.connect('postgresql://iyrxjafwmybqog:047647631db0ac1b3d727d7edd5b9e4c299586131585e1b6d41b2bc98e412521@ec2-52-7-115-250.compute-1.amazonaws.com:5432/dfmfctp63eg654')
            enter_giveaway(conn, (current_user.username,))
            flash("you've entered the giveaway!")
            return redirect(url_for('dashboard'))

    # normal page entry
    return render_template('dashboard.html', 
                            name=current_user.username, 
                            imgpath=imgpath,
                            points=current_user.points
    )



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
