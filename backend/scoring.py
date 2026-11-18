"""Resume-to-job scoring using TF-IDF similarity and skill overlap."""

from __future__ import annotations

import re
import string
from typing import Final

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from .skills_data import ALL_SKILLS
    from .text_extraction import clean_text
except ImportError:
    from skills_data import ALL_SKILLS
    from text_extraction import clean_text


TFIDF_WEIGHT: Final[float] = 0.5
SKILL_OVERLAP_WEIGHT: Final[float] = 0.5


def _normalized_skill(value: str) -> str:
    """Normalize a skill for matching while retaining phrase boundaries."""
    value = value.lower().replace("c++", "cplusplus").replace("c#", "csharp")
    value = value.translate(str.maketrans("", "", string.punctuation))
    return re.sub(r"\s+", " ", value).strip()


NORMALIZED_SKILLS: Final[dict[str, str]] = {
    _normalized_skill(skill): skill for skill in ALL_SKILLS
}


def extract_skills(text: str) -> set[str]:
    """Return dictionary skills found in text, case-insensitively."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    searchable_text = _normalized_skill(text)
    return {
        original_skill
        for normalized_skill, original_skill in NORMALIZED_SKILLS.items()
        if re.search(
            rf"(?<!\w){re.escape(normalized_skill)}(?!\w)", searchable_text
        )
    }


def _tfidf_similarity(resume_text: str, job_description_text: str) -> float:
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, job_description_text])
    return float(cosine_similarity(vectors[0:1], vectors[1:2])[0, 0])


def _sentence_similarity(sentence: str, job_description_text: str) -> float:
    sentence_clean = clean_text(sentence)
    if not sentence_clean:
        return 0.0
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([sentence_clean, clean_text(job_description_text)])
    return float(cosine_similarity(vectors[0:1], vectors[1:2])[0, 0])


def _resume_annotations(
    resume_text: str,
    job_description_text: str,
    job_skills: set[str],
) -> list[dict[str, object]]:
    """Classify resume sentences by their signal for the target role."""
    annotations: list[dict[str, object]] = []
    fragments = re.split(r"(?<=[.!?])\s+|\n+", resume_text.strip())
    for fragment in fragments:
        text = fragment.strip()
        cleaned = clean_text(text)
        if not cleaned:
            continue
        sentence_skills = extract_skills(text)
        matched_skills = sorted(sentence_skills & job_skills)
        similarity = _sentence_similarity(text, job_description_text)
        if matched_skills:
            label = "matched"
            reason = "Contains skills requested for this role."
        elif len(cleaned.split()) >= 6 and similarity < 0.05:
            label = "low_relevance"
            reason = "This sentence has little detectable overlap with the target role."
        else:
            label = "neutral"
            reason = "Potentially useful context; review it for role relevance."
        annotations.append(
            {
                "text": text,
                "label": label,
                "reason": reason,
                "matched_skills": matched_skills,
                "relevance_score": round(similarity * 100, 1),
            }
        )
    return annotations


def analyze_match(resume_text: str, job_description_text: str) -> dict[str, object]:
    """Compute the blended match score and skill-gap details."""
    resume_clean = clean_text(resume_text)
    job_clean = clean_text(job_description_text)
    if not resume_clean or not job_clean:
        raise ValueError("Resume and job description must both contain usable text")

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description_text)
    matched_skills = sorted(resume_skills & job_skills)
    missing_skills = sorted(job_skills - resume_skills)
    annotations = _resume_annotations(resume_text, job_description_text, job_skills)

    tfidf_similarity = _tfidf_similarity(resume_clean, job_clean)
    skill_overlap_ratio = (
        len(matched_skills) / len(job_skills) if job_skills else 0.0
    )
    final_score = 100 * (
        TFIDF_WEIGHT * tfidf_similarity
        + SKILL_OVERLAP_WEIGHT * skill_overlap_ratio
    )

    return {
        "match_score": round(final_score, 1),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "resume_skill_count": len(resume_skills),
        "job_required_skill_count": len(job_skills),
        "resume_annotations": annotations,
    }


if __name__ == "__main__":
    strong_match = analyze_match(
        "Python developer with SQL, Docker, AWS, and teamwork experience.",
        "We need Python, SQL, Docker, AWS, and teamwork skills.",
    )
    weak_match = analyze_match(
        "Graphic designer experienced with Figma and communication.",
        "We need Python, SQL, Docker, AWS, and Kubernetes skills.",
    )
    assert strong_match["match_score"] > weak_match["match_score"]
    assert set(strong_match["matched_skills"]) == {
        "python", "sql", "docker", "aws", "teamwork"
    }
    assert "kubernetes" in weak_match["missing_skills"]
    print(f"strong match: {strong_match}")
    print(f"weak match: {weak_match}")
