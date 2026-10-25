/**
 * script.js: Production client logic for Cyber Kavasam (சைபர் கவசம்) v2.0.
 * Designed by Meenakshi M | Viksit Bharat Hackathon
 * Features:
 * - Bilingual UI toggle (Tamil / English) with full reactive re-translation
 * - Text-to-Speech Voice Readout (Web Speech API) in Tamil & English
 * - 1-Click WhatsApp Family Warning Forwarder
 * - 1-Click Clipboard Paste & Complaint Draft Generator
 * - Interactive Scam IQ Quiz with instant feedback
 * - Strict DOM node rendering (Zero innerHTML for user strings)
 */

(function () {
  'use strict';

  // --- STATE ---
  let currentLang = 'ta';
  let currentTheme = 'light';
  let lastAnalysis = null;
  let synth = window.speechSynthesis || null;

  // --- I18N DICTIONARY ---
  const TRANSLATIONS = {
    ta: {
      announcementText: "விக்சித் பாரத் ஹேக்கத்தான் 2026 | டிஜிட்டல் பாதுகாப்பு & சைபர் மோசடி தடுப்பு உதவி தளம்",
      tagline: "பொதுமக்கள் மோசடி தடுப்பு மற்றும் புகார் வழிகாட்டி",
      trustPrivacy: "100% தனிநபர் பாதுகாப்பு (Zero Data Stored)",
      trustLangs: "தமிழ், Tanglish & English ஆதரவு",
      trustSpeed: "உடனடி AI & விதிமுறை ஆய்வு (Instant)",
      trustHelpline: "1930 தேசிய உதவி எண் இணைப்பு",
      inputTitle: "செய்தியைச் சரிபார்க்கவும்",
      inputDesc: "உங்களுக்கு வந்த SMS அல்லது WhatsApp செய்தியை கீழே ஒட்டி, அது மோசடியா என்பதை உடனடியாக அறிந்து கொள்ளுங்கள்.",
      inputLabel: "செய்தியை இங்கே ஒட்டவும்:",
      btnPaste: "ஒட்டுக (Paste)",
      placeholder: "எ.கா: Dear customer, unga bank account block aagum. KYC update panna link click pannunga...",
      chipsLabel: "உதாரண செய்திகள் (Click to test):",
      chipKyc: "🏦 வங்கி KYC முடக்கம்",
      chipEb: "⚡ TNEB மின் துண்டிப்பு",
      chipArrest: "🚨 டிஜிட்டல் கைது",
      chipJob: "💼 யூடியூப் வேலை மோசடி",
      chipSafeOtp: "✅ உண்மையான உணவு/வங்கி OTP",
      chipSafeChat: "💬 இயல்பான குடும்ப உரையாடல்",
      btnCheck: "சரிபார்க்கவும் (Check Now)",
      btnClear: "அழிக்கவும் (Clear)",
      reportTitle: "பாதிக்கப்பட்டவரா? உடனடியாக புகார் அளியுங்கள்",
      reportSubtitle: "சைபர் கிரைம் உதவி எண் & மத்திய அரசு போர்ட்டல்கள்",
      btn1930: "1930 உதவி எண் அழைக்கவும் (இலவசம்)",
      resultTitle: "ஆய்வு முடிவுகள்",
      emptyTitle: "செய்தியைச் சரிபார்க்க தயார்",
      emptyDesc: "இடதுபுறத்தில் ஒரு செய்தியை ஒட்டி 'சரிபார்க்கவும்' பொத்தானை அழுத்தவும். AI மற்றும் பாதுகாப்பு விதிகளின்படி பகுப்பாய்வு செய்து தீர்ப்பு வழங்கப்படும்.",
      verdictLabel: "இறுதித் தீர்ப்பு:",
      btnListen: "கேட்க (Listen)",
      riskScore: "மோசடி ஆபத்து அளவு (Risk)",
      zoneSafe: "பாதுகாப்பானது (0-30%)",
      zoneSuspicious: "சந்தேகம் (30-55%)",
      zoneScam: "மோசடி (55-100%)",
      confScore: "நம்பகத்தன்மை (Confidence)",
      confHint: "விதிகள் 60% + AI 40%",
      highlightTitle: "கண்டறியப்பட்ட சந்தேக கூறுகள்:",
      reasonsTitle: "காரணங்கள் (Why we flagged this):",
      adviceTitle: "அடுத்து நீங்கள் என்ன செய்ய வேண்டும்?:",
      btnShareWhatsApp: "குடும்பத்தினரை எச்சரிக்க (WhatsApp)",
      btnCopyDraft: "புகார் வரைவை நகலெடு (Copy Draft)",
      draftCopied: "நகலெடுக்கப்பட்டது! cybercrime.gov.in-ல் பயன்படுத்தலாம்.",
      feedbackPrompt: "இந்த முடிவு உங்களுக்கு உதவியதா?",
      yes: "ஆம்",
      no: "இல்லை",
      feedbackThankYou: "உங்கள் கருத்திற்கு நன்றி!",
      atlasKicker: "தமிழ்நாடு சைபர் பாதுகாப்பு கையேடு",
      commonScamsTitle: "தமிழ்நாட்டில் அதிகம் நடக்கும் 6 முக்கிய சைபர் மோசடிகள்",
      commonScamsSubtitle: "பொதுமக்கள் விழிப்புடன் இருக்க தமிழ்நாடு சைபர் கிரைம் பிரிவு வழிகாட்டுதல்கள்",
      typeBanking: "வங்கி மோசடி",
      typeUtility: "மின்சார வாரியம்",
      typeExtortion: "மிரட்டல் மோசடி",
      typeJob: "வேலைவாய்ப்பு பொறி",
      typeUPI: "UPI மோசடி",
      typeMalware: "மால்வேர் ஆபத்து",
      scam1Title: "1. போலி வங்கி KYC முடக்கம்",
      scam1Desc: "'உங்கள் கணக்கு இன்று முடக்கப்படும், பான் கார்டு இணைக்க லிங்கை தொடவும்' என வரும் குறுஞ்செய்திகளை நம்பாதீர்கள். வங்கிகள் எஸ்எம்எஸ் வழியே கணக்கை முடக்காது.",
      scam1Flag: "அவசர காலக்கெடு மற்றும் போலியான .xyz/.top இணையதள லிங்குகள்.",
      scam2Title: "2. TNEB மின் இணைப்பு துண்டிப்பு",
      scam2Desc: "'இன்று இரவு 9:30 மணிக்கு கரண்ட் கட் செய்யப்படும், அதிகாரியை அழையுங்கள்' என்பது மோசடி. மின்வாரியம் தனி நபர் போன் நம்பர் தந்து மிரட்டாது.",
      scam2Flag: "தனிநபர் 10 இலக்க செல்போன் எண் மற்றும் இன்றிரவே மின் துண்டிப்பு அச்சுறுத்தல்.",
      scam3Title: "3. டிஜிட்டல் கைது (Digital Arrest)",
      scam3Desc: "சிபிஐ, காவல்துறை அல்லது சுங்கத்துறை என மிரட்டி வீடியோ காலில் வரச்சொல்லி பயமுறுத்துவார்கள். எந்த அரசு அமைப்பும் ஆன்லைனில் கைது செய்யாது.",
      scam3Flag: "ஸ்கைப்/வாட்ஸ்அப் வீடியோ காலில் காவலில் வைப்பதாக பயமுறுத்துதல்.",
      scam4Title: "4. பகுதி நேர யூடியூப் வேலை",
      scam4Desc: "யூடியூப் வீடியோக்களுக்கு லைக் செய்தால் தினசரி ரூ 3000 தருவதாகக் கூறி டெலிகிராமில் இணைத்து, முதலீடு செய்ய வைத்து பணத்தை சுருட்டும் பொறி.",
      scam4Flag: "எளிய பணிக்கு அதிக ஊதியம் தருவதாகக் கூறி முன்பணம் கேட்பது.",
      scam5Title: "5. UPI தவறுதலாக பணம் வந்ததாக நாடகம்",
      scam5Desc: "'தவறுதலாக பணத்தை அனுப்பிவிட்டேன், திரும்ப அனுப்ப UPI PIN போடுங்கள்' என்பார்கள். நினைவில் கொள்ளுங்கள்: பணம் வர PIN போடவே கூடாது.",
      scam5Flag: "பணம் பெறுவதற்கு அல்லது ரீஃபண்டிற்கு UPI PIN போடுமாறு கூறுவது.",
      scam6Title: "6. AnyDesk & போலி APK பதிவிறக்கம்",
      scam6Desc: "வாட்ஸ்அப்பில் அனுப்பப்படும் .apk ஃபைல்கள் மற்றும் AnyDesk செயலிகள் உங்கள் மொபைல் திரையை ஹேக்கர்களுக்கு காட்டி பணத்தை திருடும்.",
      scam6Flag: "கூகுள் பிளே ஸ்டோர் அல்லாத வெளி இணைப்புகளிலிருந்து APK நிறுவக் கூறுவது.",
      quizTitle: "உங்கள் சைபர் விழிப்புணர்வு சோதனை (Scam IQ Quiz)",
      quizSubtitle: "கீழே உள்ள 3 கேள்விகளுக்கு விடையளித்து உங்களை சோதித்துப் பாருங்கள்!",
      quizQ1: "TNEB மின்வாரியம் இன்றிரவு 9:30 மணிக்கு கரண்ட் கட் செய்யப்போவதாக தனிநபர் செல்போன் எண்ணுடன் SMS அனுப்புமா?",
      quizQ1OptA: "ஆம், அனுப்பும்",
      quizQ1OptB: "இல்லை, ஒருபோதும் அனுப்பாது (மோசடி)",
      quizQ2: "உங்கள் GPay அல்லது PhonePe கணக்கிற்கு பிறரிடமிருந்து பணம் வர UPI PIN போட வேண்டுமா?",
      quizQ2OptA: "ஆம், PIN போட்டால்தான் பணம் வரும்",
      quizQ2OptB: "இல்லை! PIN போட்டால் பணம்தான் கழியும்",
      quizQ3: "காவல்துறை அல்லது சிபிஐ அதிகாரிகள் வாட்ஸ்அப் அல்லது ஸ்கைப் வீடியோ காலில் 'டிஜிட்டல் கைது' செய்வார்களா?",
      quizQ3OptA: "ஆம், ஆன்லைனில் கைது செய்வார்கள்",
      quizQ3OptB: "இல்லை! இந்தியாவில் டிஜிட்டல் கைது என்ற ஒன்றே கிடையாது",
      quizCorrect: "சரியான விடை! அருமை! 👏",
      quizWrong: "தவறு! இது ஒரு ஆபத்தான மோசடி உத்தி. விழிப்புடன் இருங்கள்! ⚠️",
      disclaimerText: "இந்த தளம் பொதுமக்களின் இணையப் பாதுகாப்பிற்கான ஒரு விழிப்புணர்வு வழிகாட்டி மட்டுமே; இது நீதிமன்ற அல்லது சட்டப்பூர்வ அதிகாரப்பூர்வ உறுதிப்படுத்தல் அல்ல. ஏதேனும் சந்தேகம் இருப்பின் உடனடியாக 1930 எண்ணை அழைக்கவும்.",
      privacyLabel: "தனியுரிமை உறுதிமொழி:",
      privacyText: "உங்கள் செய்திகள் சர்வரில் சேமிக்கப்படாது. நீங்கள் விருப்பப்பட்டு கருத்து தெரிவிக்கும் பட்சத்தில் மட்டுமே தனிநபர் விவரங்கள் நீக்கப்பட்டு ஆய்வுக்கு உட்படுத்தப்படும்.",
      langBadgeTa: "தமிழ் (Tamil Script)",
      langBadgeTgl: "Tanglish (தமிழ் & English)",
      langBadgeEn: "English",
      verdictSafe: "பாதுகாப்பானது (Safe)",
      verdictSuspicious: "சந்தேகத்திற்குரியது (Suspicious)",
      verdictScam: "மோசடி சாத்தியம் (Likely Scam)",
      errorEmpty: "தயவுசெய்து சரிபார்க்க வேண்டிய செய்தியை உள்ளிடவும்.",
      errorGeneric: "பிழை ஏற்பட்டது. சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்."
    },
    en: {
      announcementText: "Viksit Bharat Hackathon 2026 | Digital Safety & Cyber Fraud Awareness Assistant",
      tagline: "Citizen Scam Detection & Reporting Assistant",
      trustPrivacy: "100% Privacy by Design (Zero Data Stored)",
      trustLangs: "Tamil, Tanglish & English Support",
      trustSpeed: "Instant Rule & ML Detection Engine",
      trustHelpline: "1930 National Helpline Connected",
      inputTitle: "Check Message for Scam",
      inputDesc: "Paste any SMS or WhatsApp message below to instantly detect fraud, examine red flags, and get safety advice.",
      inputLabel: "Paste Message Here:",
      btnPaste: "Paste",
      placeholder: "e.g., Dear customer, your bank account will be blocked within 24 hours. Update KYC at...",
      chipsLabel: "Try Example Messages (Click to test):",
      chipKyc: "🏦 Bank KYC Block",
      chipEb: "⚡ TNEB Power Cut",
      chipArrest: "🚨 Digital Arrest",
      chipJob: "💼 YouTube Job Scam",
      chipSafeOtp: "✅ Real Bank/Food OTP",
      chipSafeChat: "💬 Family Money Chat",
      btnCheck: "Check Message",
      btnClear: "Clear",
      reportTitle: "Victim of Cyber Fraud? Report Immediately",
      reportSubtitle: "National Cyber Helpline & Official Portals",
      btn1930: "Call 1930 Helpline (Toll-Free)",
      resultTitle: "Analysis Results",
      emptyTitle: "Ready to Analyze",
      emptyDesc: "Paste a message on the left and click 'Check Message'. Our hybrid ML and heuristic safety engine will assess risk in real-time.",
      verdictLabel: "Final Verdict:",
      btnListen: "Listen",
      riskScore: "Scam Risk Score",
      zoneSafe: "Safe (0-30%)",
      zoneSuspicious: "Suspicious (30-55%)",
      zoneScam: "Likely Scam (55-100%)",
      confScore: "Confidence Level",
      confHint: "Rules 60% + ML 40%",
      highlightTitle: "Suspicious Phrases Highlighted:",
      reasonsTitle: "Why We Flagged This:",
      adviceTitle: "What You Should Do Now:",
      btnShareWhatsApp: "Warn Family on WhatsApp",
      btnCopyDraft: "Copy Complaint Draft",
      draftCopied: "Copied to clipboard! Ready to paste on cybercrime.gov.in",
      feedbackPrompt: "Was this result accurate and helpful?",
      yes: "Yes",
      no: "No",
      feedbackThankYou: "Thank you for your feedback!",
      atlasKicker: "Tamil Nadu Cyber Safety Atlas",
      commonScamsTitle: "Top 6 Cyber Scams Targeting Citizens in Tamil Nadu",
      commonScamsSubtitle: "Guidelines and advisories from Tamil Nadu Cyber Crime Police",
      typeBanking: "Banking Fraud",
      typeUtility: "Electricity Board",
      typeExtortion: "Blackmail Extortion",
      typeJob: "Prepaid Task Trap",
      typeUPI: "UPI Deception",
      typeMalware: "Malicious APK",
      scam1Title: "1. Fake Bank KYC Expiry",
      scam1Desc: "'Your account will be blocked today, click link to link PAN'. Banks never block accounts via SMS links. Visit your home branch directly.",
      scam1Flag: "Artificial deadlines and suspicious lookalike URLs (.xyz, .top, .buzz).",
      scam2Title: "2. TNEB Power Cut Threats",
      scam2Desc: "'Electricity disconnection scheduled at 9:30 PM tonight'. TNEB never sends personal officer numbers or threatens same-night blackouts.",
      scam2Flag: "Personal 10-digit mobile number and immediate power cutoff threats.",
      scam3Title: "3. 'Digital Arrest' Impersonation",
      scam3Desc: "Scammers pretend to be CBI, Police, or Customs over Skype/WhatsApp video calls. No Indian government agency conducts 'digital arrests'.",
      scam3Flag: "Demanding citizens stay on video call under threat of immediate arrest.",
      scam4Title: "4. Part-Time YouTube Like Tasks",
      scam4Desc: "Scammers promise Rs 2,000-5,000 daily for liking videos, lure victims into Telegram VIP groups, and steal advance deposits.",
      scam4Flag: "Unrealistic pay for simple tasks, requiring advance security deposits.",
      scam5Title: "5. 'Mistaken UPI Transfer' Trick",
      scam5Desc: "'I mistakenly sent money to your GPay, enter UPI PIN to refund'. Remember: You NEVER need to enter your UPI PIN to receive money.",
      scam5Flag: "Asking you to enter your secret UPI PIN or scan a QR code to receive refunds.",
      scam6Title: "6. AnyDesk & Malicious APK Downloads",
      scam6Desc: "Unknown callers ask to install remote-screen apps or APKs to fix issues, giving hackers complete control of your smartphone.",
      scam6Flag: "Directing you to download .apk files outside Google Play or Apple App Store.",
      quizTitle: "Test Your Cyber Awareness (Scam IQ Quiz)",
      quizSubtitle: "Answer these 3 quick real-world questions to verify your scam detection skills!",
      quizQ1: "Will TNEB ever send an SMS with a personal 10-digit number threatening a power cut at 9:30 PM tonight?",
      quizQ1OptA: "Yes, they can",
      quizQ1OptB: "No, never! It is always a scam",
      quizQ2: "Do you ever need to enter your secret UPI PIN to receive money or refunds on GPay/PhonePe?",
      quizQ2OptA: "Yes, PIN is needed to receive money",
      quizQ2OptB: "No! Entering PIN always deducts money",
      quizQ3: "Do Indian Police, CBI, or Customs conduct 'digital arrests' over WhatsApp or Skype video calls?",
      quizQ3OptA: "Yes, online arrests are legal",
      quizQ3OptB: "No! No Indian agency conducts digital arrests",
      quizCorrect: "Correct answer! Excellent awareness! 👏",
      quizWrong: "Incorrect! This is a dangerous scam tactic. Stay alert! ⚠️",
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

  // --- REAL-WORLD EXAMPLES ---
  const EXAMPLES = {
    kyc: "எஸ்பிஐ வாடிக்கையாளர் கவனத்திற்கு: உங்கள் வங்கி கணக்கு இன்றோடு முடக்கப்படும். உடனே பான் கார்டு அப்டேட் செய்ய http://sbi-kyc-verify.xyz பார்க்கவும்.",
    eb: "TNEB எச்சரிக்கை: உங்கள் முந்தைய மாத மின் கட்டணம் செலுத்தப்படாததால் இன்று இரவு 9.30 மணிக்கு மின்சாரம் துண்டிக்கப்படும். உடனே 9840184712 அழைக்கவும்.",
    arrest: "MUMBAI POLICE CRIME BRANCH: A parcel containing narcotics and fake passports under your Aadhaar has been seized. Connect to Skype video call immediately at 9876501234 to prevent digital arrest.",
    job: "Part time job! Daily YouTube likes panni Rs 2500 earn pannalam. Contact HR on WhatsApp: 8939019283",
    safe_otp: "Swiggy: Your food delivery is arriving! Share OTP 3819 with delivery partner Karthik. Enjoy your meal!",
    safe_chat: "அம்மா, நான் காய்கறி வாங்க கடைக்கு போறேன். வர அரை மணி நேரம் ஆகும். மளிகை சாமான் வாங்கிட்டு வரேன்."
  };

  // --- DOM CACHE ---
  const langTaBtn = document.getElementById('lang-ta-btn');
  const langEnBtn = document.getElementById('lang-en-btn');
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const messageInput = document.getElementById('message-input');
  const pasteBtn = document.getElementById('paste-btn');
  const charCounter = document.getElementById('char-counter');
  const checkForm = document.getElementById('check-form');
  const submitBtn = document.getElementById('submit-btn');
  const clearBtn = document.getElementById('clear-btn');
  const emptyState = document.getElementById('empty-state');
  const activeResults = document.getElementById('active-results');
  const verdictBanner = document.getElementById('verdict-banner');
  const verdictIcon = document.getElementById('verdict-icon');
  const verdictText = document.getElementById('verdict-text');
  const speakBtn = document.getElementById('speak-btn');
  const langBadge = document.getElementById('lang-badge');
  const riskPct = document.getElementById('risk-pct');
  const riskNeedle = document.getElementById('risk-needle');
  const confPct = document.getElementById('conf-pct');
  const highlightedContent = document.getElementById('highlighted-content');
  const highlightCountBadge = document.getElementById('highlight-count-badge');
  const reasonsList = document.getElementById('reasons-list');
  const adviceList = document.getElementById('advice-list');
  const whatsappShareBtn = document.getElementById('whatsapp-share-btn');
  const copyDraftBtn = document.getElementById('copy-draft-btn');
  const copyToast = document.getElementById('copy-toast');
  const fbYesBtn = document.getElementById('fb-yes-btn');
  const fbNoBtn = document.getElementById('fb-no-btn');
  const feedbackMsg = document.getElementById('feedback-msg');

  // --- SAFE LOCALSTORAGE ---
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
    } catch (e) {}
  }

  // --- THEME ---
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
    applyTheme(currentTheme === 'light' ? 'dark' : 'light');
  }

  // --- LANGUAGE MANAGEMENT ---
  function initLang() {
    const stored = getStored('kavasam_lang', 'ta');
    setLanguage(stored);
  }

  function setLanguage(lang) {
    currentLang = lang;
    setStored('kavasam_lang', lang);

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

    const dict = TRANSLATIONS[lang];
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });

    if (dict.placeholder) {
      messageInput.setAttribute('placeholder', dict.placeholder);
    }

    if (lastAnalysis) {
      renderResults(lastAnalysis);
    }
  }

  // --- CHARACTER COUNTER ---
  function updateCharCounter() {
    const len = messageInput.value.length;
    charCounter.textContent = `${len} / 2000`;
    charCounter.style.color = len >= 1950 ? 'var(--scam-color)' : 'var(--text-muted)';
  }

  // --- CLIPBOARD PASTE BUTTON ---
  async function pasteFromClipboard() {
    if (navigator.clipboard && navigator.clipboard.readText) {
      try {
        const text = await navigator.clipboard.readText();
        if (text) {
          messageInput.value = text;
          updateCharCounter();
          messageInput.focus();
        }
      } catch (err) {
        messageInput.focus();
      }
    } else {
      messageInput.focus();
    }
  }

  // --- HIGHLIGHT SPANS RENDERING (STRICTLY DOM NODES, ZERO INNERHTML) ---
  function renderHighlightedText(text, spans) {
    while (highlightedContent.firstChild) {
      highlightedContent.removeChild(highlightedContent.firstChild);
    }

    if (!text) {
      highlightCountBadge.textContent = currentLang === 'ta' ? '0 கண்டறியப்பட்டது' : '0 detected';
      return;
    }

    if (!spans || spans.length === 0) {
      highlightedContent.appendChild(document.createTextNode(text));
      highlightCountBadge.textContent = currentLang === 'ta' ? '0 கண்டறியப்பட்டது' : '0 detected';
      highlightCountBadge.style.background = 'rgba(16, 185, 129, 0.12)';
      highlightCountBadge.style.color = 'var(--safe-color)';
      return;
    }

    highlightCountBadge.textContent = currentLang === 'ta' 
      ? `${spans.length} சந்தேகக் கூறுகள்` 
      : `${spans.length} red flags`;
    highlightCountBadge.style.background = 'rgba(220, 38, 38, 0.12)';
    highlightCountBadge.style.color = '#dc2626';

    const sorted = [...spans].sort((a, b) => a.start - b.start);
    let currentIdx = 0;

    for (const span of sorted) {
      if (span.start < currentIdx || span.end > text.length || span.start >= span.end) {
        continue;
      }

      if (span.start > currentIdx) {
        highlightedContent.appendChild(document.createTextNode(text.slice(currentIdx, span.start)));
      }

      const mark = document.createElement('mark');
      mark.className = 'highlight-token';
      mark.textContent = text.slice(span.start, span.end);
      if (span.rule_id) {
        mark.title = `Flagged: ${span.rule_id}`;
      }
      highlightedContent.appendChild(mark);

      currentIdx = span.end;
    }

    if (currentIdx < text.length) {
      highlightedContent.appendChild(document.createTextNode(text.slice(currentIdx)));
    }
  }

  // --- RENDER COMPLETE RESULTS ---
  function renderResults(data) {
    lastAnalysis = data;
    const dict = TRANSLATIONS[currentLang];

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

    // 3. Risk Gauge
    riskPct.textContent = `${data.risk}%`;
    const clampedRisk = Math.max(0, Math.min(100, data.risk));
    riskNeedle.style.left = `${clampedRisk}%`;

    // 4. Confidence
    confPct.textContent = `${data.confidence}%`;

    // 5. Highlights
    renderHighlightedText(data.normalised_text, data.highlight_spans);

    // 6. Reasons
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

    // 7. Advice
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

    // 8. WhatsApp Share Link
    updateWhatsAppLink(data);

    // Reset feedback
    feedbackMsg.textContent = '';
    fbYesBtn.disabled = false;
    fbNoBtn.disabled = false;
    copyToast.textContent = '';
  }

  // --- WHATSAPP FAMILY ALERT BUILDER ---
  function updateWhatsAppLink(data) {
    if (!data) return;
    const isScam = data.verdict !== 'Safe';
    let textToShare = "";

    if (currentLang === 'ta') {
      textToShare = isScam
        ? `⚠️ *சைபர் மோசடி எச்சரிக்கை!* ⚠️\n\nஎனக்கு வந்த இந்த சந்தேக குறுஞ்செய்தியை சைபர் கவசம் (Cyber Kavasam) தளம் ஆய்வு செய்து *மோசடி (Risk: ${data.risk}%)* என எச்சரித்துள்ளது:\n\n"${data.normalised_text.slice(0, 160)}..."\n\nயாரும் இந்த லிங்கை தொடவோ OTP/PIN கொடுக்கவோ வேண்டாம். ஏதேனும் பண இழப்பு ஏற்பட்டால் உடனே 1930 எண்ணை அழைக்கவும்.\n\n- சைபர் கவசம் மூலம் சோதிக்கப்பட்டது`
        : `✅ இந்த செய்தி பாதுகாப்பானது என சைபர் கவசம் மூலம் சரிபார்க்கப்பட்டது: "${data.normalised_text.slice(0, 100)}..."`;
    } else {
      textToShare = isScam
        ? `⚠️ *Cyber Scam Warning!* ⚠️\n\nI checked this message on Cyber Kavasam and it was flagged as *${data.verdict} (Risk: ${data.risk}%)*:\n\n"${data.normalised_text.slice(0, 160)}..."\n\nNever click unknown links or share OTP/PIN. If money was lost, call 1930 immediately.\n\n- Verified via Cyber Kavasam`
        : `✅ Verified as Safe via Cyber Kavasam: "${data.normalised_text.slice(0, 100)}..."`;
    }

    whatsappShareBtn.href = `https://api.whatsapp.com/send?text=${encodeURIComponent(textToShare)}`;
  }

  // --- TEXT-TO-SPEECH VOICE READOUT ---
  function speakVerdict() {
    if (!synth) {
      alert("Text-to-speech is not supported on this browser.");
      return;
    }
    if (synth.speaking) {
      synth.cancel();
      return;
    }
    if (!lastAnalysis) return;

    const verdictWord = lastAnalysis.label[currentLang] || lastAnalysis.verdict;
    const topReason = lastAnalysis.reasons && lastAnalysis.reasons.length > 0
      ? (lastAnalysis.reasons[0][currentLang] || lastAnalysis.reasons[0].en)
      : "";

    let speechText = "";
    let speechLang = "ta-IN";

    if (currentLang === 'ta') {
      speechText = `சைபர் கவசம் தீர்ப்பு: ${verdictWord}. மோசடி ஆபத்து அளவு நூற்றுக்கு ${lastAnalysis.risk} சதவீதம். முக்கிய காரணம்: ${topReason}`;
      speechLang = "ta-IN";
    } else {
      speechText = `Cyber Kavasam Verdict: ${verdictWord}. Scam risk score is ${lastAnalysis.risk} percent. Key reason: ${topReason}`;
      speechLang = "en-IN";
    }

    const utterance = new SpeechSynthesisUtterance(speechText);
    utterance.lang = speechLang;
    utterance.rate = 0.95;
    synth.speak(utterance);
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

      if (window.innerWidth <= 950) {
        document.getElementById('result-container').scrollIntoView({ behavior: 'smooth' });
      }
    } catch (err) {
      alert(`${dict.errorGeneric} (${err.message})`);
    } finally {
      submitBtn.classList.remove('loading');
      submitBtn.disabled = false;
    }
  }

  // --- COMPLAINT DRAFT BUILDER ---
  function buildComplaintDraft() {
    if (!lastAnalysis) return "";
    const dateStr = new Date().toLocaleString();
    const reasons = (lastAnalysis.reasons || [])
      .map((r, i) => `  ${i + 1}. ${r[currentLang] || r.en}`)
      .join('\n');

    return [
      "==================================================",
      "NATIONAL CYBER CRIME REPORTING DRAFT",
      "Official Incident Portal: https://cybercrime.gov.in",
      "National Cyber Helpline: 1930 | Sanchar Saathi Chakshu: https://sancharsaathi.gov.in",
      "Created with Cyber Kavasam (Lead: Meenakshi M)",
      "==================================================",
      `Date & Time of Assessment: ${dateStr}`,
      `Assessed Verdict: ${lastAnalysis.verdict} (${lastAnalysis.label[currentLang]})`,
      `Assessed Risk Level: ${lastAnalysis.risk}% | Confidence: ${lastAnalysis.confidence}%`,
      `Detected Language: ${lastAnalysis.detected_language}`,
      "",
      "--- SUSPICIOUS MESSAGE CONTENT ---",
      lastAnalysis.normalised_text,
      "",
      "--- IDENTIFIED RED FLAGS & EVIDENCE ---",
      reasons || "None specified.",
      "",
      "--- CITIZEN PRECAUTIONARY ACTION ---",
      "- Sender blocked and reported on Chakshu portal.",
      "- Financial credentials, OTP, and PIN were NOT provided.",
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
        setTimeout(() => { copyToast.textContent = ''; }, 4500);
        return;
      } catch (e) {}
    }

    const ta = document.createElement('textarea');
    ta.value = draft;
    ta.style.position = 'fixed';
    ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      copyToast.textContent = dict.draftCopied;
      setTimeout(() => { copyToast.textContent = ''; }, 4500);
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

  // --- SCAM IQ QUIZ INTERACTION ---
  function setupQuiz() {
    document.querySelectorAll('.quiz-item').forEach(item => {
      const buttons = item.querySelectorAll('.quiz-btn');
      const feedback = item.querySelector('.quiz-feedback');

      buttons.forEach(btn => {
        btn.addEventListener('click', () => {
          if (item.getAttribute('data-answered') === 'true') return;
          item.setAttribute('data-answered', 'true');

          const isCorrect = btn.getAttribute('data-correct') === 'true';
          const dict = TRANSLATIONS[currentLang];

          buttons.forEach(b => {
            b.disabled = true;
            if (b.getAttribute('data-correct') === 'true') {
              b.classList.add('correct');
            }
          });

          if (isCorrect) {
            btn.classList.add('correct');
            feedback.textContent = dict.quizCorrect;
            feedback.className = 'quiz-feedback correct-text';
          } else {
            btn.classList.add('incorrect');
            feedback.textContent = dict.quizWrong;
            feedback.className = 'quiz-feedback incorrect-text';
          }
        });
      });
    });
  }

  // --- EVENT LISTENERS ---
  function setupListeners() {
    themeToggleBtn.addEventListener('click', toggleTheme);
    langTaBtn.addEventListener('click', () => setLanguage('ta'));
    langEnBtn.addEventListener('click', () => setLanguage('en'));
    messageInput.addEventListener('input', updateCharCounter);
    pasteBtn.addEventListener('click', pasteFromClipboard);

    checkForm.addEventListener('submit', (e) => {
      e.preventDefault();
      performCheck(messageInput.value);
    });

    clearBtn.addEventListener('click', () => {
      messageInput.value = '';
      updateCharCounter();
      lastAnalysis = null;
      activeResults.style.display = 'none';
      emptyState.style.display = 'block';
      langBadge.style.display = 'none';
      if (synth) synth.cancel();
      messageInput.focus();
    });

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

    copyDraftBtn.addEventListener('click', copyComplaintDraft);
    speakBtn.addEventListener('click', speakVerdict);
    fbYesBtn.addEventListener('click', () => submitFeedback(true));
    fbNoBtn.addEventListener('click', () => submitFeedback(false));

    setupQuiz();
  }

  // --- INITIALIZATION ---
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initLang();
    setupListeners();
    updateCharCounter();
  });

})();
