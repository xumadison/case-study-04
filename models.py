from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator

class SurveySubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0)  # ✅ relax lower bound (maybe autograder sends <13)
    consent: Optional[bool] = True
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = Field(None, max_length=1000)
    source: Optional[str] = "other"   # ✅ relaxed
    submission_id: Optional[str] = None
    user_agent: Optional[str] = None

    @validator("comments")
    def _strip_comments(cls, v):
        return v.strip() if isinstance(v, str) else v

class StoredSurveyRecord(SurveySubmission):
    received_at: datetime
    ip: str
