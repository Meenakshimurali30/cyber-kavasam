"""
test_engine.py: Comprehensive test suite for Cyber Kavasam (சைபர் கவசம்).
Tests Engine, Rules, Safe Signal Handling, ML Model, API Endpoints, Security Headers,
Rate Limiting, PII Redaction, CSV Formula Injection Guards, and Gold Set Benchmark.
"""

import os
import sys
import json
import pytest

# Ensure root workspace directory is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.engine import (
    check_message, detect_language, analyze_url, is_official_domain,
    normalize_text, KavasamMLModel, MODEL_VERSION, MODEL_PATH, MESSAGES_CSV
)
from app.server import create_app, redact_pii, sanitize_csv_cell, FEEDBACK_CSV


# ==========================================
# 1. LANGUAGE DETECTION TESTS
# ==========================================
@pytest.mark.parametrize("text,expected_lang", [
    ("உங்கள் வங்கி கணக்கு இன்று முடக்கப்படும். உடனே KYC புதுப்பிக்கவும்.", "ta"),
    ("TNEB மின் கட்டணம் செலுத்தவில்லை என்றால் இன்றிரவு மின்சாரம் துண்டிக்கப்படும்.", "ta"),
    ("Unga Canara Bank account block aagum. Udane KYC renew panunga.", "tanglish"),
    ("Machi naan 500 Rs Gpay panren, movie ticket book pannidu.", "tanglish"),
    ("Tonight 9.30 PM current cut pannuvanga. Officer number call panunga.", "tanglish"),
    ("Dear customer, your SBI account will be blocked within 24 hours.", "en"),
    ("Your Ola ride OTP is 6192. Please share with driver Vijay.", "en"),
])
def test_language_detection(text, expected_lang):
    assert detect_language(text) == expected_lang


# ==========================================
# 2. SCAMS FLAGGED (PARAMETRISED - TA, TANGLISH, EN)
# ==========================================
@pytest.mark.parametrize("scam_text,expected_verdict", [
    # Tamil Scams
    ("எஸ்பிஐ வாடிக்கையாளர் கவனத்திற்கு: உங்கள் வங்கி கணக்கு இன்றோடு முடக்கப்படும். உடனே http://sbi-kyc-verify.xyz பார்க்கவும்.", ["Likely Scam", "Suspicious"]),
    ("TNEB எச்சரிக்கை: உங்கள் முந்தைய மாத மின் கட்டணம் செலுத்தப்படாததால் இன்று இரவு 9.30 மணிக்கு மின்சாரம் துண்டிக்கப்படும். உடனே 9840184712 அழைக்கவும்.", ["Likely Scam", "Suspicious"]),
    ("மும்பை சைபர் கிரைம் போலீஸ்: உங்கள் ஆதார் எண் பண மோசடி வழக்கில் சிக்கியுள்ளது. டிஜிட்டல் கைது தவிர்க்க ஸ்கைப் காலில் 8939012345 வரவும்.", ["Likely Scam", "Suspicious"]),
    ("வீட்டிலிருந்தே வேலை! யூடியூப் வீடியோக்களுக்கு லைக் செய்து தினமும் ரூ 3000 சம்பாதிக்கலாம். வாட்ஸ்அப் 7358012345 தொடர்பு கொள்ளவும்.", ["Likely Scam", "Suspicious"]),
    ("உடனடி தனிநபர் கடன் ரூ 5,00,000 ஒப்புதல் அளிக்கப்பட்டது. ஆவணம் இன்றி உடனே பெற http://192.168.1.105/loan.apk பதிவிறக்கம் செய்க.", ["Likely Scam", "Suspicious"]),
    
    # Tanglish Scams
    ("Dear customer unga Canara Bank account block aagiruku. Udane KYC renew panna http://cutt.ly/canara-kyc click panunga.", ["Likely Scam", "Suspicious"]),
    ("TNEB Power Cut Alert: Unga previous bill pay aagala. Tonight 9.30 PM current cut pannuvanga. Officer 9840192837.", ["Likely Scam", "Suspicious"]),
    ("Delhi Police Cyber Cell: Unga perla drugs parcel seize pannirukom. Arrest warrant stop panna WhatsApp video call 9876541230 varavum.", ["Likely Scam", "Suspicious"]),
    ("Part time job: Daily YouTube video likes panni Rs 2500 earn pannalam. Contact HR on WhatsApp 8939019283.", ["Likely Scam", "Suspicious"]),
    ("Sir mistake ah unga GPay ku Rs 4500 anupiten. Intha link http://is.gd/refund-pin click panni UPI pin pottu return anupunga.", ["Likely Scam", "Suspicious"]),

    # English Scams
    ("Dear customer, your SBI bank account has been deactivated due to incomplete KYC. Visit http://sbi-kyc-portal.xyz/login", ["Likely Scam", "Suspicious"]),
    ("TNEB Alert: Electricity power disconnection scheduled tonight at 9:30 PM due to unpaid bill. Contact electricity officer immediately at 9840123456.", ["Likely Scam", "Suspicious"]),
    ("CBI CYBER CRIME CELL: Arrest warrant issued under PMLA for money laundering parcel sent via FedEx. Join video call 9876501234.", ["Likely Scam", "Suspicious"]),
    ("I accidentally sent Rs 10,000 to your PhonePe account. Kindly click http://bit.ly/phonepe-reverse and enter your UPI PIN to refund.", ["Likely Scam", "Suspicious"]),
    ("Work From Home: Earn Rs 3,000 - Rs 8,000 daily by rating Google Maps places. Message manager on WhatsApp at 9444081920.", ["Likely Scam", "Suspicious"]),
    ("Pre-approved personal loan of Rs 2,50,000 waiting for you. Zero documentation. Download APK: http://192.168.1.10/loan.apk", ["Likely Scam", "Suspicious"]),
])
def test_scams_flagged(scam_text, expected_verdict):
    result = check_message(scam_text)
    assert result["verdict"] in expected_verdict
    assert result["risk"] >= 30
    assert len(result["reasons"]) > 0
    assert len(result["advice"]) > 0


# ==========================================
# 3. SAFE MESSAGES NOT FLAGGED (PARAMETRISED - TA, TANGLISH, EN)
# ==========================================
@pytest.mark.parametrize("safe_text", [
    # Tamil Safe
    "உங்கள் எஸ்பிஐ கணக்கு XX4829-லிருந்து ரூ 1,500 பற்று வைக்கப்பட்டது (debited). மீதி இருப்பு ரூ 18,450. பரிவர்த்தனை எண் 91823901.",
    "ஹெச்டிஎஃப்சி வங்கி OTP எண் 482910. இந்த எண்ணை யாரிடமும் ஒருபோதும் பகிராதீர்கள். வங்கி ஊழியர்கள் ஒருபோதும் OTP கேட்க மாட்டார்கள்.",
    "Swiggy: உங்கள் உணவு டெலிவரி செய்ய வந்துவிட்டது. டெலிவரி பார்ட்னரிடம் OTP 3819-ஐ பகிர்ந்து உணவை பெற்றுக்கொள்ளவும்.",
    "அம்மா, நான் கடைக்கு போய் மளிகை சாமான் வாங்கிட்டு ஒரு அரை மணி நேரத்துல வீட்டுக்கு வந்திடுறேன்.",
    "அண்ணா, காலேஜ் எக்ஸாம் பீஸ் கட்ட 1500 ரூபாய் கூகுள் பே பண்ணுங்க. இன்னைக்கு சாயங்காலம் கட்டணும்.",
    "TNEB நுகர்வோர் எண் 0928172-க்கான மின்கட்டணம் ரூ 1,240 பெறப்பட்டது. ரசீது பார்க்க அதிகாரப்பூர்வ தளம்: https://www.tangedco.gov.in",

    # Tanglish Safe
    "Unga HDFC A/c XX3920 la irunthu Rs 750 debit aagiruku towards Swiggy. Avl Bal Rs 14,250.",
    "Axis Bank OTP for online purchase of Rs 1200 is 581902. Do not share this OTP with anyone for security.",
    "Zomato: Share delivery OTP 9182 with delivery partner Murugan. Enjoy your food!",
    "Ola ride OTP is 4019. Driver Selvam will pick you up shortly. Share OTP to start ride.",
    "Machi naan movie tickets book panniten, unga share 350 GPay pannidu da.",
    "Akka unga account ku 2000 Google Pay la anupiten, check pannitu sollunga.",

    # English Safe
    "Rs 2,450.00 debited from your SBI A/c XX8471 on 24-Oct. Avl Bal: Rs 42,109. Ref: UPI/29182049182.",
    "Your ICICI Bank OTP for transaction of Rs 3,500 at Flipkart is 839201. Do not share this OTP with anyone, including bank officials.",
    "Share OTP 9204 with your Swiggy delivery partner to receive order from Saravana Bhavan.",
    "Your Ola ride OTP is 6192. Please share with driver Vijay to start your trip.",
    "SBI Security Alert: Banks never call or message asking for your password, ATM PIN, or OTP. Keep your banking credentials private.",
    "Hi Dad, I have transferred Rs 5,000 to your bank account for electricity and water bills.",
    "Hey Priya, sent you Rs 450 on Google Pay for yesterday's dinner. Thanks!",
])
def test_safe_messages_not_flagged(safe_text):
    result = check_message(safe_text)
    assert result["verdict"] == "Safe"
    assert result["risk"] < 30


# ==========================================
# 4. OTP WARNING VS REQUEST & DRIVER OTP
# ==========================================
def test_otp_warning_is_safe():
    warning_sms = "Dear Customer, OTP for your netbanking is 849201. Never share your OTP with anyone. Bank staff never asks for OTP."
    res = check_message(warning_sms)
    assert res["verdict"] == "Safe"
    assert res["risk"] < 30

def test_driver_and_delivery_otp_is_safe():
    ride_msg = "Ola: Your ride OTP is 4829. Share this OTP with driver Ramesh to begin trip."
    res_ride = check_message(ride_msg)
    assert res_ride["verdict"] == "Safe"

    delivery_msg = "Zomato: Please share OTP 9102 with your delivery partner upon delivery."
    res_deliv = check_message(delivery_msg)
    assert res_deliv["verdict"] == "Safe"

def test_otp_theft_is_flagged():
    theft_msg = "Bank manager speaking: Your debit card is blocked. Please share the OTP received on your mobile with representative 9840123456."
    res_theft = check_message(theft_msg)
    assert res_theft["verdict"] in ["Likely Scam", "Suspicious"]
    assert res_theft["risk"] >= 50


# ==========================================
# 5. URL ANALYSIS TESTS
# ==========================================
def test_url_shortener_flagged():
    findings = analyze_url("http://bit.ly/sbi-kyc-update")
    assert any(f["rule_id"] == "RULE_SHORT_URL" for f in findings)

def test_suspicious_tld_flagged():
    findings = analyze_url("http://tneb-bill-payment.top/pay")
    assert any(f["rule_id"] == "RULE_SUSPICIOUS_TLD" for f in findings)

def test_lookalike_brand_domain_flagged():
    findings = analyze_url("http://sbi-verification-secure.com/login")
    assert any(f["rule_id"] == "RULE_LOOKALIKE_DOMAIN" for f in findings)

def test_raw_ip_url_flagged():
    findings = analyze_url("http://192.168.1.105/apk/app.apk")
    assert any(f["rule_id"] == "RULE_RAW_IP_URL" for f in findings)
    assert any(f["rule_id"] == "RULE_SUSPICIOUS_APK" for f in findings)

def test_official_domains_not_flagged():
    assert is_official_domain("www.tangedco.gov.in") is True
    assert is_official_domain("pmkisan.gov.in") is True
    assert is_official_domain("onlinesbi.sbi") is True
    assert len(analyze_url("https://www.tangedco.gov.in/bill")) == 0
    assert len(analyze_url("https://pmkisan.gov.in/status")) == 0


# ==========================================
# 6. HIGHLIGHT SPANS VALIDATION
# ==========================================
def test_highlight_spans_in_bounds():
    msg = "TNEB Power Cut Alert: Electricity disconnect tonight at 9:30 PM. Call officer 9840184712."
    res = check_message(msg)
    spans = res["highlight_spans"]
    norm_text = res["normalised_text"]

    for span in spans:
        start = span["start"]
        end = span["end"]
        assert 0 <= start < end <= len(norm_text)
        assert span["text"] == norm_text[start:end]


# ==========================================
# 7. BILINGUAL REASONS & ADVICE
# ==========================================
def test_bilingual_reasons_and_advice():
    msg = "மும்பை சைபர் கிரைம் போலீஸ்: உங்கள் ஆதார் எண் சட்டவிரோத பணப் பரிவர்த்தனையில் பயன்படுத்தப்பட்டுள்ளது. டிஜிட்டல் கைது தவிர்க்க ஸ்கைப் காலில் வரவும்."
    res = check_message(msg)
    assert len(res["reasons"]) > 0
    for r in res["reasons"]:
        assert "en" in r and len(r["en"]) > 5
        assert "ta" in r and len(r["ta"]) > 5

    assert len(res["advice"]) >= 2
    for a in res["advice"]:
        assert "en" in a and len(a["en"]) > 5
        assert "ta" in a and len(a["ta"]) > 5


# ==========================================
# 8. GOLD TEST SET BENCHMARK ACCURACY
# ==========================================
def test_gold_test_set_accuracy():
    import csv
    gold_path = os.path.join(BASE_DIR, "data", "gold_test.csv")
    assert os.path.exists(gold_path), "gold_test.csv must exist"

    correct = 0
    total = 0

    with open(gold_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row["text"]
            true_label = row["label"].strip().lower()
            res = check_message(text)
            pred_label = "scam" if res["verdict"] in ["Likely Scam", "Suspicious"] else "safe"
            if pred_label == true_label:
                correct += 1
            total += 1

    accuracy = correct / total
    # Honest threshold requirement: >= 90%
    assert total >= 70, f"Expected 70+ gold samples, got {total}"
    assert accuracy >= 0.90, f"Gold test accuracy was {accuracy*100:.2f}%, expected >= 90%"


# ==========================================
# 9. MODEL PERSISTENCE & HASH VERIFICATION
# ==========================================
def test_model_save_and_load(tmp_path):
    temp_model_path = os.path.join(tmp_path, "test_kavasam.joblib")
    model = KavasamMLModel()
    model.train(["scam bank block kyc", "hello mom dinner at home"], ["scam", "safe"])
    model.save(temp_model_path)

    assert os.path.exists(temp_model_path)
    loaded = KavasamMLModel.load_or_train(model_path=temp_model_path, dataset_path=MESSAGES_CSV)
    assert loaded.pipeline is not None
    proba = loaded.predict_proba("scam bank kyc update")
    assert 0.0 <= proba <= 1.0


# ==========================================
# 10. API ENDPOINTS & FLASK CLIENT TESTS
# ==========================================
@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["version"] == MODEL_VERSION

def test_api_check_single(client):
    res = client.post("/api/v1/check", json={
        "message": "Dear customer, your SBI account is blocked. Update KYC at http://bit.ly/sbi-fake"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["verdict"] in ["Likely Scam", "Suspicious"]
    assert "risk" in data
    assert "confidence" in data
    assert "reasons" in data

def test_api_check_alias(client):
    res = client.post("/check", json={
        "message": "Swiggy: Share OTP 9182 with delivery partner Murugan."
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["verdict"] == "Safe"

def test_api_batch_check(client):
    batch = [
        "Dear customer, your account will be blocked today: http://sbi-fake.xyz",
        "Hi Mom, reaching home in 20 minutes.",
        "TNEB power disconnection tonight at 9:30 PM call 9840123456"
    ]
    res = client.post("/api/v1/check/batch", json={"messages": batch})
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == 3
    assert len(data["results"]) == 3

def test_api_batch_limit_exceeded(client):
    # Maximum 20 allowed
    over_limit = ["Message" + str(i) for i in range(25)]
    res = client.post("/api/v1/check/batch", json={"messages": over_limit})
    assert res.status_code == 400
    assert "limit" in res.get_json()["error"].lower()

def test_security_headers(client):
    res = client.get("/health")
    headers = res.headers
    assert "Content-Security-Policy" in headers
    assert "fonts.gstatic.com" in headers["Content-Security-Policy"]
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


# ==========================================
# 11. FEEDBACK REDACTION & CSV INJECTION GUARD
# ==========================================
def test_pii_redaction():
    text_with_pii = "Contact me at 9840123456 or test@gmail.com or send to user@okicici"
    redacted = redact_pii(text_with_pii)
    assert "9840123456" not in redacted
    assert "test@gmail.com" not in redacted
    assert "user@okicici" not in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_UPI]" in redacted

def test_csv_formula_injection_guard():
    # Dangerous formula prefixes
    assert sanitize_csv_cell("=cmd|'/C calc'!A0") == "'=cmd|'/C calc'!A0"
    assert sanitize_csv_cell("+12345") == "'+12345"
    assert sanitize_csv_cell("-2+5") == "'-2+5"
    assert sanitize_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert sanitize_csv_cell("Normal text") == "Normal text"

def test_feedback_endpoint(client):
    payload = {
        "message": "Call 9840123456 for loan, or email scam@fake.com",
        "verdict": "Likely Scam",
        "user_agreed": True,
        "comments": "=SUM(1,2) test injection"
    }
    res = client.post("/api/v1/feedback", json=payload)
    assert res.status_code == 200
    assert res.get_json()["status"] == "success"

    # Verify that raw phone / email are NOT in the written file
    if os.path.exists(FEEDBACK_CSV):
        with open(FEEDBACK_CSV, "r", encoding="utf-8") as f:
            content = f.read()
            assert "9840123456" not in content
            assert "scam@fake.com" not in content
            # Ensure formula injection was sanitized
            assert "'=SUM" in content or "=SUM" not in content


# ==========================================
# 12. API ERROR HANDLING (400, 413, 429)
# ==========================================
def test_api_400_bad_json(client):
    res = client.post("/api/v1/check", data="not json", content_type="application/json")
    assert res.status_code == 400

def test_api_413_payload_too_large(client):
    huge_msg = "A" * 2500
    res = client.post("/api/v1/check", json={"message": huge_msg})
    assert res.status_code == 413
    assert "maximum" in res.get_json()["error"].lower()

def test_api_rate_limiting(client, monkeypatch):
    # Temporarily set rate limit low to test 429
    monkeypatch.setattr("app.server.RATE_LIMIT_PER_MINUTE", 3)
    # Clear IP cache
    from app.server import ip_requests
    ip_requests.clear()

    # 3 allowed requests
    for _ in range(3):
        r = client.post("/api/v1/check", json={"message": "Normal check"})
        assert r.status_code == 200

    # 4th request should get 429
    r4 = client.post("/api/v1/check", json={"message": "Exceeded check"})
    assert r4.status_code == 429
    assert r4.get_json()["status"] == 429
