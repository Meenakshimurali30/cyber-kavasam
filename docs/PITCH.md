# Cyber Kavasam (சைபர் கவசம்) - Hackathon Pitch Deck & Demo Guide

**Event**: Viksit Bharat Hackathon  
**Theme**: Digital Safety & Cyber Fraud Awareness  
**Problem Statement**: Citizen Scam Detection and Reporting Assistant  
**Target Beneficiaries**: Ordinary citizens in Tamil Nadu, elderly citizens, and first-time smartphone users.

---

## Part 1: 7-Slide Pitch Deck Structure

### Slide 1: Title & The Human Problem
- **Headline**: "Cyber Kavasam: Shielding Tamil Nadu Citizens from SMS & WhatsApp Fraud"
- **The Reality**: In India, cyber fraud losses crossed ₹1,750 Crore in early 2024 alone. In Tamil Nadu, senior citizens and rural smartphone adopters are inundated with predatory SMS: fake TNEB power cuts, fake SBI KYC blocks, digital arrest calls, and YouTube like scams.
- **The Gap**: Most scam checkers are English-only, corporate-oriented, require cloud logins, or store private personal messages.
- **Our Solution**: A zero-install, privacy-first bilingual assistant that understands Tamil script, Tanglish, and English, delivers instant verdicts, and guides users straight to 1930 / Chakshu.

### Slide 2: Why Existing Tools Fail for Tamil Citizens
- **Script Nuance**: Scammers target victims using colloquial Tamil ("இன்றிரவு 9:30 மணிக்கு கரண்ட் கட்") or Tanglish ("unga Canara bank account block aagum"). Standard NLP models trained on formal English fail completely.
- **The "Cry Wolf" Problem**: Naive keyword filters flag real bank SMS ("Rs 500 debited from A/c XX4829") or legitimate delivery OTPs ("Share OTP with Swiggy partner"), destroying user trust.
- **Lack of Actionable Closure**: Citizens are left wondering, "Okay, this is a scam, but what do I do now?"

### Slide 3: The Hybrid Engine (Heuristics + ML)
- **Heuristic Layer (60% Weight)**: 26+ fine-tuned regex patterns operating with a Noisy-OR probabilistic combiner (`1 - ∏(1 - w_i)`).
  - Inspects shorteners (`bit.ly`, `tinyurl`), suspicious TLDs (`.xyz`, `.top`, `.click`), raw IPs (`http://192.168.x.x`), and lookalike bank domains (`sbi-kyc-verify.com` vs official `sbi.co.in`).
  - Safe-signal filters: Distinguishes "Never share your OTP" (security warning) from "Share OTP with officer" (scam request).
- **Machine Learning Layer (40% Weight)**:
  - Character n-gram TF-IDF (`analyzer="char_wb"`, `ngram_range=(2, 5)`) capturing roots across morphological variations.
  - Logistic Regression calibrated for high recall on unseen templates.
- **Explainability**: Top 5 red flags highlighted visually directly in the text with bilingual justifications.

### Slide 4: Production Benchmarks (Real Measured Numbers)
- **Dataset**: 3,180 synthetic deduplicated samples across 143 template groups spanning all 22 scam families and hard safe transactional alerts.
- **5-Fold Group Cross-Validation (by Template Group)**:
  - Mean Accuracy: **96.20%**
  - Mean Precision: **95.91%**
  - Mean Recall: **99.14%**
  - Mean F1-Score: **97.47%**
- **Independent 75-Message Gold Benchmark Set**:
  - Accuracy: **100.00% (75/75)**
  - Precision: **100.00%** | Recall: **100.00%** | F1: **100.00%**
  - Zero false positives on difficult transactional bank alerts and casual family money discussions.

### Slide 5: Product Architecture & Privacy
- **Privacy-by-Design**:
  - Raw messages are processed in-memory and NEVER stored.
  - Optional user feedback strips all phone numbers, emails, and UPI IDs, with automatic spreadsheet injection (`=, +, -, @`) sanitization.
- **Resilient Stack**:
  - Frontend: Zero-framework, responsive HTML5/CSS3/ES6, accessible `:focus-visible`, `aria-live`, Google Anek Tamil typography.
  - Backend: Python 3.12/3.13, Flask API, Waitress multi-threaded WSGI server, CSP security headers.
  - Containerization: Production Docker container running as non-root `appuser` with built-in healthcheck.

### Slide 6: Citizen Empowering Features
- **Instant Risk Meter**: 3-zone visual gauge (Safe 0-30%, Suspicious 30-55%, Likely Scam 55-100%).
- **Scam-Tailored Safety Advice**: Explains *why* Digital Arrest doesn't exist, *why* TNEB doesn't threaten over personal SMS, and *why* entering a UPI PIN only deducts money.
- **1-Click Complaint Draft**: Formats an evidence-ready report ready to paste into `cybercrime.gov.in`.
- **Direct 1930 Helpline Button**: One-tap phone dialer for senior citizens who have lost funds.

### Slide 7: Sustainable Impact & Future Roadmap
- **SDG Alignment**:
  - SDG 16.4: Reduce illicit financial flows and combat cyber crime.
  - SDG 9: Build resilient, trusted digital infrastructure for rural populations.
  - SDG 4: Digital literacy and cyber safety education in regional mother tongues.
- **Next Phase**: WhatsApp community bot webhook, voice-assisted readouts for illiterate citizens, and integration with state police cyber cells.

---

## Part 2: 4-Minute Live Demonstration Script

| Time | Action | Speaking Points |
|---|---|---|
| **0:00 - 0:45** | **The Problem & Persona** | "Good morning jury. Meet Mr. Natarajan, a 68-year-old pensioner in Madurai. He gets an SMS: *'TNEB: Electricity power disconnect tonight at 9.30 PM. Call officer 9840184712.'* Panicked, he calls the number, downloads an app, and loses his savings. Why? Because existing cyber tools are in English and don't speak Tamil." |
| **0:45 - 1:30** | **Demo 1: TNEB Scam (Tamil/Tanglish)** | *[Click '⚡ TNEB மின் துண்டிப்பு' chip]* "With Cyber Kavasam, Natarajan pastes the text. Instantly: **Likely Scam**, Risk: **88%**. The suspicious phrases are highlighted in red. The tool clearly explains in natural Tamil: *'மின்வாரியம் தனி நபர் போன் நம்பர் தந்து இன்றிரவே மின்சாரம் கட் செய்யப்படும் என மிரட்டாது.'*" |
| **1:30 - 2:15** | **Demo 2: Real Bank OTP (Zero Cry-Wolf)** | *[Click '✅ உண்மையான OTP' chip]* "Now notice our safety signal filter. A real Swiggy or Bank OTP says *'Share OTP with driver'* or *'Never share OTP'*. Cyber Kavasam scores this as **Safe (Risk: 6%)**. We don't cry wolf; we build citizen trust." |
| **2:15 - 3:00** | **Demo 3: Digital Arrest & UPI Collect** | *[Click '🚨 டிஜிட்டல் கைது' chip]* "Here is a Digital Arrest threat claiming CBI parcel interception. Our engine detects the lookalike extortion scheme, assigns **Likely Scam (88%)**, and gives specific advice: *'No agency conducts digital arrest over video calls, disconnect immediately.'*" |
| **3:00 - 3:30** | **Demo 4: Reporting & Draft Generation** | *[Click '📋 Copy Complaint Draft']* "If fraud occurred, Natarajan taps 'Copy Complaint Draft'. The app generates a structured incident summary with timestamps, red flags, and evidence ready for `cybercrime.gov.in`, plus a direct link to dial **1930**." |
| **3:30 - 4:00** | **Engineering & Closing** | "Under the hood: 3,180 template-trained char n-gram models + 26 Noisy-OR rules achieving 100% on our gold test set. Zero data storage, hardened Docker container, accessible in light and dark modes. Cyber Kavasam is digital armor for every Tamil citizen. Thank you." |

---

## Part 3: Mapping to Hackathon Judging Criteria

### 1. Relevance
- Directly targets the **Digital Safety & Cyber Fraud Awareness** theme.
- Solves a rampant real-world epidemic (TNEB scams, Digital Arrest, APK malware) plaguing Tamil Nadu citizens.

### 2. Technical Strength
- Hybrid dual-engine design combining probabilistic Noisy-OR heuristics with character n-gram (`char_wb` 2-5) Logistic Regression.
- 5-fold cross-validation grouped by template (`GroupKFold`) proving generalization on unseen message formulations.
- Sub-20ms inference latency on standard CPU; robust against adversarial character spacing and typos.

### 3. Functionality
- Complete end-to-end user journey: language detection, risk scoring, highlight spans, bilingual reasoning, complaint drafting, and emergency helpline routing.
- Handles edge cases: distinguishes ride-sharing OTPs from phishing OTP theft, differentiates warning statements from phishing requests.

### 4. Creativity
- Tailored Tanglish token heuristics bridging English alphabet usage with Tamil grammatical syntax.
- Instant complaint draft builder eliminating friction when reporting to national portals.
- 3-zone visual risk gauge designed for non-technical and senior citizens.

### 5. Social Cause Impact
- Empowers regional language speakers often neglected by mainstream English-centric security software.
- Directly supports UN Sustainable Development Goals (SDG 16.4, 9, 4).
- Safe for public kiosks and shared village internet centers due to strict in-memory privacy guarantees.

### 6. Presentation
- Clean, accessible user interface adhering to WCAG guidelines (`aria-live`, `:focus-visible`, reduced motion support).
- Bilingual toggle updating 100% of the UI dynamically.
- Clear, disciplined documentation, architecture diagrams, and benchmark logs.

### 7. Teamwork & Engineering Discipline
- Modular folder structure cleanly separating ML training (`app/train.py`), detection engine (`app/engine.py`), REST API (`app/server.py`), and assets.
- Automated CI pipeline, Docker configuration, and comprehensive `pytest` test suite with 66 passing assertions.
