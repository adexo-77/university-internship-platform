"""Pydantic schemas for administrator internship review operations."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class InternshipReviewRequest(BaseModel):
    """Schema for approving, rejecting, or taking down an internship posting."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    decision: Literal["approved", "rejected"]
    review_note: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_rejection_note(self) -> Self:
        if self.decision == "rejected" and (not self.review_note or not self.review_note.strip()):
            raise ValueError("Review note is required when rejecting or taking down a posting")
        return self
