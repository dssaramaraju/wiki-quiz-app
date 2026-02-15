import { useState } from "react";
import axios from "axios";

function App() {
  const [url, setUrl] = useState("");
  const [quizData, setQuizData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Generate Quiz
  const generateQuiz = async () => {
    if (!url) return;

    setLoading(true);
    setQuizData(null);
    setScore(null);
    setAnswers({});
    setShowHistory(false);

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/generate-quiz?url=${encodeURIComponent(url)}`
      );

      setQuizData(response.data);
    } catch (error) {
      console.error("Error generating quiz", error);
      alert("Error generating quiz");
    }

    setLoading(false);
  };

  // Submit Quiz
  const submitQuiz = async () => {
    if (!quizData) return;

    let calculatedScore = 0;

    quizData.quiz.quiz.forEach((q, index) => {
      if (answers[index] === q.answer) {
        calculatedScore++;
      }
    });

    setScore(calculatedScore);

    // Save score to backend
    try {
      await axios.post("http://127.0.0.1:8000/save-score", {
        quiz_id: quizData.id,
        score: calculatedScore,
      });
    } catch (error) {
      console.error("Error saving score");
    }
  };

  // Fetch History
  const fetchHistory = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/history");
      setHistory(response.data);
      setShowHistory(true);
    } catch (error) {
      console.error("Error fetching history");
    }
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>Wiki Quiz App</h1>

      {/* Input Section */}
      <input
        type="text"
        placeholder="Enter Wikipedia URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        style={{ width: "400px", padding: "8px" }}
      />
      <button
        onClick={generateQuiz}
        style={{ marginLeft: "10px", padding: "8px 12px" }}
      >
        Generate Quiz
      </button>

      <button
        onClick={fetchHistory}
        style={{ marginLeft: "10px", padding: "8px 12px" }}
      >
        Past Quizzes
      </button>

      {loading && <p>Generating quiz... Please wait ⏳</p>}

      {/* Quiz Section */}
      {quizData && !loading && (
        <div style={{ marginTop: "30px" }}>
          <h2>{quizData.title}</h2>

          {quizData.quiz.quiz.map((question, index) => (
            <div
              key={index}
              style={{
                border: "1px solid #ccc",
                padding: "15px",
                marginBottom: "15px",
              }}
            >
              <p>
                <b>
                  Q{index + 1}. {question.question}
                </b>
              </p>

              {question.options.map((option, i) => (
                <div key={i}>
                  <input
                    type="radio"
                    name={`question-${index}`}
                    value={option}
                    onChange={() =>
                      setAnswers({ ...answers, [index]: option })
                    }
                  />
                  {option}
                </div>
              ))}

              {/* After Submit */}
              {score !== null && (
                <div style={{ marginTop: "10px" }}>
                  <p>
                    <b>Correct Answer:</b> {question.answer}
                  </p>

                  <p>
                    <b>Explanation:</b> {question.explanation}
                  </p>

                  <p>
                    <b>Difficulty:</b> {question.difficulty}
                  </p>
                </div>
              )}
            </div>
          ))}

          {score === null && (
            <button
              onClick={submitQuiz}
              style={{ padding: "10px 15px", marginTop: "10px" }}
            >
              Submit Quiz
            </button>
          )}

          {score !== null && (
            <h3>
              Your Score: {score} / {quizData.quiz.quiz.length}
            </h3>
          )}
        </div>
      )}

      {/* History Section (Separate Button Only) */}
      {showHistory && (
        <div style={{ marginTop: "40px" }}>
          <h2>Past Quizzes</h2>

          {history.map((quiz) => (
            <div key={quiz.id} style={{ marginBottom: "10px" }}>
              <b>ID:</b> {quiz.id} | <b>Title:</b> {quiz.title} |{" "}
              <b>Score:</b> {quiz.score ?? "Not Attempted"}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;