# CareerGraph AI — Backend

Real-time career intelligence platform backend, built for the SerpApi India
Hackathon 2026. SerpApi is the core, real-time data source — the primary
workflow never uses fake/mock job data.

> **Status: Stage 5 (final) of the build plan.** The full backend is
> implemented: real SerpApi Google Jobs integration, rule-based skill
> extraction, transparent market analysis, skill-gap scoring, per-job
> match scoring, roadmap/project/resource generation, JWT auth, and
> persistence (users, profiles, saved roadmaps).

## Stage 5 — what's implemented (new this stage)

- **`app/database/session.py`** + **`app/models/*.py`** — SQLAlchemy 2.0
  models (`User`, `Profile`, `SavedRoadmap`). Works out of the box with
  SQLite for local dev; point `DATABASE_URL` at a Postgres/Supabase
  connection string (`postgresql+psycopg://...`) for production with no
  code changes. Tables are created automatically on startup (no
  migrations framework for this MVP -- see "Known limitations").
- **`app/core/security.py`** — password hashing (passlib `pbkdf2_sha256`)
  and JWT issuance/verification (`python-jose`). `hashed_password` is
  never included in any API response.
- **`POST /api/auth/register`**, **`POST /api/auth/login`**,
  **`GET /api/auth/me`** — register auto-logs-in (returns a token
  immediately); duplicate emails are rejected (409); wrong credentials
  return 401.
- **`GET /api/profile`** / **`PUT /api/profile`** — persisted user
  profile (target career, experience level, location, skills). `PUT`
  supports partial updates (only sends fields change). An unset profile
  is a normal `200` with empty fields, not a `404`.
- **`POST /api/roadmap/generate`** now accepts an *optional* Bearer
  token: anonymous callers still get a full roadmap (nothing is gated
  behind login), but if authenticated, the result is persisted and the
  response includes `saved: true` + `roadmap_id`.
- **`GET /api/roadmap`** is now fully implemented (no longer a 501 stub):
  requires auth, returns the user's most recently generated roadmap, or a
  clear `404` if they haven't generated one yet.
- 21 new tests across `test_auth_api.py`, `test_profile_api.py`, and
  `test_roadmap_persistence.py` (using an isolated in-memory SQLite DB
  per test via `tests/conftest.py`) — **78 tests total, all passing.**

## Stage 4 — what's implemented (new this stage)

- **`app/services/ai_service.py`** — pluggable AI provider abstraction.
  Defaults to `AI_PROVIDER=none` (a `NullAIProvider` that always signals
  "unavailable"), so the product is fully functional with zero AI
  configuration and zero AI cost — perfect for a hackathon demo/judging
  environment. Set `AI_PROVIDER=anthropic` + `AI_API_KEY` to enable a real
  Anthropic-backed provider that enriches roadmap summaries; if it fails
  or times out for any reason, the app **falls back to the deterministic
  rule-based output** rather than erroring or fabricating text.
- **`app/services/roadmap_service.py`** — deterministic, documented
  algorithm that turns a `skill_gap` into learning phases (priority
  skills first, chunked into phases, with a final "Portfolio & Job
  Search" phase always included). AI (if configured) only enriches the
  free-text summary — never the phase structure.
- **`app/services/project_service.py`** — rule-based project
  recommendations from a curated template library (~13 common skills),
  with a sensible generic fallback template for any skill not in the
  library, so no skill is ever left without a suggestion.
- **`app/services/resource_service.py`** — real learning resources via
  SerpApi Google Search (`"learn {skill} tutorial for beginners"`).
  **No fabricated links, ever**: if SerpApi returns nothing for a skill,
  that skill is skipped with an explicit warning instead.
- **`POST /api/roadmap/generate`** — takes a `skill_gap` (from
  `/api/careers/analyze` or `/api/analysis/skill-gap`) and returns a full
  `roadmap` + `projects` + `resources` payload, matching the shape those
  fields have in the `/api/careers/analyze` response. Deliberately kept
  separate from `/api/careers/analyze` so the core analyze call stays
  fast — this endpoint does the heavier SerpApi + optional-AI work only
  when explicitly requested.
- **`GET /api/roadmap`** — stub that returns `501 Not Implemented` with a
  clear explanation (retrieving a *saved* roadmap needs user accounts +
  persistence, landing in Stage 5) rather than pretending to have data it
  doesn't.
- **`GET /api/resources?skill=...`** — standalone real-resource lookup
  for a single skill, independent of the roadmap flow.
- 22 new tests across `test_ai_service.py`, `test_roadmap_service.py`,
  `test_project_service.py`, `test_resource_service.py`, and
  `test_roadmap_and_resources_api.py` — 57 tests total, all passing.

## Stage 3 — what's implemented (new this stage)

- **`app/services/job_matching_service.py`** — transparent per-job match
  score. Formula (documented in the module docstring):

  ```
  required_skills   = job.detected_skills
  matched_skills    = required_skills ∩ user_skills   (case-insensitive, normalized)
  missing_skills    = required_skills - matched_skills
  match_percentage  = round(len(matched_skills) / len(required_skills) * 100, 1)
  ```

  If a job has **zero** detected skills (e.g. no usable description text),
  `match_percentage` is left `None` with an explanatory `match_note` —
  never fabricated as 0% or 100%.
- `POST /api/careers/analyze` now returns a real `match_percentage`,
  `matched_skills`, and `missing_skills` for every job, and the `jobs`
  array is **sorted by match percentage descending** (jobs with no
  computable score sort last).
- New standalone endpoint: `POST /api/analysis/job-match` — score a
  single job's detected skills against a user's skills, independent of
  the full SerpApi pipeline.
- 8 new tests (`test_job_matching_service.py` + 2 new endpoint tests) — 35
  tests total, all passing.

## Stage 2 — what's implemented (new this stage)

- **`app/services/skill_extraction_service.py`** — rule-based (no LLM)
  skill extraction/normalization over a ~65-skill taxonomy. Handles
  variations like `ML` → `Machine Learning`, `Py Torch` → `PyTorch`,
  `python programming` → `Python`, `k8s` → `Kubernetes`, etc.
- **`app/services/market_analysis_service.py`** — computes skill
  frequency + percentage across the analyzed job sample, with the formula
  documented in the module docstring (a skill mentioned in 46 of 50 jobs
  = 92%). Each skill counts at most once per job.
- **`app/services/skill_gap_service.py`** — transparent, documented
  scoring: `strong_skills` (user already has), `missing_skills` (high
  market demand, user lacks), `develop_skills` (moderate demand, user
  lacks), `priority_skills` (top 5 missing by demand). Explicitly does
  **not** claim to predict hiring outcomes — see `scoring_note` in every
  response.
- **`POST /api/careers/analyze`** now returns real `market.skills` and a
  real `skill_gap`, plus `detected_skills` per job showing exactly what
  was extracted from that listing's text.
- **New standalone endpoints** so the frontend can use these building
  blocks independently of the full SerpApi pipeline:
  - `POST /api/analysis/skills` — extract skills from arbitrary text
  - `POST /api/analysis/market` — compute market analysis from a list of
    job description texts
  - `POST /api/analysis/skill-gap` — score a skill gap from user skills +
    market skill data
- 20 new tests (`test_skill_extraction_service.py`,
  `test_market_analysis_service.py`, `test_skill_gap_service.py`, plus
  additions to `test_careers_analyze.py`) — 27 tests total, all passing.

## Stage 1 — what's implemented

- FastAPI app (`app/main.py`) with CORS for a local React dev frontend,
  health checks, and centralized logging.
- `app/services/serpapi_service.py` — the **only** module allowed to talk to
  SerpApi. Supports `google_jobs`, `google`, `google_scholar`, `google_news`
  engines, with retries, timeouts, a simple TTL cache, and clear error
  types. The API key is read from `SERPAPI_API_KEY` and is never included
  in any response.
- `app/services/job_normalization_service.py` — turns SerpApi's raw
  `jobs_results` into a consistent internal `NormalizedJob` shape.
- `app/services/career_service.py` — orchestrates the request → SerpApi →
  normalization → response pipeline for `POST /api/careers/analyze`.
- `app/api/careers.py` — the route itself, plus a small `GET /api/careers`
  suggestion list for a frontend dropdown.
- Basic in-process rate limiting (`app/core/rate_limiter.py`) and caching
  (`app/services/cache_service.py`) — simple building blocks, swappable for
  Redis later without touching calling code.
- Tests in `tests/test_careers_analyze.py` (SerpApi calls mocked with
  `respx`, so tests are fast/free and don't require a real API key).

## Project structure

```
backend/
  app/
    main.py                  # FastAPI app entrypoint, lifespan (creates DB tables)
    api/
      careers.py              # /api/careers routes
      analysis.py              # /api/analysis/* (skills, market, skill-gap, job-match)
      roadmap.py                # /api/roadmap/generate, GET /api/roadmap
      resources.py               # /api/resources
      auth.py                     # /api/auth/register, /login, /me
      profile.py                   # /api/profile
    services/
      serpapi_service.py      # SerpApi integration (ONLY module that calls SerpApi)
      job_normalization_service.py
      career_service.py       # orchestration for /api/careers/analyze
      cache_service.py        # simple TTL cache
      skill_extraction_service.py # rule-based skill taxonomy/normalization
      market_analysis_service.py  # skill frequency/percentage
      skill_gap_service.py        # transparent skill-gap formula
      job_matching_service.py     # transparent per-job match formula
      ai_service.py                # pluggable AI provider abstraction
      roadmap_service.py            # rule-based roadmap + optional AI enrichment
      project_service.py             # rule-based project recommendations
      resource_service.py             # real resources via SerpApi google_search
    models/
      user.py                  # SQLAlchemy User model
      profile.py                 # SQLAlchemy Profile model
      saved_roadmap.py             # SQLAlchemy SavedRoadmap model
    schemas/
      career.py                # Pydantic schemas for /api/careers/*
      analysis.py                # schemas for /api/analysis/*
      roadmap.py                   # schemas for /api/roadmap/*
      auth.py                        # schemas for /api/auth/*
      profile.py                       # schemas for /api/profile
    database/
      session.py                # SQLAlchemy engine/session/get_db/init_db
    core/
      config.py                # env-var driven settings
      logging_config.py
      rate_limiter.py
      security.py                # password hashing, JWT, auth dependencies
    utils/
  tests/
    conftest.py               # isolated in-memory-SQLite DB fixture (db_client)
    test_careers_analyze.py
    test_*_service.py          # unit tests per service
    test_auth_api.py
    test_profile_api.py
    test_roadmap_persistence.py
  requirements.txt
  .env.example
  README.md
```

## Setup

1. **Python 3.11+** and a virtualenv are recommended.

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables.**

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and set a real key:

   ```
   SERPAPI_API_KEY=your_real_serpapi_key
   ```

   Get a key at https://serpapi.com/manage-api-key (the hackathon likely
   provides one, or use SerpApi's free tier for testing).

   Also set a real `JWT_SECRET_KEY` (used to sign auth tokens) -- any long
   random string works for a hackathon build, e.g.:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

3. **Run the server.**

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. **Open the interactive API docs:** http://localhost:8000/docs
   (Swagger/OpenAPI, generated automatically by FastAPI.)

## Testing

Run the automated test suite (SerpApi is mocked, no real key/network
needed):

```bash
pytest -q
```

### Manually test the priority endpoint with a REAL SerpApi request

With a real `SERPAPI_API_KEY` set in `.env` and the server running:

```bash
curl -X POST http://localhost:8000/api/careers/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "target_career": "AI Engineer",
    "skills": ["Python", "React", "JavaScript", "Git"],
    "experience_level": "Beginner",
    "location": "India"
  }'
```

#### Example response (Stage 3 shape)

`roadmap`, `projects`, and `resources` are still placeholders (later
stages). `market`, `skill_gap`, and each job's `detected_skills` /
`match_percentage` / `matched_skills` / `missing_skills` are all now real,
computed from the live SerpApi data. Jobs are sorted by match percentage
descending.

```json
{
  "career": "AI Engineer",
  "market": {
    "sample_size": 23,
    "skills": [
      { "skill": "Python", "frequency": 21, "percentage": 91.3 },
      { "skill": "Machine Learning", "frequency": 14, "percentage": 60.9 },
      { "skill": "Docker", "frequency": 9, "percentage": 39.1 }
    ]
  },
  "skill_gap": {
    "strong_skills": ["Python", "Git"],
    "develop_skills": ["SQL"],
    "missing_skills": ["Machine Learning", "Docker", "PyTorch"],
    "priority_skills": ["Machine Learning", "Docker", "PyTorch"],
    "scoring_note": "Skills are compared by name only (not proficiency depth). ... This does NOT predict whether you will get hired."
  },
  "jobs": [
    {
      "job_id": "eyJqb2JfdGl0bG...",
      "title": "AI Engineer - Entry Level",
      "company_name": "Example Corp",
      "location": "Bengaluru, Karnataka, India",
      "via": "via LinkedIn",
      "posted_at": "3 days ago",
      "apply_link": "https://...",
      "detected_skills": ["Python", "Machine Learning", "Docker"],
      "match_percentage": 66.7,
      "matched_skills": ["Python", "Machine Learning"],
      "missing_skills": ["Docker"],
      "match_note": null
    }
  ],
  "roadmap": null,
  "projects": [],
  "resources": [],
  "warnings": []
}
```

If SerpApi returns zero jobs for the query, `jobs` will be `[]`,
`market.sample_size` will be `0`, and `warnings` will explain why — the
API never invents fake listings, fake skills, or fake match scores to
fill the gap.

### Roadmap, projects & resources (Stage 4)

```bash
curl -X POST http://localhost:8000/api/roadmap/generate \
  -H "Content-Type: application/json" \
  -d '{
    "target_career": "AI Engineer",
    "experience_level": "Beginner",
    "skill_gap": {
      "strong_skills": ["Python"],
      "develop_skills": ["SQL"],
      "missing_skills": ["Docker", "Machine Learning"],
      "priority_skills": ["Docker", "Machine Learning"],
      "scoring_note": "..."
    },
    "include_resources": true,
    "max_resources_per_skill": 2
  }'
```

```json
{
  "roadmap": {
    "summary": "Based on 1 skill(s) you already have and 3 market-demanded skill(s) you don't yet list, here is a beginner-friendly path toward AI Engineer...",
    "phases": [
      { "phase_number": 1, "title": "Phase 1: Build Docker", "duration_weeks": 4, "focus_skills": ["Docker", "Machine Learning"], "description": "Learn and practice: Docker, Machine Learning." },
      { "phase_number": 2, "title": "Phase 2: Core Skills", "duration_weeks": 3, "focus_skills": ["SQL"], "description": "Learn and practice: SQL." },
      { "phase_number": 3, "title": "Phase 3: Portfolio & Job Search", "duration_weeks": 3, "focus_skills": ["Docker", "Machine Learning"], "description": "Build 1-2 portfolio projects..." }
    ],
    "generated_by": "rule_based"
  },
  "projects": [
    { "title": "Containerize an Existing App", "description": "...", "skills_used": ["Docker"], "difficulty": "Beginner" },
    { "title": "End-to-End ML Classifier", "description": "...", "skills_used": ["Machine Learning", "Python"], "difficulty": "Intermediate" }
  ],
  "resources": [
    { "skill": "Docker", "title": "Get Started | Docker Docs", "link": "https://docs.docker.com/get-started/", "source": "docs.docker.com" }
  ],
  "warnings": []
}
```

```bash
curl "http://localhost:8000/api/resources?skill=PyTorch&limit=3"
```

### Auth & profile (Stage 5)

```bash
# Register (returns a token immediately -- no separate login needed)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"supersecret123","full_name":"Your Name"}'
# {"access_token": "...", "token_type": "bearer", "user": {"id":1,"email":"you@example.com",...}}

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"supersecret123"}'

# Use the token for authenticated requests
TOKEN="paste-your-access_token-here"

curl http://localhost:8000/api/auth/me -H "Authorization: Bearer $TOKEN"

curl -X PUT http://localhost:8000/api/profile \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"target_career":"AI Engineer","experience_level":"Beginner","location":"India","skills":["Python","Git"]}'

curl http://localhost:8000/api/profile -H "Authorization: Bearer $TOKEN"
```

Passing the same `Authorization: Bearer $TOKEN` header on
`POST /api/roadmap/generate` persists the result, and
`GET /api/roadmap -H "Authorization: Bearer $TOKEN"` retrieves the most
recent one:

```bash
curl -X POST http://localhost:8000/api/roadmap/generate \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"target_career":"AI Engineer","experience_level":"Beginner","skill_gap":{"strong_skills":["Python"],"develop_skills":["SQL"],"missing_skills":["Docker"],"priority_skills":["Docker"],"scoring_note":"..."},"include_resources":false}'
# {"roadmap": {...}, "projects": [...], "resources": [], "warnings": [], "saved": true, "roadmap_id": 1}

curl http://localhost:8000/api/roadmap -H "Authorization: Bearer $TOKEN"
```

### Enabling real AI enrichment (optional)

By default `AI_PROVIDER=none` and the roadmap summary is entirely
rule-based (no AI cost, no AI dependency). To enable AI-enriched summaries:

```
AI_PROVIDER=anthropic
AI_API_KEY=your_anthropic_key
AI_MODEL=claude-3-5-haiku-20241022
```

If the AI call fails for any reason (bad key, timeout, rate limit), the
response silently falls back to the rule-based summary and adds a note to
`warnings` -- it never blocks the request or fabricates output.

### Standalone analysis endpoints

```bash
curl -X POST http://localhost:8000/api/analysis/skills \
  -H "Content-Type: application/json" \
  -d '{"text": "Looking for Python, Docker and ML experience."}'
# {"skills": ["Machine Learning", "Docker", "Python"]}

curl -X POST http://localhost:8000/api/analysis/market \
  -H "Content-Type: application/json" \
  -d '{"job_descriptions": ["Python and Docker required.", "Python only."]}'

curl -X POST http://localhost:8000/api/analysis/skill-gap \
  -H "Content-Type: application/json" \
  -d '{"user_skills": ["Python"], "market_skills": [{"skill":"Python","frequency":10,"percentage":100.0},{"skill":"Docker","frequency":8,"percentage":80.0}]}'

curl -X POST http://localhost:8000/api/analysis/job-match \
  -H "Content-Type: application/json" \
  -d '{"job_detected_skills": ["Python","Git","PyTorch","Docker"], "user_skills": ["Python","Git"]}'
# {"match_percentage": 50.0, "matched_skills": ["Python","Git"], "missing_skills": ["PyTorch","Docker"], "match_note": null}
```

## Known limitations

- `/api/careers/analyze` itself still leaves `roadmap`/`projects`/
  `resources` as `null`/`[]` by design — call `POST /api/roadmap/generate`
  with the `skill_gap` it returns to get those, kept separate so the core
  analyze call stays fast.
- AI enrichment is optional and off by default (`AI_PROVIDER=none`); the
  roadmap summary is rule-based unless you configure a real provider, and
  always falls back to rule-based if the AI call fails for any reason.
- Match scoring, skill-gap scoring, and resource discovery are keyword/
  name-based or real-search-based — none of it predicts hiring outcomes,
  and every response says so (`scoring_note` / `match_note`).
- The skill taxonomy (~65 skills) is curated for common software/AI/ML
  roles. Niche or very new skills not in the list are still preserved in
  `normalize_skill_list` output (never dropped), but won't be recognized
  inside free-text job descriptions until added to the taxonomy in
  `skill_extraction_service.py`.
- No migrations framework (Alembic) is set up — tables are created via
  `Base.metadata.create_all()` on startup. Fine for a hackathon MVP and
  for adding new tables/columns during development; a real production
  deployment with existing data would want Alembic migrations instead.
- Password hashing uses passlib's `pbkdf2_sha256` (pure-Python, no native
  extension version issues) rather than bcrypt — a deliberate MVP choice,
  swappable in `core/security.py` in one line.
- The rate limiter and cache are simple in-process implementations,
  intended for the MVP/single-instance hackathon deployment, not
  multi-instance production scale.
- `GET /api/jobs/search`, `GET /api/jobs/{job_id}` are not implemented —
  job data is currently only reachable via `/api/careers/analyze`.
- No password-reset, email-verification, or refresh-token flow — a single
  long-lived access token (24h default) issued at register/login.

## Build stages (all complete)

1. ✅ **Stage 1** — FastAPI + real SerpApi Google Jobs integration,
   `POST /api/careers/analyze`.
2. ✅ **Stage 2** — Rule-based skill extraction, transparent market
   analysis, documented skill-gap scoring.
3. ✅ **Stage 3** — Transparent per-job match scoring.
4. ✅ **Stage 4** — AI service abstraction + roadmap/project/resource
   generation.
5. ✅ **Stage 5** — JWT auth, SQLAlchemy models (users, profiles, saved
   roadmaps), profile persistence, roadmap persistence.
6. Full test coverage + final documentation pass.
