import os
from flask import Flask, render_template, redirect, url_for, flash,abort
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,IntegerField
from wtforms.validators import DataRequired, URL
from functools import wraps
from sqlalchemy import Table, Column, Integer, ForeignKey
from Amazon import Amazon_Price
from Email import Send_Email
import redis
from rq import Queue


os.environ["SECRET_KEY"]="38493290320383843"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)

##Redis
r=redis.Redis()
q=Queue(connection=r)

##WTFORM
class LoginForm(FlaskForm):
    email=StringField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Let me in")

class RegisterForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    email=StringField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Sign up!")

class AddForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    item_url=StringField("URL",validators=[DataRequired(),URL()])
    budget=IntegerField("Budget",validators=[DataRequired()])
    submit=SubmitField("Add")

class NameForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    submit = SubmitField("Update")

class PasswordForm(FlaskForm):
    old_password=PasswordField("Old Password",validators=[DataRequired()])
    new_password=PasswordField("New Password",validators=[DataRequired()])
    confirm_password=PasswordField("Confirm Password",validators=[DataRequired()])
    submit=SubmitField("Update")

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL","sqlite:///amazon.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##DECORATOR
def admin_only(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args,**kwargs)
    return decorated_function




##CONFIGURE TABLES

class User(UserMixin,db.Model):
    __tablename__="users"
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(200),unique=True)
    password=db.Column(db.String(200))
    name=db.Column(db.String(200))
    items=relationship("Items",back_populates="author")

class Items(db.Model):
    __tablename__="items"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(250))
    url=db.Column(db.String(250))
    url_name=db.Column(db.String(250))
    img_url=db.Column(db.String(250))
    low_price=db.Column(db.Integer)
    price=db.Column(db.Integer)
    budget=db.Column(db.Integer)
    author_id=db.Column(db.Integer,ForeignKey("users.id"))
    author=relationship("User",back_populates="items")

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("index.html",logged_in=current_user.is_authenticated)

@app.route('/login',methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password.data
        user=db.session.query(User).filter_by(email=email).first()
        if not user:
            flash("This email does not exist, please try again")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password,password):
            flash("Password incorrect, please try again")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html",form=form,logged_in=current_user.is_authenticated)

@app.route('/register',methods=["POST","GET"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        email=form.email.data
        user=db.session.query(User).filter_by(email=email).first()
        if user:
            flash("You've already signed up with that email, login instead.")
            return redirect(url_for('register'))
        new_user=User()
        new_user.name=form.name.data
        new_user.email=email
        new_user.password=generate_password_hash(form.password.data,method='pbkdf2:sha256',salt_length=8)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template("register.html",form=form,logged_in=current_user.is_authenticated)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/add',methods=["POST","GET"])
@login_required
def add():
    form=AddForm()
    if form.validate_on_submit():
        product=Amazon_Price(url=form.item_url.data)
        print(form.item_url.data)
        product.get_add()
        product_price = product.price
        price = product_price
        new_item=Items()
        new_item.name=form.name.data
        new_item.url_name=product.name
        new_item.url=form.item_url.data
        new_item.price=price
        new_item.img_url=product.img_url
        new_item.budget=form.budget.data
        new_item.low_price=price
        new_item.author=current_user
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html',form=form,logged_in=current_user.is_authenticated)


@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html',logged_in=current_user.is_authenticated)

@app.route('/item/<int:item_id>',methods=["GET","POST"])
@login_required
def show_item(item_id):
    item=db.session.query(Items).get(item_id)
    product=Amazon_Price(url=item.url)
    product.get_price()
    price=product.price
    item.price=price
    db.session.commit()
    if(price<int(item.low_price)):
        item.low_price=price
        db.session.commit()
    return render_template('item.html',item=item,logged_in=current_user.is_authenticated)

@app.route('/delete/<int:item_id>')
def delete(item_id):
    item = Items.query.get(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/settings',methods=["GET","POST"])
@login_required
def settings():
    name_form=NameForm(name=current_user.name)
    pass_form=PasswordForm()
    if name_form.validate_on_submit():
        current_user.name=name_form.name.data
        db.session.commit()
        return redirect(url_for('home'))
    if pass_form.validate_on_submit():
        if not check_password_hash(current_user.password,pass_form.old_password.data):
            flash("Old password is incorrect, please try again")
            return redirect(url_for('settings'))
        if pass_form.new_password.data != pass_form.confirm_password.data:
            flash("Both passwords do not match, please try again")
            return redirect(url_for('settings'))
        else:
            current_user.password=generate_password_hash(pass_form.new_password.data,method="pbkdf2:sha256",salt_length=8)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('settings.html',name_form=name_form,pass_form=pass_form,logged_in=current_user.is_authenticated)

@app.route('/message',methods=["GET","POST"])
@login_required
@admin_only
def admin():
    jobs=q.jobs
    users = db.session.query(User).all()
    message=None
    product=Amazon_Price(url=users[0].item.url)
    task=q.enqueue(product.update,users,db)
    jobs=q.jobs
    return render_template('admin.html')






if __name__=="__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)