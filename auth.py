from flask import Flask, render_template, request, redirect, flash, session, url_for
import sqlite3
from auth import auth

app = Flask(__name__)
app.secret_key = "parcel_tracking_secret"

# Upload folder configuration
UPLOAD_FOLDER = "uploads" 
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}

app.register_blueprint(auth)

@app.route("/track", methods=["GET", "POST"])

def add_parcel():

    if request.method == "POST":

        tracking_number = request.form.get("tracking_number")
        sender_name = request.form.get("sender_name")
        receiver_name = request.form.get("receiver_name")
        status = request.form.get("status")
        location = request.form.get("location")

        conn = sqlite3.connect("database/parcels.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO parcels
            (tracking_number, sender_name, receiver_name, status, location, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (
            tracking_number,
            sender_name,
            receiver_name,
            status,
            location
        ))

        conn.commit()
        conn.close()

        flash("Parcel added successfully.", "success")

        return redirect(url_for("admin"))

    return render_template("add_parcel.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

if __name__ == "main":
    app.run(debug=True)