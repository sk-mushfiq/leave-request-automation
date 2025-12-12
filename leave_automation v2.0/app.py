# app.py

import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from llm_utils import classify_and_summarize
from sheets_utils import append_row_to_sheet
from datetime import datetime

load_dotenv()

app = Flask(__name__)

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")  # optional

def send_slack_notification(text: str):
    if not SLACK_WEBHOOK:
        return 0, "no-slack"
    try:
        resp = requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=10)
        return resp.status_code, resp.text
    except Exception as e:
        print("Slack error:", e)
        return 0, str(e)

# @app.route("/webhook", methods=["POST"])
@app.route("/process-leave", methods=["POST"])

def webhook():
    try:
        data = request.get_json(silent=True) or request.form.to_dict() or {}
        # Normalize fields (adjust to what your form sends)
        employee_name = data.get("employee_name") or data.get("name") or data.get("employee") or "Unknown"
        department = data.get("department", "Unknown")
        leave_date = data.get("leave_date", data.get("date", "Unknown"))
        reason = (data.get("reason") or data.get("message") or "")[:3000]
        timestamp = datetime.utcnow().isoformat() + "Z"

        # LLM
        llm_result = classify_and_summarize(reason)
        urgency = llm_result.get("urgency", "Unknown")
        summary = llm_result.get("summary", "")

        # Log to Google Sheets (best-effort)
        sheet_row = [timestamp, employee_name, department, leave_date, reason, summary, urgency]
        try:
            append_row_to_sheet(sheet_row)
            sheet_status = "ok"
        except Exception as e:
            sheet_status = f"error: {e}"
            print("Sheets error:", e)

        # Slack notify
        slack_text = (
            f"*Leave Request*\nEmployee: *{employee_name}*\nDepartment: {department}\n"
            f"Date: {leave_date}\nSummary: {summary}\nUrgency: {urgency}\nTime(UTC): {timestamp}"
        )
        slack_status, slack_resp = send_slack_notification(slack_text)

        # Return the response (n8n will forward to user)
        return jsonify({
            "success": True,
            "message": f"Leave request processed for {employee_name}",
            "data": {
                "employee": employee_name,
                "department": department,
                "date": leave_date,
                "urgency": urgency,
                "summary": summary,
                "timestamp": timestamp
            },
            "logs": {
                "sheet_status": sheet_status,
                "slack_status": slack_status
            }
        }), 200
        #     "ok": True,
        #     "llm": llm_result,
        #     "sheet": sheet_status,
        #     "slack_status": slack_status
        # }), 200

    except Exception as e:
        # Always return JSON so n8n can forward a helpful message
        print("Server error:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
