from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from jose import JWTError
import markdown

from app.database import get_db
from app.models import Result
from app.services import decode_access_token, get_gemini_response, input_pdf_setup, PROMPTS

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_current_user(request: Request) -> dict[str, object] | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        return decode_access_token(token)
    except JWTError:
        return None


@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "index.html", {
        "username": str(user["sub"]),
        "response": [],
        "error": None,
        "task": None,
    })


@router.post("/home", response_class=HTMLResponse)
async def analyze_resume(
    request: Request,
    job_description: str = Form(...),
    task: str = Form(...),
    resume_files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    username = str(user["sub"])
    input_prompt = PROMPTS.get(task)
    responses = []
    error = None

    if not input_prompt:
        error = "Invalid task selected."
    else:
        for uploaded_file in resume_files:
            if not uploaded_file.filename:
                continue
            file_bytes = await uploaded_file.read()
            pdf_text = input_pdf_setup(file_bytes)
            if not pdf_text:
                error = f"Error extracting content from {uploaded_file.filename}."
                continue
            try:
                raw = get_gemini_response(job_description, pdf_text, input_prompt)
                responses.append(f"<h3>Results for {uploaded_file.filename}:</h3>{markdown.markdown(raw)}")

                if task == "percentage_match":
                    import re
                    name_match = re.search(r"Name\s*</b>?\*?\*?:\s*(.+)", raw, re.IGNORECASE)
                    match_match = re.search(r"Match Percentage\s*</b>?\*?\*?:\s*([0-9]+(?:\.[0-9]+)?)%?", raw, re.IGNORECASE)
                    if name_match and match_match:
                        name = name_match.group(1).replace("*", "").replace("<b>", "").replace("</b>", "").strip()
                        percentage = float(match_match.group(1))
                        db.add(Result(username=username, name=name, percentage=percentage))
                        db.commit()
                    else:
                        name_line = next((l for l in raw.split("\n") if "Name" in l), None)
                        match_line = next((l for l in raw.split("\n") if "Match Percentage" in l), None)
                        if name_line and match_line:
                            name = name_line.split(":")[-1].replace("*", "").replace("<b>", "").replace("</b>", "").strip()
                            pct_str = match_line.split(":")[-1].replace("%", "").replace("*", "").strip()
                            db.add(Result(username=username, name=name, percentage=float(pct_str)))
                            db.commit()
            except Exception as e:
                error = f"Error processing {uploaded_file.filename}: {str(e)}"

    return templates.TemplateResponse(request, "index.html", {
        "username": username,
        "response": responses,
        "error": error,
        "task": task,
    })
