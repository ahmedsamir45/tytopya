
from webapp.models import User
from flask import render_template ,url_for,flash ,redirect,request
from webapp.forms import RegistrationForm , LoginForm
from webapp import bcrypt,db
from flask_login import login_user,current_user,logout_user
from flask import Blueprint





auth1 = Blueprint("auth1",__name__)

# start login logout register
@auth1.post("/register")
@auth1.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('summarization1.summary'))
    form = RegistrationForm()
    
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fname=form.fname.data,lname=form.lname.data,username=form.username.data,email=form.email.data,password=hash_password)
     
    
        db.session.add(user)
        db.session.commit()
        flash(f"Account created successfully for {form.username.data}", "success")
        return redirect(url_for("auth1.login"))
    return render_template("register.html", title="Register", form=form)


@auth1.get("/login")
@auth1.post("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes1.summary'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if (user and bcrypt.check_password_hash(user.password , form.password.data)):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            flash("You have been logged in!", "success")
            return redirect(next_page) if next_page else redirect(url_for("routes1.home"))
        else:
            flash("Login Unsuccessful. Please check credentials", "danger")
    return render_template("login.html", title="Login", form=form)




@auth1.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("routes1.home"))

# end login logout register










