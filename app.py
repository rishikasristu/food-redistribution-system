import os
from flask import Flask, render_template, request, redirect, session
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from geopy.distance import geodesic
from datetime import datetime , date
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

    scheduled_time = db.Column(
    db.DateTime)
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
    address = db.Column(db.Text)
    userid = db.Column(db.String(50))
    password = db.Column(db.String(100))

class Receiver(db.Model):

    __tablename__ = "receivers"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    organization_name = db.Column(
        db.String(200)
    )

    phone = db.Column(
        db.String(20)
    )

    email = db.Column(
        db.String(100)
    )

    password = db.Column(
        db.String(100)
    )

    address = db.Column(
        db.Text
    )

# Home Page
"""@app.route("/")
def home():
    return redirect("/register")"""
@app.route("/")
def home():

    return render_template(
        "index.html"
    )

@app.route("/donor_home")
def donor_home():

    return render_template(
        "donor_home.html"
    )
@app.route("/receiver_home")
def receiver_home():

    return render_template(
        "receiver_home.html"
    )
@app.route("/donate")
def donate():

    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(
        session["user_id"]
    )

    return render_template(
        "donor.html",
        user=user,
        today=datetime.now().strftime("%Y-%m-%dT%H:%M")
    )
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

    scheduled_time = request.form.get("scheduled_time")

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
    if scheduled_time:

        scheduled_dt = datetime.strptime(
            scheduled_time,
            "%Y-%m-%dT%H:%M"
        )

    else:

        scheduled_dt = None
    print("========== DEBUG ==========")
    print("Food Type:", repr(food_type))
    print("Expiry DT:", expiry_dt)
    print("Current :", datetime.now())
    print("Expired?", expiry_dt < datetime.now())
    print("===========================")

    if food_type == "Cooked Food":

        if expiry_dt < datetime.now():

            return "Cooked food expiry must be in the future."

    else:

        if expiry_dt.date() < date.today():

            return "Expiry date cannot be in the past."

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

        scheduled_time=scheduled_dt,

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

    search = request.args.get(
        "search",
        ""
    )

    donations = Donation.query.filter(
        Donation.archived == False,
        Donation.food_name.ilike(
            f"%{search}%"
        )
    ).order_by(
        Donation.priority_score.desc()
    ).all()
    collected = Donation.query.filter_by(
        status="Collected"
    ).count()

    return render_template(
        "receiver.html",
        donations=donations,
        total=total,
        pending=pending,
        accepted=accepted,
        expired=expired,
        collected = collected
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
"""@app.route("/delete/<int:id>")
def delete(id):

    donation = Donation.query.get(id)

    db.session.delete(donation)

    db.session.commit()

    return redirect("/receiver")"""
@app.route("/archive/<int:id>")
def archive(id):

    donation = Donation.query.get(id)

    donation.status = "Archived"

    "donation.archived = True"

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

    user_id = session["user_id"]

    total = Donation.query.filter_by(
        user_id=user_id
    ).count()

    pending = Donation.query.filter_by(
        user_id=user_id,
        status="Pending"
    ).count()

    accepted = Donation.query.filter_by(
        user_id=user_id,
        status="Accepted"
    ).count()

    expired = Donation.query.filter_by(
        user_id=user_id,
        status="Expired"
    ).count()

    return render_template(
        "dashboard.html",
        name=session["name"],
        total=total,
        pending=pending,
        accepted=accepted,
        expired=expired
    )
@app.route("/profile")
def profile():

    user = User.query.get(
        session["user_id"]
    )

    return render_template(
        "profile.html",
        user=user
    )
@app.route("/edit_profile")
def edit_profile():

    user = User.query.get(
        session["user_id"]
    )

    return render_template(
        "edit_profile.html",
        user=user
    )
@app.route("/update_profile", methods=["POST"])
def update_profile():

    user = User.query.get(
        session["user_id"]
    )

    user.name = request.form["name"]
    user.phone = request.form["phone"]
    user.email = request.form["email"]
    user.address = request.form["address"]

    db.session.commit()

    session["name"] = user.name

    return redirect("/profile")
@app.route("/tracking")
def tracking():

    donations = Donation.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "tracking.html",
        donations=donations
    )
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route(
    "/receiver_register",
    methods=["GET", "POST"]
)
def receiver_register():

    if request.method == "POST":

        receiver = Receiver(

            organization_name=
            request.form["organization_name"],

            phone=
            request.form["phone"],

            email=
            request.form["email"],

            address=
            request.form["address"],

            password=
            request.form["password"]

        )

        db.session.add(receiver)

        db.session.commit()

        return redirect(
            "/receiver"
        )

    return render_template(
        "receiver_register.html"
    )

@app.route(
    "/receiver_login",
    methods=["GET", "POST"]
)
def receiver_login():

    if request.method == "POST":

        receiver = Receiver.query.filter_by(

            email=request.form["email"],

            password=request.form["password"]

        ).first()

        if receiver:

            session["receiver_id"] = receiver.id

            session["receiver_name"] = (
                receiver.organization_name
            )

            return redirect(
                "/receiver_dashboard"
            )

        return "Invalid Login"

    return render_template(
        "receiver_login.html"
    )

@app.route("/receiver_dashboard")
def receiver_dashboard():

    if "receiver_id" not in session:
        return redirect("/receiver_login")

    total = Donation.query.count()

    pending = Donation.query.filter_by(
        status="Pending"
    ).count()

    accepted = Donation.query.filter_by(
        status="Accepted"
    ).count()

    collected = Donation.query.filter_by(
        status="Collected"
    ).count()

    expired = Donation.query.filter_by(
        status="Expired"
    ).count()

    rejected = Donation.query.filter_by(
        status="Rejected"
    ).count()

    scheduled = Donation.query.filter(
        Donation.scheduled_time != None
    ).count()

    return render_template(
        "receiver_dashboard.html",
        name=session["receiver_name"],
        total=total,
        pending=pending,
        accepted=accepted,
        collected=collected,
        expired=expired,
        rejected=rejected,
        scheduled=scheduled
    )


@app.route("/receiver_profile")
def receiver_profile():

    receiver = Receiver.query.get(
        session["receiver_id"]
    )

    return render_template(
        "receiver_profile.html",
        receiver=receiver
    )

@app.route(
    "/edit_receiver_profile"
)
def edit_receiver_profile():

    receiver = Receiver.query.get(
        session["receiver_id"]
    )

    return render_template(
        "edit_receiver_profile.html",
        receiver=receiver
    )
@app.route("/scheduled_donations")
def scheduled_donations():

    donations = Donation.query.filter(
        Donation.scheduled_time != None
    ).order_by(
        Donation.scheduled_time.asc()
    ).all()

    return render_template(
        "scheduled_donations.html",
        donations=donations
    )
@app.route("/accepted_donations")
def accepted_donations():

    donations = Donation.query.filter_by(
        status="Accepted"
    ).all()

    return render_template(
        "accepted_donations.html",
        donations=donations
    )

@app.route("/receiver_analytics")
def receiver_analytics():

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

    collected = Donation.query.filter_by(
        status="Collected"
    ).count()

    return render_template(
        "receiver_analytics.html",
        total=total,
        pending=pending,
        accepted=accepted,
        expired=expired,
        collected=collected
    )

@app.route("/collect/<int:id>")
def collect(id):

    donation = Donation.query.get(id)

    donation.status = "Collected"

    db.session.commit()

    return redirect("/accepted_donations")

@app.route("/receiver_logout")
def receiver_logout():

    session.pop(
        "receiver_id",
        None
    )

    session.pop(
        "receiver_name",
        None
    )

    return redirect(
        "/receiver_login"
    )
@app.route("/archive")
def archive_page():

    donations = Donation.query.filter_by(
        status="Archived"
    ).all()

    return render_template(
        "archive.html",
        donations=donations
    )
if __name__ == "__main__":
    app.run(debug=True)