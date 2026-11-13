import os
from datetime import datetime, timedelta

import bcrypt
import fitz  
from google import genai
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("SECRET_KEY")
gemini_client = genai.Client(api_key=api_key) if api_key else genai.Client()

SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

PROMPTS = {
    "analyze_resume": """Conduct a detailed analysis of the resume against the job description, highlighting strengths, weaknesses, and alignment with the role.
    Give proper padding and proper text allign and bold text wherever necesary also <b>..</b> means bold in below prompt.
    Respond in the following structured format in Markdown:
    1. <b>Overview</b>: A shortest summary of the candidate's suitability.
    2. <b>Strengths</b>: Bullet key points highlighting strong skills or experiences.
    3. <b>Weaknesses<b>: Bullet key points identifying areas of misalignment.
    4. <b>Final Verdict</b>: A concise one-line evaluation of the candidate's fit for the role.""",

    "percentage_match": """Extract the candidate's name from the resume. Then, expertly calculate the alignment percentage between the resume and the job description, focusing on key skills and qualifications.
    Give proper padding and proper text allign
    Respond in the following structured format in Markdown:
    1. <b>Name</b>: Extracted name of the candidate.
    2. <b>Match Percentage</b>: Provide the alignment score as a percentage.
    3. <b>Matched Keywords</b>: List the most keywords or skills from the job description present in the resume.
    4. <b>Missing Keywords</b>: Highlight key skills or qualifications missing from the resume.
    5. <b>Suggestions</b>: Offer actionable recommendations to improve alignment.""",
}


def hash_password(password: str) -> str:
    hashed: bytes = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(data: dict[str, object]) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore[arg-type]


def decode_access_token(token: str) -> dict[str, object]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore[return-value]


def get_gemini_response(input_text: str, pdf_text: str, prompt: str) -> str:
    try:
        message = f"{prompt}\n\nJob Description:\n{input_text}\n\nResume:\n{pdf_text}"
        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash",
            contents=message,
        )
        return response.text or ""
    except Exception as e:
        return f"Error in generating response: {str(e)}"



def input_pdf_setup(file_bytes: bytes) -> str | None:
    try:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join(page.get_text() for page in pdf_document)
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None
