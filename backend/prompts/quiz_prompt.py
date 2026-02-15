QUIZ_PROMPT_TEMPLATE = """
You are an expert quiz generator.

Based STRICTLY on the following Wikipedia article content:

-----------------------
{content}
-----------------------

Instructions:

1. Generate 5 to 10 multiple choice questions.
2. Each question must include:
   - question (string)
   - options (array of 4 choices)
   - answer (must exactly match one option)
   - explanation (short, based only on the article content)
   - difficulty (easy / medium / hard)

3. Questions must:
   - Be factual and grounded in the provided content.
   - Not include information outside the content.
   - Have varied difficulty levels.

4. Also suggest 3 to 5 related Wikipedia topics for further reading.

Return output ONLY in valid JSON format structured like this:

{{
  "quiz": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "...",
      "difficulty": "easy",
      "explanation": "..."
    }}
  ],
  "related_topics": ["topic1", "topic2"]
}}

DO NOT include any extra text outside JSON.
"""
