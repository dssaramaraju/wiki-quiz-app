from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, SessionLocal
from services.scraper import scrape_wikipedia
from services.llm_service import generate_quiz_from_content
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ PROPER CORS CONFIGURATION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Generate Quiz
@app.post("/generate-quiz")
def generate_quiz(url: str, db: Session = Depends(get_db)):

    scraped_data = scrape_wikipedia(url)
    quiz_data = generate_quiz_from_content(scraped_data["content"])

    new_quiz = models.Quiz(
        url=url,
        title=scraped_data["title"],
        content=scraped_data["content"],
        quiz_data=json.dumps(quiz_data),
        score=None
    )

    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)

    return {
        "id": new_quiz.id,
        "title": new_quiz.title,
        "quiz": quiz_data
    }


# Save Score
@app.post("/save-score")
def save_score(data: dict, db: Session = Depends(get_db)):

    quiz_id = data.get("quiz_id")
    score = data.get("score")

    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

    if quiz:
        quiz.score = score
        db.commit()
        return {"message": "Score saved successfully"}

    return {"message": "Quiz not found"}


# History
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
