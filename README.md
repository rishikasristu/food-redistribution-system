# Smart Food Redistribution System

## 📌 Project Overview

The **Smart Food Redistribution System** is a web-based platform designed to reduce food wastage by efficiently connecting food donors with receivers such as NGOs, orphanages, and other organizations. The system also provides volunteer coordination, GPS-based location tracking, donation priority management, and real-time status tracking.

## 🎯 Objectives

* Reduce food wastage by redistributing surplus food.
* Connect donors with suitable receivers.
* Enable volunteers to manage food pickup and delivery.
* Provide GPS-based location information for efficient coordination.
* Track donations from submission to delivery.
* Provide dashboard-based monitoring of system activities.

## ✨ Features

* Donor registration and login
* Receiver registration and login
* Food donation submission
* Food image upload
* GPS-based location detection
* Donation expiry management
* Priority-based donation allocation
* Receiver acceptance and rejection
* Rejection reason recording
* Volunteer assignment
* Pickup and delivery status tracking
* Donor donation history
* Receiver dashboard
* Administrative monitoring
* Expired donation management
* Dashboard analytics

## 👥 System Modules

### 1. Donor Module

Donors can register, log in, submit surplus food details, upload food images, provide expiry information, and share their location.

### 2. Receiver Module

Receivers such as NGOs and organizations can view available donations, accept suitable donations, reject donations with a reason, and track accepted donations.

### 3. Volunteer Module

Volunteers are assigned to accepted donations and update the pickup and delivery status throughout the process.

### 4. Admin Module

The administrator can monitor users, donations, volunteers, and overall system activities through the dashboard.

## 🛠️ Technology Stack

* **Frontend:** HTML, CSS, JavaScript, Bootstrap
* **Backend:** Python, Flask
* **Database:** MySQL
* **ORM:** SQLAlchemy
* **Location:** GPS / Geolocation API
* **Mapping & Distance:** Geopy
* **Image Handling:** Python `secure_filename`
* **Development Tools:** MySQL Workbench, VS Code

## 🔄 System Workflow

1. Donor registers and logs into the system.
2. Donor submits surplus food details with image, expiry time, and location.
3. The donation is stored in the database.
4. The system calculates the donation priority.
5. Available donations are displayed to receivers.
6. A receiver accepts a suitable donation.
7. A volunteer is assigned for pickup.
8. The volunteer updates the pickup and delivery status.
9. The donor and receiver can track the donation status.
10. Expired donations are moved to the expired donations records.

## 📊 Donation Status

The system manages donations through different statuses, including:

* Pending
* Accepted
* Rejected
* Collected
* Delivered
* Expired

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd food-redistribution
```

### 2. Install Dependencies

```bash
pip install flask flask-sqlalchemy mysql-connector-python geopy
```

Install any additional packages used by the project.

### 3. Configure MySQL

Create the required MySQL database using **MySQL Workbench** and update the database connection configuration in the Flask application.

### 4. Run the Application

```bash
python app.py
```

The application can then be accessed through the local Flask server.

## 🗄️ Database

The application uses **MySQL** to store information related to users, donations, receivers, volunteers, and donation status.

The main donation record contains information such as:

* Donation ID
* Food name
* Food type
* Quantity
* Preparation time
* Expiry time
* Description
* Donor phone
* Donor address
* GPS coordinates
* Image path
* Priority score
* Status
* Volunteer assignment
* Pickup status
* Estimated pickup time

## 🔐 Security and Validation

The system uses role-based access through Flask sessions. User input is validated before database operations, and uploaded filenames are handled using `secure_filename()` to reduce risks associated with unsafe file names.

## 🚀 Future Scope

* Mobile application for Android and iOS.
* AI-based food demand prediction.
* Improved automatic receiver matching.
* Integration with additional NGOs and organizations.
* Multilingual support.
* Advanced analytics and reporting.

## 👩‍💻 Project

**Smart Food Redistribution System**

Developed as a web-based food donation and redistribution platform using **Python Flask and MySQL**.
