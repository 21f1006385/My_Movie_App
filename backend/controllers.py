# App routes
from flask import Flask,render_template,request,url_for,redirect
from .models import *
from flask import current_app as app
from datetime import datetime


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
            return redirect(url_for("admin_dashboard",name=uname))
        elif usr and usr.role==1: # Existed and normal user
            return redirect(url_for("user_dashboard",name=uname))
        else:
            return render_template("login.html",       msg="Invalide User Credentials...")
    return render_template("login.html",msg="")



@app.route("/register",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        full_name=request.form.get("full_name")
        address=request.form.get("location")
        pin_code=request.form.get("pin_code")
        # Validate required fields
        if not uname or not pwd or not full_name or not address or not pin_code:
            return render_template(
                "signup.html",
                msg="All fields are required. Please fill out the form completely."
            )
        usr=User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html",msg="Sorry, already register with this email!!! try to signup with another email.")
        new_user=User_Info(email=uname,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_user)
        db.session.commit()
        return render_template("login.html",msg="Registration Successfull, try login now.")
    return render_template("signup.html",msg="")


# Common route for admin dashboard
@app.route("/admin/<name>")
def admin_dashboard(name):
    theatres=get_theatres()
    return render_template("admin_dashborad.html",name=name,theatres=theatres)

# Common route for user dashboard
@app.route("/user/<name>")
def user_dashboard(name):
    return render_template("user_dashboard.html",name=name)

# Many controllers/routers here

@app.route("/venue/<name>",methods=["POST","GET"])
def add_venue(name):
    if request.method=="POST":
        vname=request.form.get("name")
        location=request.form.get("location")
        pin_code=request.form.get("pin_code")
        capacity=request.form.get("capacity")
        new_theatre=Theatre(name=vname,location=location,pin_code=pin_code,capacity=capacity)
        db.session.add(new_theatre)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("add_venue.html",name=name)


@app.route("/show/<venue_id>/<name>",methods=["POST","GET"])
def add_show(venue_id,name):
    if request.method=="POST":
        tname=request.form.get("name")
        tags=request.form.get("tags")
        tkt_price=request.form.get("tkt_price")
        date_time=request.form.get("dt_time") # Date is starting format
        # Processing date & time
        dt_time=datetime.strptime(date_time,"%Y-%m-%dT%H:%M")
        new_show=Show(name=tname,tags=tags,tkt_price=tkt_price,date_time=dt_time,theatre_id=venue_id)
        db.session.add(new_show)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("add_show.html",venue_id=venue_id,name=name)


# Other support function
def get_theatres():
    theatres=Theatre.query.all()
    return theatres