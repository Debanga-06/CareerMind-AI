"""
Project recommendations.

Rule-based (no LLM required): a small curated template library maps
common skills to concrete project ideas that exercise that skill. Skills
without a specific template fall back to a generic template so every
priority skill still gets a suggestion, without ever inventing a project
description that misrepresents what the skill actually involves.
"""
from typing import Dict, List

from app.schemas.career import SkillGap
from app.schemas.roadmap import ProjectRecommendation

_TEMPLATES: Dict[str, ProjectRecommendation] = {
    "python": ProjectRecommendation(
        title="CLI Data Utility",
        description="Build a command-line tool in Python that ingests a CSV/JSON dataset, cleans it, and outputs summary statistics or a report.",
        skills_used=["Python"],
        difficulty="Beginner",
    ),
    "machine learning": ProjectRecommendation(
        title="End-to-End ML Classifier",
        description="Train a classification model on a public dataset (e.g. via scikit-learn), evaluate it properly (train/test split, metrics), and wrap it in a small API for predictions.",
        skills_used=["Machine Learning", "Python"],
        difficulty="Intermediate",
    ),
    "deep learning": ProjectRecommendation(
        title="Image Classifier with a Pretrained Model",
        description="Fine-tune a pretrained CNN (transfer learning) on a small custom image dataset and evaluate accuracy vs. the base model.",
        skills_used=["Deep Learning", "PyTorch"],
        difficulty="Intermediate",
    ),
    "pytorch": ProjectRecommendation(
        title="Custom Neural Network from Scratch",
        description="Implement and train a small neural network in PyTorch on a toy dataset (e.g. MNIST) without high-level wrappers, to build real understanding of the training loop.",
        skills_used=["PyTorch"],
        difficulty="Intermediate",
    ),
    "large language models": ProjectRecommendation(
        title="RAG-Powered Q&A Bot",
        description="Build a retrieval-augmented Q&A tool over a small document set: chunk + embed the docs, store vectors, and answer questions by retrieving relevant chunks before generating a response.",
        skills_used=["Large Language Models", "RAG"],
        difficulty="Intermediate",
    ),
    "rag": ProjectRecommendation(
        title="RAG-Powered Q&A Bot",
        description="Build a retrieval-augmented Q&A tool over a small document set: chunk + embed the docs, store vectors, and answer questions by retrieving relevant chunks before generating a response.",
        skills_used=["RAG"],
        difficulty="Intermediate",
    ),
    "react": ProjectRecommendation(
        title="Dashboard Frontend",
        description="Build a React dashboard that fetches data from a public API and displays it with filters, search, and a couple of charts.",
        skills_used=["React", "JavaScript"],
        difficulty="Beginner",
    ),
    "fastapi": ProjectRecommendation(
        title="REST API with Auth",
        description="Build a small FastAPI backend with CRUD endpoints, request validation, and JWT-based authentication, documented via the built-in Swagger UI.",
        skills_used=["FastAPI", "Python"],
        difficulty="Intermediate",
    ),
    "docker": ProjectRecommendation(
        title="Containerize an Existing App",
        description="Write a Dockerfile (and docker-compose.yml if there's a database) for one of your existing projects, so it can be built and run identically on any machine.",
        skills_used=["Docker"],
        difficulty="Beginner",
    ),
    "kubernetes": ProjectRecommendation(
        title="Deploy a Containerized App to a Local Cluster",
        description="Take a Dockerized app and write Kubernetes manifests (Deployment + Service) to run it on a local cluster (e.g. minikube/kind), including a basic health check.",
        skills_used=["Kubernetes", "Docker"],
        difficulty="Advanced",
    ),
    "sql": ProjectRecommendation(
        title="Data Modeling + Analysis Project",
        description="Design a normalized schema for a small domain (e.g. an e-commerce store), load sample data, and write queries (joins, aggregations, window functions) to answer real business questions.",
        skills_used=["SQL"],
        difficulty="Beginner",
    ),
    "aws": ProjectRecommendation(
        title="Deploy a Serverless API",
        description="Deploy a small API using a serverless approach (e.g. Lambda + API Gateway) and connect it to a managed database or S3 for storage.",
        skills_used=["AWS"],
        difficulty="Intermediate",
    ),
    "git": ProjectRecommendation(
        title="Open-Source Contribution",
        description="Find a beginner-friendly open-source repo, fork it, make a small improvement (docs, bug fix, or test), and open a well-described pull request.",
        skills_used=["Git", "GitHub"],
        difficulty="Beginner",
    ),
}

_GENERIC_DIFFICULTY_BY_LEVEL = {
    "beginner": "Beginner",
    "intermediate": "Intermediate",
    "advanced": "Advanced",
    "expert": "Advanced",
}


def _generic_project(skill: str, experience_level: str) -> ProjectRecommendation:
    difficulty = _GENERIC_DIFFICULTY_BY_LEVEL.get(experience_level.strip().lower(), "Intermediate")
    return ProjectRecommendation(
        title=f"Applied {skill} Mini-Project",
        description=(
            f"Pick a small, real problem and solve it using {skill} end-to-end: define the "
            f"scope, build a working solution, and write a short README explaining your "
            f"approach and trade-offs."
        ),
        skills_used=[skill],
        difficulty=difficulty,
    )


def recommend_projects(
    skill_gap: SkillGap,
    experience_level: str,
    max_projects: int = 4,
) -> List[ProjectRecommendation]:
    target_skills = (skill_gap.priority_skills or skill_gap.develop_skills or skill_gap.strong_skills)[:max_projects]

    projects: List[ProjectRecommendation] = []
    seen_titles = set()
    for skill in target_skills:
        template = _TEMPLATES.get(skill.lower())
        project = template if template else _generic_project(skill, experience_level)
        if project.title not in seen_titles:
            seen_titles.add(project.title)
            projects.append(project)

    return projects
