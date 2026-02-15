from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from services.scraper import extract_text_from_wikipedia
from services.llm_service import generate_quiz_from_text
from pydantic import BaseModel
import json

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ CORS FIX FOR PRODUCTION
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # local frontend
        "https://wiki-quiz-crl770xwf-dssaramarajus-projects.vercel.app",  # your vercel frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Root check
@app.get("/")
def read_root():
    return {"message": "AI Wiki Quiz Generator Backend Running 🚀"}


# Generate Quiz
@app.post("/generate-quiz")
def generate_quiz(url: str, db: Session = Depends(get_db)):
    try:
        text = extract_text_from_wikipedia(url)
        quiz_data = generate_quiz_from_text(text)

        title = url.split("/")[-1].replace("_", " ")

        new_quiz = models.Quiz(
            url=url,
            title=title,
            content=text,
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get History
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


# Get Quiz by ID
@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return {
        "id": quiz.id,
        "title": quiz.title,
        "quiz": json.loads(quiz.quiz_data),
        "score": quiz.score
    }


# Update Score
class ScoreUpdate(BaseModel):
    score: int


@app.put("/quiz/{quiz_id}/score")
def update_score(quiz_id: int, score_data: ScoreUpdate, db: Session = Depends(get_db)):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz.score = score_data.score
    db.commit()

    return {"message": "Score updated successfully"}
