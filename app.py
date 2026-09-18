import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Get PostgreSQL URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")


# -----------------------------
# Database Connection
# -----------------------------
def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set")

    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require"
    )


# -----------------------------
# Create Database Table
# -----------------------------
def create_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL,
            course VARCHAR(100) NOT NULL
        )
    """)

    conn.commit()

    cursor.close()
    conn.close()


# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, course
        FROM students
        ORDER BY id DESC
    """)

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        students=students
    )


# -----------------------------
# Add Student
# -----------------------------
@app.route("/add", methods=["POST"])
def add_student():

    name = request.form["name"]
    email = request.form["email"]
    course = request.form["course"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students
        (name, email, course)
        VALUES (%s, %s, %s)
    """, (name, email, course))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("home"))


# -----------------------------
# Delete Student
# -----------------------------
@app.route("/delete/<int:id>")
def delete_student(id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = %s",
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("home"))


# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":

    create_table()

    port = int(os.getenv("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )