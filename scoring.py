# ==========================================
# SCORING FUNCTIONS
# ==========================================

def calculate_resume_score(found_skills, sections):
    """
    Calculates the overall resume quality score.
    This score is independent of any company.
    """

    MAX_RESUME_SKILLS = 12

    skill_score = min(
        60,
        int((len(found_skills) / MAX_RESUME_SKILLS) * 60)
    )

    section_score = 0

    if sections["Education"]:
        section_score += 8

    if sections["Projects"]:
        section_score += 10

    if sections["Experience"]:
        section_score += 10

    if sections["Certifications"]:
        section_score += 6

    if sections["Achievements"]:
        section_score += 6

    resume_score = min(100, skill_score + section_score)

    return resume_score


# ==========================================
# ATS SCORE
# ==========================================

def calculate_ats_score(found_skills, company_skills, sections):
    """
    Calculates ATS score based on company requirements.
    """

    if len(company_skills) == 0:
        ats = 0
    else:
        ats = int((len(found_skills) / len(company_skills)) * 70)

    if sections["Education"]:
        ats += 8

    if sections["Projects"]:
        ats += 8

    if sections["Experience"]:
        ats += 8

    if sections["Certifications"]:
        ats += 3

    if sections["Achievements"]:
        ats += 3

    return min(100, ats)


# ==========================================
# COMPANY MATCH
# ==========================================

def calculate_company_match(found_skills, company_skills, sections):
    """
    Calculates compatibility with the selected company.
    """

    if len(company_skills) == 0:
        compatibility = 0
    else:
        compatibility = int(
            (len(found_skills) / len(company_skills)) * 70
        )

    if sections["Projects"]:
        compatibility += 10

    if sections["Experience"]:
        compatibility += 10

    if sections["Certifications"]:
        compatibility += 5

    if sections["Achievements"]:
        compatibility += 5

    return min(100, compatibility)


# ==========================================
# GRADE
# ==========================================

def get_grade(score):

    if score >= 90:
        return "A+"

    elif score >= 80:
        return "A"

    elif score >= 70:
        return "B"

    elif score >= 60:
        return "C"

    else:
        return "Need to Improve"