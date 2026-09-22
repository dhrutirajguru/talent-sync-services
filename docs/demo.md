# Demo recording script: Flows A, B, C

A script for the video submitted to judges. It runs the three live flows defined in
[`design-anthropic.md` Section 6.1](design-anthropic.md) end to end, on the real deployed
backend and real seeded data, in one continuous recording: Student (Flow A), Industry (Flow B),
Academician (Flow C), stitched together by the one shared moment that makes it read as one
platform rather than three demos: a student applies, and the industry recruiter sees that
applicant appear.

Everything in this script is against the live deployment and has been verified against the
actual seeded data (exact match percentages below), not assumed.

## Before you record

1. **Reset applications to empty**, so the "apply, then see it on the industry side" moment is
   clean. Applications are currently empty on a fresh seed; if you have re-recorded and
   generated test applications, clear them first:

   ```bash
   ssh -i talentsync-demo.pem ubuntu@3.225.213.152
   cd app
   sudo docker compose -f docker-compose.prod.yml exec -T postgres \
     psql -U talentsync -d talentsync -c "TRUNCATE applications, application_status_history;"
   ```

2. **Use an incognito/private window**, so no leftover login session or cached UI state shows
   up on camera.
3. **Confirm the live site loads** before you hit record: `https://dhrutirajguru.github.io/`
   (also mirrored at `https://dhrutirajguru.github.io/talentsync/`, same build, either works).
   If GitHub Pages or the EC2 instance is flaky on the day, have a `npm run dev` local instance
   pointed at the same backend as a fallback (fastest fix: nothing to redeploy, just switch the
   URL you're recording).
4. **Zoom/scale your browser** so text is legible at the recording resolution; hide bookmarks
   bar and any dev tools.
5. Decide narration approach: live voiceover while screen recording is simplest and most
   reliable for a hackathon deadline; record video first and narrate over it in a second pass
   only if you want tighter pacing.

## Cast

All seeded accounts share the password `Demo@1234` (see [`demo-users.md`](demo-users.md) for
the full roster). This script uses:

| Role | Account | Why this one |
|---|---|---|
| Student | `aarav.sharma@niat.edu.in` | Data Analyst track: Python, SQL, Data Analysis, MS Excel, Statistics all ADVANCED. Matches Vertex's "Data Analyst Intern" at 5/5 required skills, a clean 100% top match to show live scoring working correctly. |
| Industry | `recruiter@vertexanalytics.io` | Posts to the same skill pool Aarav matches; already has 2 live postings seeded, so "post a new one" reads as adding a third, not conjuring a company from nothing. |
| Academician | `academician@niat.edu.in` | Dr. Anjali Mehta, tied to the one seeded institution all 6 students belong to, so the skill-gap report has real signal. |

Verified scoring, so you know exactly what will appear on screen:

- **Data Analyst Intern** (Vertex) requires Statistics, MS Excel, Python, SQL, Data Analysis.
  Aarav: 5/5 (100%). Meera: 3/5 (60%). Ishita: 2/5 (40%). Kabir: 1/5 (20%). Diya/Rohan: 0%.
- **Institution skill gap**: `REST API Design` is required (HIGH importance) by the Full Stack
  Developer Intern posting and held by zero of the 6 seeded students, so it should surface as
  the top gap, exactly as called out in `demo-users.md`.

## Narrative arc (suggested opening line)

> "TalentSync connects students, industry, and academic institutions on one platform. What
> you're about to see is running against a real Postgres database and a real FastAPI backend,
> not mock data: a student's applications, an industry's ranked candidates, and an
> institution's skill-gap report all come from the same live matching engine, viewed from three
> different angles."

That framing matters: say once, near the start, that this is real data and a real scoring
engine, not a static prototype, then let the flows demonstrate it rather than repeating the
claim.

## Segment 1: Flow A, Student (about 100 seconds)

1. Go to `https://dhrutirajguru.github.io/`, log in as `aarav.sharma@niat.edu.in`.
2. **Dashboard**: point out the skill profile is real (seeded, but genuinely stored and read
   from `user_skills`), not hardcoded in the UI.
3. **Skill Assessment**: open this screen and click through the quiz to "Generate My Skill
   Profile." This is a good moment to state the one deliberate shortcut in the demo, since it's
   a design choice worth owning rather than a gap to be caught later:

   > "This questionnaire is a mock: it doesn't compute a score yet. What's real is where it
   > lands you, the skill profile it would produce is already seeded and live on the next
   > screen."

   Submitting it navigates straight to Skill Mapping, which reinforces that line visually.
4. **Skill Mapping / edit skills**: show the current skill list. Optionally add or adjust one
   skill live to prove it round-trips to the database (a small, real edit), then navigate back
   to Dashboard to show the number changed.
5. **Opportunities**: go to Recommended Opportunities. Call out the ranked list, and that Data
   Analyst Intern is the top match. Say the scoring rule out loud, since it's meant to be
   explainable on stage:

   > "The match score is the overlap between the skills this posting requires and the skills
   > Aarav has: right now that's five out of five, a 100% match."

6. **Apply**: click Apply on Data Analyst Intern. Confirm it submits.
7. Go to **Applications**, show it now listed under "Submitted."

## Segment 2: bridge (about 15 seconds)

Log out, log in as `recruiter@vertexanalytics.io`. Say the bridging line:

> "Now switching to the company side. Vertex Analytics posted that internship. Here's what
> they see the moment a student applies."

## Segment 3: Flow B, Industry (about 90 seconds)

1. **Dashboard**: point out it shows Vertex's existing postings (2, before you add a third).
2. **Post a new opportunity**: fill the form with required skills (e.g. a short posting like
   "Business Analyst Intern" with 2 to 3 required skills), submit.
3. **My Opportunities**: show the count went from 2 to 3.
4. **Candidates**: open Data Analyst Intern's candidate list. Point at Aarav at the top, and
   that his application (from Segment 1) is right there:

   > "This is the same overlap score, from the recruiter's side: Aarav ranks highest because he
   > has all five required skills. And because he just applied, he's already in this list, not
   > a separate mock candidate feed."

5. Optionally scroll to show Meera/Ishita/Kabir ranked below him at their real, lower scores, to
   demonstrate the ranking isn't just showing one hardcoded "winner."

## Segment 4: bridge (about 10 seconds)

Log out, log in as `academician@niat.edu.in`.

> "Same matching engine, third angle: the institution's view."

## Segment 5: Flow C, Academician (about 60 seconds)

1. **Dashboard**: point out the real student count (6) and the headline skill gap.
2. **Skill Gap Report**: show the full ranked list. Call out `REST API Design` at the top,
   required by a live posting and held by zero students right now, and say what that number
   means in plain terms:

   > "This aggregates every skill required across live postings against what our students
   > actually have. Nothing here is precomputed for the demo: it's the same scoring approach as
   > the student and industry views, aggregated per institution instead of per user."

## Optional: quick static-screen sweep (about 20 seconds, trim-safe)

The rest of the nav (Digital Portfolio, Learning Programs, Industry Collaboration, Institution
Analytics, Notifications, Profile) is real, designed UI backed by mock or partly-mock data, not
generic "coming soon" placeholders. A brief sweep of one or two of these adds visual proof the
platform is fully designed end to end, without claiming they're live:

- From the student side: **Digital Portfolio** blends Aarav's real skills (live query) with mock
  projects and certifications, a nice visual note if you have time for it.
- From the academician side: **Institution Analytics** has real-looking stat cards and charts
  (placement trends, skill distribution).

Narrate it plainly if you include it:

> "The rest of the platform, portfolio, learning programs, collaboration, institution analytics,
> is fully designed in the UI, running on mock data behind the same API client interface. Wiring
> each of these to live logic is a fixture-to-endpoint swap, not a rebuild."

## Closing line (about 15 seconds)

Be upfront about scope, since judges will ask anyway and it reads better coming from you first:

> "Everything you just saw, login, skill profiles, matching, applications, and the skill-gap
> report, is running live. The rest of the platform is scaffolded in the UI and schema but
> intentionally not wired to live logic yet: that's exactly where Phase 1 picks up."

## Total runtime target

About 4.5 to 5.5 minutes end to end (add ~20 seconds if you include the optional static-screen
sweep). If you're cutting for time, Segment 1 steps 3 to 4 (assessment beat and skill edit) and
Segment 3 step 5 (scrolling the full ranked list) are the safest trims, along with the entire
optional sweep above; the apply-to-candidates bridge (Segment 1 steps 6/7 through Segment 3
step 4) is the connective tissue that makes this read as one platform and should not be cut.

## If something goes wrong on camera

- **A request fails or is slow**: the API is on a t2.micro; a cold request after idle time can
  be slower than local dev. Pause, refresh once, resume narration; don't try to talk over a
  spinner.
- **Login fails**: double-check you're not still on a stale session in the same tab; use a
  fresh incognito window per role switch rather than logging out in place, to avoid any stale
  client-side auth state.
- **Wrong ranking shows up**: means applications or seed data drifted from a previous take; re-run
  the reset command above and, if needed, re-run the seed script:
  `sudo docker compose -f docker-compose.prod.yml exec api python -m app.seed`.
