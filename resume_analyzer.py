import PyPDF2


# ==========================
# EXTRACT PDF TEXT
# ==========================
def extract_resume_text(filepath):

    text = ""

    try:
        with open(filepath, "rb") as pdf_file:

            reader = PyPDF2.PdfReader(pdf_file)

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    except:
        return ""

    return text


# ==========================
# CLEAN TEXT
# ==========================
def clean_resume_text(text):

    text = text.lower()

    text = text.replace(",", " ")
    text = text.replace("&", " ")
    text = text.replace("-", " ")
    text = text.replace("/", " ")

    text = " ".join(text.split())

    return text


# ==========================
# DETECT SKILLS
# ==========================
def detect_skills(resume_text, company_skills):

    found_skills = []

    for skill in company_skills:

        s = skill.lower()

        if s == "c++":

            if "c++" in resume_text or "cpp" in resume_text:
                found_skills.append(skill)

        elif s == "node.js":

            if "node" in resume_text or "nodejs" in resume_text:
                found_skills.append(skill)

        elif s == "machine learning":

            if "machine learning" in resume_text or "ml" in resume_text:
                found_skills.append(skill)

        elif s == "data structures":

            if "data structures" in resume_text or "dsa" in resume_text:
                found_skills.append(skill)

        else:

            if s in resume_text:
                found_skills.append(skill)

    return found_skills


# ==========================
# DETECT RESUME SECTIONS
# ==========================
def detect_sections(resume_text):

    return {

        "Education": "education" in resume_text,

        "Projects": "project" in resume_text,

        "Experience": "experience" in resume_text,

        "Certifications": "certification" in resume_text,

        "Achievements": "achievement" in resume_text

    }