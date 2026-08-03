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

app = Flask(__name__)
app.secret_key ="your_secret_key"
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def send_email(receiver_email, subject, message):
    msg = EmailMessage()
    msg["From"] = os.getenv("EMAIL_ADDRESS")
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(message)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(
            os.getenv("EMAIL_ADDRESS"),
            os.getenv("EMAIL_PASSWORD")
        )
        smtp.send_message(msg)

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
        "SELECT * FROM parcels WHERE tracking_number = ?",
        (tracking_number,)
    )

    parcel = cursor.fetchone()

    if parcel:
     cursor.execute("""
        SELECT *
        FROM parcel_history
        WHERE parcel_id = ?
        ORDER BY updated_at DESC
    """, (parcel["id"],))

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
        else:
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

    per_page = 10
    offset = (page - 1) * per_page

    search = request.args.get("search", "")
    status = request.args.get("status", "")

    conn = sqlite3.connect("database/parcels.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Dashboard Statistics
    cursor.execute("SELECT COUNT(*) FROM parcels")
    total_parcels = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM parcels WHERE status = 'Created'")
    created_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM parcels WHERE status = 'In Transit'")
    transit_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM parcels WHERE status = 'Delivered'")
    delivered_count = cursor.fetchone()[0]

    # Search query
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
        query += " AND status = ?"
        params.append(status)

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
        result_count=result_count, page=page
    )

@app.route("/admin/update/<int:parcel_id>", methods=["GET", "POST"])
def admin_update(parcel_id):

    conn = sqlite3.connect("database/parcels.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == "POST":

        sender_name = request.form.get("sender_name")
        receiver_name = request.form.get("receiver_name")
        receiver_email = request.form.get("receiver_email")
        status = request.form.get("status")
        location = request.form.get("location")

        message = f"""
        Parcel Update:

        Tracking ID: {parcel_id}
        New Status: {status}
        Current Location: {location}
    """

        cursor.execute("""
            UPDATE parcels
        SET sender_name = ?,
            receiver_name = ?,
            receiver_email = ?,
            status = ?,
            location = ?,
            updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
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
        conn.close()

        flash("Parcel updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    cursor.execute(
        "SELECT * FROM parcels WHERE id = ?",
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

    conn = sqlite3.connect("database/parcels.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM parcels WHERE id = ?",
        (parcel_id,)
    )

    conn.commit()
    conn.close()

    flash("Parcel deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
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
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

        conn = sqlite3.connect("database/parcels.db")
        cursor = conn.cursor()

        cursor.execute("""
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
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            tracking_number,
            sender_name,
            receiver_name,
            receiver_email,
            status,
            location,
            filename
        ))

        conn.commit()
        conn.close()

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
        "SELECT * FROM parcels WHERE id = ?",
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

    tracking_url = request.host_url + "track/" + str(parcel_id)

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
        "SELECT * FROM parcels WHERE id = ?",
        (parcel_id,)
    )

    parcel = cursor.fetchone()

    conn.close()

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
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)