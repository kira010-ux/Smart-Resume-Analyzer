"""FastAPI application for resume-to-job matching."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

try:
    from .database import list_analyses, save_analysis
    from .scoring import analyze_match
    from .text_extraction import (
        EmptyTextError,
        FileTooLargeError,
        TextExtractionError,
        UnsupportedFileTypeError,
        extract_text_from_text,
        extract_raw_text_from_file,
    )
except ImportError:
    from database import list_analyses, save_analysis
    from scoring import analyze_match
    from text_extraction import (
        EmptyTextError,
        FileTooLargeError,
        TextExtractionError,
        UnsupportedFileTypeError,
        extract_text_from_text,
        extract_raw_text_from_file,
    )


app = FastAPI(
    title="Smart Resume Analyzer",
    description="Compare a resume with a job description and identify skill gaps.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _resolve_input(
    text: str | None,
    upload: UploadFile | None,
    field_name: str,
) -> str:
    if text and text.strip() and upload and upload.filename:
        raise HTTPException(
            status_code=400,
            detail=f"Provide either {field_name}_text or {field_name}_file, not both",
        )
    if upload and upload.filename:
        try:
            content = await upload.read()
            return extract_raw_text_from_file(content, upload.filename)
        except TextExtractionError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(
                status_code=400,
                detail=f"Could not read {field_name} file",
            ) from error
    if text and text.strip():
        try:
            extract_text_from_text(text)
            return text
        except EmptyTextError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
    raise HTTPException(
        status_code=400,
        detail=f"Provide {field_name}_text or {field_name}_file",
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    resume_text: Annotated[str | None, Form()] = None,
    job_description_text: Annotated[str | None, Form()] = None,
    resume_file: Annotated[UploadFile | None, File()] = None,
    job_description_file: Annotated[UploadFile | None, File()] = None,
    job_title: Annotated[str | None, Form()] = None,
) -> dict[str, object]:
    """Analyze pasted text or uploaded documents from either input source."""
    resume = await _resolve_input(resume_text, resume_file, "resume")
    job_description = await _resolve_input(
        job_description_text,
        job_description_file,
        "job_description",
    )
    try:
        result = analyze_match(resume, job_description)
        analysis_id = save_analysis(
            result,
            resume_filename=resume_file.filename if resume_file else None,
            job_title=job_title,
        )
        return {**result, "analysis_id": analysis_id}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail="Analysis failed") from error


@app.get("/history")
def history() -> list[dict[str, object]]:
    """Return the most recent completed analyses."""
    return list_analyses()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
