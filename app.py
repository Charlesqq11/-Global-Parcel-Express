from flask import Flask, flash, redirect, render_template, request, url_for, session, Response, send_file
import sqlite3
import csv
import qrcode
import smtplib
import os
from werkzeug.utils import secure_filename
from email.message import EmailMessage
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def send_email(receiver_email, subject, message):

    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("Email configuration missing.")
        return False

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(message)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        print("Email sent successfully.")
        return True

    except Exception as e:
        print("Email Error:", e)
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/track", methods=["POST"])
def track():

    tracking_number = request.form.get("trackingNumber")

    if not tracking_number:
        return render_template(
            "index.html",
            message="Please enter a tracking number."
        )

    conn = sqlite3.connect("database/parcels.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM parcels WHERE tracking_number=?",
        (tracking_number,)
    )

    parcel = cursor.fetchone()

    if parcel:

        cursor.execute(
            """
            SELECT *
            FROM parcel_history
            WHERE parcel_id=?
            ORDER BY updated_at DESC
            """,
            (parcel["id"],)
        )

        history = cursor.fetchall()

        conn.close()

        return render_template(
            "result.html",
            parcel=parcel,
            history=history
        )

    conn.close()

    return render_template(
        "index.html",
        message="Tracking number not found."
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == os.getenv("ADMIN_PASSWORD"):
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        return render_template(
            "login.html",
            message="Invalid username or password."
        )

    return render_template("login.html")

@app.route("/admin")
def admin_dashboard():

    if "admin" not in session:
        return redirect(url_for("login"))

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    status = request.args.get("status", "")

    per_page = 10
    offset = (page - 1) * per_page

    conn = sqlite3.connect("database/parcels.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM parcels")
    total_parcels = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM parcels WHERE status='Created'")
    created_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM parcels WHERE status='In Transit'")
    transit_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM parcels WHERE status='Delivered'")
    delivered_count = cursor.fetchone()[0]

    query = "SELECT * FROM parcels WHERE 1=1"
    params = []

    if search:
        query += """
        AND (
            tracking_number LIKE ?
            OR sender_name LIKE ?
            OR receiver_name LIKE ?
        )
        """
        params.extend([
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ])

    if status:
        query += " AND status=?"
        params.append(status)

    query += """
        ORDER BY updated_at DESC
        LIMIT ? OFFSET ?
    """

    params.extend([per_page, offset])

    cursor.execute(query, params)

    parcels = cursor.fetchall()

    result_count = len(parcels)

    conn.close()

    return render_template(
        "admin_dashboard.html",
        parcels=parcels,
        search=search,
        status=status,
        total_parcels=total_parcels,
        created_count=created_count,
        transit_count=transit_count,
        delivered_count=delivered_count,
        result_count=result_count,
        page=page
    )

@app.route("/admin/update/<int:parcel_id>", methods=["GET", "POST"])
def admin_update(parcel_id):
    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database/parcels.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":

        sender_name = request.form.get("sender_name")
        receiver_name = request.form.get("receiver_name")
        receiver_email = request.form.get("receiver_email")
        status = request.form.get("status")
        location = request.form.get("location")

        cursor.execute("""
            UPDATE parcels
            SET sender_name=?,
                receiver_name=?,
                receiver_email=?,
                status=?,
                location=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (
            sender_name,
            receiver_name,
            receiver_email,
            status,
            location,
            parcel_id
        ))

        cursor.execute("""
            INSERT INTO parcel_history
            (parcel_id, status, location)
            VALUES (?, ?, ?)
        """, (
            parcel_id,
            status,
            location
        ))

        conn.commit()

        send_email(
            receiver_email,
            "Parcel Status Updated",
            f"""
            Hello {receiver_name},

            Your parcel status has been updated.

            Tracking Number: {parcel_id}
            Status: {status}
            Location: {location}

            Thank you for using our Parcel Tracking System.
        """
        )

        flash("Parcel updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    cursor.execute(
        "SELECT * FROM parcels WHERE id=?",
        (parcel_id,)
    )

    parcel = cursor.fetchone()

    conn.close()

    return render_template(
        "admin_update.html",
        parcel=parcel
    )

@app.route("/admin/delete/<int:parcel_id>")
def admin_delete(parcel_id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database/parcels.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM parcels WHERE id=?",
        (parcel_id,)
    )

    conn.commit()
    conn.close()

    flash("Parcel deleted successfully!", "success")

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():

    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        tracking_number = request.form.get("tracking_number")
        sender_name = request.form.get("sender_name")
        receiver_name = request.form.get("receiver_name")
        receiver_email = request.form.get("receiver_email")
        status = request.form.get("status")
        location = request.form.get("location")

        image = request.files.get("parcel_image")
        filename = None

        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        conn = sqlite3.connect("database/parcels.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO parcels
            (
                tracking_number,
                sender_name,
                receiver_name,
                receiver_email,
                status,
                location,
                parcel_image,
                updated_at
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                tracking_number,
                sender_name,
                receiver_name,
                receiver_email,
                status,
                location,
                filename
            )
        )

        conn.commit()
        conn.close()

        # Send notification email to the receiver
        send_email(
            receiver_email,
            "Your Parcel Has Been Created",
            f"""
Hello {receiver_name},

Your parcel has been created successfully.

Here are your parcel details:

📦 Tracking Number: {tracking_number}
👤 Sender: {sender_name}
📍 Current Status: {status}
🌍 Current Location: {location}

You can now track your parcel at any time using your tracking number.

Please keep your tracking number safe, as you will need it to check the latest status of your shipment.

Thank you for choosing our Parcel Tracking System.

Best regards,
Parcel Tracking Team
"""
        )

        flash("Parcel added successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_add.html")

@app.route("/admin/view/<int:parcel_id>")
def admin_view(parcel_id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database/parcels.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM parcels WHERE id=?",
        (parcel_id,)
    )

    parcel = cursor.fetchone()

    conn.close()

    return render_template(
        "admin_view.html",
        parcel=parcel
    )

@app.route("/admin/export")
def admin_export():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database/parcels.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM parcels")
    parcels = cursor.fetchall()

    conn.close()

    def generate():
        yield "ID,Tracking Number,Sender,Receiver,Status,Location,Updated At\n"

        for parcel in parcels:
            yield ",".join(map(str, parcel)) + "\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=parcels.csv"
        }
    )

@app.route("/admin/qrcode/<int:parcel_id>")
def generate_qrcode(parcel_id):

    if "admin" not in session:
        return redirect(url_for("login"))

    tracking_url = url_for(
        "track_parcel",
        parcel_id=parcel_id,
        _external=True
    )

    img = qrcode.make(tracking_url)

    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(
        img_io,
        mimetype="image/png"
    )

@app.route("/track/<int:parcel_id>")
def track_parcel(parcel_id):

    conn = sqlite3.connect("database/parcels.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM parcels WHERE id=?",
        (parcel_id,)
    )

    parcel = cursor.fetchone()

    conn.close()

    if not parcel:
        return render_template(
            "index.html",
            message="Tracking number not found."
        )

    return render_template(
        "result.html",
        parcel=parcel
    )

@app.route("/admin/profile")
def admin_profile():

    if "admin" not in session:
        return redirect(url_for("login"))

    return render_template("admin_profile.html")

@app.route("/logout")
def logout():

    session.pop("admin", None)

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("login"))

def send_email(receiver_email, subject, message):
    """
    Send an email notification.
    """

    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("ERROR: EMAIL_ADDRESS or EMAIL_PASSWORD is missing.")
        return

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(message)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)

        print("Email sent successfully.")

    except Exception as e:
        print("Email Error:", e)

if __name__ == "__main__":
     app.run(debug=True)