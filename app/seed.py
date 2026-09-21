"""
Demo seed data (Section 6.8, items 26-27 of the design doc).

Idempotent: safe to run more than once. Get-or-create everywhere, keyed on
natural identifiers (role code, skill name, org name, user email).

Run with:  uv run python -m app.seed
"""

from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.opportunity import Opportunity, OpportunitySkill
from app.models.organization import Organization, OrganizationMember
from app.models.profile import AcademicianProfile, IndustryProfile, StudentProfile
from app.models.role import Role
from app.models.skill import Skill, SkillCategory, UserSkill
from app.models.user import User, UserRole
from app.models.application import Application  # noqa: F401 (registers table)

DEMO_PASSWORD = "Demo@1234"


# ---------------------------------------------------------------------------
# Reference data: roles + skill taxonomy
# ---------------------------------------------------------------------------

ROLES = [
    ("STUDENT", "Student"),
    ("ACADEMICIAN", "Academician"),
    ("INDUSTRY", "Industry"),
    ("INSTITUTION_ADMIN", "Institution Admin"),
    ("PLATFORM_ADMIN", "Platform Admin"),
]

SKILL_TAXONOMY = {
    "Programming Languages": ["Python", "Java", "JavaScript", "C++", "SQL"],
    "Web Development": ["HTML/CSS", "React.js", "Node.js", "REST API Design", "FastAPI"],
    "Data & AI": ["Machine Learning", "Data Analysis", "Pandas", "Statistics", "Deep Learning"],
    "Cloud & DevOps": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux Administration"],
    "Databases": ["PostgreSQL", "MongoDB", "Database Design"],
    "Mobile Development": ["Android Development", "Flutter"],
    "Tools & Productivity": ["Git & GitHub", "MS Excel", "Agile/Scrum"],
    "Soft Skills": ["Communication", "Teamwork", "Problem Solving", "Time Management"],
}


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------

INSTITUTION_NAME = "National Institute of Applied Technology"

INDUSTRY_ORGS = [
    {"name": "Vertex Analytics Solutions", "description": "Data analytics and applied ML consultancy."},
    {"name": "CloudPeak Systems", "description": "Cloud infrastructure and DevOps platform company."},
    {"name": "Nimbus Web Technologies", "description": "Product engineering studio building web applications."},
]


# ---------------------------------------------------------------------------
# People
# ---------------------------------------------------------------------------

ACADEMICIAN = {
    "email": "academician@niat.edu.in",
    "first_name": "Anjali",
    "last_name": "Mehta",
    "department": "Computer Science & Engineering",
    "designation": "Associate Professor",
}

RECRUITERS = [
    {"email": "recruiter@vertexanalytics.io", "first_name": "Karan", "last_name": "Desai", "org": "Vertex Analytics Solutions"},
    {"email": "recruiter@cloudpeak.io", "first_name": "Sana", "last_name": "Iqbal", "org": "CloudPeak Systems"},
    {"email": "recruiter@nimbusweb.io", "first_name": "Vikram", "last_name": "Rao", "org": "Nimbus Web Technologies"},
]

# skills: list of (skill_name, proficiency_level, years_experience)
STUDENTS = [
    {
        "email": "aarav.sharma@niat.edu.in", "first_name": "Aarav", "last_name": "Sharma",
        "branch": "Computer Science", "semester": 6,
        "skills": [
            ("Python", "ADVANCED", 2.0), ("SQL", "ADVANCED", 2.0), ("Data Analysis", "ADVANCED", 1.5),
            ("Statistics", "INTERMEDIATE", 1.0), ("Pandas", "ADVANCED", 1.5), ("MS Excel", "ADVANCED", 2.0),
            ("Communication", "INTERMEDIATE", 1.0),
        ],
    },
    {
        "email": "diya.patel@niat.edu.in", "first_name": "Diya", "last_name": "Patel",
        "branch": "Information Technology", "semester": 6,
        "skills": [
            ("React.js", "ADVANCED", 1.5), ("JavaScript", "ADVANCED", 2.0), ("HTML/CSS", "ADVANCED", 2.0),
            ("Node.js", "INTERMEDIATE", 1.0), ("Git & GitHub", "ADVANCED", 1.5), ("Teamwork", "ADVANCED", 1.5),
        ],
    },
    {
        "email": "rohan.verma@niat.edu.in", "first_name": "Rohan", "last_name": "Verma",
        "branch": "Computer Science", "semester": 7,
        "skills": [
            ("AWS", "ADVANCED", 1.5), ("Docker", "ADVANCED", 1.5), ("Linux Administration", "ADVANCED", 2.0),
            ("CI/CD", "INTERMEDIATE", 1.0), ("Git & GitHub", "ADVANCED", 1.5), ("Problem Solving", "ADVANCED", 2.0),
        ],
    },
    {
        "email": "ishita.nair@niat.edu.in", "first_name": "Ishita", "last_name": "Nair",
        "branch": "Computer Science", "semester": 5,
        "skills": [
            ("Python", "INTERMEDIATE", 1.0), ("React.js", "INTERMEDIATE", 1.0), ("SQL", "INTERMEDIATE", 1.0),
            ("Git & GitHub", "INTERMEDIATE", 1.0), ("Communication", "ADVANCED", 1.5), ("Agile/Scrum", "BEGINNER", 0.5),
        ],
    },
    {
        "email": "kabir.singh@niat.edu.in", "first_name": "Kabir", "last_name": "Singh",
        "branch": "Information Technology", "semester": 4,
        "skills": [
            ("HTML/CSS", "BEGINNER", 0.5), ("MS Excel", "INTERMEDIATE", 1.0),
            ("Communication", "INTERMEDIATE", 1.0), ("Teamwork", "INTERMEDIATE", 1.0),
            ("Time Management", "BEGINNER", 0.5),
        ],
    },
    {
        "email": "meera.iyer@niat.edu.in", "first_name": "Meera", "last_name": "Iyer",
        "branch": "Computer Science", "semester": 7,
        "skills": [
            ("Python", "ADVANCED", 2.0), ("Machine Learning", "ADVANCED", 1.5), ("Deep Learning", "INTERMEDIATE", 1.0),
            ("Statistics", "ADVANCED", 1.5), ("Data Analysis", "ADVANCED", 1.5), ("Problem Solving", "ADVANCED", 2.0),
        ],
    },
]

# opportunities: (org_name, title, type, description, required_skills[(skill_name, importance, required)])
OPPORTUNITIES = [
    (
        "Vertex Analytics Solutions", "Data Analyst Intern", "INTERNSHIP",
        "Work with the analytics team to clean, analyze, and visualize client datasets, "
        "and help build recurring reporting dashboards.",
        [("Python", "HIGH", True), ("SQL", "HIGH", True), ("Data Analysis", "HIGH", True),
         ("Statistics", "MEDIUM", True), ("MS Excel", "MEDIUM", False)],
    ),
    (
        "Vertex Analytics Solutions", "Machine Learning Intern", "INTERNSHIP",
        "Assist in building and evaluating predictive models for client engagements, "
        "under the guidance of senior data scientists.",
        [("Python", "HIGH", True), ("Machine Learning", "HIGH", True), ("Statistics", "HIGH", True),
         ("Pandas", "MEDIUM", True), ("Deep Learning", "MEDIUM", False)],
    ),
    (
        "CloudPeak Systems", "Cloud Engineer Intern", "INTERNSHIP",
        "Support the platform team in provisioning, monitoring, and automating cloud "
        "infrastructure for internal and client environments.",
        [("AWS", "HIGH", True), ("Docker", "HIGH", True), ("Linux Administration", "HIGH", True),
         ("CI/CD", "MEDIUM", True), ("Git & GitHub", "MEDIUM", True)],
    ),
    (
        "Nimbus Web Technologies", "Frontend Developer Intern", "INTERNSHIP",
        "Build and ship UI features for client-facing web products, working closely "
        "with design and backend teams.",
        [("React.js", "HIGH", True), ("JavaScript", "HIGH", True), ("HTML/CSS", "HIGH", True),
         ("Git & GitHub", "MEDIUM", True)],
    ),
    (
        "Nimbus Web Technologies", "Full Stack Developer Intern", "INTERNSHIP",
        "End-to-end feature ownership across our React frontend and Python/Node backend "
        "services, including API design.",
        [("React.js", "HIGH", True), ("Node.js", "HIGH", True), ("SQL", "MEDIUM", True),
         ("REST API Design", "HIGH", True), ("Python", "MEDIUM", False)],
    ),
]


def get_or_create(db: Session, model, defaults: dict | None = None, **filters):
    instance = db.query(model).filter_by(**filters).first()
    if instance:
        return instance, False
    params = {**filters, **(defaults or {})}
    instance = model(**params)
    db.add(instance)
    db.flush()
    return instance, True


def seed_roles(db: Session) -> dict[str, Role]:
    roles = {}
    for code, name in ROLES:
        role, _ = get_or_create(db, Role, code=code, defaults={"name": name})
        roles[code] = role
    return roles


def seed_skills(db: Session) -> dict[str, Skill]:
    skills = {}
    for category_name, skill_names in SKILL_TAXONOMY.items():
        category, _ = get_or_create(db, SkillCategory, name=category_name)
        for skill_name in skill_names:
            skill, _ = get_or_create(
                db, Skill, category_id=category.id, name=skill_name, defaults={"skill_type": "TECHNICAL"}
            )
            skills[skill_name] = skill
    return skills


def seed_organizations(db: Session) -> tuple[Organization, dict[str, Organization]]:
    institution, _ = get_or_create(
        db, Organization, name=INSTITUTION_NAME,
        defaults={"organization_type": "INSTITUTION", "verified": True, "city": "Vadodara", "country": "India"},
    )
    industry_orgs = {}
    for org in INDUSTRY_ORGS:
        instance, _ = get_or_create(
            db, Organization, name=org["name"],
            defaults={"organization_type": "INDUSTRY", "verified": True, "description": org["description"]},
        )
        industry_orgs[org["name"]] = instance
    return institution, industry_orgs


def seed_user(db: Session, *, email: str, first_name: str, last_name: str, role: Role) -> tuple[User, bool]:
    user, created = get_or_create(
        db, User, email=email,
        defaults={
            "password_hash": hash_password(DEMO_PASSWORD),
            "first_name": first_name,
            "last_name": last_name,
            "email_verified": True,
        },
    )
    if created:
        db.add(UserRole(user_id=user.id, role_id=role.id))
        db.flush()
    return user, created


def seed_academician(db: Session, roles: dict, institution: Organization) -> None:
    user, created = seed_user(
        db, email=ACADEMICIAN["email"], first_name=ACADEMICIAN["first_name"],
        last_name=ACADEMICIAN["last_name"], role=roles["ACADEMICIAN"],
    )
    get_or_create(
        db, AcademicianProfile, user_id=user.id,
        defaults={
            "institution_id": institution.id,
            "department": ACADEMICIAN["department"],
            "designation": ACADEMICIAN["designation"],
        },
    )
    get_or_create(
        db, OrganizationMember, organization_id=institution.id, user_id=user.id,
        defaults={"member_role": "ACADEMICIAN", "department": ACADEMICIAN["department"]},
    )


def seed_recruiters(db: Session, roles: dict, industry_orgs: dict[str, Organization]) -> dict[str, User]:
    recruiter_users = {}
    for r in RECRUITERS:
        org = industry_orgs[r["org"]]
        user, _ = seed_user(db, email=r["email"], first_name=r["first_name"], last_name=r["last_name"], role=roles["INDUSTRY"])
        get_or_create(db, IndustryProfile, user_id=user.id, defaults={"organization_id": org.id})
        get_or_create(
            db, OrganizationMember, organization_id=org.id, user_id=user.id,
            defaults={"member_role": "RECRUITER"},
        )
        recruiter_users[r["org"]] = user
    return recruiter_users


def seed_students(db: Session, roles: dict, institution: Organization, skills: dict[str, Skill]) -> list[User]:
    student_users = []
    for s in STUDENTS:
        user, _ = seed_user(db, email=s["email"], first_name=s["first_name"], last_name=s["last_name"], role=roles["STUDENT"])
        get_or_create(
            db, StudentProfile, user_id=user.id,
            defaults={"institution_id": institution.id, "branch": s["branch"], "semester": s["semester"], "degree": "B.Tech"},
        )
        for skill_name, level, years in s["skills"]:
            skill = skills[skill_name]
            row = db.query(UserSkill).filter_by(user_id=user.id, skill_id=skill.id).first()
            if row is None:
                db.add(UserSkill(user_id=user.id, skill_id=skill.id, proficiency_level=level, years_experience=years, source="SELF_DECLARED"))
        db.flush()
        student_users.append(user)
    return student_users


def seed_opportunities(db: Session, industry_orgs: dict[str, Organization], recruiter_users: dict[str, User], skills: dict[str, Skill]) -> None:
    for org_name, title, opp_type, description, required in OPPORTUNITIES:
        org = industry_orgs[org_name]
        creator = recruiter_users[org_name]
        opportunity = db.query(Opportunity).filter_by(organization_id=org.id, title=title).first()
        if opportunity is not None:
            continue
        opportunity = Opportunity(
            organization_id=org.id,
            created_by_user_id=creator.id,
            title=title,
            opportunity_type=opp_type,
            description=description,
            location="Remote",
            work_mode="REMOTE",
            duration_text="3 months",
            status="PUBLISHED",
        )
        db.add(opportunity)
        db.flush()
        for skill_name, importance, required_flag in required:
            db.add(
                OpportunitySkill(
                    opportunity_id=opportunity.id,
                    skill_id=skills[skill_name].id,
                    importance=importance,
                    required=required_flag,
                )
            )
    db.flush()


def run():
    Base.metadata.create_all(bind=engine)  # no-op if Alembic already applied; safe either way
    db = SessionLocal()
    try:
        roles = seed_roles(db)
        skills = seed_skills(db)
        institution, industry_orgs = seed_organizations(db)
        seed_academician(db, roles, institution)
        recruiter_users = seed_recruiters(db, roles, industry_orgs)
        seed_students(db, roles, institution, skills)
        seed_opportunities(db, industry_orgs, recruiter_users, skills)
        db.commit()
        print("Seed complete.")
        print(f"Demo password for every seeded user: {DEMO_PASSWORD}")
        print(f"Institution: {INSTITUTION_NAME}")
        print(f"Academician login: {ACADEMICIAN['email']}")
        print("Industry logins: " + ", ".join(r["email"] for r in RECRUITERS))
        print("Student logins: " + ", ".join(s["email"] for s in STUDENTS))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
