# CareerGraph AI

**Live career intelligence from the job market.**
See where the market is going. Discover where you stand. Build the path to get there.

CareerGraph AI turns real, current job postings into a personal action plan. You enter a target career, your skills, your experience level, and (optionally) a location. It searches live job listings, measures which skills employers are asking for right now, compares them to yours, scores every job against your profile, and generates a learning roadmap, project ideas, and resources to close the gaps.

---

## Table of contents

- [What it does](#what-it-does)
- [How SerpApi is used](#how-serpapi-is-used)
- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Try a sample analysis](#try-a-sample-analysis)
- [How the numbers are calculated](#how-the-numbers-are-calculated)
- [API overview](#api-overview)
- [AI usage](#ai-usage)
- [Testing](#testing)
- [Security notes](#security-notes)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)

---

## What it does

1. **Searches live job listings** for your target career using SerpApi's Google Jobs engine.
2. **Extracts the skills** those listings ask for, using a rule-based skill taxonomy (no LLM needed). Variants are normalized, for example `ML` becomes `Machine Learning` and `Py Torch` becomes `PyTorch`.
3. **Measures market demand.** Each skill gets a frequency and a percentage of the analyzed jobs.
4. **Finds your skill gap.** Your skills are sorted into strong, develop, missing, and priority.
5. **Scores every job** with a match percentage, listing matched and missing skills per posting, with a link to apply.
6. **Builds an action plan.** A phased roadmap, project ideas that target your priority gaps, and learning resources found through live search.

The core idea: **Live Market -> Your Skill Profile -> Skill Gap -> Recommended Action.**

### Principles

- **No fabricated data.** Empty results, missing fields, and partial failures show honest empty states and warnings. If a job has too little text to score, the UI says "Match score unavailable" instead of showing a made-up number.
- **No hiring predictions.** Every score measures skill-name overlap with a sample of live listings. It does not predict whether anyone will be hired, and the app says so.
- **Rule-based first, AI optional.** Everything works with no AI provider configured.

### Features

User accounts (register, login, profile), protected routes, a dashboard, market intelligence charts, skill-gap analysis with a priority-skill breakdown, live job matching, a roadmap timeline, project recommendations, a learning-resources page, saved roadmaps, loading and error states throughout, and a responsive layout with mobile navigation.

---

## How SerpApi is used

SerpApi is called **only by the backend**. The frontend never holds a SerpApi key and never calls SerpApi directly.

| SerpApi engine | Used for | In the user-facing flow? |
|---|---|---|
| Google Jobs | Live job listings. This is the data source behind every market percentage, skill gap, and job match. | Yes |
| Google Search | Finding learning resources for priority skills. | Yes |
| Google Scholar | Research and emerging-technology signals. | Supported in the service layer, not yet surfaced in the UI |
| Google News | Industry trend articles. | Supported in the service layer, not yet surfaced in the UI |

All SerpApi access goes through one module, `careergraph-backend/app/services/serpapi_service.py`, which handles retries, timeouts, error mapping, and a 30-minute response cache so repeated identical searches don't burn quota.

---

## Architecture

```
 Browser (React + Vite)
        |
        |  HTTPS / JSON   (JWT in Authorization header)
        v
 FastAPI backend  --------------------------->  SerpApi
        |             Google Jobs / Search      (the only caller)
        |
        +--> Rule-based services
        |      skill extraction -> market analysis -> skill gap -> job matching
        |      roadmap / project / resource generation
        |
        +--> SQLAlchemy (SQLite in dev, Postgres/Supabase-ready)
        |      users, profiles, saved roadmaps
        |
        +--> Optional AI provider (off by default)
```

Layers are kept separate: external API logic (`serpapi_service`) is isolated from business logic (extraction, analysis, scoring), which is isolated from the HTTP layer.

---

## Repository layout

```
.
├── README.md
├── careergraph-backend/          FastAPI service
│   ├── app/
│   │   ├── main.py               App entrypoint, CORS, routers
│   │   ├── api/                  Route handlers (careers, analysis, roadmap, resources, auth, profile)
│   │   ├── services/             serpapi, skill extraction, market analysis, skill gap,
│   │   │                         job matching, roadmap, projects, resources, AI abstraction, cache
│   │   ├── models/               SQLAlchemy models
│   │   ├── schemas/              Pydantic request/response models
│   │   ├── database/             Engine and session setup
│   │   └── core/                 Settings, security (JWT), logging, rate limiter
│   ├── tests/                    pytest suite (SerpApi mocked)
│   ├── requirements.txt
│   └── .env.example
└── careergraph-frontend/         React single-page app
    ├── src/
    │   ├── api/                  Axios client and per-domain API modules
    │   ├── context/              Auth, analysis, and toast state
    │   ├── components/           UI kit, layout, charts, roadmap components
    │   ├── pages/                Landing, auth, onboarding, dashboard, market, jobs, ...
    │   └── test/                 Vitest suite
    ├── package.json
    └── .env.example
```

---

## Quick start

### Prerequisites

- Python 3.11 or newer
- Node.js 18.18 or newer (tested on Node 22)
- A SerpApi key from <https://serpapi.com/manage-api-key>

### 1. Backend

```bash
cd careergraph-backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set SERPAPI_API_KEY and JWT_SECRET_KEY (see Configuration)

uvicorn app.main:app --reload --port 8000
```

The API is now at <http://localhost:8000> and interactive Swagger docs are at <http://localhost:8000/docs>. Database tables are created automatically on startup.

### 2. Frontend

In a second terminal:

```bash
cd careergraph-frontend
npm install
cp .env.example .env                 # defaults to http://localhost:8000/api
npm run dev
```

Open <http://localhost:5173>.

---

## Configuration

### Backend (`careergraph-backend/.env`)

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SERPAPI_API_KEY` | **Yes** | none | Your SerpApi key. Backend only; never sent to the browser. |
| `JWT_SECRET_KEY` | **Yes** (change it) | placeholder | Signs login tokens. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(48))"`. |
| `CORS_ORIGINS` | No | `http://localhost:3000,http://localhost:5173` | Comma-separated list of allowed frontend origins. Add your deployed URL here. |
| `DATABASE_URL` | No | `sqlite:///./careergraph_dev.db` | Use `postgresql+psycopg://user:pass@host:5432/db` for Postgres or Supabase. |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | `1440` | Token lifetime (24 hours). |
| `SERPAPI_CACHE_TTL_SECONDS` | No | `1800` | How long identical SerpApi searches are cached. |
| `SERPAPI_TIMEOUT_SECONDS` / `SERPAPI_MAX_RETRIES` | No | `20` / `2` | SerpApi request behavior. |
| `RATE_LIMIT_REQUESTS` / `RATE_LIMIT_WINDOW_SECONDS` | No | `30` / `60` | Per-IP rate limit on the heavier endpoints. |
| `AI_PROVIDER` | No | `none` | `none` or `anthropic`. See [AI usage](#ai-usage). |
| `AI_API_KEY` / `AI_MODEL` | No | empty | Only needed if `AI_PROVIDER` is not `none`. |

### Frontend (`careergraph-frontend/.env`)

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `VITE_API_BASE_URL` | No | `http://localhost:8000/api` | Base URL of the backend API. |

`.env` files are git-ignored. The `.env.example` files contain placeholders only.

---

## Try a sample analysis

With both servers running:

1. Open <http://localhost:5173> and click **Analyze My Career**.
2. Register an account (any email, password of 8+ characters).
3. On the onboarding form, enter:
   - Target career: `AI Engineer`
   - Skills: `Python`, `React`, `JavaScript`, `Git`
   - Experience: `Beginner`
   - Location: `India`
4. Submit. After the loading sequence you land on the **Dashboard** with live market data, your skill gap, and matched jobs.
5. Visit **Market Intelligence**, **Skill Gap**, and **Jobs** from the sidebar.
6. Open **Roadmap** and click **Generate My Roadmap**. **Projects** and **Resources** then fill in.

You can also call the API directly:

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

Results come from live data, so exact numbers will vary by day.

---

## How the numbers are calculated

All scoring is transparent and deterministic. The formulas are documented in the source and echoed in the UI.

**Market demand** (`market_analysis_service.py`)

```
frequency(skill)  = number of analyzed jobs that mention the skill (counted once per job)
percentage(skill) = round(frequency / sample_size * 100, 1)
```

If Python appears in 46 of 50 jobs, it shows as 92.0%.

**Skill gap** (`skill_gap_service.py`)

| Category | Rule |
|---|---|
| Strong | A market skill you already listed. |
| Missing | A market skill you don't have, appearing in 30% or more of jobs. |
| Develop | A market skill you don't have, appearing in 10-30% of jobs. |
| Priority | The top 5 missing skills by demand. |

Skills below 10% are ignored as noise.

**Job match** (`job_matching_service.py`)

```
required_skills  = skills detected in that job's listing text
matched_skills   = required_skills that you have
match_percentage = round(len(matched) / len(required) * 100, 1)
```

If a listing has no detectable skills, the score is left empty (`null`) with an explanatory note, rather than shown as 0% or 100%.

---

## API overview

Base path: `/api`. Full interactive docs at `/docs`.

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | No | Health check |
| GET | `/careers` | No | Suggested target careers |
| POST | `/careers/analyze` | No | Live job search, market analysis, skill gap, job matches |
| POST | `/analysis/skills` | No | Extract skills from text |
| POST | `/analysis/market` | No | Market analysis for supplied job descriptions |
| POST | `/analysis/skill-gap` | No | Skill-gap scoring from supplied data |
| POST | `/analysis/job-match` | No | Score one job against a skill list |
| POST | `/roadmap/generate` | Optional | Roadmap, projects, resources. Saved server-side if a token is sent. |
| GET | `/roadmap` | Yes | Your most recently saved roadmap |
| GET | `/resources?skill=` | No | Learning resources for one skill (live search) |
| POST | `/auth/register` | No | Create an account, returns a token |
| POST | `/auth/login` | No | Sign in, returns a token |
| GET | `/auth/me` | Yes | Current user |
| GET / PUT | `/profile` | Yes | Read or update your saved profile |

---

## AI usage

- **Building the project:** the code was written with the help of an AI coding assistant (Claude by Anthropic), then run, tested, and reviewed.
- **Inside the product:** an optional AI provider layer exists in `ai_service.py`. It is **off by default** (`AI_PROVIDER=none`). When enabled, it only rewrites the short summary at the top of a roadmap. It does not produce market data, skill percentages, job matches, skill gaps, roadmap phases, or project recommendations. If the AI call fails, the app falls back to the rule-based summary.

---

## Testing

```bash
# Backend: 78 tests, SerpApi fully mocked, no key or .env needed
cd careergraph-backend
pytest -q

# Frontend: 87 tests, lint, and production build
cd careergraph-frontend
npm test
npm run lint
npm run build
```

The backend suite sets its own dummy SerpApi settings, so it passes on a fresh clone and is unaffected by your real `.env`.

---

## Security notes

- The SerpApi key and JWT secret live only in the backend environment and are never returned in any response.
- Passwords are hashed (PBKDF2-SHA256) and never returned by the API.
- The frontend stores only the login token (in `localStorage`) and the current analysis (in `sessionStorage`). Logging out clears both.
- External job and resource links open with `rel="noopener noreferrer"`.
- Before deploying, set a strong `JWT_SECRET_KEY` and restrict `CORS_ORIGINS` to your real frontend URL.

---

## Known limitations

- **The market sample is one page of Google Jobs results** (typically around 10 listings), so percentages describe that sample and not the whole market.
- **The skill taxonomy covers about 65 common software and AI skills.** Skills outside it are kept in your profile but won't be detected inside job text until added.
- **Skills are matched by name, not proficiency.** "Beginner Python" and "5 years of Python" both count as Python.
- **Job description wording varies.** Some listings have too little text to score; those show "Match score unavailable".
- **Short or ambiguous terms** (for example `RAG` or `React`) are matched by pattern and can occasionally over-match.
- **Auth is basic:** one 24-hour token, with no refresh tokens, password reset, or email verification.
- **No migrations framework.** Tables are created on startup with `create_all`. Fine for development; use Alembic before running against real data.
- **The current analysis is not stored on the server.** It lives in the browser session. Roadmaps are saved server-side for logged-in users, and restored on login if nothing is cached locally.
- **The planned `GET /api/jobs/search` and `GET /api/jobs/{job_id}` endpoints were not built.** Jobs are returned inside the analyze response.
- **Google Scholar and Google News** are implemented in the SerpApi service but not yet shown in the UI.
- **The frontend is a single JavaScript bundle** with no code-splitting yet.
- **Responsive layouts were reviewed in code**, not screenshot-tested at every breakpoint. Spot-check on a real device before a demo.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Analyze returns a warning like "Could not retrieve live job data" | `SERPAPI_API_KEY` is missing or invalid, or your SerpApi quota is used up. Check the backend log. |
| Browser shows a network or CORS error | The backend isn't running, or your frontend origin isn't in `CORS_ORIGINS`. |
| Everything redirects to `/login` | You're signed out or your 24-hour token expired. Sign in again. |
| `429` errors | The per-IP rate limit was hit. Wait a minute or raise `RATE_LIMIT_REQUESTS`. |
| Resources are empty | The live Google Search lookup returned nothing for that skill. Use the "Find resources" button on the Resources page to retry a specific skill. |
| Frontend can't find the API | Check `VITE_API_BASE_URL` in `careergraph-frontend/.env` and restart `npm run dev`. |
