from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator

class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
    consent: bool = Field(True, description="Must be true to accept")  # ✅ default True
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    source: str = Field("other", regex="^(web|mobile|other)$")  # default = "other"
    submission_id: Optional[str] = None
    user_agent: Optional[str] = None  # optional field

    # validators
    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v


# This record adds server-enriched fields
class StoredSurveyRecord(SurveySubmission):
    received_at: datetime
    ip: str
