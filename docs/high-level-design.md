# TalentSync – High Level Design, Domain Model & PostgreSQL Schema
## Foundational CRUD Implementation Blueprint
**Stack: React.js + FastAPI + PostgreSQL**

# 1. Purpose

TalentSync is a unified Academia–Industry Collaboration Platform supporting:

- Skill assessment and skill-gap identification
- Skill mapping and career readiness
- Learning and certification programs
- Student and academician portfolios
- Internships, jobs and other opportunities
- Application tracking
- Academia–industry collaboration
- Institution and industry analytics

Primary roles:

1. Student
2. Academician
3. Industry User
4. Institution Admin
5. Platform Admin

Core journey:

```text
Profile → Skill Assessment → Skill Profile → Skill Gap Analysis
→ Learning → Portfolio → Opportunity Matching → Application
→ Progress Tracking → Feedback & Analytics
```

# 2. Phase Strategy

## Phase 1: Foundational CRUD

Implement:

- Core domain models and relationships
- PostgreSQL schema
- CRUD APIs
- Validation
- Pagination and filtering
- Role-ready access model
- Seed/demo data

Do NOT implement yet:

- AI/LLM logic
- Recommendation algorithms
- Complex workflows
- Third-party integrations
- Advanced analytics
- Real-time notifications

Architecture:

```text
React.js
   │ REST/JSON
   ▼
FastAPI
   ├── API
   ├── Services
   ├── Repositories
   └── SQLAlchemy ORM
          │
          ▼
      PostgreSQL
```

Use a modular monolith.

# 3. Common Technical Standards

- PostgreSQL UUID primary keys
- SQLAlchemy 2.x
- Alembic migrations
- Pydantic v2
- UTC timestamps
- `created_at`, `updated_at` on business entities
- VARCHAR + application enums for evolving statuses
- Database tables: `snake_case` plural
- Python classes: PascalCase
- Python attributes: snake_case
- REST API version prefix: `/api/v1`
- JSON response convention: camelCase preferred

Base fields:

```text
id UUID PRIMARY KEY
created_at TIMESTAMPTZ
updated_at TIMESTAMPTZ
```

# 4. High-Level Domain Model

```text
USER
 ├── USER_ROLE ─── ROLE
 ├── ORGANIZATION_MEMBER ─── ORGANIZATION
 ├── STUDENT_PROFILE
 ├── ACADEMICIAN_PROFILE
 ├── INDUSTRY_PROFILE
 ├── USER_SKILL ─── SKILL ─── SKILL_CATEGORY
 ├── ASSESSMENT_ATTEMPT ─── ASSESSMENT
 ├── PORTFOLIO_PROJECT
 ├── CERTIFICATION
 ├── DOCUMENT
 ├── APPLICATION ─── OPPORTUNITY
 └── COLLABORATION_PARTICIPANT ─── COLLABORATION

ORGANIZATION
 ├── ORGANIZATION_MEMBER
 ├── OPPORTUNITY
 ├── LEARNING_PROGRAM
 └── COLLABORATION

OPPORTUNITY
 └── OPPORTUNITY_SKILL ─── SKILL

LEARNING_PROGRAM
 └── LEARNING_PROGRAM_SKILL ─── SKILL

ASSESSMENT
 └── ASSESSMENT_QUESTION
       └── QUESTION_OPTION

ASSESSMENT_ATTEMPT
 └── ASSESSMENT_ANSWER
```

# 5. Models, Fields and Relationships

## 5.1 Role

### roles

Fields:

```text
id
code                  UNIQUE
name
description
created_at
updated_at
```

Seed roles:

```text
STUDENT
ACADEMICIAN
INDUSTRY_USER
INSTITUTION_ADMIN
PLATFORM_ADMIN
```

### user_roles

```text
id
user_id               FK → users
role_id               FK → roles
created_at
```

Constraint:

```text
UNIQUE(user_id, role_id)
```

Relationship:

```text
User * ↔ * Role
```

---

## 5.2 User

### users

```text
id
email                 UNIQUE, NOT NULL
password_hash
first_name
last_name
mobile_number
profile_image_url
status
email_verified
last_login_at
created_at
updated_at
```

Status:

```text
ACTIVE
INACTIVE
PENDING
```

Relationships:

```text
User
 ├── many Roles
 ├── many OrganizationMemberships
 ├── one StudentProfile (optional)
 ├── one AcademicianProfile (optional)
 ├── one IndustryProfile (optional)
 ├── many UserSkills
 ├── many AssessmentAttempts
 ├── many PortfolioProjects
 ├── many Certifications
 ├── many Documents
 ├── many Applications
 └── many CollaborationParticipations
```

---

# 6. Organization Model

Use a common organization model instead of separate college/company tables.

## organizations

```text
id
name
organization_type
description
website
email
phone
address_line1
city
state
country
postal_code
logo_url
verified
status
created_at
updated_at
```

organization_type:

```text
INSTITUTION
INDUSTRY
TRAINING_PROVIDER
CERTIFICATION_PROVIDER
GOVERNMENT
OTHER
```

## organization_members

```text
id
organization_id       FK → organizations
user_id               FK → users
member_role
department
designation
status
created_at
updated_at
```

Constraint:

```text
UNIQUE(organization_id, user_id)
```

Examples:

```text
Student → Institution
Professor → Institution
HR Manager → Industry
Training Manager → Industry
```

---

# 7. Profile Models

## student_profiles

```text
id
user_id               UNIQUE FK → users
institution_id        FK → organizations
enrollment_number
branch
degree
semester
current_year
graduation_year
cgpa
career_summary
career_interests      JSONB
preferred_locations   JSONB
open_to_remote
profile_completion_percent
created_at
updated_at
```

Relationship:

```text
User 1 → 0..1 StudentProfile
Institution 1 → * Students
```

## academician_profiles

```text
id
user_id               UNIQUE FK → users
institution_id        FK → organizations
employee_number
department
designation
specialization
experience_years
research_interests    JSONB
bio
profile_completion_percent
created_at
updated_at
```

## industry_profiles

```text
id
user_id               UNIQUE FK → users
organization_id       FK → organizations
department
designation
expertise             JSONB
bio
created_at
updated_at
```

---

# 8. Skills Domain

## skill_categories

```text
id
name                  UNIQUE
description
status
created_at
updated_at
```

Examples:

```text
Programming
Cloud
Data Science
Artificial Intelligence
Cybersecurity
Database
Soft Skills
Communication
Leadership
Domain Knowledge
```

## skills

```text
id
category_id           FK → skill_categories
name
description
skill_type
status
created_at
updated_at
```

Constraint:

```text
UNIQUE(category_id, name)
```

## user_skills

```text
id
user_id               FK → users
skill_id              FK → skills
proficiency_level
proficiency_score
years_experience
source
verified
last_assessed_at
created_at
updated_at
```

proficiency_level:

```text
BEGINNER
INTERMEDIATE
ADVANCED
EXPERT
```

source:

```text
SELF_DECLARED
ASSESSMENT
CERTIFICATION
PROJECT
ADMIN_VERIFIED
AI_GENERATED
```

Constraint:

```text
UNIQUE(user_id, skill_id)
```

---

# 9. Assessment Domain

Phase 1 stores assessment data. Advanced scoring can be added later.

## assessments

```text
id
name
description
target_role
assessment_type
status
created_by_user_id    FK → users
created_at
updated_at
```

assessment_type:

```text
TECHNICAL
SOFT_SKILL
APTITUDE
CAREER_INTEREST
MIXED
```

## assessment_questions

```text
id
assessment_id         FK → assessments
skill_id              FK → skills, nullable
question_text
question_type
display_order
required
weight
status
created_at
updated_at
```

question_type:

```text
SINGLE_CHOICE
MULTIPLE_CHOICE
TEXT
RATING
YES_NO
```

## assessment_question_options

```text
id
question_id           FK → assessment_questions
option_text
score
display_order
```

## assessment_attempts

```text
id
assessment_id         FK → assessments
user_id               FK → users
status
started_at
completed_at
overall_score
created_at
updated_at
```

status:

```text
NOT_STARTED
IN_PROGRESS
COMPLETED
ABANDONED
```

## assessment_answers

```text
id
attempt_id            FK → assessment_attempts
question_id           FK → assessment_questions
selected_option_ids   JSONB
text_answer
rating_value
calculated_score
created_at
updated_at
```

---

# 10. Opportunity Domain

Use one generalized model for all opportunity types.

## opportunities

```text
id
organization_id       FK → organizations
created_by_user_id    FK → users
title
opportunity_type
description
department
location
work_mode
duration_text
stipend_amount
currency
application_deadline
start_date
end_date
eligibility_criteria
min_cgpa
openings_count
status
published_at
created_at
updated_at
```

opportunity_type:

```text
INTERNSHIP
JOB
APPRENTICESHIP
LIVE_PROJECT
RESEARCH_PROJECT
FACULTY_INTERNSHIP
INDUSTRIAL_TRAINING
FDP
CONSULTANCY
MENTORSHIP
WORKSHOP
CERTIFICATION
```

work_mode:

```text
ONSITE
REMOTE
HYBRID
```

status:

```text
DRAFT
PUBLISHED
CLOSED
EXPIRED
CANCELLED
```

## opportunity_skills

```text
id
opportunity_id        FK → opportunities
skill_id              FK → skills
required_level
importance
required
created_at
```

importance:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Constraint:

```text
UNIQUE(opportunity_id, skill_id)
```

Relationship:

```text
Opportunity * ↔ * Skill
```

---

# 11. Application Domain

## applications

```text
id
opportunity_id        FK → opportunities
applicant_user_id     FK → users
resume_document_id    FK → documents, nullable
cover_letter
application_data      JSONB
applied_at
status
status_updated_at
created_at
updated_at
```

status:

```text
DRAFT
SUBMITTED
UNDER_REVIEW
SHORTLISTED
INTERVIEW
SELECTED
OFFERED
REJECTED
WITHDRAWN
COMPLETED
```

Constraint:

```text
UNIQUE(opportunity_id, applicant_user_id)
```

## application_status_history

```text
id
application_id        FK → applications
old_status
new_status
remarks
changed_by_user_id    FK → users
changed_at
```

Relationship:

```text
Opportunity 1 → * Applications
User 1 → * Applications
Application 1 → * StatusHistory
```

---

# 12. Learning Domain

## learning_programs

```text
id
provider_organization_id  FK → organizations
created_by_user_id        FK → users
title
description
program_type
duration_text
delivery_mode
external_url
certificate_available
cost_amount
currency
status
created_at
updated_at
```

program_type:

```text
COURSE
CERTIFICATION
WORKSHOP
TRAINING
MENTORSHIP
BOOTCAMP
FDP
```

## learning_program_skills

```text
id
learning_program_id   FK → learning_programs
skill_id              FK → skills
skill_level
created_at
```

Constraint:

```text
UNIQUE(learning_program_id, skill_id)
```

---

# 13. Portfolio Domain

## portfolio_projects

```text
id
user_id               FK → users
title
description
project_type
start_date
end_date
repository_url
project_url
status
visibility
created_at
updated_at
```

visibility:

```text
PUBLIC
PRIVATE
INSTITUTION_ONLY
```

## project_skills

```text
id
project_id            FK → portfolio_projects
skill_id              FK → skills
created_at
```

Constraint:

```text
UNIQUE(project_id, skill_id)
```

## certifications

```text
id
user_id               FK → users
title
issuing_organization
credential_id
credential_url
issue_date
expiry_date
verified
status
created_at
updated_at
```

## documents

Generic metadata; actual object storage can be added later.

```text
id
user_id               FK → users
document_type
file_name
file_url
mime_type
file_size_bytes
verified
status
created_at
updated_at
```

document_type:

```text
RESUME
CERTIFICATE
PROJECT_DOCUMENT
INTERNSHIP_REPORT
ACADEMIC_RECORD
PROFILE_IMAGE
OTHER
```

---

# 14. Collaboration Domain

## collaborations

```text
id
host_organization_id  FK → organizations
partner_organization_id FK → organizations, nullable
created_by_user_id    FK → users
title
description
collaboration_type
location
meeting_url
start_date
end_date
max_participants
status
created_at
updated_at
```

collaboration_type:

```text
MENTORSHIP
WORKSHOP
GUEST_LECTURE
LIVE_PROJECT
RESEARCH
INNOVATION_CHALLENGE
INDUSTRIAL_TRAINING
CONSULTANCY
FDP
```

status:

```text
DRAFT
OPEN
ONGOING
COMPLETED
CANCELLED
```

## collaboration_participants

```text
id
collaboration_id      FK → collaborations
user_id               FK → users
participant_role
status
joined_at
```

participant_role:

```text
PARTICIPANT
MENTOR
SPEAKER
ORGANIZER
REVIEWER
```

Constraint:

```text
UNIQUE(collaboration_id, user_id)
```

---

# 15. Future Recommendation Models

Create CRUD-ready persistence models but do not implement AI logic.

## recommendations

```text
id
user_id               FK → users
recommendation_type
target_entity_type
target_entity_id
score
reason
generated_by
status
generated_at
created_at
```

recommendation_type:

```text
CAREER_PATH
SKILL
LEARNING_PROGRAM
OPPORTUNITY
CERTIFICATION
COLLABORATION
```

generated_by:

```text
RULE_ENGINE
ML_MODEL
LLM
ADMIN
HYBRID
```

## career_readiness_scores

```text
id
user_id               FK → users
target_role
overall_score
technical_score
soft_skill_score
experience_score
portfolio_score
assessment_score
calculation_version
calculated_at
```

Future logic will calculate:

```text
Career Readiness Score
+
Skill Gap
+
Opportunity Match Score
+
Learning Recommendation
```

without changing the foundational schema.

# 16. PostgreSQL DDL

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(50) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  last_name VARCHAR(100),
  mobile_number VARCHAR(30),
  profile_image_url VARCHAR(500),
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, role_id)
);

CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  organization_type VARCHAR(50) NOT NULL,
  description TEXT,
  website VARCHAR(500),
  email VARCHAR(255),
  phone VARCHAR(30),
  address_line1 VARCHAR(255),
  city VARCHAR(100),
  state VARCHAR(100),
  country VARCHAR(100),
  postal_code VARCHAR(30),
  logo_url VARCHAR(500),
  verified BOOLEAN NOT NULL DEFAULT FALSE,
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE organization_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  member_role VARCHAR(50),
  department VARCHAR(150),
  designation VARCHAR(150),
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(organization_id, user_id)
);

CREATE TABLE student_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  institution_id UUID REFERENCES organizations(id),
  enrollment_number VARCHAR(100),
  branch VARCHAR(150),
  degree VARCHAR(150),
  semester INTEGER,
  current_year INTEGER,
  graduation_year INTEGER,
  cgpa NUMERIC(4,2),
  career_summary TEXT,
  career_interests JSONB NOT NULL DEFAULT '[]',
  preferred_locations JSONB NOT NULL DEFAULT '[]',
  open_to_remote BOOLEAN NOT NULL DEFAULT TRUE,
  profile_completion_percent INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE academician_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  institution_id UUID REFERENCES organizations(id),
  employee_number VARCHAR(100),
  department VARCHAR(150),
  designation VARCHAR(150),
  specialization VARCHAR(255),
  experience_years NUMERIC(5,2),
  research_interests JSONB NOT NULL DEFAULT '[]',
  bio TEXT,
  profile_completion_percent INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE industry_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  organization_id UUID REFERENCES organizations(id),
  department VARCHAR(150),
  designation VARCHAR(150),
  expertise JSONB NOT NULL DEFAULT '[]',
  bio TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(150) NOT NULL UNIQUE,
  description TEXT,
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category_id UUID REFERENCES skill_categories(id),
  name VARCHAR(150) NOT NULL,
  description TEXT,
  skill_type VARCHAR(50),
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(category_id, name)
);

CREATE TABLE user_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id),
  proficiency_level VARCHAR(30) NOT NULL,
  proficiency_score NUMERIC(5,2),
  years_experience NUMERIC(5,2),
  source VARCHAR(50) NOT NULL DEFAULT 'SELF_DECLARED',
  verified BOOLEAN NOT NULL DEFAULT FALSE,
  last_assessed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, skill_id)
);

CREATE TABLE assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  target_role VARCHAR(150),
  assessment_type VARCHAR(50) NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_by_user_id UUID REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assessment_questions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
  skill_id UUID REFERENCES skills(id),
  question_text TEXT NOT NULL,
  question_type VARCHAR(50) NOT NULL,
  display_order INTEGER NOT NULL,
  required BOOLEAN NOT NULL DEFAULT TRUE,
  weight NUMERIC(5,2) NOT NULL DEFAULT 1,
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assessment_question_options (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question_id UUID NOT NULL REFERENCES assessment_questions(id) ON DELETE CASCADE,
  option_text TEXT NOT NULL,
  score NUMERIC(5,2),
  display_order INTEGER NOT NULL
);

CREATE TABLE assessment_attempts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID NOT NULL REFERENCES assessments(id),
  user_id UUID NOT NULL REFERENCES users(id),
  status VARCHAR(30) NOT NULL DEFAULT 'NOT_STARTED',
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  overall_score NUMERIC(5,2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assessment_answers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  attempt_id UUID NOT NULL REFERENCES assessment_attempts(id) ON DELETE CASCADE,
  question_id UUID NOT NULL REFERENCES assessment_questions(id),
  selected_option_ids JSONB NOT NULL DEFAULT '[]',
  text_answer TEXT,
  rating_value NUMERIC(5,2),
  calculated_score NUMERIC(5,2)
);

CREATE TABLE opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  created_by_user_id UUID NOT NULL REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  opportunity_type VARCHAR(50) NOT NULL,
  description TEXT NOT NULL,
  department VARCHAR(150),
  location VARCHAR(255),
  work_mode VARCHAR(30),
  duration_text VARCHAR(100),
  stipend_amount NUMERIC(12,2),
  currency VARCHAR(10) DEFAULT 'INR',
  application_deadline TIMESTAMPTZ,
  start_date DATE,
  end_date DATE,
  eligibility_criteria TEXT,
  min_cgpa NUMERIC(4,2),
  openings_count INTEGER,
  status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE opportunity_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id),
  required_level VARCHAR(30),
  importance VARCHAR(30) NOT NULL DEFAULT 'MEDIUM',
  required BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE(opportunity_id, skill_id)
);

CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  document_type VARCHAR(50) NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  file_url VARCHAR(1000),
  mime_type VARCHAR(100),
  file_size_bytes BIGINT,
  verified BOOLEAN NOT NULL DEFAULT FALSE,
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id),
  applicant_user_id UUID NOT NULL REFERENCES users(id),
  resume_document_id UUID REFERENCES documents(id),
  cover_letter TEXT,
  application_data JSONB NOT NULL DEFAULT '{}',
  applied_at TIMESTAMPTZ,
  status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
  status_updated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(opportunity_id, applicant_user_id)
);

CREATE TABLE application_status_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  old_status VARCHAR(50),
  new_status VARCHAR(50) NOT NULL,
  remarks TEXT,
  changed_by_user_id UUID REFERENCES users(id),
  changed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE learning_programs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_organization_id UUID REFERENCES organizations(id),
  created_by_user_id UUID REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  program_type VARCHAR(50) NOT NULL,
  duration_text VARCHAR(100),
  delivery_mode VARCHAR(30),
  external_url VARCHAR(500),
  certificate_available BOOLEAN NOT NULL DEFAULT FALSE,
  cost_amount NUMERIC(12,2),
  currency VARCHAR(10) DEFAULT 'INR',
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE learning_program_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  learning_program_id UUID NOT NULL REFERENCES learning_programs(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id),
  skill_level VARCHAR(30),
  UNIQUE(learning_program_id, skill_id)
);

CREATE TABLE portfolio_projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  project_type VARCHAR(50),
  start_date DATE,
  end_date DATE,
  repository_url VARCHAR(500),
  project_url VARCHAR(500),
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  visibility VARCHAR(30) NOT NULL DEFAULT 'PUBLIC',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES portfolio_projects(id) ON DELETE CASCADE,
  skill_id UUID NOT NULL REFERENCES skills(id),
  UNIQUE(project_id, skill_id)
);

CREATE TABLE certifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  issuing_organization VARCHAR(255),
  credential_id VARCHAR(255),
  credential_url VARCHAR(500),
  issue_date DATE,
  expiry_date DATE,
  verified BOOLEAN NOT NULL DEFAULT FALSE,
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE collaborations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  host_organization_id UUID NOT NULL REFERENCES organizations(id),
  partner_organization_id UUID REFERENCES organizations(id),
  created_by_user_id UUID REFERENCES users(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  collaboration_type VARCHAR(50) NOT NULL,
  location VARCHAR(255),
  meeting_url VARCHAR(500),
  start_date DATE,
  end_date DATE,
  max_participants INTEGER,
  status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE collaboration_participants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  collaboration_id UUID NOT NULL REFERENCES collaborations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id),
  participant_role VARCHAR(50) NOT NULL DEFAULT 'PARTICIPANT',
  status VARCHAR(30) NOT NULL DEFAULT 'REGISTERED',
  joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(collaboration_id, user_id)
);

CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  recommendation_type VARCHAR(50) NOT NULL,
  target_entity_type VARCHAR(50) NOT NULL,
  target_entity_id UUID,
  score NUMERIC(5,2),
  reason TEXT,
  generated_by VARCHAR(50) NOT NULL DEFAULT 'RULE_ENGINE',
  status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
  generated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE career_readiness_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_role VARCHAR(150),
  overall_score NUMERIC(5,2),
  technical_score NUMERIC(5,2),
  soft_skill_score NUMERIC(5,2),
  experience_score NUMERIC(5,2),
  portfolio_score NUMERIC(5,2),
  assessment_score NUMERIC(5,2),
  calculation_version VARCHAR(50),
  calculated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

# 17. Recommended Indexes

```sql
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_organizations_type ON organizations(organization_type);
CREATE INDEX idx_organization_members_user ON organization_members(user_id);
CREATE INDEX idx_student_profiles_institution ON student_profiles(institution_id);
CREATE INDEX idx_skills_category ON skills(category_id);
CREATE INDEX idx_user_skills_user ON user_skills(user_id);
CREATE INDEX idx_user_skills_skill ON user_skills(skill_id);
CREATE INDEX idx_assessment_attempts_user ON assessment_attempts(user_id);
CREATE INDEX idx_opportunities_org ON opportunities(organization_id);
CREATE INDEX idx_opportunities_type_status ON opportunities(opportunity_type, status);
CREATE INDEX idx_opportunities_deadline ON opportunities(application_deadline);
CREATE INDEX idx_opportunity_skills_skill ON opportunity_skills(skill_id);
CREATE INDEX idx_applications_user ON applications(applicant_user_id);
CREATE INDEX idx_applications_opportunity ON applications(opportunity_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_projects_user ON portfolio_projects(user_id);
CREATE INDEX idx_certifications_user ON certifications(user_id);
CREATE INDEX idx_collaborations_host ON collaborations(host_organization_id);
CREATE INDEX idx_recommendations_user_type ON recommendations(user_id, recommendation_type);
CREATE INDEX idx_readiness_user ON career_readiness_scores(user_id);
```

# 18. FastAPI Project Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── organization.py
│   │   ├── profile.py
│   │   ├── skill.py
│   │   ├── assessment.py
│   │   ├── opportunity.py
│   │   ├── application.py
│   │   ├── learning_program.py
│   │   ├── portfolio.py
│   │   ├── collaboration.py
│   │   ├── recommendation.py
│   │   └── career_readiness.py
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── api/
│   │   └── v1/
│   └── tests/
├── alembic/
├── requirements.txt
└── README.md
```

Recommended libraries:

```text
FastAPI
SQLAlchemy 2.x
Alembic
Pydantic v2
psycopg
pytest
```

# 19. React Project Structure

```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   │   ├── common/
│   │   ├── layout/
│   │   └── forms/
│   ├── features/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── profiles/
│   │   ├── skills/
│   │   ├── assessments/
│   │   ├── opportunities/
│   │   ├── applications/
│   │   ├── learning/
│   │   ├── portfolio/
│   │   ├── collaboration/
│   │   └── dashboard/
│   ├── hooks/
│   ├── routes/
│   ├── store/
│   ├── types/
│   ├── utils/
│   └── App.jsx
└── package.json
```

Frontend feature modules should align with backend domain modules.

# 20. Phase 1 CRUD API Scope

## Users

```text
GET    /api/v1/users
POST   /api/v1/users
GET    /api/v1/users/{id}
PUT    /api/v1/users/{id}
DELETE /api/v1/users/{id}
```

## Organizations

```text
GET    /api/v1/organizations
POST   /api/v1/organizations
GET    /api/v1/organizations/{id}
PUT    /api/v1/organizations/{id}
DELETE /api/v1/organizations/{id}
```

## Profiles

```text
GET/POST/PUT /api/v1/student-profiles
GET/POST/PUT /api/v1/academician-profiles
GET/POST/PUT /api/v1/industry-profiles
```

## Skills

```text
GET/POST/PUT/DELETE /api/v1/skill-categories
GET/POST/PUT/DELETE /api/v1/skills

GET  /api/v1/users/{user_id}/skills
POST /api/v1/users/{user_id}/skills
PUT  /api/v1/users/{user_id}/skills/{id}
DELETE /api/v1/users/{user_id}/skills/{id}
```

## Assessments

```text
GET/POST/PUT       /api/v1/assessments
GET/POST/PUT/DELETE /api/v1/questions
POST/GET/PUT       /api/v1/assessment-attempts
```

## Opportunities

```text
GET/POST/PUT/DELETE /api/v1/opportunities
GET/POST            /api/v1/opportunities/{id}/skills
```

Required filters:

```text
type
status
organizationId
location
workMode
skillId
page
pageSize
```

## Applications

```text
GET/POST/PUT /api/v1/applications
GET          /api/v1/applications/{id}/history
```

## Learning

```text
GET/POST/PUT/DELETE /api/v1/learning-programs
```

## Portfolio

```text
GET/POST/PUT/DELETE /api/v1/projects
GET/POST/PUT/DELETE /api/v1/certifications
GET/POST/DELETE     /api/v1/documents
```

## Collaborations

```text
GET/POST/PUT/DELETE /api/v1/collaborations
POST/GET            /api/v1/collaborations/{id}/participants
```

# 21. Phase 1 Implementation Order

## Priority 1 – Foundation

```text
Database
Users
Roles
Organizations
Organization Membership
Profiles
Authentication-ready security structure
```

## Priority 2 – Skill Foundation

```text
Skill Categories
Skills
User Skills
```

## Priority 3 – Assessment

```text
Assessments
Questions
Options
Attempts
Answers
```

## Priority 4 – Opportunities

```text
Opportunities
Opportunity Skills
Applications
Application History
```

## Priority 5 – Portfolio & Learning

```text
Projects
Project Skills
Certifications
Documents
Learning Programs
Learning Program Skills
```

## Priority 6 – Collaboration

```text
Collaborations
Participants
```

## Priority 7 – Future Persistence

```text
Recommendations
Career Readiness Scores
```

# 22. Future Phases

## Phase 2 – Workflows

- Registration workflow
- Profile completion workflow
- Assessment completion workflow
- Opportunity publishing workflow
- Application workflow
- Application status transitions
- Collaboration participation workflow
- Basic notifications

## Phase 3 – Rules and Matching

- Skill-gap calculation
- Rule-based opportunity matching
- Skill compatibility score
- Learning recommendations
- Career readiness calculation
- Explainable recommendations

## Phase 4 – AI

- LLM-assisted career guidance
- AI skill extraction
- AI-generated skill-gap explanations
- Intelligent opportunity recommendations
- Natural language profile assistance

## Phase 5 – Integrations

- Learning platforms
- Certification providers
- Institution databases
- Object/document storage
- Email notifications
- Calendar integration

## Phase 6 – Analytics

- Student readiness dashboards
- Institution skill-gap analytics
- Placement analytics
- Industry demand trends
- Collaboration metrics

# 23. Code Generation Requirements

The generated application MUST:

1. Use SQLAlchemy ORM models.
2. Use Alembic migrations.
3. Use Pydantic request/response schemas.
4. Separate API, service and repository layers.
5. Use UUID identifiers.
6. Implement foreign key relationships.
7. Enforce unique constraints.
8. Return correct HTTP status codes.
9. Support pagination.
10. Support basic filtering.
11. Validate input.
12. Add CORS for React.
13. Generate OpenAPI docs.
14. Add seed/demo data.
15. Keep APIs modular.
16. Do not implement AI logic yet.
17. Do not tightly couple CRUD models to future AI.
18. Keep service interfaces extensible.

Seed data should include:

```text
Roles
Skill Categories
Skills
1 Institution
3 Sample Industries
Students
Academicians
Industry Users
Opportunities
Learning Programs
Collaborations
Assessment Template
Assessment Questions
```

# 24. Final Prompt for Code Generation

Use this document as the authoritative technical blueprint for TalentSync Phase 1.

Generate:

```text
FRONTEND
- React.js
- Feature-based modular architecture
- Role-aware navigation
- CRUD screens
- Forms
- Tables
- Search and filtering
- Pagination
- API integration

BACKEND
- FastAPI
- SQLAlchemy 2.x
- Pydantic v2
- Alembic migrations
- PostgreSQL
- REST APIs
- Layered architecture
- OpenAPI documentation

DATABASE
- Implement Phase 1 tables
- Foreign keys
- Unique constraints
- Indexes
- Seed data
```

Important constraint:

> Build Phase 1 as a clean CRUD foundation, while preserving the ability to add workflows, AI, recommendations, analytics and third-party integrations later without redesigning the core schema.

Core objective:

```text
Correct Domain Model
+
Clean Relationships
+
Stable Database Schema
+
Extensible APIs
+
Modular Architecture
=
Strong TalentSync Foundation
```
