"""
server.py: Production Flask API for Cyber Kavasam (சைபர் கவசம்).
Configured with security headers, privacy-preserving logging, in-memory rate limiting,
feedback sanitization (anti-PII, anti-CSV-injection), and served via Waitress.
"""

import os
import re
import csv
import time
import logging
from datetime import datetime, timezone
from threading import Lock
from flask import Flask, request, jsonify, send_from_directory
from app.engine import check_message, MODEL_VERSION, get_model

# Environment configurations
MAX_MESSAGE_LENGTH = int(os.environ.get("KAVASAM_MAX_LENGTH", "2000"))
RATE_LIMIT_PER_MINUTE = int(os.environ.get("KAVASAM_RATE_LIMIT", "30"))
ADMIN_TOKEN = os.environ.get("KAVASAM_ADMIN_TOKEN", "")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
FEEDBACK_CSV = os.path.join(BASE_DIR, "data", "feedback.csv")

# Configure logger (Message text is strictly NEVER logged)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("cyber_kavasam")

# ==========================================
# IN-MEMORY RATE LIMITER & STATS COUNTER
# ==========================================
rate_limit_lock = Lock()
ip_requests = {}

stats_lock = Lock()
stats_counters = {
    "total_checks": 0,
    "verdicts": {
        "Safe": 0,
        "Suspicious": 0,
        "Likely Scam": 0
    },
    "languages": {
        "ta": 0,
        "tanglish": 0,
        "en": 0
    }
}

def is_rate_limited(client_ip: str) -> bool:
    """Check if IP has exceeded requests per minute."""
    now = time.time()
    with rate_limit_lock:
        timestamps = ip_requests.get(client_ip, [])
        # Prune older than 60 seconds
        valid_timestamps = [t for t in timestamps if now - t < 60]
        if len(valid_timestamps) >= RATE_LIMIT_PER_MINUTE:
            ip_requests[client_ip] = valid_timestamps
            return True
        valid_timestamps.append(now)
        ip_requests[client_ip] = valid_timestamps
        return False

def record_stats(verdict: str, lang: str):
    """Update anonymous usage counters."""
    with stats_lock:
        stats_counters["total_checks"] += 1
        if verdict in stats_counters["verdicts"]:
            stats_counters["verdicts"][verdict] += 1
        if lang in stats_counters["languages"]:
            stats_counters["languages"][lang] += 1

# ==========================================
# PII REDACTION & CSV SANITIZATION
# ==========================================
def redact_pii(text: str) -> str:
    """Redact phone numbers, email addresses, and UPI IDs."""
    if not text:
        return ""
    # Redact Emails
    text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED_EMAIL]", text)
    # Redact UPI IDs (e.g., user@okhdfcbank, name@upi)
    text = re.sub(r"[a-zA-Z0-9.\-_]{2,49}@[a-zA-Z]{2,}", "[REDACTED_UPI]", text)
    # Redact Phone numbers (10 digits, optional country code)
    text = re.sub(r"(\+?91[\-\s]?)?[6-9]\d{9}", "[REDACTED_PHONE]", text)
    return text

def sanitize_csv_cell(value: str) -> str:
    """Prevent CSV formula injection by quoting trigger characters (=, +, -, @, \t, \r)."""
    if not value:
        return ""
    str_val = str(value)
    if str_val.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + str_val
    return str_val

# ==========================================
# FLASK APPLICATION FACTORY
# ==========================================
def create_app():
    app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

    # Ensure model is initialized at startup
    get_model()

    # Security Headers Hook
    @app.after_request
    def set_security_headers(response):
        csp = (
            "default-src 'self'; "
            "font-src 'self' https://fonts.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "script-src 'self'; "
            "img-src 'self' data:; "
            "connect-src 'self';"
        )
        response.headers["Content-Security-Policy"] = csp
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    # 1. UI route
    @app.route("/", methods=["GET"])
    def index():
        return send_from_directory(STATIC_DIR, "index.html")

    # 2. Health check
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "model_loaded": True,
            "version": MODEL_VERSION
        }), 200

    # 3. Check message (Single)
    @app.route("/api/v1/check", methods=["POST"])
    @app.route("/check", methods=["POST"])
    def check_single():
        client_ip = request.remote_addr or "127.0.0.1"
        if is_rate_limited(client_ip):
            return jsonify({
                "error": "Rate limit exceeded. Please wait a minute.",
                "status": 429
            }), 429

        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON body. Expected {'message': '...'}", "status": 400}), 400

        msg = data.get("message", "")
        if not isinstance(msg, str):
            return jsonify({"error": "'message' field must be a string", "status": 400}), 400

        if len(msg) > MAX_MESSAGE_LENGTH:
            return jsonify({
                "error": f"Message length ({len(msg)}) exceeds maximum allowed ({MAX_MESSAGE_LENGTH} characters)",
                "status": 413
            }), 413

        start_time = time.time()
        result = check_message(msg)
        latency_ms = (time.time() - start_time) * 1000

        # Log verdict, risk, language, length, latency (NEVER message text!)
        logger.info(
            f"CHECK: verdict={result['verdict']} risk={result['risk']}% "
            f"lang={result['detected_language']} len={len(msg)} latency={latency_ms:.1f}ms"
        )

        record_stats(result["verdict"], result["detected_language"])

        return jsonify(result), 200

    # 4. Check batch (Max 20)
    @app.route("/api/v1/check/batch", methods=["POST"])
    def check_batch():
        client_ip = request.remote_addr or "127.0.0.1"
        if is_rate_limited(client_ip):
            return jsonify({
                "error": "Rate limit exceeded. Please wait a minute.",
                "status": 429
            }), 429

        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON body. Expected {'messages': [...] }", "status": 400}), 400

        messages = data.get("messages")
        if not isinstance(messages, list):
            return jsonify({"error": "'messages' field must be an array of strings", "status": 400}), 400

        if len(messages) == 0:
            return jsonify({"error": "'messages' array cannot be empty", "status": 400}), 400

        if len(messages) > 20:
            return jsonify({"error": "Batch limit exceeded. Maximum 20 messages per batch request.", "status": 400}), 400

        results = []
        for msg in messages:
            if not isinstance(msg, str):
                results.append({"error": "Item must be a string", "verdict": "Error"})
                continue
            if len(msg) > MAX_MESSAGE_LENGTH:
                results.append({"error": "Message exceeds max length", "verdict": "Error"})
                continue

            res = check_message(msg)
            record_stats(res["verdict"], res["detected_language"])
            results.append(res)

        return jsonify({
            "count": len(results),
            "results": results
        }), 200

    # 5. User feedback
    @app.route("/api/v1/feedback", methods=["POST"])
    @app.route("/feedback", methods=["POST"])
    def submit_feedback():
        client_ip = request.remote_addr or "127.0.0.1"
        if is_rate_limited(client_ip):
            return jsonify({"error": "Rate limit exceeded.", "status": 429}), 429

        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid JSON body", "status": 400}), 400

        raw_msg = str(data.get("message", ""))
        verdict = str(data.get("verdict", ""))
        user_agreed = bool(data.get("user_agreed", True))
        comments = str(data.get("comments", ""))

        if len(raw_msg) > MAX_MESSAGE_LENGTH or len(comments) > MAX_MESSAGE_LENGTH:
            return jsonify({"error": "Input text too long", "status": 413}), 413

        # Redact PII (phones, emails, UPI)
        clean_msg = redact_pii(raw_msg)
        clean_comments = redact_pii(comments)

        # Sanitize against CSV formula injection
        safe_msg = sanitize_csv_cell(clean_msg)
        safe_comments = sanitize_csv_cell(clean_comments)
        safe_verdict = sanitize_csv_cell(verdict)
        timestamp = datetime.now(timezone.utc).isoformat()

        # Save to feedback.csv (never used for training automatically)
        os.makedirs(os.path.dirname(FEEDBACK_CSV), exist_ok=True)
        file_exists = os.path.exists(FEEDBACK_CSV)

        with open(FEEDBACK_CSV, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "verdict", "user_agreed", "redacted_message", "comments"])
            writer.writerow([timestamp, safe_verdict, user_agreed, safe_msg, safe_comments])

        logger.info(f"FEEDBACK: recorded agreed={user_agreed} verdict={verdict}")

        return jsonify({
            "status": "success",
            "message": "Feedback submitted successfully. Thank you!"
        }), 200

    # 6. Admin stats (Protected)
    @app.route("/api/v1/stats", methods=["GET"])
    def get_stats():
        if not ADMIN_TOKEN:
            return jsonify({"error": "Stats endpoint disabled. KAVASAM_ADMIN_TOKEN not set on server.", "status": 403}), 403

        client_token = request.headers.get("X-Admin-Token", "")
        if client_token != ADMIN_TOKEN:
            return jsonify({"error": "Unauthorized. Invalid admin token.", "status": 401}), 401

        with stats_lock:
            return jsonify({
                "status": "ok",
                "stats": stats_counters,
                "server_time": datetime.now(timezone.utc).isoformat()
            }), 200

    # Custom JSON Error Handlers
    @app.errorhandler(400)
    def handle_400(e):
        return jsonify({"error": "Bad request", "details": str(e), "status": 400}), 400

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "Resource not found", "status": 404}), 404

    @app.errorhandler(413)
    def handle_413(e):
        return jsonify({"error": "Payload too large", "details": str(e), "status": 413}), 413

    @app.errorhandler(429)
    def handle_429(e):
        return jsonify({"error": "Too many requests", "details": str(e), "status": 429}), 429

    @app.errorhandler(500)
    def handle_500(e):
        return jsonify({"error": "Internal server error", "status": 500}), 500

    return app

# For waitress-serve command
app = create_app()

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", "5000"))
    print(f"Cyber Kavasam server starting on http://127.0.0.1:{port}")
    serve(app, host="127.0.0.1", port=port)
