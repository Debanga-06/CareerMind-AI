"""
Normalizes raw SerpApi `google_jobs` results into a consistent internal shape
so the rest of the app never has to deal with SerpApi's raw/variable JSON.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional

from app.schemas.career import NormalizedJob


def _stable_job_id(raw: Dict[str, Any]) -> str:
    """
    SerpApi's google_jobs results include a `job_id` field in most regions,
    but it's not guaranteed to always be present/stable. Fall back to a
    deterministic hash of title+company+location so we always have an id.
    """
    existing = raw.get("job_id")
    if existing:
        return str(existing)

    basis = f"{raw.get('title', '')}|{raw.get('company_name', '')}|{raw.get('location', '')}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def _extract_apply_link(raw: Dict[str, Any]) -> Optional[str]:
    apply_options = raw.get("apply_options") or []
    if isinstance(apply_options, list) and apply_options:
        first = apply_options[0]
        if isinstance(first, dict):
            return first.get("link")
    return raw.get("share_link")


def _extract_description(raw: Dict[str, Any]) -> Optional[str]:
    description = raw.get("description")
    if description:
        return description

    # Some listings only carry structured "job_highlights" (Qualifications,
    # Responsibilities, Benefits) instead of a single description blob.
    highlights = raw.get("job_highlights") or []
    if isinstance(highlights, list) and highlights:
        parts: List[str] = []
        for section in highlights:
            if not isinstance(section, dict):
                continue
            title = section.get("title", "")
            items = section.get("items", [])
            if items:
                parts.append(f"{title}: " + " ".join(items))
        if parts:
            return "\n".join(parts)
    return None


def normalize_google_jobs_result(raw: Dict[str, Any]) -> NormalizedJob:
    detected_extensions = raw.get("detected_extensions") or {}

    return NormalizedJob(
        job_id=_stable_job_id(raw),
        title=raw.get("title"),
        company_name=raw.get("company_name"),
        location=raw.get("location"),
        description=_extract_description(raw),
        via=raw.get("via"),
        posted_at=detected_extensions.get("posted_at"),
        schedule_type=detected_extensions.get("schedule_type"),
        apply_link=_extract_apply_link(raw),
    )


def normalize_google_jobs_results(raw_jobs: List[Dict[str, Any]]) -> List[NormalizedJob]:
    normalized = []
    for raw in raw_jobs:
        if not isinstance(raw, dict):
            continue
        try:
            normalized.append(normalize_google_jobs_result(raw))
        except Exception:
            # Never let one malformed listing break the whole batch.
            continue
    return normalized
