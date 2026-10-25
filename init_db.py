
import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
""")

# Clear the old sample records
cursor.execute("DELETE FROM students")

# Five sample student records
students = [
    ("2026-00101", "Juan Dela Cruz", "BSIT", 1, "A"),
    ("2026-00102", "Maria Santos", "BSIT", 1, "B"),
    ("2026-00103", "Pedro Reyes", "BSCS", 2, "A"),
    ("2026-00104", "Ana Garcia", "BSIT", 2, "C"),
    ("2026-00105", "Mark Ramos", "BSCS", 3, "B")
]

cursor.executemany("""
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
""", students)

conn.commit()
conn.close()

print("Database created successfully.")
