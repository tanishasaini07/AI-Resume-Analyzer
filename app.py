from flask import Flask, render_template, request, redirect, session, flash
import os
import sqlite3
import PyPDF2
from company_profiles import company_profiles

from resume_analyzer import (
    clean_resume_text,
    detect_skills,
    detect_sections
)

from scoring import (
    calculate_resume_score,
    calculate_ats_score,
    calculate_company_match,
    get_grade
)

app = Flask(__name__)
app.secret_key = "resume_ai_secret_key"
dashboard_data = {}
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ==========================================
# MASTER SKILL LIST (Used for Resume Score)
# ==========================================

ALL_SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "html",
    "css",
    "javascript",
    "sql",
    "git",
    "react",
    "flask",
    "django",
    "node.js",
    "mongodb",
    "linux",
    "machine learning",
    "data structures",
    "algorithms"
]


def extract_text(filepath):
    text = ""

    with open(filepath, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            text += page.extract_text() or ""

    return text


@app.route("/")
def home():
    return render_template("home.html")
@app.route("/upload-page")
def upload_page():
    return render_template("upload.html")
@app.route("/dashboard")
def dashboard():
    return render_template("result.html", **dashboard_data)
@app.route("/about")
def about():    
    return render_template("about.html")
@app.route("/resources")
def resources():
    return render_template("resources.html")
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template(
                "signup.html",
                password_error="Passwords do not match."
            )

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Check username
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            conn.close()
            return render_template(
                "signup.html",
                username_error="Username already exists."
            )

        # Check email
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            conn.close()
            return render_template(
                "signup.html",
                email_error="Email already registered."
            )

        # Save user
        cursor.execute("""
            INSERT INTO users(username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")
@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, password FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:
        flash("No account found. Please sign up.", "email_error")
        return redirect("/")

    username, saved_password = user

    if password != saved_password:
        flash("Incorrect password.", "password_error")
        return redirect("/")

    session["username"] = username

    return redirect("/upload-page")
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST": 

        email = request.form["email"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user is None:

            return render_template(
                "forgot_password.html",
                error="No account found with this email."
            )

        return redirect(f"/reset-password/{email}")

    return render_template("forgot_password.html")
@app.route("/reset-password/<email>", methods=["GET", "POST"])
def reset_password(email):

    if request.method == "POST":

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            return render_template(
                "reset_password.html",
                error="Passwords do not match."
            )

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password=? WHERE email=?",
            (password, email)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("reset_password.html")
@app.route("/upload", methods=["POST"])
def upload():
    global dashboard_data
    file = request.files["resume"]
    company = request.form["company"]

    if file:

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Extract resume text
        resume_text = extract_text(filepath)

        # Clean resume text
        cleaned_text = clean_resume_text(resume_text)

        # Selected company profile
        profile = company_profiles.get(company)

        if profile is None:
            return "Invalid company selected."

        company_skills = profile["skills"]

        # ===============================
        # Detect ALL resume skills
        # ===============================

        resume_skills = detect_skills(
            cleaned_text,
            ALL_SKILLS
        )

        # ===============================
        # Detect company matched skills
        # ===============================

        found_skills = detect_skills(
            cleaned_text,
            company_skills
        )

        # Detect resume sections
        sections = detect_sections(cleaned_text)

        # Missing company skills
        missing_skills = [
            skill
            for skill in company_skills
            if skill not in found_skills
        ]

        # ===============================
        # Scores
        # ===============================

        resume_score = calculate_resume_score(
            resume_skills,
            sections
        )


        ats_score = calculate_ats_score(
            found_skills,
            company_skills,
            sections
        )

        company_match = calculate_company_match(
            found_skills,
            company_skills,
            sections
        )

        grade = get_grade(resume_score)
        dashboard_data = {
        "score": resume_score,
        "ats_score": ats_score,
        "company_match": company_match,
        "grade": grade,
        "skills": resume_skills,
        "matched_skills": found_skills,
        "missing_skills": missing_skills,
        "suggestions": profile["tips"],
        "resume_text": resume_text,
        "sections": sections,
        "selected_company": company,
        "username": session.get("username", "User")
}

    return redirect("/dashboard")   

    return "No file uploaded"


if __name__ == "__main__":
    app.run(debug=True)