# App routes
from flask import Flask,render_template,request,url_for,redirect
from .models import *
from flask import current_app as app
from datetime import datetime
from sqlalchemy import func
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

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
            return redirect(url_for("user_dashboard",name=uname,id=usr.id))
        else:
            return render_template("login.html",msg1="Invalide User Credentials...")
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
            return render_template("signup.html",msg="All fields are required. Please fill out the form completely.")
        usr=User_Info.query.filter_by(email=uname).first()
        if usr:
            return render_template("signup.html",msg="Sorry, already register with this email!!! try to signup with another email.")
        new_user=User_Info(email=uname,password=pwd,full_name=full_name,address=address,pin_code=pin_code)
        db.session.add(new_user)
        db.session.commit()
        return render_template("login.html",msg2="Registration Successfull, try login now.")
    return render_template("signup.html",msg="")


# Common route for admin dashboard
@app.route("/admin/<name>")
def admin_dashboard(name):
    theatres=get_theatres()
    return render_template("admin_dashboard.html",name=name,theatres=theatres)

# Common route for user dashboard
@app.route("/user/<id>/<name>")
def user_dashboard(id,name):
    theatres=get_theatres()
    dt_time_now=datetime.today().strftime("%Y-%m-%dT%H:%M")
    dt_time_now=datetime.strptime(dt_time_now,"%Y-%m-%dT%H:%M")
    return render_template("user_dashboard.html",uid=id,name=name,theatres=theatres,dt_time_now=dt_time_now)

# Many controllers/routers here

@app.route("/venue/<name>",methods=["POST","GET"])
def add_venue(name):
    if request.method=="POST":
        vname=request.form.get("name")
        location=request.form.get("location")
        pin_code=request.form.get("pin_code")
        capacity=request.form.get("capacity")
        file=request.files["file_upload"]
        url=""
        if file.filename:
            file_name=secure_filename(file.filename) # Verification of the file is done
            url="./uploaded_files/"+vname+"_"+file_name
            file.save(url)
        new_theatre=Theatre(name=vname,location=location,pin_code=pin_code,capacity=capacity,venue_pic_url=url)
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


@app.route("/search/<name>",methods=["GET","POST"])
def search(name):
    if request.method=="POST":
        # Retrieve the search text from the form
        search_txt=request.form.get("search_txt")

        if search_txt: # Ensure the input is not empty
            # Query the database for venues and locations  
            by_venue=search_by_venue(search_txt)
            by_location=search_by_location(search_txt)

            # Check if any results are found
            if by_venue:
                return render_template("admin_dashboard.html",name=name,theatres=by_venue)
            elif by_location:
                return render_template("admin_dashboard.html",name=name,theatres=by_location)
            else:
                return render_template("admin_dashboard.html",name=name,msg="No matching results found.")
        else:
            return render_template("admin_dashboard.html",name=name,msg="Please enter a search term.")
    else:
        return redirect(url_for("admin_dashboard",name=name))


@app.route("/edit_venue/<id>/<name>",methods=["GET","POST"])
def edit_venue(id,name):
    v=get_venue(id)
    if request.method=="POST":
        name=request.form.get("name")
        location=request.form.get("location")
        pin_code=request.form.get("pin_code")
        capacity=request.form.get("capacity")
        v.name=name
        v.location=location
        v.pin_code=pin_code
        v.capacity=capacity
        db.session.commit()        
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("edit_venue.html",venue=v,name=name)



@app.route("/delete_venue/<id>/<name>",methods=["GET","POST"])
def delete_venue(id,name):
    v=get_venue(id)
    db.session.delete(v)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))


@app.route("/edit_show/<id>/<name>",methods=["GET","POST"])
def edit_show(id,name):
    s=get_show(id)
    if request.method=="POST":
        name=request.form.get("name")
        tags=request.form.get("tags")
        tkt_price=request.form.get("tkt_price")
        date_time=request.form.get("dt_time") # Date is starting format
        dt_time=datetime.strptime(date_time,"%Y-%m-%dT%H:%M")
        s.name=name
        s.tags=tags
        s.tkt_price=tkt_price
        s.date_time=dt_time
        db.session.commit()        
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("edit_show.html",show=s,name=name)



@app.route("/delete_show/<id>/<name>",methods=["GET","POST"])
def delete_show(id,name):
    s=get_show(id)
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))


@app.route("/book_ticket/<uid>/<sid>/<name>",methods=["GET","POST"])
def book_ticket(uid,sid,name):
    if request.method=="POST":
        no_of_tickets=request.form.get("no_of_tickets")
        new_ticket=Ticket(no_of_tickets=no_of_tickets,s1_nos="",user_id=uid,show_id=sid)
        db.session.add(new_ticket)
        db.session.commit()
        return redirect(url_for("user_dashboard",id=uid,name=name))
    
    # Get method is executed
    show=Show.query.filter_by(id=sid).first()
    theatre=Theatre.query.filter_by(id=show.theatre_id).first()
    available_seats=theatre.capacity
    # Booked_tickets by aggregate function sum
    book_tickets=Ticket.query.with_entities(func.sum(Ticket.no_of_tickets)).group_by(Ticket.show_id).filter_by(show_id=sid).first()
    if book_tickets:
        available_seats -= book_tickets[0]
    return render_template("book_ticket.html",uid=uid,sid=sid,name=name,tname=theatre.name,sname=show.name,available_seats=available_seats,tktprice=show.tkt_price)


@app.route("/admin_summary")
def admin_summary():
    plot=get_theatres_summary()
    plot.savefig("./static/images/theatre_summary.jpeg")
    plot.clf()
    return render_template("admin_summary.html")


# Other support function
def get_theatres():
    theatres=Theatre.query.all()
    return theatres


def search_by_venue(search_txt):
    theatres=Theatre.query.filter(Theatre.name.ilike(f"%{search_txt}%")).all()
    return theatres


def search_by_location(search_txt):
    theatres=Theatre.query.filter(Theatre.location.ilike(f"%{search_txt}%")).all()
    return theatres

def get_venue(id):
    theatre=Theatre.query.filter_by(id=id).first()
    return theatre


def get_show(id):
    show=Show.query.filter_by(id=id).first()
    return show

def get_theatres_summary():
    theatres=get_theatres()
    
    summary={}
    for t in theatres:
        summary[t.name]=t.capacity
    x_names=list(summary.keys())
    y_capacities=list(summary.values())
    plt.bar(x_names,y_capacities,color="blue",width=0.4)
    plt.title("Theatres/Capacities")
    plt.xlabel("Theatre")
    plt.ylabel("Capacity")
    return plt



# JSON data -it's simple dictionary key:value
# JSON data can be used by 
