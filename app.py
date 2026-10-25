
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


# Display your website from templates/index.html
@app.route('/')
def home():
    return render_template('index.html')


# Your original student API
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00162",
        "name": "Johannes Aguilar",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


# Your original hello API
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
        "message": f"Hello, {name}!"
    })


# Connect to your SQLite database
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# Display all students from the database
@app.route('/students')
def get_students():
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# Display one student by database ID
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# Additional task: display students by program
@app.route('/students/program/<string:program>')
def get_students_by_program(program):
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students WHERE program = ?',
        (program,)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
