/**
 * script.js: Production client logic for Cyber Kavasam (சைபர் கவசம்).
 * Features:
 * - Bilingual UI toggle (Tamil / English) with full reactive re-translation
 * - Dark / Light theme toggle with persistence
 * - Safe DOM manipulation (Strictly ZERO innerHTML for user strings)
 * - Interactive risk gauge & accessible highlights
 * - Ready-to-file complaint draft generator with fallback clipboard
 * - Feedback reporting & example chips
 */

(function () {
  'use strict';

  // --- STATE ---
  let currentLang = 'ta'; // default to Tamil
  let currentTheme = 'light';
  let lastAnalysis = null; // caches last API response for re-rendering on lang toggle

  // --- I18N DICTIONARY ---
  const TRANSLATIONS = {
    ta: {
      tagline: "பொதுமக்கள் மோசடி தடுப்பு மற்றும் புகார் வழிகாட்டி",
      inputTitle: "செய்தியைச் சரிபார்க்கவும்",
      inputDesc: "உங்களுக்கு வந்த SMS அல்லது WhatsApp செய்தியை கீழே ஒட்டி, அது மோசடியா என்பதை உடனடியாக அறிந்து கொள்ளுங்கள்.",
      inputLabel: "செய்தியை இங்கே ஒட்டவும்:",
      placeholder: "எ.கா: Dear customer, unga bank account block aagum. KYC update panna link click pannunga...",
      chipsLabel: "உதாரண செய்திகள்:",
      chipKyc: "⚠️ வங்கி KYC முடக்கம்",
      chipEb: "⚡ TNEB மின் துண்டிப்பு",
      chipArrest: "🚨 டிஜிட்டல் கைது",
      chipJob: "💼 யூடியூப் வேலை",
      chipSafeOtp: "✅ உண்மையான OTP",
      chipSafeChat: "✅ இயல்பான உரையாடல்",
      btnCheck: "சரிபார்க்கவும் (Check Now)",
      btnClear: "அழிக்கவும் (Clear)",
      reportTitle: "பாதிக்கப்பட்டவரா? உடனடியாக புகார் அளியுங்கள்",
      reportSubtitle: "சைபர் கிரைம் உதவி எண் & மத்திய அரசு போர்ட்டல்கள்",
      btn1930: "1930 உதவி எண் அழைக்கவும் (இலவசம்)",
      resultTitle: "ஆய்வு முடிவுகள்",
      emptyTitle: "செய்தியைச் சரிபார்க்க தயார்",
      emptyDesc: "இடதுபுறத்தில் ஒரு செய்தியை ஒட்டி 'சரிபார்க்கவும்' பொத்தானை அழுத்தவும். AI மற்றும் பாதுகாப்பு விதிகளின்படி பகுப்பாய்வு செய்து தீர்ப்பு வழங்கப்படும்.",
      verdictLabel: "இறுதித் தீர்ப்பு:",
      riskScore: "மோசடி ஆபத்து அளவு (Risk)",
      zoneSafe: "பாதுகாப்பானது (Safe)",
      zoneSuspicious: "சந்தேகம் (Suspicious)",
      zoneScam: "மோசடி (Likely Scam)",
      confScore: "நம்பகத்தன்மை (Confidence)",
      confHint: "விதிகள் + AI ஒருங்கிணைப்பு",
      highlightTitle: "கண்டறியப்பட்ட சந்தேக கூறுகள்:",
      reasonsTitle: "காரணங்கள் (Why we flagged this):",
      adviceTitle: "அடுத்து நீங்கள் என்ன செய்ய வேண்டும்?:",
      btnCopyDraft: "புகார் வரைவை நகலெடு (Copy Complaint Draft)",
      draftCopied: "நகலெடுக்கப்பட்டது! cybercrime.gov.in-ல் பயன்படுத்தலாம்.",
      feedbackPrompt: "இந்த முடிவு உங்களுக்கு உதவியதா?",
      yes: "ஆம்",
      no: "இல்லை",
      feedbackThankYou: "உங்கள் கருத்திற்கு நன்றி!",
      commonScamsTitle: "தமிழ்நாட்டில் அதிகம் நடக்கும் 6 முக்கிய சைபர் மோசடிகள்",
      commonScamsSubtitle: "பொதுமக்கள் விழிப்புடன் இருக்க தமிழ்நாடு சைபர் கிரைம் பிரிவு வழிகாட்டுதல்கள்",
      scam1Title: "1. போலி வங்கி KYC முடக்கம்",
      scam1Desc: "'உங்கள் கணக்கு இன்று முடக்கப்படும், பான் கார்டு இணைக்க லிங்கை தொடவும்' என வரும் குறுஞ்செய்திகளை நம்பாதீர்கள். வங்கிகள் எஸ்எம்எஸ் வழியே கணக்கை முடக்காது.",
      scam2Title: "2. TNEB மின் இணைப்பு துண்டிப்பு",
      scam2Desc: "'இன்று இரவு 9:30 மணிக்கு கரண்ட் கட் செய்யப்படும், அதிகாரியை அழையுங்கள்' என்பது மோசடி. மின்வாரியம் தனி நபர் போன் நம்பர் தந்து மிரட்டாது.",
      scam3Title: "3. டிஜிட்டல் கைது (Digital Arrest)",
      scam3Desc: "சிபிஐ, காவல்துறை அல்லது சுங்கத்துறை என மிரட்டி வீடியோ காலில் வரச்சொல்லி பயமுறுத்துவார்கள். எந்த அரசு அமைப்பும் ஆன்லைனில் கைது செய்யாது.",
      scam4Title: "4. பகுதி நேர யூடியூப் வேலை",
      scam4Desc: "யூடியூப் வீடியோக்களுக்கு லைக் செய்தால் தினசரி ரூ 3000 தருவதாகக் கூறி டெலிகிராமில் இணைத்து, முதலீடு செய்ய வைத்து பணத்தை சுருட்டும் பொறி.",
      scam5Title: "5. UPI தவறுதலாக பணம் வந்ததாக நாடகம்",
      scam5Desc: "'தவறுதலாக பணத்தை அனுப்பிவிட்டேன், திரும்ப அனுப்ப UPI PIN போடுங்கள்' என்பார்கள். நினைவில் கொள்ளுங்கள்: பணம் வர PIN போடவே கூடாது.",
      scam6Title: "6. AnyDesk & போலி APK பதிவிறக்கம்",
      scam6Desc: "வாட்ஸ்அப்பில் அனுப்பப்படும் .apk ஃபைல்கள் மற்றும் AnyDesk செயலிகள் உங்கள் மொபைல் திரையை ஹேக்கர்களுக்கு காட்டி பணத்தை திருடும்.",
      disclaimerText: "இந்த தளம் பொதுமக்களின் இணையப் பாதுகாப்பிற்கான ஒரு விழிப்புணர்வு வழிகாட்டி மட்டுமே; இது நீதிமன்ற அல்லது சட்டப்பூர்வ அதிகாரப்பூர்வ உறுதிப்படுத்தல் அல்ல. ஏதேனும் சந்தேகம் இருப்பின் உடனடியாக 1930 எண்ணை அழைக்கவும்.",
      privacyLabel: "தனியுரிமை உறுதிமொழி:",
      privacyText: "உங்கள் செய்திகள் சர்வரில் சேமிக்கப்படாது. நீங்கள் விருப்பப்பட்டு கருத்து தெரிவிக்கும் பட்சத்தில் மட்டுமே தனிநபர் விவரங்கள் நீக்கப்பட்டு ஆய்வுக்கு உட்படுத்தப்படும்.",
      langBadgeTa: "தமிழ் (Tamil Script)",
      langBadgeTgl: "Tanglish (தமிழ் & ஆங்கிலம்)",
      langBadgeEn: "English",
      verdictSafe: "பாதுகாப்பானது (Safe)",
      verdictSuspicious: "சந்தேகத்திற்குரியது (Suspicious)",
      verdictScam: "மோசடி சாத்தியம் (Likely Scam)",
      errorEmpty: "தயவுசெய்து சரிபார்க்க வேண்டிய செய்தியை உள்ளிடவும்.",
      errorGeneric: "பிழை ஏற்பட்டது. சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்."
    },
    en: {
      tagline: "Citizen Scam Detection & Reporting Assistant",
      inputTitle: "Check Message for Scam",
      inputDesc: "Paste any SMS or WhatsApp message below to instantly detect fraud, examine red flags, and get safety advice.",
      inputLabel: "Paste Message Here:",
      placeholder: "e.g., Dear customer, your bank account will be blocked within 24 hours. Update KYC at...",
      chipsLabel: "Try Example Messages:",
      chipKyc: "⚠️ Bank KYC Block",
      chipEb: "⚡ TNEB Power Cut",
      chipArrest: "🚨 Digital Arrest",
      chipJob: "💼 YouTube Job Scam",
      chipSafeOtp: "✅ Real Bank OTP",
      chipSafeChat: "✅ Family Chat",
      btnCheck: "Check Message",
      btnClear: "Clear",
      reportTitle: "Victim of Cyber Fraud? Report Immediately",
      reportSubtitle: "National Cyber Helpline & Official Portals",
      btn1930: "Call 1930 Helpline (Toll-Free)",
      resultTitle: "Analysis Results",
      emptyTitle: "Ready to Analyze",
      emptyDesc: "Paste a message on the left and click 'Check Message'. Our hybrid ML and heuristic safety engine will assess risk in real-time.",
      verdictLabel: "Final Verdict:",
      riskScore: "Scam Risk Score",
      zoneSafe: "Safe",
      zoneSuspicious: "Suspicious",
      zoneScam: "Likely Scam",
      confScore: "Confidence Level",
      confHint: "Weighted Rules + ML Char n-grams",
      highlightTitle: "Suspicious Phrases Highlighted:",
      reasonsTitle: "Why We Flagged This:",
      adviceTitle: "What You Should Do Now:",
      btnCopyDraft: "Copy Complaint Draft for cybercrime.gov.in",
      draftCopied: "Copied to clipboard! Ready to paste on cybercrime.gov.in",
      feedbackPrompt: "Was this result accurate and helpful?",
      yes: "Yes",
      no: "No",
      feedbackThankYou: "Thank you for your feedback!",
      commonScamsTitle: "Top 6 Cyber Scams Targeting Citizens in Tamil Nadu",
      commonScamsSubtitle: "Guidelines and advisories from Tamil Nadu Cyber Crime Police",
      scam1Title: "1. Fake Bank KYC Expiry",
      scam1Desc: "'Your account will be blocked today, click link to link PAN'. Banks never block accounts via SMS links. Visit your home branch directly.",
      scam2Title: "2. TNEB Power Cut Threats",
      scam2Desc: "'Electricity disconnection scheduled at 9:30 PM tonight'. TNEB never sends personal officer numbers or threatens same-night blackouts.",
      scam3Title: "3. 'Digital Arrest' Impersonation",
      scam3Desc: "Scammers pretend to be CBI, Police, or Customs over Skype/WhatsApp video calls. No Indian government agency conducts 'digital arrests'.",
      scam4Title: "4. Part-Time YouTube Like Tasks",
      scam4Desc: "Scammers promise Rs 2,000-5,000 daily for liking videos, lure victims into Telegram VIP groups, and steal advance deposits.",
      scam5Title: "5. 'Mistaken UPI Transfer' Trick",
      scam5Desc: "'I mistakenly sent money to your GPay, enter UPI PIN to refund'. Remember: You NEVER need to enter your UPI PIN to receive money.",
      scam6Title: "6. AnyDesk & Malicious APK Downloads",
      scam6Desc: "Unknown callers ask to install remote-screen apps or APKs to fix issues, giving hackers complete control of your smartphone.",
      disclaimerText: "This tool provides guidance only and does not constitute a legal or official confirmation. If in doubt or in case of financial loss, call 1930 immediately.",
      privacyLabel: "Privacy Guarantee:",
      privacyText: "Your messages are processed in-memory and NEVER stored. Only optional feedback with redacted PII is retained for quality improvement.",
      langBadgeTa: "Tamil Script",
      langBadgeTgl: "Tanglish (Tamil in English)",
      langBadgeEn: "English",
      verdictSafe: "Safe",
      verdictSuspicious: "Suspicious",
      verdictScam: "Likely Scam",
      errorEmpty: "Please enter a message to check.",
      errorGeneric: "An error occurred. Please try again shortly."
    }
  };

  // --- EXAMPLE MESSAGES ---
  const EXAMPLES = {
    kyc: "எஸ்பிஐ வாடிக்கையாளர் கவனத்திற்கு: உங்கள் வங்கி கணக்கு இன்றோடு முடக்கப்படும். உடனே பான் கார்டு அப்டேட் செய்ய http://sbi-kyc-verify.xyz பார்க்கவும்.",
    eb: "TNEB எச்சரிக்கை: உங்கள் முந்தைய மாத மின் கட்டணம் செலுத்தப்படாததால் இன்று இரவு 9.30 மணிக்கு மின்சாரம் துண்டிக்கப்படும். உடனே 9840184712 அழைக்கவும்.",
    arrest: "MUMBAI POLICE CRIME BRANCH: A parcel containing narcotics and fake passports under your Aadhaar has been seized. Connect to Skype video call immediately at 9876501234 to prevent digital arrest.",
    job: "Part time job! Daily YouTube likes panni Rs 2500 earn pannalam. Contact HR on WhatsApp: 8939019283",
    safe_otp: "Swiggy: Your food delivery is arriving! Share OTP 3819 with delivery partner Karthik. Enjoy your meal!",
    safe_chat: "அம்மா, நான் காய்கறி வாங்க கடைக்கு போறேன். வர அரை மணி நேரம் ஆகும். மளிகை சாமான் வாங்கிட்டு வரேன்."
  };

  // --- DOM ELEMENTS ---
  const langTaBtn = document.getElementById('lang-ta-btn');
  const langEnBtn = document.getElementById('lang-en-btn');
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const messageInput = document.getElementById('message-input');
  const charCounter = document.getElementById('char-counter');
  const checkForm = document.getElementById('check-form');
  const submitBtn = document.getElementById('submit-btn');
  const clearBtn = document.getElementById('clear-btn');
  const emptyState = document.getElementById('empty-state');
  const activeResults = document.getElementById('active-results');
  const verdictBanner = document.getElementById('verdict-banner');
  const verdictIcon = document.getElementById('verdict-icon');
  const verdictText = document.getElementById('verdict-text');
  const langBadge = document.getElementById('lang-badge');
  const riskPct = document.getElementById('risk-pct');
  const riskNeedle = document.getElementById('risk-needle');
  const confPct = document.getElementById('conf-pct');
  const highlightedContent = document.getElementById('highlighted-content');
  const reasonsList = document.getElementById('reasons-list');
  const adviceList = document.getElementById('advice-list');
  const copyDraftBtn = document.getElementById('copy-draft-btn');
  const copyToast = document.getElementById('copy-toast');
  const fbYesBtn = document.getElementById('fb-yes-btn');
  const fbNoBtn = document.getElementById('fb-no-btn');
  const feedbackMsg = document.getElementById('feedback-msg');

  // --- LOCAL STORAGE HELPERS (Safe wrapped in try/catch) ---
  function getStored(key, fallback) {
    try {
      const val = localStorage.getItem(key);
      return val !== null ? val : fallback;
    } catch (e) {
      return fallback;
    }
  }

  function setStored(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      // Storage unavailable or quota exceeded
    }
  }

  // --- THEME MANAGEMENT ---
  function initTheme() {
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const stored = getStored('kavasam_theme', prefersDark ? 'dark' : 'light');
    applyTheme(stored);
  }

  function applyTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    setStored('kavasam_theme', theme);
  }

  function toggleTheme() {
    const next = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(next);
  }

  // --- LANGUAGE / TRANSLATION MANAGEMENT ---
  function initLang() {
    const stored = getStored('kavasam_lang', 'ta');
    setLanguage(stored);
  }

  function setLanguage(lang) {
    currentLang = lang;
    setStored('kavasam_lang', lang);

    // Update active button state
    if (lang === 'ta') {
      langTaBtn.classList.add('active');
      langTaBtn.setAttribute('aria-pressed', 'true');
      langEnBtn.classList.remove('active');
      langEnBtn.setAttribute('aria-pressed', 'false');
      document.documentElement.lang = 'ta';
    } else {
      langEnBtn.classList.add('active');
      langEnBtn.setAttribute('aria-pressed', 'true');
      langTaBtn.classList.remove('active');
      langTaBtn.setAttribute('aria-pressed', 'false');
      document.documentElement.lang = 'en';
    }

    // Update static translated elements
    const dict = TRANSLATIONS[lang];
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });

    // Update placeholder
    if (dict.placeholder) {
      messageInput.setAttribute('placeholder', dict.placeholder);
    }

    // If analysis results are currently visible, re-render them with current language
    if (lastAnalysis) {
      renderResults(lastAnalysis);
    }
  }

  // --- CHARACTER COUNTER ---
  function updateCharCounter() {
    const len = messageInput.value.length;
    charCounter.textContent = `${len} / 2000`;
    if (len >= 1950) {
      charCounter.style.color = 'var(--scam-color)';
    } else {
      charCounter.style.color = 'var(--text-muted)';
    }
  }

  // --- RENDERING RESULTS (STRICTLY DOM NODES, NO INNERHTML FOR USER CONTENT) ---
  function renderHighlightedText(text, spans) {
    // Clear container
    while (highlightedContent.firstChild) {
      highlightedContent.removeChild(highlightedContent.firstChild);
    }

    if (!text) return;
    if (!spans || spans.length === 0) {
      highlightedContent.appendChild(document.createTextNode(text));
      return;
    }

    // Sort spans non-overlapping
    const sorted = [...spans].sort((a, b) => a.start - b.start);
    let currentIdx = 0;

    for (const span of sorted) {
      // Validate boundaries
      if (span.start < currentIdx || span.end > text.length || span.start >= span.end) {
        continue;
      }

      // Append text before highlight
      if (span.start > currentIdx) {
        const textBefore = text.slice(currentIdx, span.start);
        highlightedContent.appendChild(document.createTextNode(textBefore));
      }

      // Create highlight token
      const mark = document.createElement('mark');
      mark.className = 'highlight-token';
      mark.textContent = text.slice(span.start, span.end);
      if (span.rule_id) {
        mark.title = span.rule_id;
      }
      highlightedContent.appendChild(mark);

      currentIdx = span.end;
    }

    // Append trailing text
    if (currentIdx < text.length) {
      highlightedContent.appendChild(document.createTextNode(text.slice(currentIdx)));
    }
  }

  function renderResults(data) {
    lastAnalysis = data;
    const dict = TRANSLATIONS[currentLang];

    // Hide empty state, reveal active results
    emptyState.style.display = 'none';
    activeResults.style.display = 'block';

    // 1. Language Badge
    langBadge.style.display = 'inline-block';
    if (data.detected_language === 'ta') {
      langBadge.textContent = dict.langBadgeTa;
    } else if (data.detected_language === 'tanglish') {
      langBadge.textContent = dict.langBadgeTgl;
    } else {
      langBadge.textContent = dict.langBadgeEn;
    }

    // 2. Verdict Banner
    verdictBanner.className = 'verdict-banner';
    if (data.verdict === 'Safe') {
      verdictBanner.classList.add('verdict-safe');
      verdictIcon.textContent = '🛡️';
      verdictText.textContent = data.label[currentLang] || dict.verdictSafe;
    } else if (data.verdict === 'Suspicious') {
      verdictBanner.classList.add('verdict-suspicious');
      verdictIcon.textContent = '⚠️';
      verdictText.textContent = data.label[currentLang] || dict.verdictSuspicious;
    } else {
      verdictBanner.classList.add('verdict-scam');
      verdictIcon.textContent = '🚨';
      verdictText.textContent = data.label[currentLang] || dict.verdictScam;
    }

    // 3. Risk Gauge Needle
    riskPct.textContent = `${data.risk}%`;
    const clampedRisk = Math.max(0, Math.min(100, data.risk));
    riskNeedle.style.left = `${clampedRisk}%`;

    // 4. Confidence
    confPct.textContent = `${data.confidence}%`;

    // 5. Highlighted Message
    renderHighlightedText(data.normalised_text, data.highlight_spans);

    // 6. Reasons List (DOM nodes)
    while (reasonsList.firstChild) {
      reasonsList.removeChild(reasonsList.firstChild);
    }
    if (data.reasons && data.reasons.length > 0) {
      data.reasons.forEach(r => {
        const li = document.createElement('li');
        li.textContent = r[currentLang] || r.en || r.ta;
        reasonsList.appendChild(li);
      });
    }

    // 7. Advice List (DOM nodes)
    while (adviceList.firstChild) {
      adviceList.removeChild(adviceList.firstChild);
    }
    if (data.advice && data.advice.length > 0) {
      data.advice.forEach(a => {
        const li = document.createElement('li');
        li.textContent = a[currentLang] || a.en || a.ta;
        adviceList.appendChild(li);
      });
    }

    // Reset feedback UI
    feedbackMsg.textContent = '';
    fbYesBtn.disabled = false;
    fbNoBtn.disabled = false;
    copyToast.textContent = '';
  }

  // --- API CALL ---
  async function performCheck(messageText) {
    const text = messageText.trim();
    const dict = TRANSLATIONS[currentLang];

    if (!text) {
      alert(dict.errorEmpty);
      messageInput.focus();
      return;
    }

    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    try {
      const response = await fetch('/api/v1/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || `HTTP ${response.status}`);
      }

      const result = await response.json();
      renderResults(result);

      // Smooth scroll to result on mobile
      if (window.innerWidth <= 900) {
        document.getElementById('result-container').scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err) {
      alert(`${dict.errorGeneric} (${err.message})`);
    } finally {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
    }
  }

  // --- COPY COMPLAINT DRAFT ---
  function buildComplaintDraft() {
    if (!lastAnalysis) return "";
    const dateStr = new Date().toLocaleString();
    const reasons = (lastAnalysis.reasons || [])
      .map((r, i) => `  ${i + 1}. ${r[currentLang] || r.en}`)
      .join('\n');

    return [
      "==================================================",
      "CYBER CRIME INCIDENT REPORT DRAFT",
      "Official Reporting Portal: https://cybercrime.gov.in",
      "National Cyber Helpline: 1930 | Sanchar Saathi Chakshu: https://sancharsaathi.gov.in",
      "==================================================",
      `Date & Time of Assessment: ${dateStr}`,
      `Assessed Verdict: ${lastAnalysis.verdict} (${lastAnalysis.label[currentLang]})`,
      `Assessed Risk Level: ${lastAnalysis.risk}% | Confidence: ${lastAnalysis.confidence}%`,
      `Language: ${lastAnalysis.detected_language}`,
      "",
      "--- SUSPICIOUS MESSAGE CONTENT ---",
      lastAnalysis.normalised_text,
      "",
      "--- IDENTIFIED RED FLAGS & EVIDENCE ---",
      reasons || "None specified.",
      "",
      "--- IMMEDIATE ACTION TAKEN ---",
      "- Sender blocked and message reported on Chakshu portal.",
      "- Financial credentials were NOT shared.",
      "=================================================="
    ].join('\n');
  }

  async function copyComplaintDraft() {
    const draft = buildComplaintDraft();
    const dict = TRANSLATIONS[currentLang];
    if (!draft) return;

    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(draft);
        copyToast.textContent = dict.draftCopied;
        setTimeout(() => { copyToast.textContent = ''; }, 4000);
        return;
      } catch (e) {
        // Fall through to textarea copy fallback
      }
    }

    // Fallback for older browsers
    const ta = document.createElement('textarea');
    ta.value = draft;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      copyToast.textContent = dict.draftCopied;
      setTimeout(() => { copyToast.textContent = ''; }, 4000);
    } catch (err) {
      copyToast.textContent = "Error copying. Please select and copy manually.";
    }
    document.body.removeChild(ta);
  }

  // --- FEEDBACK SUBMISSION ---
  async function submitFeedback(userAgreed) {
    if (!lastAnalysis) return;
    const dict = TRANSLATIONS[currentLang];
    fbYesBtn.disabled = true;
    fbNoBtn.disabled = true;

    try {
      await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: lastAnalysis.normalised_text,
          verdict: lastAnalysis.verdict,
          user_agreed: userAgreed,
          comments: userAgreed ? "User confirmed accuracy" : "User disputed accuracy"
        })
      });
      feedbackMsg.textContent = dict.feedbackThankYou;
    } catch (e) {
      feedbackMsg.textContent = dict.feedbackThankYou;
    }
  }

  // --- EVENT LISTENERS ---
  function setupListeners() {
    // Theme toggle
    themeToggleBtn.addEventListener('click', toggleTheme);

    // Language buttons
    langTaBtn.addEventListener('click', () => setLanguage('ta'));
    langEnBtn.addEventListener('click', () => setLanguage('en'));

    // Input typing & char counter
    messageInput.addEventListener('input', updateCharCounter);

    // Form submit
    checkForm.addEventListener('submit', (e) => {
      e.preventDefault();
      performCheck(messageInput.value);
    });

    // Clear button
    clearBtn.addEventListener('click', () => {
      messageInput.value = '';
      updateCharCounter();
      lastAnalysis = null;
      activeResults.style.display = 'none';
      emptyState.style.display = 'block';
      langBadge.style.display = 'none';
      messageInput.focus();
    });

    // Example chips
    document.querySelectorAll('.chip-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const type = btn.getAttribute('data-type');
        if (EXAMPLES[type]) {
          messageInput.value = EXAMPLES[type];
          updateCharCounter();
          performCheck(messageInput.value);
        }
      });
    });

    // Copy complaint draft
    copyDraftBtn.addEventListener('click', copyComplaintDraft);

    // Feedback buttons
    fbYesBtn.addEventListener('click', () => submitFeedback(true));
    fbNoBtn.addEventListener('click', () => submitFeedback(false));
  }

  // --- INITIALIZATION ---
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initLang();
    setupListeners();
    updateCharCounter();
  });

})();
