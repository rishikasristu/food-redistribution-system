import os
from flask import Flask, render_template, request, redirect, session
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from geopy.distance import geodesic
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "foodredistribution"

# MySQL Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:TUcaEoZHqldRNfhyoUGhcsfVVsskfNbd@yamabiko.proxy.rlwy.net:39246/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Donations Table
class Donation(db.Model):
    __tablename__ = "donations"


    donation_id = db.Column(db.Integer, primary_key=True)

    food_name = db.Column(db.String(200))
    food_type = db.Column(db.String(50))
    quantity = db.Column(db.String(100))

    prep_time = db.Column(db.String(50))
    expiry_time = db.Column(db.DateTime)

    description = db.Column(db.Text)

    donor_phone = db.Column(db.String(15))
    donor_address = db.Column(db.Text)

    donor_latitude = db.Column(db.Float)
    donor_longitude = db.Column(db.Float)

    image_path = db.Column(db.String(255))
    priority_score = db.Column(
        db.Float,
        default=0
    )

    user_id = db.Column(db.Integer)
    status = db.Column(db.String(20))

class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    type = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    fulladdress = db.Column(db.Text)
    phone = db.Column(db.String(20))
    google_maps_url = db.Column(db.Text)
class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    userid = db.Column(db.String(50))
    password = db.Column(db.String(100))

# Home Page
@app.route("/")
def home():
    return redirect("/register")

@app.route("/donate")
def donate():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("donor.html")

# Submit Donation
@app.route("/submit", methods=["POST"])
def submit():

    food_name = request.form["food_name"]

    food_type = request.form["food_type"]

    quantity = request.form["quantity"]

    prep_time = request.form["prep_time"]

    if prep_time == "":
        prep_time = None

    expiry_time = request.form["expiry_time"]

    description = request.form["description"]

    phone = request.form["phone"]

    address = request.form["address"]


    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    image = request.files["image"]

    filename = secure_filename(image.filename)

    image_path = os.path.join(
        "static/uploads",
        filename
    )

    image.save(image_path)




    priority_score = 0

    print("Food Type =", food_type)
    print("Expiry Time =", expiry_time)

    if not expiry_time:
        return "Please select Expiry Date/Time"

    if "T" in expiry_time:

        expiry_dt = datetime.strptime(
            expiry_time,
            "%Y-%m-%dT%H:%M"
        )

    else:

        expiry_dt = datetime.strptime(
            expiry_time,
            "%Y-%m-%d"
        )

    hours_left = (
        expiry_dt - datetime.now()
    ).total_seconds() / 3600

# Expiry-based priority

    if hours_left <= 2:
        priority_score += 80

    elif hours_left <= 6:
        priority_score += 60

    elif hours_left <= 12:
        priority_score += 40

# Quantity-based priority

    qty = float(quantity)

    if qty >= 1000:
        priority_score += 30

    elif qty >= 500:
        priority_score += 20

    elif qty >= 200:
        priority_score += 10

    user_id = session["user_id"]
    donation = Donation(

        food_name=food_name,

        food_type=food_type,

        quantity=quantity,

        prep_time=prep_time,

        expiry_time=expiry_dt,

        priority_score=priority_score,


        description=description,

        donor_phone=phone,

        donor_address=address,

        donor_latitude=float(latitude),

        donor_longitude=float(longitude),

        image_path=image_path,

        user_id=user_id,

        status="Pending"


    )


    db.session.add(donation)
    db.session.commit()
    organizations = Organization.query.all()

    donor_location = (
    float(latitude),
    float(longitude)
    )

    nearest = []
    print("Organizations:", len(organizations))
    for org in organizations:

        org_location = (
            org.latitude,
            org.longitude
        )

        distance = geodesic(
            donor_location,
            org_location
        ).km

        nearest.append({
            "name": org.name,
            "distance": round(distance, 2),
            "phone": org.phone,
            "maps": org.google_maps_url,
            "type": org.type
        })

    nearest.sort(key=lambda x: x["distance"])
    print("Total organizations read:", len(organizations))
    print("Total distances calculated:", len(nearest))
    top5 = nearest[:5]

    return render_template(
    "results.html",
    top5=top5
    )

    return "Donation Saved Successfully!"




@app.route("/receiver")
def receiver():

    expired_donations = Donation.query.filter(
        Donation.status == "Pending"
    ).all()

    for donation in expired_donations:

        if datetime.now() > donation.expiry_time:
            donation.status = "Expired"

    db.session.commit()

    # Dashboard Counts

    total = Donation.query.count()

    pending = Donation.query.filter_by(
        status="Pending"
    ).count()

    accepted = Donation.query.filter_by(
        status="Accepted"
    ).count()

    expired = Donation.query.filter_by(
        status="Expired"
    ).count()

    donations = Donation.query.order_by(
        Donation.priority_score.desc()
    ).all()

    return render_template(
        "receiver.html",
        donations=donations,
        total=total,
        pending=pending,
        accepted=accepted,
        expired=expired
    )
@app.route("/accept/<int:id>")
def accept(id):

    donation = Donation.query.get(id)

    donation.status = "Accepted"

    db.session.commit()

    return redirect("/receiver")
@app.route("/reject/<int:id>")
def reject(id):

    donation = Donation.query.get(id)

    donation.status = "Rejected"

    db.session.commit()

    return redirect("/receiver")
@app.route("/delete/<int:id>")
def delete(id):

    donation = Donation.query.get(id)

    db.session.delete(donation)

    db.session.commit()

    return redirect("/receiver")
@app.route("/register")
def register_page():

    return render_template(
        "register.html"
    )
@app.route(
    "/register",
    methods=["POST"]
)
@app.route("/register", methods=["POST"])
def register():

    try:

        user = User(
            name=request.form["name"],
            phone=request.form["phone"],
            email=request.form["email"],
            userid=request.form["userid"],
            password=request.form["password"]
        )

        db.session.add(user)
        db.session.commit()

        return "Registration Successful"

    except IntegrityError:

        db.session.rollback()

        return "User ID already exists. Choose another User ID."
@app.route("/login")
def login_page():

    return render_template(
        "login.html"
    )
@app.route(
    "/login",
    methods=["POST"]
)
def login():

    userid = request.form["userid"]

    password = request.form["password"]

    user = User.query.filter_by(
        userid=userid,
        password=password
    ).first()

    if user:

        session["user_id"] = user.id

        session["name"] = user.name

        return redirect("/dashboard")

    return "Invalid Login"

@app.route("/history")
def history():

    donations = Donation.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "history.html",
        donations=donations
    )
@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html",
        name=session["name"]
    )
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
if __name__ == "__main__":
    app.run(debug=True)