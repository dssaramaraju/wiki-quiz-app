import os
import json
import ast
import requests
from dotenv import load_dotenv
from prompts.quiz_prompt import QUIZ_PROMPT_TEMPLATE

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def generate_quiz_from_content(content: str):
    try:
        trimmed_content = content[:8000]

        prompt = QUIZ_PROMPT_TEMPLATE.format(content=trimmed_content)

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
        )

        result = response.json()

        text_output = result["choices"][0]["message"]["content"].strip()

        # Remove markdown formatting
        if text_output.startswith("```"):
            text_output = text_output.replace("```json", "").replace("```", "").strip()

        # Extract JSON portion
        start = text_output.find("{")
        end = text_output.rfind("}") + 1
        json_string = text_output[start:end]

        try:
            quiz_data = json.loads(json_string)
        except:
            quiz_data = ast.literal_eval(json_string)

        return quiz_data

    except Exception as e:
        raise Exception(f"Error generating quiz from LLM: {str(e)}")
