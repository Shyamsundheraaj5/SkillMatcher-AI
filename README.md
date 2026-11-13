# SkillMatcher — AI-Powered ATS Resume Analyzer

> Upload resumes, paste a job description, and instantly get AI-driven insights on candidate fit — powered by Google's Gemini 3.5 Flash model.

<img width="1200" height="1600" alt="myfirsthackathon" src="https://github.com/user-attachments/assets/97e47427-4128-4f51-ad3b-42354dc2ef67" />


---

## 🌟 Introduction

**SkillMatcher** is an easy-to-use website that automatically reads and rates PDF resumes against job descriptions. Instead of spending hours reading every single resume, recruiters can upload dozens of PDFs at once. Our backend parses the text, extracts the candidate's name, calculates a match score, and gives clear tips to improve the resume.

---

## 🔄 Project Structure & Request Flow

This project is built using a clean, layered backend architecture. Below is a diagram showing how data moves from a user's browser, through our backend layers, to the AI service, and back:

### Data Flow Diagram:
```
[User Browser]  ---(Submit Resumes & Job Details)---> [main.py] (FastAPI Main Entry)
                                                           │
                                                           ▼
[Jinja2 HTML Template] <---(Displays Results)--- [routers/resume.py] (Resume Router)
                                                           │
                      ┌────────────────────────────────────┴───────────────────────────────────┐
                      ▼                                                                        ▼
            [services.py (PDF Parsing)]                                              [services.py (Auth Verification)]
                      │                                                                        │
                      ├─► Extracts text using PyMuPDF                                          ├─► Decodes session cookie (JWT)
                      ▼                                                                        ▼
            [services.py (Gemini LLM Client)]                                        [models.py & database.py (SQLAlchemy)]
                      │                                                                        │
                      ├─► Sends text to Gemini 3.5 Flash API                                   ├─► Saves matched percentage to SQLite
                      ▼                                                                        └────────────────────────┐
            [Markdown Converter]                                                                                        │
                      │                                                                                                 ▼
                      └────────────────────────────►(Structured results merged with database records)───────────────────┘
```

### File Structure:
- **`main.py`**: The starting point of the app. It mounts static files and connects all backend routes.
- **`app/database.py` & `models.py`**: Handles how our database stores data. It creates the database tables for users and their analysis history.
- **`app/services.py`**: The main business logic of the backend. It contains code to extract text from PDFs, verify login tokens, and communicate with the Google Gemini API.
- **`app/routers/`**: Handles different URL routes. `auth.py` deals with signup/login, and `resume.py` deals with the dashboard and resume uploading.
- **`templates/`**: HTML files that form the website pages.
- **`static/`**: CSS styling files to make the pages look clean and professional.

---

## 🌐 API Routes

Here is the list of web links (routes) the backend supports:

| Method | Web Address (Route) | What it does | Who can access it? |
|---|---|---|---|
| `GET` | `/` | Redirects the user to the Login page | Anyone |
| `GET` | `/login` | Shows the Login page | Anyone |
| `POST` | `/login` | Checks credentials and logs the user in | Anyone |
| `GET` | `/register` | Shows the Sign Up page | Anyone |
| `POST` | `/register` | Creates a new user account | Anyone |
| `GET` | `/logout` | Logs the user out and clears login session | Logged-in users only |
| `GET` | `/home` | Shows the main resume upload dashboard | Logged-in users only |
| `POST` | `/home` | Accepts uploaded resumes and shows results | Logged-in users only |

---

## 📁 Database Design
We use a small local SQLite database (`users.db`) to keep track of accounts and results. It has two tables:

### 1. `users` Table (Stores user accounts)
| Column | Type | Description |
|---|---|---|
| `id` | Integer | Unique ID number (Auto-increment) |
| `username` | String | Unique username chosen at registration |
| `email` | String | User's email address |
| `password_hash` | String | Scrambled password using bcrypt |

### 2. `results` Table (Stores match history)
| Column | Type | Description |
|---|---|---|
| `id` | Integer | Unique ID number (Auto-increment) |
| `username` | String | Links the result to the user who uploaded it |
| `name` | String | Candidate's name (extracted by AI) |
| `percentage` | Float | Calculated match score (e.g. 85.0) |

---

## ⚙️ How to Set Up and Run Locally

### Prerequisites

- **Python**: Version `3.10` or higher (Tested and fully functional on **Python 3.14**)
- **Local Database**: **SQLite** (No external database installation required — standard library)
- **API Access**: A [Google Gemini API key](https://aistudio.google.com/apikey)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd backup2
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_super_secret_jwt_key_here
```

> **Note:** `SECRET_KEY` is used to sign JWT session cookies. Use a long, random string in production.

### 5. Run the Application

```bash
uvicorn main:app --reload
```

The app will be available at **[http://localhost:8000](http://localhost:8000)**.
The SQLite database (`users.db`) and all tables are created automatically on first run.

---

## 🔒 Security Notes

- Passwords are encrypted with **bcrypt** before storage — plain-text passwords are never saved.
- Sessions are managed via **HTTP-only JWT cookies**, protecting against standard web token theft.
- JWT login sessions automatically expire after **60 minutes**.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
