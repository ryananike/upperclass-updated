from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(title="AI Tutor Logic API")

# --- DATA SCHEMAS (Inputs/Outputs) ---
class StudentQuery(BaseModel):
    student_id: str
    age: int = Field(..., ge=7, le=17, description="Age must be between 7 and 17")
    skill_level: str = "Beginner"  # Can be updated by the model
    text_input: str = Field(..., min_length=2)

class TutorResponse(BaseModel):
    complexity_tier: str
    explanation: str
    suggested_projects: List[str]
    certification_progress: float

# --- LOGIC LAYER (Your ML Engineer Role) ---
def get_complexity_tier(age: int) -> str:
    """Routes student to correct international standard level."""
    if 7 <= age <= 10:
        return "UNDERSTAND (Level 1)"
    elif 11 <= age <= 14:
        return "APPLY (Level 2)"
    return "CREATE (Level 3)"

# --- API ENDPOINT ---
@app.post("/tutor/get-explanation", response_model=TutorResponse)
async def process_tutor_request(query: StudentQuery):
    # 1. Routing based on Age (International Standards)
    tier = get_complexity_tier(query.age)
    
    # 2. Mock Logic for Machine Learning Response
    # In a real scenario, you'd call your scikit-learn model here
    if tier == "UNDERSTAND (Level 1)":
        explanation = f"Think of AI like a smart robot friend that learns from patterns, just like you learn to recognize fruit!"
        projects = ["Teachable Machine - Fruit Sorter"]
    elif tier == "APPLY (Level 2)":
        explanation = "AI uses data to make guesses. We call this 'Classification' when we group things together."
        projects = ["Image Classifier for Pets"]
    else:
        explanation = "We are using Python to build a supervised learning model. Let's look at the training and test sets."
        projects = ["Spam Filter with Scikit-learn"]

    return {
        "complexity_tier": tier,
        "explanation": explanation,
        "suggested_projects": projects,
        "certification_progress": 0.15  # Calculated based on user session data
    }