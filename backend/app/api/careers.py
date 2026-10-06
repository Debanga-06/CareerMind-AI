"""
/api/careers routes.

Stage 1 implements POST /api/careers/analyze end-to-end against real
SerpApi data. GET /api/careers (list of supported target careers) is
included as a small, honest placeholder for the frontend to build a
dropdown against.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.rate_limiter import rate_limit_dependency
from app.schemas.career import CareerAnalyzeRequest, CareerAnalyzeResponse
from app.services.career_service import analyze_career
from app.services.serpapi_service import SerpApiError

router = APIRouter(prefix="/careers", tags=["careers"])


# A small, curated starter list. This is UI convenience data, not a claim
# about the job market — it is NOT used to fabricate job results.
SUPPORTED_CAREER_SUGGESTIONS = [
    "AI Engineer",
    "Machine Learning Engineer",
    "Data Scientist",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Data Analyst",
    "Cloud Engineer",
    "Cybersecurity Analyst",
]


@router.get("")
async def list_supported_careers() -> dict:
    return {"careers": SUPPORTED_CAREER_SUGGESTIONS}


@router.post(
    "/analyze",
    response_model=CareerAnalyzeResponse,
    dependencies=[Depends(rate_limit_dependency)],
)
async def careers_analyze(payload: CareerAnalyzeRequest) -> CareerAnalyzeResponse:
    """
    Analyze a target career against real, current job market data.

    Stage 1: fetches + normalizes real Google Jobs results via SerpApi.
    Market analysis, skill-gap, job matching, roadmap, projects and
    resources are filled in during later stages.
    """
    try:
        return await analyze_career(payload)
    except SerpApiError as exc:
        # Should be rare (career_service already catches SerpApiError),
        # but guard against any surface we missed.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream SerpApi error: {exc.message}",
        ) from exc
