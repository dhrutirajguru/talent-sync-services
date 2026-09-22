## Idea Title

TalentSync – Closing India's Skill Gap Through Unified Academia-Industry Matching

## Idea Description

### The Problem, at Scale
India's own employability data shows the gap this problem statement is trying to close: the Wheebox India Skills Report 2025 found employability among Indian graduates reached 54.81 per cent — meaning roughly 45 out of every 100 graduating students are not considered industry-ready at the point of graduation. This isn't a talent shortage; it's a visibility shortage — students don't know which specific skills close that gap for their target role, and institutions have no live signal telling them where their curriculum is falling behind industry demand until placement season already shows the damage. 
morungexpress

### Proposed Solution
TalentSync closes that visibility gap with one shared skill graph across three stakeholders, instead of three disconnected systems. A rule-based matching engine scores fit in every direction: opportunities ranked for students by real skill overlap, candidates ranked for recruiters the same way, and — because the same data already exists — an institution-level skill-gap report generated for academicians with zero extra data entry.

### Key Features (implemented in this prototype)

- Student: live skill profile, opportunities ranked by match score across every registered organization, one-click apply, application tracking.
- Industry: post roles with weighted required skills, see the entire student pool ranked by fit for that exact role, view who applied.
- Academician: a skill-gap report showing precisely which industry-demanded skills their student body is short on — turning a national 45%-employability-gap statistic into an actionable, per-skill, per-institution number.
- Role-based JWT authentication; Student, Academician, and Industry as independently onboarded user types.
- Supporting modules (skill assessment, digital portfolio, learning programs, industry collaboration, notifications) are UI-complete and architected to plug into live endpoints in the next phase.

### Projected Impact

- Time-to-shortlist: manual resume screening for a single internship posting typically takes recruiters hours across dozens of applicants; ranked candidate matching in this prototype returns a scored, sorted list instantly, for any number of applicants.
- Curriculum feedback loop: today, institutions learn about a skills mismatch only when placement outcomes lag — often a full academic year too late. TalentSync's skill-gap report gives that signal continuously, in real time, per skill.
- Reach per institution: the underlying schema is built to scale to an institution's full student body (the design targets institutions with 1,000+ students) and an unlimited number of partner companies on one shared skill taxonomy — not a one-to-one placement-cell relationship.
- Demonstrated in this prototype: 3 industry organizations, 6 students with distinct skill profiles, 5 live postings, and a matching engine computing real scores on every request against a live PostgreSQL database — not pre-scripted demo data.

### Technology Stack
React (TypeScript, Vite) frontend with role-driven navigation; FastAPI (Python) backend in a layered API → services → repositories architecture; PostgreSQL schema spanning 30+ tables across skills, opportunities, applications, organizations, collaboration, learning, and portfolio domains — designed upfront for the full platform, not just this prototype. Container-ready for AWS (ECS/RDS/S3/ElastiCache) deployment at production scale.

### Uniqueness
Most placement portals are job boards with a resume upload bolted on. TalentSync's differentiator is a single skill-matching engine serving all three stakeholders — so one improvement benefits everyone simultaneously — and an institution-level skill-gap report that costs zero additional faculty effort because it's derived, not surveyed.

### Feasibility & Current Status
Working prototype, not a mockup: live backend, real database, realistic seeded data, and all three core user journeys functioning end-to-end today. Remaining modules are UI-complete with mock data shaped to match the real API contract, so scaling to full functionality requires no frontend rework — the platform is designed to grow from this exact foundation.

## Abstract/Summary

TalentSync is a unified Academia-Industry Collaboration Portal built to close a gap that national data confirms is real: India Skills Report 2025 puts graduate employability at just 54.81 per cent, leaving nearly half of graduating students without a clear, actionable view of what industry actually needs from them. 
morungexpress

TalentSync fixes this with one shared skill-matching engine serving three stakeholders from three angles: students get opportunities ranked by real skill fit across every registered organization; recruiters get every candidate ranked by fit for their specific posting, replacing hours of manual screening with an instant, scored shortlist; and academicians get a live, zero-effort skill-gap report showing exactly which industry-demanded skills their students are missing — turning a lagging, once-a-year placement statistic into a continuous, per-skill signal.

Built on React (TypeScript), FastAPI, and PostgreSQL with a production-scale architecture from day one, TalentSync is demonstrated here as a functioning prototype — live backend, live database, real-time matching across three working user journeys — with a clear, already-designed path to its remaining modules: AI-assisted skill assessment, verified digital portfolios, and structured industry collaboration.

A few notes on what I did and didn't do here: the 54.81%/45% figure is a real, cited statistic (Wheebox India Skills Report 2025). The "Projected Impact" numbers (instant vs. hours, continuous vs. once-a-year, 1,000+ student scale) are framed as projections/design targets, not measured results — because this prototype hasn't been in production long enough to measure them, and I don't want to hand the judges a claim that falls apart under questioning. If you want punchier numbers, I'd suggest running a quick timed comparison yourself (e.g., actually time how long it takes to manually rank your 6 seeded students against a posting vs. the instant API response) — that gives you a real, defensible number instead of an estimate.