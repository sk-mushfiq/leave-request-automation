# app.py
import os
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from llm_utils import classify_and_summarize
from sheets_utils import append_row_to_sheet
import requests
from datetime import datetime

load_dotenv()

app = Flask(__name__)

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
SHEET_ID = os.getenv("SHEETS_SPREADSHEET_ID")

def send_slack_notification(manager_identifier, message_text):
    payload = {"text": message_text}
    resp = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
    return resp.status_code, resp.text

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form.to_dict()
        # data = request.get_json() or request.form.to_dict()
        # Normalise fields
        employee_name = data.get("employee_name") or data.get("name") or data.get("employee")
        department = data.get("department", "Unknown")
        leave_date = data.get("leave_date", data.get("date", "Unknown"))
        reason = data.get("reason", data.get("message", ""))[:3000]  # limit size

        # Step 1: call LLM to classify & summarise
        llm_result = classify_and_summarize(reason)
        urgency = llm_result.get("urgency")
        summary = llm_result.get("summary")

        # Step 2: notify manager
        timestamp = datetime.utcnow().isoformat() + "Z"
        slack_msg = (
            f"*Leave Request*\n"
            f"Employee: *{employee_name}*\n"
            f"Department: {department}\n"
            f"Date: {leave_date}\n"
            f"Summary: {summary}\n"
            f"Urgency: {urgency}\n"
            f"Time(UTC): {timestamp}"
        )
        status_code, resp_text = send_slack_notification(os.getenv("MANAGER_SLACK_ID", ""), slack_msg)

        # Step 3: log to Google Sheets
        row = [timestamp, employee_name, department, leave_date, reason, summary, urgency, status_code]
        append_row_to_sheet(row)

        return jsonify({
            "ok": True,
            "slack_status": status_code,
            "llm": llm_result
        }), 200

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
