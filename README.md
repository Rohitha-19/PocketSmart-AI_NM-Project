# PocketSmart AI - Your Smart Budget and Recommendation Assistant 

## 👥 Project Team Details

| Team Information | Details |
| :--- | :--- |
| **Team ID** | `SWTID-2026-6545` |
| **Project Title** | PocketSmart AI - Your Smart Budget & Recommendation Assistant|
| **Team Leader** | **ROHITHA V** |
| **Team Members** | • **SANDHIYA R**<br>• **PRIYANKA G**<br>• **NIVETHA D** |

PocketSmart AI is a complete FastAPI + Jinja2 + SQLite application based on the supplied project documentation. It provides:

- User registration/login with JWT authentication
- Home Interior Planner
- Party Budget Planner
- Jewelry Planner with optional image upload
- Recommendation history
- Deterministic fallback catalog so the app works without an AI key
- Optional Gemini integration for structured recommendation generation
- Responsive HTML/CSS/JavaScript frontend
- Automated API tests

## Important implementation note

The supplied document names several marketplaces/services (Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO) but does not provide authenticated live API credentials or API contracts. This implementation therefore uses destination search URLs and clearly labels prices as estimates. It does **not** fake live inventory, live prices, ratings, or availability.

The source document also contains both Flask and FastAPI references. The implementation follows the later and more detailed FastAPI architecture because the document's milestones explicitly specify FastAPI, Uvicorn, Jinja2, modular routes/services/models, and FastAPI-style authentication dependencies.

## Architecture

```text
Browser
  |
  | HTML/CSS/JS + fetch()
  v
FastAPI
  |-- /api/register, /api/login, /api/me
  |-- /api/generate-home
  |-- /api/generate-party
  |-- /api/generate-jewelry
  |-- /api/history
  |
  +--> Recommendation service
  |      +--> deterministic catalog fallback
  |      +--> optional Gemini structured JSON
  |
  +--> SQLite + SQLAlchemy
```

## 1. VS Code setup

Install:

- Python 3.11+ recommended
- VS Code
- VS Code Python extension

Open this project folder in VS Code.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### Command Prompt

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## 2. Run without Gemini

This is the easiest first test. Open `.env` and set:

```env
USE_AI=false
```

Then:

```powershell
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The project still generates recommendations using the built-in demo catalog.

## 3. Enable Gemini

Create a Gemini API key and put it in `.env`:

```env
USE_AI=true
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

The app uses Google's current `google-genai` Python SDK. Gemini is requested with structured JSON output so the backend can reliably render recommendation cards.
If the configured Gemini model is temporarily rate-limited or at capacity, the app retries once with `gemini-flash-lite-latest`. Generated plans identify Gemini as the source; when both requests fail, the built-in catalog is used and the result is labeled accordingly.

If your account exposes a different current Flash model, change `GEMINI_MODEL` accordingly.

Restart the server after editing `.env`.

## 4. Test

Run:

```powershell
pytest -q
```

Expected result: health, authentication, and Home Planner tests pass.

You can also open:

```text
http://127.0.0.1:8000/docs
```

to test the API interactively.

## 5. Demo flow

1. Open `/register`.
2. Create an account.
3. Open Dashboard.
4. Try Home Planner.
5. Try Party Planner.
6. Try Jewelry Planner with or without an image.
7. Return to Dashboard and view history.
8. Open a recommendation's source-search link.

## Security notes

- Never commit `.env`.
- Replace `SECRET_KEY` before deployment.
- For production, use HTTPS.
- For production marketplace integrations, use official APIs and store provider credentials server-side.
- The demo SQLite database is intended for development/college-project use.

## Project tree

```text
PocketSmart-AI/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── pages.py
│   │   └── planners.py
│   ├── services/
│   │   ├── catalog.py
│   │   ├── gemini.py
│   │   └── recommendations.py
│   ├── static/
│   │   ├── css/app.css
│   │   └── js/
│   └── templates/
├── tests/
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```
## 🔗 Project Links

- **GitHub Repository:** [View Source Code](https://github.com/Rohitha-19/PocketSmart-AI_NM-Project)
- **Demo Video:** [Watch Project Demo](https://drive.google.com/drive/folders/15py1MV06ZY8_-cG_r9_0pC2kU9ps8Dub)
