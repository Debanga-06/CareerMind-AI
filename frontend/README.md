# CareerGraph AI — Frontend

React + Vite + Tailwind frontend for CareerGraph AI.

> **Status: Frontend Step 1.** Foundation, routing, design system, reusable
> components, and all 8 pages are built and wired to the real backend
> contract. Roadmap/project generation is intentionally NOT called yet —
> those pages show honest empty states until that step.

## Tech stack

React 18 · Vite 5 · Tailwind CSS 3 · React Router 6 · Axios · Recharts · Lucide React

## Setup

```bash
npm install
cp .env.example .env
# edit .env if your backend isn't at http://localhost:8000/api
npm run dev
```

Open http://localhost:5173. The backend (see `../careergraph-backend`) must
be running for anything past the landing page to return real data —
`npm run dev` with no backend will show honest loading/error states, not
fake data.

```bash
npm run build     # production build -> dist/
npm run preview   # preview the production build
npm run test      # vitest: component + route smoke tests (20 tests)
```

## Environment variables

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Base URL of the FastAPI backend, e.g. `http://localhost:8000/api`. The frontend **never** talks to SerpApi directly — only to this backend. |

## Project structure

```
src/
  api/
    client.js          # Axios instance, error normalization, auth header
    careerApi.js        # analyzeCareer(), listSuggestedCareers()
  context/
    AnalysisContext.jsx # shared analysis result + status, sessionStorage cache
  hooks/
    useAnalysis.js
  lib/
    skillMeta.js         # skill-gap category copy, %/tone formatting helpers
  components/
    layout/
      Navbar.jsx           # public (landing) top nav
      Sidebar.jsx           # app sidebar + mobile drawer
      PublicLayout.jsx       # navbar + footer wrapper (landing)
      DashboardLayout.jsx     # sidebar + topbar wrapper (app pages)
    ui/
      Button.jsx Card.jsx Badge.jsx SkillBadge.jsx StatCard.jsx
      EmptyState.jsx LoadingState.jsx ErrorState.jsx MatchMeter.jsx
    jobs/
      JobCard.jsx
    charts/
      SkillDemandChart.jsx  # Recharts horizontal bar chart
    hero/
      HeroGraph.jsx          # decorative node-graph brand illustration
  pages/
    Landing.jsx Onboarding.jsx Dashboard.jsx Jobs.jsx Market.jsx
    SkillGap.jsx Roadmap.jsx Projects.jsx NotFound.jsx
  test/
    routes.smoke.test.jsx   # every route renders without crashing
    pages.data.test.jsx      # pages render correctly against realistic API data
    mockData.js                # mirrors the real backend response shape
    testUtils.jsx               # renderWithAnalysis() test helper
```

## Routes

| Path | Page |
|---|---|
| `/` | Landing |
| `/onboarding` | Career analysis form |
| `/dashboard` | Overview (stats, market summary, skill gap, top job matches) |
| `/jobs` | Full job list, search/sort |
| `/market` | Skill demand chart + table |
| `/skill-gap` | Strong/Develop/Missing/Priority + scoring methodology |
| `/roadmap` | Roadmap (honest empty state — see below) |
| `/projects` | Project recommendations (honest empty state — see below) |

## Data flow

1. `/onboarding` submits the form to `AnalysisContext.runAnalysis()`, which
   calls `POST /api/careers/analyze` and stores the full response.
2. Every other app page reads from the same context (`useAnalysis()`) — no
   page re-fetches, and the result is cached in `sessionStorage` so a page
   refresh doesn't lose it.
3. `roadmap` and `projects` are read directly from that same response. The
   backend currently returns `roadmap: null` and `projects: []` from
   `/api/careers/analyze` (roadmap generation is a separate backend
   endpoint, `POST /api/roadmap/generate`, not called by this build yet) —
   so `/roadmap` and `/projects` show the literal required empty state:
   *"Your personalized roadmap will appear here after analysis."* No
   fabricated roadmap phases or project ideas are ever rendered.

## Design notes

- Palette: `ink` (near-navy text), `paper`/`surface` (warm-neutral
  backgrounds), `signal` (teal — strong/positive), `amber`
  (develop/priority), `rose` (missing) — see `tailwind.config.js`.
- Type: Space Grotesk for headlines/numbers, Inter for UI/body text.
- The landing hero uses a custom SVG node-graph illustration
  (`HeroGraph.jsx`) instead of a generic gradient blob, tying visually to
  the "graph" in the product name and the skill → role relationship the
  product actually models.
- Every match/skill-gap percentage shown anywhere in the UI comes straight
  from the API response — nothing is computed or invented client-side,
  and no copy anywhere claims to predict hiring outcomes.

## Known limitations (Step 1)

- No auth UI yet (the backend has `/api/auth/*`, but this build doesn't
  have login/register screens — `apiClient` is wired to send a stored
  token if one exists, ready for that step).
- `/roadmap` and `/projects` don't call `POST /api/roadmap/generate` yet
  (out of scope for this step, per the brief).
- No route-based code splitting yet (single JS bundle, ~190KB gzipped) —
  fine for this stage, worth revisiting later.
