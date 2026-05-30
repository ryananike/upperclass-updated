from google import genai

#print(response.text)#

import asyncio
import pygame 
import time
import os
from playsound import playsound
import edge_tts
from dotenv import load_dotenv
from google import genai
import json
import re
#from PyPDF2 import PdfReader


# Load the key from .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
CURRICULUM_PDF = "curriculum.pdf"
#PROFILE_FILE = "student_profile.json"
#VOICE_CHILD = "en-US-JennyNeural"
#VOICE_TEEN = "en-US-GuyNeural"
#VOICE_ADULT = "en-US-AriaNeural"
##OUTPUT_AUDIO = "tutor_response.mp3"
#PROFILE_FILE = "student_profile.json"


client = genai.Client(api_key=API_KEY)

# 2. Defining the Personality
SYSTEM_INSTRUCTION = """
You are UpperclassAI Tutor, a world-class adaptive tutor specializing in Artificial Intelligence, Machine Learning, Python programming, Data Science, and Responsible AI.
- If interests are unknown, ask: "What do you enjoy (games, sports, music, business, science, art)?"
- If the student says "teach me AI", begin at Level 1 unless an assessment shows prior knowledge.
- If the student says "quiz me", generate questions based on the current topic.
- If the student says "I don't understand", re-explain using a simpler analogy.
- If the student says "give me a project", generate an age-appropriate hands-on project.

OUTPUT FORMAT
Lesson Title:
What You'll Learn:
Explanation:
Example:
Practice:
Quick Quiz:
Summary:
Next Step:

IMPORTANT FORMATTING RULES
- Do NOT use markdown.
- Do NOT use hashtags (#).
- Do NOT use asterisks (*).
- Do NOT use bullet points.
- Do NOT use subheadings with ## or ###.
- Write in clean plain text optimized for text-to-speech narration.
- Make the response sound natural when spoken aloud.

CODING RULES
- Use Python by default unless another language is requested.
- Explain every line of code.
- Use age-appropriate comments.
- Start simple and gradually increase complexity.

MATH RULES
- Introduce intuition first.
- Then show formulas.
- Then work through examples.
- Then connect formulas to code.

ETHICS RULES
Always teach:
- Bias in AI
- Privacy and security
- Hallucinations and fact-checking
- Fairness and responsible deployment

ASSESSMENT TYPES
- Multiple choice
- True/false
- Short answer
- Coding challenges
- Mini-projects
- Debate and reflection

COMMUNICATION STYLE
- Friendly
- Encouraging
- Professional
- Patient
- Clear and structured

INTERACTIVE QUESTION RULES
- Whenever you ask a direct question that requires a student response, stop your response immediately after the question.
- Do not provide the answer, explanation, summary, or next lesson until the student responds.
- Treat quiz questions, comprehension checks, and practice questions as turn-ending questions.
- After the student answers:
  1. Evaluate whether the answer is correct, partially correct, or incorrect.
  2. Give feedback.
  3. Ask a follow-up question or continue the lesson.
- Only ask one non-rhetorical question at a time.
- If a section contains a question, end the message at that question.

ULTIMATE GOAL
Transform the student into an independent AI practitioner who understands theory, writes code, builds machine learning models, evaluates results, and applies AI responsibly.

CURRICULUM KNOWLEDGE
{CURRICULUM_CONTENT}

"""


chat_session = client.chats.create(
    model="gemini-2.5-flash",
    config={
        "system_instruction": SYSTEM_INSTRUCTION,
        "temperature": 0.7
    }
)

# 3. LOADING CURRICULUM FROM PDF
def load_curriculum(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Curriculum PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)

    curriculum_text = "\n\n".join(pages)

    # Limiting the size to reduce token usage if needed
    if len(curriculum_text) > 50000:
        curriculum_text = curriculum_text[:50000]

    return curriculum_text

# 4. THE STUDENT PROFILE MANAGEMENT
def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "name": None,
        "age": None,
        "interests": [],
        "current_level": "Level 1",
        "current_module": "Module 1.1",
        "current_topic": "What is Artificial Intelligence?",
        "completed_topics": [],
        "quiz_scores": {},
        "strengths": [],
        "weak_areas": []
    }


def save_profile(profile):
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

# age based code
def get_age_context(age):
    """
    Returns age-specific instructions to inject into each prompt.
    """
    if age is None:
        return """
Student age is unknown.
Ask: 'How old are you so I can teach you in the best way for your age?'
"""

    if 7 <= age <= 9:
        return """
Student Age Group: 7-9 years old

Teaching Style:
- Use very simple words.
- Keep sentences short.
- Use fun analogies involving LEGO, Minecraft, Roblox, animals, and cartoons.
- Avoid advanced mathematics.
- Keep explanations under 120 words.
- Ask only one multiple-choice question with 3 options.
"""

    elif 10 <= age <= 12:
        return """
Student Age Group: 10-12 years old

Teaching Style:
- Introduce technical words with simple definitions.
- Use relatable examples from games, school, and everyday life.
- Include mini-projects and simple code examples.
- Ask one multiple-choice question with 3 options.
"""

    elif 13 <= age <= 17:
        return """
Student Age Group: 13-17 years old

Teaching Style:
- Use real programming concepts and technical terminology.
- Explain concepts clearly and directly.
- Include Python examples and practical projects.
- Ask one multiple-choice question with 3 options.
"""

    else:
        return """
Student Age Group: 18+ years old

Teaching Style:
- Teach at professional depth.
- Include industry best practices and optimization techniques.
- Use advanced code examples and career guidance.
- Ask one multiple-choice question with 3 options.
"""
    
#voice based code
def get_voice_by_age(age):
    if age is None:
        return "en-US-GuyNeural"

    if age <= 12:
        return "en-US-JennyNeural"   # Friendly voice for younger learners
    elif age <= 17:
        return "en-US-GuyNeural"     # Teen voice
    else:
        return "en-US-AriaNeural"    # Professional adult voice
   
#building the prompt with age based context
def build_prompt(user_input, age):
    age_context = get_age_context(age)

    return f"""
{age_context}

Student Message:
{user_input}
"""   


student_age = None
while student_age is None:
    try:
        student_age = int(input("🎂 How old is the student? "))
        if student_age < 7:
            print("This tutor is designed for learners age 7 and above.")
            student_age = None
    except ValueError:
        print("Please enter a valid age.")

def play_audio(filename):
    try:
        full_path = os.path.abspath(filename)
        print(f"🔊 Playing via playsound: {full_path}")
        playsound(full_path) 
        print("✅ Finished Speaking.")
    except Exception as e:
        print(f"❌ playsound failed: {e}")
       
        os.startfile(filename)


def clean_text_for_speech(text):
    """
    Clean tutor text for natural speech.
    """

    # Removing emojis
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FAFF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )

    text = emoji_pattern.sub('', text)

    # Remove markdown headings
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Remove bullets
    text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)

    # Remove markdown symbols
    text = re.sub(r'[*_`>|~#]', '', text)

    # Clean whitespace
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


async def tutor_process(user_input, student_age):
    try:
        # Ask the Brain (Gemini)
        print("🧠 Thinking...")
        prompt = build_prompt(user_input, student_age)
        response = chat_session.send_message(prompt)
        tutor_text = response.text
        print(f"📝 Tutor: {tutor_text}")
        
        # Generate the Voice (Edge-TTS)
        voice_name = get_voice_by_age(student_age)
        output_file = "tutor_response.mp3"
        if os.path.exists(output_file):
            try: os.remove(output_file)
            except: pass # Prevents crash if file is locked
        
        speech_text = clean_text_for_speech(tutor_text)
        communicate = edge_tts.Communicate(speech_text, voice_name)
        await communicate.save(output_file)
        
        
        play_audio(output_file)
    
    except Exception as e:
        print(f"❌ Error: {e}")

# The Main loop Block
async def main():
    print("🎓 AI Tutor is Online! (Type 'quit' to exit)")
    
    while True:
        user_q = input("\n👶 You: ")
        
        if user_q.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye! Happy learning!")
            break
            
        if not user_q.strip():
            continue


        await tutor_process(user_q, student_age)

if __name__ == "__main__":
    asyncio.run(main())
    
