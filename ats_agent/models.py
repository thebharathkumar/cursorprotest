from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ATSReviewResponse(BaseModel):
    filename: Optional[str] = Field(default=None, description="Uploaded file name.")
    score: int = Field(ge=0, le=100, description="Overall ATS compatibility score.")
    verdict: str = Field(description="Summary verdict for the score.")
    component_scores: Dict[str, int] = Field(
        description="Breakdown of scores by ATS evaluation component."
    )
    matched_keywords: List[str] = Field(
        default_factory=list, description="Keywords found in resume and target job description."
    )
    missing_keywords: List[str] = Field(
        default_factory=list,
        description="Important target keywords missing from the resume.",
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Actionable recommendations to improve ATS score."
    )
    text_length: int = Field(
        ge=0, description="Number of characters extracted from the uploaded resume."
    )

