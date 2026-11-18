# Smart Resume Analyzer

A full-stack application that compares a resume with a job description, calculates a blended match score, and highlights matched and missing skills.

## Stack

- Backend: FastAPI, scikit-learn, pandas, pdfplumber, python-docx
- Frontend: React and Vite with plain CSS
- Storage: SQLite for recent analysis history

## Run Locally

From the project root in PowerShell:

```powershell
\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

In a second terminal:

```powershell
Push-Location frontend
npm install
npm run dev
Pop-Location
```

Open `http://localhost:5173` in a browser. The frontend expects the API at `http://localhost:8000`; set `VITE_API_URL` if the API runs elsewhere.

## API

### `POST /analyze`

Send multipart form data with either pasted text or one uploaded file for each side:

- `resume_text` or `resume_file`
- `job_description_text` or `job_description_file`
- optional `job_title`

Supported uploads are PDF, DOCX, and TXT files up to 5 MB. The response includes `match_score`, `matched_skills`, `missing_skills`, and both skill counts.

### `GET /history`

Returns the 25 most recent saved analyses. SQLite data is stored in `backend/analyses.db`.

## Scoring

The score is a 50/50 blend:

```text
final score = 100 * (0.5 * TF-IDF cosine similarity + 0.5 * skill overlap ratio)
```

The skill vocabulary contains 200 common programming, framework, platform, soft, and methodology skills. Text is lowercased, punctuation is removed, whitespace is normalized, and common stopwords are removed before TF-IDF comparison. Skill matching also supports multi-word skills such as `machine learning` and `project management`.

## Checks

```powershell
\.venv\Scripts\python.exe backend\scoring.py
Push-Location frontend; npm run build; Pop-Location
```