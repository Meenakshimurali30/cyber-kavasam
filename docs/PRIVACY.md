# Privacy Architecture & Data Policy

**Cyber Kavasam (சைபர் கவசம்)** is built on a strict **Privacy-by-Design** foundation. As a tool designed to protect everyday citizens from cyber fraud, safeguarding citizen privacy is our primary engineering mandate.

---

## 1. What We NEVER Store

| Data Type | Policy | Technical Implementation |
|---|---|---|
| **Raw Message Content** | **Never Stored** | Processed entirely in-memory in ephemeral Python variables. Garbage-collected immediately after response dispatch. |
| **User Phone Numbers / Contacts** | **Never Stored** | Regex-based automatic sanitization masks all 10-digit Indian numbers and contact strings (`[REDACTED_PHONE]`). |
| **Financial Identifiers (UPI / Accounts)** | **Never Stored** | VPA addresses (`user@okhdfcbank`, `user@upi`) are stripped (`[REDACTED_UPI]`). |
| **IP Addresses** | **Ephemeral Only** | Client IP is used in volatile in-memory sliding windows for rate limiting (30 requests/min). Flushed after 60 seconds; never written to persistent disk or database. |
| **Tracking Cookies / Ad Trackers** | **Zero Trackers** | No analytics SDKs, third-party trackers, beacons, or third-party cookies are used. |

---

## 2. Server Logging Practices

Our production WSGI logs record strictly operational metadata. A representative production log line:

```text
2026-10-25 18:38:00 [INFO] CHECK: verdict=Likely Scam risk=88% lang=ta len=142 latency=14.2ms
```

**Notice**: The message body, sender identity, and receiver context are omitted from the log stream.

---

## 3. Voluntary User Feedback

When a citizen explicitly chooses to submit feedback ("Was this helpful? Yes / No"):

1. **Explicit Consent**: Initiated only by an affirmative click by the user.
2. **Double PII Redaction**:
   - Phone numbers masked to `[REDACTED_PHONE]`.
   - Email addresses masked to `[REDACTED_EMAIL]`.
   - UPI handles masked to `[REDACTED_UPI]`.
3. **CSV Formula Injection Mitigation**:
   - Spreadsheet injection attacks (cells starting with `=`, `+`, `-`, `@`, `\t`, `\r`) are automatically prepended with a single quote (`'`), neutralizing any macro execution.
4. **Air-Gapped From Training**:
   - Feedback records written to `data/feedback.csv` are **never** automatically ingested into model retraining loops, preventing poisoned or malicious feedback injection.

---

## 4. Security Headers & Browser Hardening

Every HTTP response dispatched by Cyber Kavasam includes industry-standard security headers:

- **Content-Security-Policy (CSP)**: `default-src 'self'; font-src 'self' https://fonts.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; script-src 'self'; img-src 'self' data:; connect-src 'self';`
  - Restricts resource loading to local origin and trusted Google Fonts CDN.
- **X-Content-Type-Options**: `nosniff` (prevents MIME-confusion attacks).
- **X-Frame-Options**: `DENY` (prevents clickjacking attacks).
- **Referrer-Policy**: `strict-origin-when-cross-origin` (prevents URL leakage).

---

## 5. Non-Legal Disclaimer

Cyber Kavasam is an automated assistant designed to help citizens assess cyber fraud indicators. It does not provide legal certificates or official police determinations. Citizens who have suffered financial losses are guided to immediately call the **National Cyber Crime Helpline at 1930** or visit **[cybercrime.gov.in](https://cybercrime.gov.in)**.
