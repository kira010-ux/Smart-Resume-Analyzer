"""Canonical skill vocabulary used by the resume/job matching analyzer."""

from __future__ import annotations

from typing import Final


SKILLS_BY_CATEGORY: Final[dict[str, tuple[str, ...]]] = {
    "programming_languages": (
        "python", "javascript", "typescript", "java", "c", "c++", "c#",
        "go", "golang", "rust", "ruby", "php", "swift", "kotlin",
        "r", "matlab", "sql", "bash", "powershell", "html", "css",
        "dart", "perl", "lua", "groovy",
    ),
    "frameworks": (
        "react", "react native", "angular", "vue", "svelte", "next.js",
        "node.js", "express", "fastapi", "django", "flask", "spring",
        "spring boot", "asp.net", ".net", "laravel", "ruby on rails",
        "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "bootstrap", "tailwind css", "jquery", "graphql",
        "flutter", "electron", "selenium", "cypress",
    ),
    "tools_platforms": (
        "git", "github", "gitlab", "bitbucket", "docker", "kubernetes",
        "terraform", "ansible", "jenkins", "github actions", "circleci",
        "aws", "amazon web services", "azure", "google cloud", "gcp",
        "heroku", "vercel", "netlify", "linux", "unix",
        "macos", "postgresql", "mysql", "sqlite", "mongodb",
        "elasticsearch", "firebase", "supabase", "oracle",
        "apache kafka", "rabbitmq", "rest api", "restful api", "websocket",
        "microservices", "jira", "confluence", "figma",
        "postman", "tableau", "power bi", "looker", "datadog", "new relic",
        "splunk", "networking", "oauth", "jwt",
        "openai api", "langchain", "machine learning", "deep learning",
        "natural language processing", "computer vision", "data analysis",
        "data visualization", "data engineering", "etl", "data structures",
        "algorithms", "object-oriented programming", "functional programming",
        "unit testing", "integration testing", "test-driven development",
        "continuous integration", "continuous deployment", "ci/cd",
    ),
    "soft_skills": (
        "communication", "written communication", "verbal communication",
        "presentation", "public speaking", "teamwork", "collaboration",
        "leadership", "mentoring", "coaching", "problem solving",
        "critical thinking", "analytical thinking", "creativity", "adaptability",
        "time management", "organization", "attention to detail", "work ethic",
        "decision making", "conflict resolution", "negotiation", "empathy",
        "emotional intelligence", "customer service", "stakeholder management",
        "relationship building", "self-motivation", "flexibility", "resilience",
        "strategic thinking", "documentation", "active listening", "interpersonal skills",
    ),
    "methodologies": (
        "agile", "scrum", "kanban", "waterfall", "lean", "six sigma",
        "safe", "extreme programming", "pair programming", "code review",
        "version control", "software development lifecycle", "sdlc",
        "product management", "project management", "program management",
        "requirements gathering", "user research", "user experience", "ux design",
        "ui design", "design thinking", "a/b testing", "quality assurance",
        "risk management", "change management", "business analysis", "roadmapping",
        "sprint planning", "backlog management", "devops", "site reliability engineering",
        "sre", "cybersecurity", "information security", "privacy", "compliance",
        "gdpr", "accessibility", "technical writing", "research", "recruiting",
    ),
}

# Flattened vocabulary for callers that only need to test membership.
ALL_SKILLS: Final[frozenset[str]] = frozenset(
    skill for skills in SKILLS_BY_CATEGORY.values() for skill in skills
)


def skills_by_category() -> dict[str, list[str]]:
    """Return a mutable copy suitable for API responses or UI metadata."""
    return {category: list(skills) for category, skills in SKILLS_BY_CATEGORY.items()}


if __name__ == "__main__":
    category_count = len(SKILLS_BY_CATEGORY)
    skill_count = len(ALL_SKILLS)
    print(f"{category_count} categories, {skill_count} unique skills")
    assert 150 <= skill_count <= 200
    assert all(skill == skill.lower() for skill in ALL_SKILLS)
