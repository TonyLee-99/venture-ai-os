"""Pydantic output contracts for every agent. An output that does not validate is a job failure."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Claim(BaseModel):
    id: str
    section: Literal["market", "pmf", "narrative", "execution", "risk", "inflection"]
    text: str
    doc_id: str | None = None   # citation: a snapshot in the DAKR doc store
    quote: str | None = None    # exact span copied from that snapshot
    metric: str | None = None   # citation: a warehouse metric key from the facts sheet
    value: float | None = None

    @model_validator(mode="after")
    def has_receipt(self):
        if not ((self.doc_id and self.quote) or (self.metric and self.value is not None)):
            raise ValueError(f"claim {self.id} has no receipt (needs doc_id+quote or metric+value)")
        return self


class DimensionScore(BaseModel):
    score: int = Field(ge=1, le=5)
    rationale: str


class Scores(BaseModel):
    pmf: DimensionScore
    narrative: DimensionScore
    execution: DimensionScore


class Memo(BaseModel):
    company: str
    one_liner: str
    thesis_fit: str
    claims: list[Claim] = Field(min_length=6)
    scores: Scores
    risks: list[str] = Field(min_length=2)
    open_questions: list[str] = Field(min_length=3)
    recommendation: Literal["advance", "watch", "pass"]


class ClaimRepair(BaseModel):
    """Drafter's answer when shown its unverified claims: fix the receipt or drop the claim."""
    fixed: list[Claim]
    dropped: list[str]


class UnsupportedClaim(BaseModel):
    claim_id: str
    reason: str


class Critique(BaseModel):
    scores: Scores
    recommendation: Literal["advance", "watch", "pass"]
    unsupported_claims: list[UnsupportedClaim]
    missing_risks: list[str]
    strongest_counterargument: str


class InflectionNote(BaseModel):
    series: str
    date: str
    headline: str
    claims: list[Claim] = Field(min_length=1)
    confidence: Literal["high", "medium", "low"]


class WeeklyBrief(BaseModel):
    week_of: str
    summary: str
    inflections: list[InflectionNote]
    watchlist: list[str]


class JudgedItem(BaseModel):
    item_id: str
    probability: int = Field(ge=0, le=100)
    reason: str


class JudgmentBatch(BaseModel):
    items: list[JudgedItem]


class HumanDecision(BaseModel):
    """One row of ledger/human_feedback.jsonl: the human verdict on a decision card (the RLEN reward signal)."""
    date: str
    entity: str
    memo_version: int
    decision: Literal["advance", "watch", "pass"]
    agreed_with: Literal["drafter", "critic", "both", "neither"]
    reviewer: str
    reason: str
    example: bool = False  # True = illustrative seed row, not a real decision
