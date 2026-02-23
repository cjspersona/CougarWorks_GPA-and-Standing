from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["student_portal"]
students = db["students"]

def calculate_gpa(grades):
    total_quality_points = 0
    total_credits = 0

    for grade in grades:
        total_quality_points += grade["gradePoints"] * grade["credits"]
        total_credits += grade["credits"]

    if total_credits == 0:
        return 0.0

    return round(total_quality_points / total_credits, 2)

def determine_standing(gpa):
    if gpa >= 3.5:
        return "Dean's List"
    elif gpa >= 2.0:
        return "Good Standing"
    elif gpa >= 1.0:
        return "Academic Warning"
    else:
        return "Academic Probation"

@app.route("/")
def dashboard():
    student = students.find_one({"_id": "S1001"})
    return render_template("dashboard.html", student=student)

@app.route("/add_grade", methods=["POST"])
def add_grade():
    student = students.find_one({"_id": "S1001"})

    new_grade = {
        "courseId": request.form["courseId"],
        "credits": int(request.form["credits"]),
        "letterGrade": request.form["letterGrade"],
        "gradePoints": float(request.form["gradePoints"])
    }

    student["grades"].append(new_grade)

    new_gpa = calculate_gpa(student["grades"])
    new_standing = determine_standing(new_gpa)

    students.update_one(
        {"_id": "S1001"},
        {
            "$set": {
                "grades": student["grades"],
                "gpa": new_gpa,
                "academicStanding": new_standing,
                "lastUpdated": datetime.utcnow()
            }
        }
    )

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)