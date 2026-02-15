import os
import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db
import models
from services.scraper import scrape_wikipedia
from services.llm_service import generate_quiz_from_content

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ==============================
# CORS CONFIG (IMPORTANT)
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production you can restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# ROOT
# ==============================

@app.get("/")
def home():
    return {"message": "AI Wiki Quiz Generator Backend Running 🚀"}


# ==============================
# GENERATE QUIZ
# ==============================

@app.post("/generate-quiz")
def generate_quiz(url: str, db: Session = Depends(get_db)):

    # 1️⃣ Scrape Wikipedia
    scraped_data = scrape_wikipedia(url)

    # 2️⃣ Generate Quiz from LLM
    quiz_data = generate_quiz_from_content(scraped_data["content"])

    # 3️⃣ Store in DB
    new_quiz = models.Quiz(
        url=url,
        title=scraped_data["title"],
        content=scraped_data["content"],
        quiz_data=json.dumps(quiz_data),
        score=0
    )

    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    return {
        "id": new_quiz.id,
        "title": new_quiz.title,
        "quiz": quiz_data
    }


# ==============================
# GET QUIZ HISTORY
# ==============================

@app.get("/history")
def get_history(db: Session = Depends(get_db)):

    quizzes = db.query(models.Quiz).all()

    return [
        {
            "id": quiz.id,
            "title": quiz.title,
            "score": quiz.score
        }
        for quiz in quizzes
    ]


# ==============================
# GET QUIZ BY ID
# ==============================

@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):

    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

    if not quiz:
        return {"error": "Quiz not found"}

    return {
        "id": quiz.id,
        "title": quiz.title,
        "quiz": json.loads(quiz.quiz_data),
        "score": quiz.score
    }


# ==============================
# UPDATE SCORE
# ==============================

@app.put("/quiz/{quiz_id}/score")
def update_score(quiz_id: int, data: dict, db: Session = Depends(get_db)):

    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

    if not quiz:
        return {"error": "Quiz not found"}

    quiz.score = data.get("score", 0)

    db.commit()

    return {"message": "Score updated successfully"}
