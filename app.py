
import os
import sqlite3
import json

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

DATABASE = os.path.join(os.path.dirname(__file__), "students.db")

CLASSMATE_API_URL = "https://kleinjasperagrabio.onrender.com/api/students"


# DATABASE CONNECTION
def db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# CREATE DATABASE AND SAMPLE RECORDS
def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                program TEXT NOT NULL,
                year TEXT NOT NULL,
                section TEXT NOT NULL
            )
        """)

        conn.executemany("""
            INSERT OR IGNORE INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("STU001", "Juan Dela Cruz", "BSIT", "1", "A"),
            ("STU002", "Maria Santos", "BSIT", "2", "B"),
            ("STU003", "Pedro Reyes", "BSCS", "1", "A"),
            ("STU004", "Ana Garcia", "BSIT", "3", "A"),
            ("STU005", "Mark Villanueva", "BSCS", "2", "B")
        ])


init_db()


# HOME PAGE
@app.route("/")
def home():
    return render_template("index.html")


# GET ALL STUDENTS
@app.route("/api/students", methods=["GET"])
def get_students():
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()

    return jsonify([dict(row) for row in rows])


# GET ONE STUDENT
@app.route("/api/students/<int:id>", methods=["GET"])
def get_student(id):
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

    if row is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(row))


# ADD STUDENT
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}
    fields = ["student_id", "name", "program", "year", "section"]

    if any(not str(data.get(key, "")).strip() for key in fields):
        return jsonify({"error": "All fields are required"}), 400

    values = [str(data[key]).strip() for key in fields]

    try:
        with db() as conn:
            conn.execute("""
                INSERT INTO students
                (student_id, name, program, year, section)
                VALUES (?, ?, ?, ?, ?)
            """, values)

        return jsonify({"message": "Student added successfully"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 409


# UPDATE STUDENT
@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True) or {}
    fields = ["student_id", "name", "program", "year", "section"]

    if any(not str(data.get(key, "")).strip() for key in fields):
        return jsonify({"error": "All fields are required"}), 400

    values = [str(data[key]).strip() for key in fields]
    values.append(id)

    try:
        with db() as conn:
            cursor = conn.execute("""
                UPDATE students
                SET student_id = ?, name = ?, program = ?,
                    year = ?, section = ?
                WHERE id = ?
            """, values)

            if cursor.rowcount == 0:
                return jsonify({"error": "Student not found"}), 404

        return jsonify({"message": "Student updated successfully"})

    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 409


# DELETE STUDENT
@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    with db() as conn:
        cursor = conn.execute(
            "DELETE FROM students WHERE id = ?", (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"})


# LOAD CLASSMATE'S STUDENT RECORDS
@app.route("/api/classmate-proxy", methods=["GET"])
def classmate_proxy():
    url = request.args.get("url", "").strip().rstrip("/")

    allowed_urls = {
        "https://kleinjasperagrabio.onrender.com",
        CLASSMATE_API_URL
    }

    if url not in allowed_urls:
        return jsonify({
            "error": "Enter your classmate's website URL or its /api/students endpoint."
        }), 400

    try:
        req = Request(
            CLASSMATE_API_URL,
            headers={
                "User-Agent": "Mozilla/5.0 StudentHub-Lab8",
                "Accept": "application/json"
            }
        )

        with urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not isinstance(data, list):
            return jsonify({
                "error": "Classmate API must return a JSON list."
            }), 502

        return jsonify(data), 200

    except HTTPError as error:
        return jsonify({
            "error": f"Classmate server returned HTTP {error.code}."
        }), 502

    except URLError as error:
        return jsonify({
            "error": f"Cannot connect to classmate server: {error.reason}"
        }), 502

    except (TimeoutError, ValueError, OSError) as error:
        return jsonify({
            "error": f"Could not load classmate records: {str(error)}"
        }), 502


# RUN FLASK APP
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
