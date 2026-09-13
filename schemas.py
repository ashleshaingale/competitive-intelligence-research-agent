from pydantic import BaseModel, Field


class CompetitorList(BaseModel):
    """Structured output returned by the competitor discovery agent."""

    competitors: list[str] = Field(
        description="Exactly three major competitors of the company being researched."
    )


class CompetitorReport(BaseModel):
    """Structured report returned by the analyst agent."""

    competitor_name: str = Field(
        description="Name of the competitor."
    )

    why_competitor: str = Field(
        description="Why this company is considered a competitor."
    )

    pricing_model: str = Field(
        description="Pricing approach or business model, including specific prices when available."
    )

    key_features: list[str] = Field(
        description="Three to five important products, capabilities, or features."
    )

    market_positioning: str = Field(
        description="Target market, target customers, and competitive positioning."
    )

    recent_developments: str = Field(
        description="Recent launches, partnerships, funding, acquisitions, or other relevant news."
    )