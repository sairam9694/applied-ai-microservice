import os
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="NLP Entity & Sentiment Service", version="1.0.0")

# 1. Define strict Input Contract
class TextRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Raw customer review or support ticket")

# 2. Define strict Output Contract (What downstream engineers rely on)
class AnalysisResponse(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    urgency_score: int = Field(..., ge=1, le=5)
    summary: str

@app.get("/health")
async def health_check():
    """Load balancers (AWS ALB/Kubernetes) ping this to see if your container is alive."""
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(payload: TextRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Fallback mode if no API key is passed so you can test the architecture immediately
    if not api_key:
        is_urgent = "broken" in payload.text.lower() or "cancel" in payload.text.lower()
        return AnalysisResponse(
            sentiment="negative" if is_urgent else "neutral",
            urgency_score=5 if is_urgent else 2,
            summary=f"Processed {len(payload.text.split())} words (Mock Mode)."
        )

    # Real LLM Structured Output Call (Uncomment/use if you pass an OPENAI_API_KEY)
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract sentiment, urgency (1-5), and a 1-sentence summary."},
                {"role": "user", "content": payload.text},
            ],
            response_format=AnalysisResponse,
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
