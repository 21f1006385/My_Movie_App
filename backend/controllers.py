# App routes
from flask import Flask,render_template,request
from .models import *
from flask import current_app as app


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        usr=User_Info.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0: # Existed and admin 
            return render_template("admin_dashborad.html")
        elif usr and usr.role==1: # Existed and normal user
            return render_template("user_dashboard.html")
        else:
            return render_template("login.html",msg="Invalide User Credentials...")
    return render_template("login.html",msg="")



@app.route("/register",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        full_name=request.form.get("full_name")
        address=request.form.get("location")
        pin_code=request.form.get("pin_code")
        usr=User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html",msg="Sorry, already register with this email!!! try to signup with another email.")
        new_user=User_Info(email=uname,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_user)
        db.session.commit()
        return render_template("login.html",msg="Registration Successfull, try login now.")
    return render_template("signup.html",msg="")


# Many controllers/routers here

