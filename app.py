from datetime import datetime, timezone
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from models import SurveySubmission, StoredSurveyRecord
from storage import append_json_line

app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "*"}})

@app.route("/ping", methods=["GET"])
def ping():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "API is alive",
        "utc_time": datetime.now(timezone.utc).isoformat()
    })


@app.post("/v1/survey")
def submit_survey():
    # 1. Parse JSON safely
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            "error": "invalid_json",
            "detail": "Body must be application/json"
        }), 400

    # 2. Validate with Pydantic
    try:
        submission = SurveySubmission(**payload)
    except ValidationError as ve:
        return jsonify({
            "error": "validation_error",
            "detail": ve.errors()
        }), 422

    # 3. Generate submission_id if missing
    if not submission.submission_id:
        date_hour = datetime.utcnow().strftime("%Y%m%d%H")
        raw = submission.email + date_hour
        submission.submission_id = hashlib.sha256(raw.encode()).hexdigest()

    # 4. Capture user_agent
    submission.user_agent = request.headers.get("User-Agent")

    # 5. Build StoredSurveyRecord with server metadata
    record = StoredSurveyRecord(
        **submission.dict(),
        received_at=datetime.now(timezone.utc),
        ip=request.headers.get("X-Forwarded-For", request.remote_addr or "")
    )

    # 6. Save to NDJSON (storage.py handles hashing PII)
    append_json_line(record.dict())

    return jsonify({"status": "ok"}), 201


if __name__ == "__main__":
    app.run(port=0, debug=True)
