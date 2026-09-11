# TalentSync – High Level Design, Domain Model & PostgreSQL Schema
## Foundational CRUD Implementation Blueprint
**Stack: React.js + FastAPI + PostgreSQL**

---

# 0. Architect Review Notes (v2)

Reviewed against `sih-story.md`, the pitch deck (`ppt-images.png`) and the UI mocks (`ui-images.png`). The v1 domain model and DDL are solid — normalized, UUID-based, cleanly layered, and genuinely future-proof for AI/recommendation phases. The tech stack (React + FastAPI + PostgreSQL + AWS) is kept as-is; changes below are additive libraries/patterns on top of it, not a stack change.

**Gaps found (things the UI/pitch already promise but v1 schema has no model for):**

1. **Notifications** — Screen 15 of the UI mock is a full notification center (application/opportunity/system, read/unread), but v1 has no `notifications` table anywhere, not even as a "future" placeholder like recommendations. Added as a Phase-1-ready table (Section 14A).
2. **Search** — Screen 5 shows a search box over internships/jobs. At institution/industry scale, `ILIKE` scans on `opportunities` won't hold up. Added a generated `tsvector` column + GIN index (Postgres full-text search — no new infra needed yet).
3. **Auth token lifecycle & security** — The doc says "authentication-ready" but never models it. For a platform explicitly pitched on "Strong authentication & data encryption" (Slide 3), you need revocable refresh tokens and password-reset tokens, not just a `password_hash` column. Added `refresh_tokens` and `password_reset_tokens` tables.
4. **Audit trail** — Beyond `application_status_history`, there's no generic audit log for who changed what (opportunity edits, profile verification, admin actions). Added a lightweight `audit_logs` table — important once Institution Admins and Platform Admins can act on other users' data.
5. **Destructive cascades on business records** — `ON DELETE CASCADE` from `users` wipes `applications`, `assessment_attempts`, `documents`, etc. That's fine for a throwaway account, but it silently destroys placement/analytics history the institution dashboards (Screens 12–13) depend on. Recommended a soft-delete (`deleted_at`) convention for record-of-truth tables instead of hard cascade deletes.
6. **File upload path** — "Resume download / digital portfolio" is core Phase-1 UI (Screen 7), not a future integration, but the doc defers all storage. Clarified that Phase 1 should wire real S3 (or MinIO locally) with presigned URLs — `documents.file_url` needs somewhere real to point to from day one.
7. **Read-heavy aggregate dashboards** — Screens 12–13 (institution placement trends, skill distribution donut) aggregate across potentially thousands of rows. Running that live against OLTP tables on every page load doesn't scale. Added materialized views + a refresh strategy instead of ad-hoc COUNT/GROUP BY on request.
8. **No background job story** — sending notifications, refreshing the above materialized views, and (later) generating recommendations all need an async worker, or they'll block request/response cycles. Added Redis + a lightweight async task queue to the architecture diagram.
9. **No observability** — the pitch deck's own methodology (Slide 2, step 5: "Monitor & Improve") isn't reflected anywhere in the technical doc. Added a short NFR section covering logging, health checks, and metrics.
10. **Institution ↔ Industry "partnership" vs. one-off collaboration** — the Institution Dashboard mock shows a persistent "Industry Partners: 32" count, which is a different concept from a time-boxed `collaboration` (mentorship/workshop/etc.). Clarified this is derived from distinct organization pairs across collaborations/opportunities rather than a new table — noted explicitly so it isn't reinvented ad hoc later.

None of these require touching the existing tables' shapes — they're additive, which preserves the "don't redesign the core schema later" goal already stated in the doc.

---

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
React.js (Vite + TypeScript)
   │ REST/JSON
   ▼
FastAPI
   ├── API
   ├── Services
   ├── Repositories
   └── SQLAlchemy ORM
          │
          ├──────────────▶ PostgreSQL (system of record)
          │
          ├──────────────▶ Redis (cache + rate limiting + job broker)
          │                     │
          │                     ▼
          │              Async Worker (arq/Celery)
          │              - notification dispatch
          │              - materialized view refresh
          │              - future: recommendation jobs
          │
          └──────────────▶ S3 (resumes, certificates, logos — via presigned URLs)
```

Use a modular monolith. Redis and the async worker are lightweight additions (not a services split) — they run as a second small process against the same codebase, so the monolith boundary is unchanged. This keeps Phase 1 deployable as "one API + one worker + Postgres + Redis," which is still simple to run on a single AWS environment (e.g., ECS with two task definitions) while leaving room to scale the worker independently later.

# 2A. Non-Functional Requirements & Cross-Cutting Concerns

These apply across every module below and should be scaffolded in Phase 1, even though most of the *content* they protect (recommendations, analytics, integrations) lands in later phases.

## Security
- Password hashing via `argon2` (preferred) or `bcrypt` — never store or log raw passwords.
- Access tokens: short-lived JWT (15–30 min). Refresh tokens: opaque, stored hashed in `refresh_tokens`, revocable (needed because JWTs alone can't be invalidated on logout/compromise).
- Password reset via single-use, expiring tokens in `password_reset_tokens` — never email a raw reusable link with no expiry.
- All file uploads (resumes, certificates, logos) go directly to S3 via presigned URLs; FastAPI never proxies binary payloads through the request/response cycle.
- Rate limiting on auth endpoints and public opportunity/search endpoints (`slowapi`, backed by Redis) to blunt credential stuffing and scraping.
- Field-level encryption is not needed for Phase 1 (no PII beyond standard profile data); rely on TLS in transit and AWS-managed encryption at rest (RDS/S3 SSE).

## Auditability
- `audit_logs` captures who changed what on sensitive entities (opportunity edits, application status changes, verification actions, admin overrides) — separate from `application_status_history`, which is domain-specific.
- Soft delete (`deleted_at TIMESTAMPTZ NULL`) on record-of-truth tables (`applications`, `assessment_attempts`, `documents`, `certifications`, `portfolio_projects`) instead of `ON DELETE CASCADE`, so institution/industry analytics and placement history survive account deactivation. `users` and `organizations` should also soft-delete (flip `status` to `INACTIVE`) rather than hard-delete.

## Performance & Scalability
- Read-heavy dashboard aggregates (institution skill distribution, placement trends, industry demand trends) should be served from materialized views refreshed on a schedule or on write-trigger, not computed live from OLTP tables per request.
- Full-text search on `opportunities` (title/description) via a generated `tsvector` column + GIN index — avoids `ILIKE '%...%'` table scans as the opportunity catalog grows.
- Redis cache for frequently-read, slow-changing reference data (skills list, skill categories, published opportunity listings) with short TTLs.
- Connection pooling via SQLAlchemy's pool settings tuned for the deployment (or PgBouncer in front of RDS once concurrent connections grow beyond a few dozen).
- Pagination is mandatory on every list endpoint (already specified) — cap `pageSize` server-side (e.g., max 100) regardless of what the client requests.

## Observability
- Structured JSON logging (`structlog`) with request IDs, so logs are traceable per request across API → service → repository.
- `/health` and `/ready` endpoints for load balancer checks.
- Basic metrics (request latency, error rate, queue depth) exported for CloudWatch — this is what actually implements the "Monitor & Improve" step already promised in the pitch deck's methodology slide.

## Extensibility
- Service layer methods should accept/return domain objects, not ORM models directly, so a future AI/recommendation service can call into (e.g.) `SkillService.get_gap(user_id)` without depending on FastAPI or SQLAlchemy internals.
- New `opportunity_type` / `collaboration_type` / `document_type` values are additive VARCHAR values (already the doc's convention) — no migration needed to introduce new categories.

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

# 14A. Notifications Domain (New in v2)

The UI mock's "Notifications" screen (application status changes, new matching opportunities, scheduled workshops, system messages) needs a persisted table now — this is Phase 1 UI, not a Phase 5 integration. Actual delivery channels (email/push/SMS) stay a later phase; this table is just the in-app notification feed and its read state.

## notifications

```text
id
user_id               FK → users
notification_type
title
body
related_entity_type
related_entity_id
action_url
read
read_at
created_at
```

notification_type:

```text
APPLICATION_STATUS
NEW_OPPORTUNITY_MATCH
OPPORTUNITY_DEADLINE
COLLABORATION_INVITE
LEARNING_PROGRAM_UPDATE
SYSTEM
```

Relationship:

```text
User 1 → * Notifications
```

Notifications are written synchronously by the service layer on the triggering event (e.g., `ApplicationService.update_status()` also calls `NotificationService.create(...)`) and, from Phase 2 onward, fanned out to email/push by the async worker reading a lightweight outbox rather than blocking the request.

## Institution ↔ Industry Partnership (clarification, not a new table)

The Institution Dashboard mock's "Industry Partners: 32" is a **derived count**, not a new persisted relationship: it's the distinct set of `organizations` an institution's students/academicians have an active `collaboration` or `opportunity.applications` history with. Modeling it as a first-class `institution_industry_partners` table would duplicate what's already derivable and risks the two going out of sync. If a future requirement needs a formal MOU/partnership status (e.g., "verified partner" badge, contract dates) independent of any activity, add a dedicated table then — don't pre-build it speculatively now.

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
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

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
  deleted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- New in v2: revocable refresh tokens + single-use password reset tokens
CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(255) NOT NULL UNIQUE,
  issued_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ,
  replaced_by_token_id UUID REFERENCES refresh_tokens(id),
  user_agent VARCHAR(255),
  ip_address VARCHAR(64)
);

CREATE TABLE password_reset_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(255) NOT NULL UNIQUE,
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- New in v2: generic audit trail for admin/sensitive actions (distinct from application_status_history)
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_user_id UUID REFERENCES users(id),
  entity_type VARCHAR(50) NOT NULL,
  entity_id UUID NOT NULL,
  action VARCHAR(50) NOT NULL,
  before_data JSONB,
  after_data JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
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
  deleted_at TIMESTAMPTZ,
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
  deleted_at TIMESTAMPTZ,
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
  updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- New in v2: generated full-text search column, populated automatically by Postgres
  search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description, '')), 'B')
  ) STORED
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
  deleted_at TIMESTAMPTZ,
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
  deleted_at TIMESTAMPTZ,
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
  deleted_at TIMESTAMPTZ,
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
  deleted_at TIMESTAMPTZ,
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

# 16A. Additional DDL — Notifications & Dashboard Materialized Views (New in v2)

```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  notification_type VARCHAR(50) NOT NULL,
  title VARCHAR(255) NOT NULL,
  body TEXT,
  related_entity_type VARCHAR(50),
  related_entity_id UUID,
  action_url VARCHAR(500),
  read BOOLEAN NOT NULL DEFAULT FALSE,
  read_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Institution dashboard: skill distribution donut (Screen 13)
CREATE MATERIALIZED VIEW mv_institution_skill_distribution AS
SELECT
  sp.institution_id,
  sc.name AS skill_category,
  COUNT(DISTINCT us.user_id) AS student_count
FROM student_profiles sp
JOIN user_skills us ON us.user_id = sp.user_id
JOIN skills s ON s.id = us.skill_id
JOIN skill_categories sc ON sc.id = s.category_id
WHERE sp.institution_id IS NOT NULL
GROUP BY sp.institution_id, sc.name;

CREATE UNIQUE INDEX idx_mv_institution_skill_distribution
  ON mv_institution_skill_distribution(institution_id, skill_category);

-- Institution dashboard: placement trends over time (Screen 12)
CREATE MATERIALIZED VIEW mv_institution_placement_trends AS
SELECT
  sp.institution_id,
  date_trunc('year', a.status_updated_at) AS period,
  COUNT(*) FILTER (WHERE a.status IN ('SELECTED', 'OFFERED', 'COMPLETED')) AS placements
FROM applications a
JOIN student_profiles sp ON sp.user_id = a.applicant_user_id
WHERE a.deleted_at IS NULL
GROUP BY sp.institution_id, date_trunc('year', a.status_updated_at);

CREATE UNIQUE INDEX idx_mv_institution_placement_trends
  ON mv_institution_placement_trends(institution_id, period);

-- Refresh strategy: schedule via the async worker (e.g. every 15–30 min), not per-request.
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_institution_skill_distribution;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_institution_placement_trends;
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

-- New in v2
CREATE INDEX idx_opportunities_search_vector ON opportunities USING GIN(search_vector);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, read, created_at DESC);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE UNIQUE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);
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
│   │   ├── cache.py            # New in v2: Redis client
│   │   ├── storage.py          # New in v2: S3 presigned URL helper
│   │   ├── logging.py          # New in v2: structlog setup
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
│   │   ├── notification.py     # New in v2
│   │   ├── audit_log.py        # New in v2
│   │   ├── recommendation.py
│   │   └── career_readiness.py
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── api/
│   │   └── v1/
│   ├── workers/                # New in v2: async job entrypoints
│   │   ├── worker.py
│   │   ├── notification_jobs.py
│   │   └── refresh_view_jobs.py
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
pydantic-settings
psycopg
pytest / pytest-asyncio / httpx (test client)

# New in v2
argon2-cffi              # password hashing
python-jose[cryptography] # JWT signing/verification
redis                    # cache + rate limiting + job broker
arq                      # lightweight async-native job queue (fits FastAPI's async model
                         # better than Celery, which is thread/process-based)
boto3                    # S3 presigned URLs for resumes/certificates/logos
slowapi                  # rate limiting middleware
structlog                # structured logging
faker / factory_boy      # seed & test data generation
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
│   │   ├── notifications/      # New in v2
│   │   └── dashboard/
│   ├── hooks/
│   ├── routes/
│   ├── store/
│   ├── types/
│   ├── utils/
│   └── App.tsx
└── package.json
```

Frontend feature modules should align with backend domain modules.

Recommended libraries (added on top of the existing React.js choice, not a stack change):

```text
TypeScript              # the UI already models ~16 distinct screens with structured data
                        # (skill scores, application status, analytics) — types catch
                        # cross-feature drift as the app grows; plain JS won't scale here.
Vite                    # faster dev/build than CRA, which is unmaintained
React Router v6         # role-aware routing (Student/Academician/Industry/Institution dashboards)
TanStack Query          # server-state caching/invalidation for API data — avoids hand-rolled
                        # loading/error/refetch logic in every feature module
Zustand (or Redux Toolkit if the team prefers more structure)  # client-only UI state
React Hook Form + Zod   # the multi-step forms in the mocks (Skill Assessment wizard,
                        # Post Opportunity 3-step form) need this more than plain state
Recharts or Chart.js    # institution analytics screens (skill donut, placement trend line)
```

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

## Notifications (New in v2)

```text
GET  /api/v1/notifications              (filters: read, type; paginated)
POST /api/v1/notifications/{id}/read
POST /api/v1/notifications/read-all
```

## Search (New in v2)

```text
GET /api/v1/opportunities/search?q=...  (uses opportunities.search_vector, same pagination/filter contract as the list endpoint)
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
Authentication: password hashing, JWT access tokens, refresh_tokens,
  password_reset_tokens (New in v2 — was vaguely "authentication-ready" in v1)
S3 presigned upload flow for documents (New in v2 — needed for resume/certificate
  upload, which is core Phase-1 UI, not a later integration)
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

## Priority 6A – Notifications & Search (New in v2)

```text
Notifications table + read/unread endpoints
Opportunity full-text search (search_vector + GIN index)
audit_logs wired into opportunity/application/verification write paths
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
19. Use soft delete (`deleted_at`) on `applications`, `assessment_attempts`, `documents`, `certifications`, `portfolio_projects`, `users`, `organizations` — never hard-delete via cascade on these.
20. Upload files (resumes, certificates, logos) directly to S3 via presigned URLs; the API only stores/returns metadata.
21. Write to `notifications` from the service layer whenever an application status changes, an opportunity match is created, or a collaboration invite is sent.
22. Write to `audit_logs` for admin/verification/status-change actions on opportunities, applications, and organization membership.
23. Scaffold (but don't over-build) the async worker process and Redis connection now, even if its only Phase-1 job is notification writes and materialized view refresh — retrofitting a job queue later is more disruptive than the schema changes it was meant to avoid.

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
Sample Notifications (New in v2 — at least one per notification_type, so the
  notification screen isn't empty on first demo run)
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
- Implement Phase 1 tables (including notifications, refresh_tokens,
  password_reset_tokens, audit_logs — New in v2)
- Foreign keys
- Unique constraints
- Indexes (including the search_vector GIN index)
- Materialized views for institution dashboard aggregates
- Soft-delete columns on record-of-truth tables
- Seed data

WORKER
- Minimal async worker (arq) wired to Redis for notification writes and
  scheduled materialized view refresh
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
