from pydantic import BaseModel, Field

class AnalysisResult(BaseModel):
    explanation: str = Field(description="Detailed explanation of the analysis")
    action: str = Field(description="Recommended action based on the analysis")

class SentimentResult(BaseModel):
    explanation: str = Field(description="Detailed explanation of the analysis")
    sentiment: str = Field(description="The sentiment of the article")