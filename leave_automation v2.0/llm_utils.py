# llm_utils.py

import os, re, json
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

Return JSON exactly like:
{{"urgency":"<Low|Medium|High>", "summary":"<one-sentence summary>"}}
"""

def classify_and_summarize(reason_text: str):
    try:
        prompt = CLASSIFY_PROMPT.format(reason=reason_text[:3000])
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",   # Replace with model you have access to
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=200
        )
        content = response.choices[0].message.content.strip()
        
        # Extract JSON using regex (LLMs sometimes add formatting)
        json_match = re.search(r"\{[\s\S]*\}", content)
        if json_match:
            parsed = json.loads(json_match.group(0))
            return {"urgency": parsed.get("urgency"), "summary": parsed.get("summary")}
        # fallback
        return {"urgency": "Unknown", "summary": reason_text[:200]}
    
    except Exception as e:
        # non-fatal: return sensible fallback so workflow continues
        print("LLM error:", e)
        return {"urgency": "Unknown", "summary": (reason_text or "")[:200]}
