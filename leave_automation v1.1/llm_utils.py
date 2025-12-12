# # llm_utils.py
# import os
# import openai

# openai.api_key = os.getenv("OPENAI_API_KEY")

# CLASSIFY_PROMPT = """
# You are an assistant that takes a leave reason and:
# 1) Classify urgency as one of: Low, Medium, High.
# 2) Give a one-sentence summary of the reason.

# Input:
# {reason}

# Output JSON format exactly:
# {{"urgency":"<Low|Medium|High>", "summary":"<one-sentence summary>"}}
# """

# def classify_and_summarize(reason_text):
#     prompt = CLASSIFY_PROMPT.format(reason=reason_text)
#     resp = openai.ChatCompletion.create(
#         model="gpt-4o-mini",    # replace with your available model
#         messages=[{"role":"user","content":prompt}],
#         temperature=0.0,
#         max_tokens=200
#     )
#     content = resp["choices"][0]["message"]["content"].strip()
#     # Best-effort parse JSON out of content
#     import json, re
#     # Remove possible surrounding text
#     json_text = re.search(r'\{[\s\S]*\}', content)
#     if json_text:
#         parsed = json.loads(json_text.group(0))
#         return {"urgency": parsed.get("urgency"), "summary": parsed.get("summary")}
#     else:
#         # fallback: attempt manual extraction
#         return {"urgency":"Unknown", "summary": reason_text[:200]}

# llm_utils.py
import os
import json
import re
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CLASSIFY_PROMPT = """
You are an assistant that takes a leave reason and:
1) Classify urgency as one of: Low, Medium, High.
2) Give a one-sentence summary of the reason.

Input:
{reason}

Return JSON in EXACT format:
{{"urgency":"<Low|Medium|High>", "summary":"<one-sentence summary>"}}
"""

def classify_and_summarize(reason_text: str):
    try:
        prompt = CLASSIFY_PROMPT.format(reason=reason_text)

        response = client.chat.completions.create(
            model="gpt-4o-mini",    # update this model name as needed
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=200
        )

        content = response.choices[0].message.content.strip()

        # Extract JSON using regex (LLMs sometimes add formatting)
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            parsed = json.loads(json_match.group(0))
            return {
                "urgency": parsed.get("urgency"),
                "summary": parsed.get("summary")
            }

        # fallback
        return {
            "urgency": "Unknown",
            "summary": reason_text[:200]
        }

    except Exception as e:
        print("LLM call failed:", e)
        return {
            "urgency": "Unknown",
            "summary": reason_text[:200]
        }