# --- LOGIC LAYER (Expansion) ---

def calculate_progress(quiz_scores: List[int], labs_completed: int, tier: str) -> float:
    """
    Calculates progress toward a specific level certificate.
    Standard: 40% Knowledge (Quizzes) + 60% Application (Labs)
    """
    if not quiz_scores and labs_completed == 0:
        return 0.0

    # Calculate average quiz performance
    avg_quiz = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
    
    # Define required labs per tier (e.g., Level 3 requires more labs)
    required_labs = {"UNDERSTAND (Level 1)": 3, "APPLY (Level 2)": 5, "CREATE (Level 3)": 8}
    lab_goal = required_labs.get(tier, 5)
    
    # Progress Calculation
    quiz_weight = (avg_quiz / 100) * 0.40
    lab_weight = min((labs_completed / lab_goal), 1.0) * 0.60
    
    total_progress = round((quiz_weight + lab_weight) * 100, 2)
    return total_progress

# --- UPDATED API ENDPOINT ---

@app.post("/tutor/update-progress", response_model=TutorResponse)
async def update_student_progress(
    query: StudentQuery, 
    quiz_scores: List[int], 
    labs_completed: int
):
    tier = get_complexity_tier(query.age)
    
    # Calculate progress using our weighted logic
    current_progress = calculate_progress(quiz_scores, labs_completed, tier)
    
    # Logic to trigger Certificate Generation
    milestone_msg = "Keep going!"
    if current_progress >= 100:
        milestone_msg = f"Congratulations! You've unlocked the {tier} Certificate!"
    elif current_progress > 75:
        milestone_msg = "Almost there! Complete your final project to certify."

    return {
        "complexity_tier": tier,
        "explanation": milestone_msg,
        "suggested_projects": ["Final Capstone Project"] if current_progress > 80 else [],
        "certification_progress": current_progress
    }
    
    
    
    
    
    