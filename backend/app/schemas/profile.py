from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    """All fields optional -- PUT /api/profile only updates fields you send."""

    target_career: Optional[str] = Field(default=None, max_length=200)
    experience_level: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=200)
    skills: Optional[List[str]] = None


class ProfileResponse(BaseModel):
    target_career: Optional[str] = None
    experience_level: Optional[str] = None
    location: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    updated_at: Optional[datetime] = None
