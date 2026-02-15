import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "https://wiki-quiz-app-xac3.onrender.com";

export default function App() {
  const [url, setUrl] = useState("");
  const [quizData, setQuizData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch history
  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/history`);
      setHistory(res.data);
    } catch (err) {
      console.error("Error fetching history", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // Generate Quiz
  const generateQuiz = async () => {
    if (!url) return;

    setLoading(true);
    setQuizData(null);
    setScore(null);
    setAnswers({});

    try {
      const res = await axios.post(
        `${API_BASE}/generate-quiz?url=${encodeURIComponent(url)}`
      );

      setQuizData(res.data);
      setShowHistory(false);
    } catch (err) {
      console.error("Error generating quiz", err);
      alert("Error generating quiz. Please check backend.");
    }

    setLoading(false);
  };

  // Submit Quiz
  const submitQuiz = async () => {
    if (!quizData || !quizData.quiz) return;

    let calculatedScore = 0;

    quizData.quiz.quiz.forEach((q, index) => {
      if (answers[index] === q.answer) {
        calculatedScore++;
      }
    });

    setScore(calculatedScore);

    try {
      await axios.put(
        `${API_BASE}/quiz/${quizData.id}/score`,
        { score: calculatedScore }
      );
      fetchHistory();
    } catch (err) {
      console.error("Error updating score", err);
    }
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>🚀 AI Wiki Quiz Generator</h1>

      {/* URL Input */}
      <input
        type="text"
        placeholder="Enter Wikipedia URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        style={{ width: "400px", padding: "10px" }}
      />
      <button
        onClick={generateQuiz}
        style={{ marginLeft: "10px", padding: "10px 20px" }}
      >
        Generate Quiz
      </button>

      <button
        onClick={() => setShowHistory(!showHistory)}
        style={{ marginLeft: "20px", padding: "10px 20px" }}
      >
        📜 Past Quizzes
      </button>

      {/* Loading Animation */}
      {loading && <h3>⏳ Generating quiz...</h3>}

      {/* Quiz Section */}
      {quizData && quizData.quiz && (
        <div style={{ marginTop: "30px" }}>
          <h2>{quizData.title}</h2>

          {quizData.quiz.quiz.map((q, index) => (
            <div key={index} style={{ marginBottom: "20px" }}>
              <h4>
                Q{index + 1}. {q.question}
              </h4>

              {q.options.map((option, i) => (
                <div key={i}>
                  <label>
                    <input
                      type="radio"
                      name={`question-${index}`}
                      value={option}
                      onChange={() =>
                        setAnswers({ ...answers, [index]: option })
                      }
                    />
                    {option}
                  </label>
                </div>
              ))}

              {score !== null && (
                <div style={{ marginTop: "5px" }}>
                  <strong>Correct Answer:</strong> {q.answer}
                  <br />
                  <strong>Explanation:</strong> {q.explanation}
                  <br />
                  <strong>Difficulty:</strong> {q.difficulty}
                </div>
              )}
            </div>
          ))}

          {score === null && (
            <button
              onClick={submitQuiz}
              style={{ padding: "10px 20px" }}
            >
              Submit Quiz
            </button>
          )}

          {score !== null && (
            <h3>🎯 Your Score: {score}</h3>
          )}
        </div>
      )}

      {/* History Section */}
      {showHistory && (
        <div style={{ marginTop: "40px" }}>
          <h2>📜 Past Quiz History</h2>

          {history.length === 0 && <p>No quizzes yet.</p>}

          {history.map((quiz) => (
            <div key={quiz.id} style={{ marginBottom: "10px" }}>
              <strong>ID:</strong> {quiz.id} |{" "}
              <strong>Title:</strong> {quiz.title} |{" "}
              <strong>Score:</strong> {quiz.score ?? 0}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
