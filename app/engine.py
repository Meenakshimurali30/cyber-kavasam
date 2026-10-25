"""
engine.py: Detection Engine for Cyber Kavasam (சைபர் கவசம்).
Combines 26+ bilingual weighted regex rules (Noisy-OR) and character n-gram
TF-IDF + Logistic Regression ML model (60% Rules + 40% ML) with safe signal filtering.
"""

import os
import re
import hashlib
import unicodedata
from urllib.parse import urlparse
import joblib
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_VERSION = "1.0.0"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MESSAGES_CSV = os.path.join(DATA_DIR, "messages.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "kavasam.joblib")

# ==========================================
# ALLOWLIST & URL PATTERNS
# ==========================================
OFFICIAL_DOMAINS = {
    "sbi.co.in", "onlinesbi.sbi", "onlinesbi.com",
    "hdfcbank.com", "netbanking.hdfcbank.com",
    "icicibank.com", "infinity.icicibank.com",
    "axisbank.com", "canarabank.com", "indianbank.in",
    "bankofbaroda.in", "pnbindia.in", "kotak.com",
    "tangedco.gov.in", "tnebnet.org",
    "incometax.gov.in", "pmkisan.gov.in",
    "sancharsaathi.gov.in", "cybercrime.gov.in",
    "uidai.gov.in", "parivahan.gov.in", "echallan.parivahan.gov.in",
    "rbi.org.in", "npci.org.in", "swiggy.com", "zomato.com",
    "olacabs.com", "uber.com", "amazon.in", "flipkart.com", "irctc.co.in"
}

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "is.gd", "cutt.ly", "t.ly",
    "t.co", "rb.gy", "goo.gl", "ow.ly", "buff.ly", "shorturl.at"
}

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".click", ".buzz", ".club", ".vip",
    ".work", ".site", ".online", ".live", ".loan", ".stream",
    ".gq", ".cf", ".tk", ".ml", ".cc", ".icu"
}

TARGET_BRAND_KEYWORDS = ["sbi", "hdfc", "icici", "axis", "canara", "tneb", "tangedco", "incometax", "pmkisan", "fastag", "challan"]

# ==========================================
# 26+ BILINGUAL WEIGHTED RULES
# ==========================================
RULES = [
    {
        "id": "RULE_DIGITAL_ARREST",
        "family": "digital_arrest",
        "weight": 0.90,
        "en_reason": "Threatens fake 'digital arrest' or illegal parcel seizure by law enforcement",
        "ta_reason": "காவல்துறை அல்லது சிபிஐ பெயரில் 'டிஜிட்டல் கைது' அல்லது பார்சல் வழக்கில் மிரட்டுகிறது",
        "patterns": [
            r"(?i)(cbi|mumbai police|delhi police|cyber crime|narcotics control|ncb|சைபர் கிரைம்|காவல்துறை|போலீஸ்|சிபிஐ)\b.*?(digital arrest|skype|video call|warrant|drugs|seized|illegal|டிஜிட்டல் கைது|ஸ்கைப்|வீடியோ கால்|பண மோசடி)",
            r"(?i)(digital arrest|டிஜிட்டல் கைது|வீடியோ கால்|video conference|ஸ்கைப்|skype)",
            r"(?i)(போதைப்பொருள்|பார்சல்|பிடிவாரண்ட்|customs|illegal consignment).*?(கைது|arrest|police|போலீஸ்|வாட்ஸ்அப் கால்)",
            r"(?i)(drugs parcel|illegal consignment|contraband).*?(police|arrest|customs)",
        ]
    },
    {
        "id": "RULE_TNEB_POWER_CUT",
        "family": "tneb",
        "weight": 0.88,
        "en_reason": "Fake electricity bill threat claiming immediate power disconnection tonight",
        "ta_reason": "மின் கட்டணம் செலுத்தவில்லை என இன்றிரவே மின்சாரம் துண்டிக்கப்படும் என மிரட்டுகிறது",
        "patterns": [
            r"(?i)(tneb|electricity|power disconnect|மின் இணைப்பு|மின்சாரம்).*?(night 9\.?30|இன்று இரவு|துண்டிக்கப்படும்|disconnect tonight|officer \d{10})",
            r"(?i)(previous month bill was not updated|eb bill pending).*?(disconnect|contact officer|call \d{10})",
            r"(?i)(மின் கட்டண பாக்கி|மின் இணைப்பு துண்டிப்பு).*?(உடனே|தொடர்பு கொள்ளவும்|\d{10})",
        ]
    },
    {
        "id": "RULE_BANK_BLOCK_KYC",
        "family": "kyc",
        "weight": 0.85,
        "en_reason": "Urgent false threat to block or suspend bank account over pending KYC or PAN",
        "ta_reason": "KYC அல்லது பான் கார்டு உடனே புதுப்பிக்காவிட்டால் வங்கி கணக்கு முடக்கப்படும் என மிரட்டுகிறது",
        "patterns": [
            r"(?i)(account (will be|has been) (blocked|suspended|deactivated|put on hold)).*?(kyc|pan|verify|reactivate)",
            r"(?i)(வங்கி கணக்கு|account).*?(முடக்கப்படும்|பிளாக்|suspend|block).*?(kyc|pan|பான் கார்டு|புதுப்பிக்க|update)",
            r"(?i)(unga|ungal).*?(account block|suspend).*?(udane|today|kyc|pan)",
            r"(?i)(pan card|aadhaar).*?(not linked|pending).*?(block|deactivat)",
        ]
    },
    {
        "id": "RULE_OTP_THEFT",
        "family": "otp_theft",
        "weight": 0.88,
        "en_reason": "Requests sharing, sending or forwarding confidential OTP or verification code",
        "ta_reason": "ரகசிய ஓடிபி அல்லது சரிபார்ப்புக் குறியீட்டை மற்றவர்களிடம் தெரிவிக்குமாறு கேட்கிறது",
        "patterns": [
            r"(?i)(share|forward|send|solunga|பகிரவும்|தெரிவிக்கவும்).*?(otp|verification code|ரகசிய எண்).*?(representative|officer|manager|number|\d{10})",
            r"(?i)(credit aaga|to unblock|verification kaga).*?(otp).*?(share|solunga|send|அனுப்பவும்)",
            r"(?i)(bank customer care|வங்கி அதிகாரி).*?(otp).*?(share|solunga|forward)",
        ]
    },
    {
        "id": "RULE_UPI_PIN_RECEIVE",
        "family": "upi_fraud",
        "weight": 0.86,
        "en_reason": "Trick claiming you must enter UPI PIN or approve collect request to receive money or refunds",
        "ta_reason": "பணம் பெற அல்லது தவறுதலான பணத்தை திருப்பி அனுப்ப UPI PIN போடுமாறு ஏமாற்றுகிறது",
        "patterns": [
            r"(?i)(enter|input|podunga|போடவும்).*?(upi pin).*?(to receive|to refund|cashback|collect|திருப்பி அனுப்ப)",
            r"(?i)(mistakenly|thappaa|தவறுதலாக).*?(transferred|sent|அனுப்பிவிட்டேன்).*?(upi pin|click|refund)",
            r"(?i)(cashback|refund).*?(claim panna|receive panna).*?(upi pin|approve)",
            r"(?i)(scan (this )?qr).*?(enter upi pin|receive payment)",
        ]
    },
    {
        "id": "RULE_JOB_TASK_SCAM",
        "family": "job_scam",
        "weight": 0.82,
        "en_reason": "Prepaid task fraud promising daily income for liking YouTube videos or rating maps",
        "ta_reason": "யூடியூப் லைக் செய்து தினசரி பணம் சம்பாதிக்கலாம் என ஆசைகாட்டும் போலி வேலை மோசடி",
        "patterns": [
            r"(?i)(part time job|work from home|வீட்டிலிருந்தே வேலை|பகுதி நேர வேலை).*?(youtube|யூடியூப்|like|லைக்|hotel|review|maps|daily rs|earn rs|சம்பாதிக்கலாம்)",
            r"(?i)(earn rs \d+ to rs \d+ daily|per day rs \d+ guaranteed).*?(youtube|யூடியூப்|whatsapp|வாட்ஸ்அப்|telegram|டெலிகிராம்|rating)",
            r"(?i)(daily youtube|யூடியூப் வீடியோ).*?(likes|videos|லைக்|சம்பாதிக்க)",
        ]
    },
    {
        "id": "RULE_LOTTERY_PRIZE",
        "family": "lottery",
        "weight": 0.84,
        "en_reason": "Unsolicited lottery or lucky draw claim (e.g. KBC, car) asking to claim prize",
        "ta_reason": "கேபிசி அல்லது குலுக்கலில் லட்சக்கணக்கில் பணம் வென்றுள்ளதாகக் கூறும் போலி பரிசு அறிவிப்பு",
        "patterns": [
            r"(?i)(kbc|lucky draw|லக்கி டிரா|mega draw|lottery).*?(won|win|25 lakh|பரிசு|வென்று)",
            r"(?i)(congratulations|வாழ்த்துக்கள்).*?(won a brand new|car prize|ரூ 25,00,000|25 lakhs prize)",
            r"(?i)(claim (your )?prize|collect panna).*?(call \d{10}|registration charge)",
        ]
    },
    {
        "id": "RULE_REMOTE_ACCESS_APP",
        "family": "remote_app",
        "weight": 0.90,
        "en_reason": "Instructs installing remote screen-sharing tools like AnyDesk, TeamViewer, or RustDesk",
        "ta_reason": "மொபைலை முழுமையாகக் கட்டுப்படுத்தும் எனிடெஸ்க் (AnyDesk) போன்ற ஆபத்தான செயலிகளை நிறுவக் கூறுகிறது",
        "patterns": [
            r"(?i)(anydesk|teamviewer|rustdesk|quicksupport).*?(install|download|டவுன்லோட்|screen share|code)",
            r"(?i)(install|download).*?(anydesk|teamviewer|rustdesk)",
        ]
    },
    {
        "id": "RULE_SUSPICIOUS_APK",
        "family": "apk_malware",
        "weight": 0.90,
        "en_reason": "Direct link or instruction to download untrusted Android APK file outside official store",
        "ta_reason": "அங்கீகரிக்கப்படாத ஆபத்தான APK கோப்பைப் பதிவிறக்கம் செய்யத் தூண்டுகிறது",
        "patterns": [
            r"(?i)https?://[^\s]+\.apk(\b|\?)",
            r"(?i)(download|install|பதிவிறக்கம்).*?(\.apk|apk file|support\.apk|security\.apk)",
            r"(?i)\b\w+\.apk\b",
        ]
    },
    {
        "id": "RULE_CUSTOMS_PARCEL",
        "family": "customs_parcel",
        "weight": 0.85,
        "en_reason": "Fake courier or customs warning claiming seized illegal goods in your overseas shipment",
        "ta_reason": "வெளிநாட்டு பார்சலில் தடைசெய்யப்பட்ட பொருட்கள் உள்ளதாக சுங்கத்துறை பெயரில் மிரட்டுகிறது",
        "patterns": [
            r"(?i)(fedex|dhl|customs|சுங்கத்துறை|courier).*?(parcel|shipment|பார்சல்).*?(drugs|illegal|contraband|போதைப்பொருள்|gold bar|seized)",
            r"(?i)(overseas shipment|parcel).*?(detained|illegal contraband|customs agent)",
        ]
    },
    {
        "id": "RULE_LOAN_APP",
        "family": "loan_app",
        "weight": 0.80,
        "en_reason": "Predatory instant loan offering without documentation or credit check",
        "ta_reason": "ஆவணங்கள் இன்றி உடனடி கடன் தருவதாகக் கூறும் ஏமாற்று கடன் செயலி அறிவிப்பு",
        "patterns": [
            r"(?i)(instant loan|quick personal loan|உடனடி கடன்).*?(approved|no cibil|zero interest|5 mins|ஆவணங்கள் தேவையில்லை)",
            r"(?i)(pre-approved personal loan of rs).*?(zero documentation|download apk|apply here)",
        ]
    },
    {
        "id": "RULE_INVESTMENT_CRYPTO",
        "family": "investment",
        "weight": 0.82,
        "en_reason": "High-yield investment fraud promising guaranteed stock/crypto returns or VIP groups",
        "ta_reason": "பங்குச் சந்தை அல்லது கிரிப்டோவில் அபரிமிதமான உத்தரவாத லாபம் தருவதாகக் கூறும் நிதி மோசடி",
        "patterns": [
            r"(?i)(share market|crypto|trading|பங்குச் சந்தை).*?(guaranteed \d+%|200%|300%|500% profit|vip telegram|insider group)",
            r"(?i)(invest rs \d+).*?(earn rs \d+|weekly profit|daily profit)",
            r"(?i)(color prediction|aviator game).*?(win real cash|deposit bonus)",
        ]
    },
    {
        "id": "RULE_SEXTORTION",
        "family": "sextortion",
        "weight": 0.95,
        "en_reason": "Sextortion blackmail threatening to leak private videos to friends and family",
        "ta_reason": "அந்தரங்க வீடியோவை இணையத்தில் கசியவிடுவதாக மிரட்டிப் பணம் பறிக்கும் அச்சுறுத்தல்",
        "patterns": [
            r"(?i)(compromise video|nude video|அந்தரங்க வீடியோ|video call record).*?(pay rs|leak|upload|facebook|contacts)",
            r"(?i)(2 hours la rs|pay within).*?(social media la leak|send to family)",
        ]
    },
    {
        "id": "RULE_HI_MUM_EMERGENCY",
        "family": "hi_mum",
        "weight": 0.78,
        "en_reason": "Impersonates child or family member claiming broken phone and urgent money need",
        "ta_reason": "போன் உடைந்துவிட்டதாகக் கூறி மகன்/மகள் போல் நடித்து அவசரப் பணம் கேட்கும் மோசடி",
        "patterns": [
            r"(?i)(hi mom|hello mum|அம்மா என் போன்|amma en phone).*?(broken|damaged|water|தொலைந்துவிட்டது|new number|new whatsapp).*?(urgent|money|rs \d+|gpay)",
            r"(?i)(new whatsapp number).*?(urgent ah|hospital bill|hostel fees).*?(gpay|transfer)",
        ]
    },
    {
        "id": "RULE_CREDIT_CARD_LIMIT",
        "family": "card_fraud",
        "weight": 0.75,
        "en_reason": "False claim of free credit card limit increase or expiring reward points redemption",
        "ta_reason": "கிரெடிட் கார்டு வரம்பு உயர்வு அல்லது காலாவதியாகும் ரிவார்டு புள்ளிகளை பணமாக்கும் தூண்டில்",
        "patterns": [
            r"(?i)(credit card limit|கார்டு வரம்பு).*?(increased|raise|free|இலவசமாக).*?(activate|click)",
            r"(?i)(reward points|ரிவார்டு பாயிண்ட்ஸ்).*?(expire|expiring|convert to cash|redeem to cash)",
        ]
    },
    {
        "id": "RULE_TRAFFIC_CHALLAN_FAKE",
        "family": "challan",
        "weight": 0.80,
        "en_reason": "Fake traffic police e-challan notice threatening court summons",
        "ta_reason": "நீதிமன்ற நடவடிக்கை என அச்சுறுத்தும் போலியான போக்குவரத்து அபராத குறுஞ்செய்தி",
        "patterns": [
            r"(?i)(traffic police|e-challan|போக்குவரத்து காவல்துறை).*?(unpaid|pending fine|அபராதம்).*?(court summons|pay online|நீதிமன்ற)",
            r"(?i)(echallan-traffic-fine|pending fine rs).*?(avoid court|pay now)",
        ]
    },
    {
        "id": "RULE_FASTAG_SUSPENDED",
        "family": "fastag",
        "weight": 0.75,
        "en_reason": "Fake FASTag suspension notice urging immediate recharge/KYC via link",
        "ta_reason": "பாஸ்டேக் முடக்கப்பட்டுவிட்டதாக கூறி போலியான தளத்திற்கு வழிநடத்துகிறது",
        "patterns": [
            r"(?i)(fastag).*?(blacklisted|deactivated|முடக்கப்பட்டுள்ளது|toll booth block).*?(kyc|recharge|pay)",
            r"(?i)(fastag-recharge-failed|fastag update kyc)",
        ]
    },
    {
        "id": "RULE_OLX_ARMY_QR",
        "family": "olx_army",
        "weight": 0.88,
        "en_reason": "OLX buyer scam impersonating an army officer asking to scan QR or input UPI PIN",
        "ta_reason": "ராணுவ அதிகாரி போல் நடித்து க்யூஆர் ஸ்கேன் செய்து பின் போடச் சொல்லும் ஓஎல்எக்ஸ் மோசடி",
        "patterns": [
            r"(?i)(army officer|ராணுவ அதிகாரி).*?(olx|furniture|bike|sofa).*?(advance|scan qr|upi pin|scanner)",
            r"(?i)(scan (this )?qr code).*?(input upi pin|receive advance)",
        ]
    },
    {
        "id": "RULE_SIM_BLOCK_5G",
        "family": "sim_kyc",
        "weight": 0.78,
        "en_reason": "Fake telecom alert threatening SIM card deactivation unless KYC/5G upgrade completed",
        "ta_reason": "சிம் கார்டு முடங்கும் என அச்சுறுத்தி போலி 5G அல்லது e-KYC செய்யத் தூண்டுகிறது",
        "patterns": [
            r"(?i)(sim card|4g sim).*?(blocked|deactivated|முடக்கப்படும்|tonight).*?(5g|e-kyc|biometric|renew)",
            r"(?i)(sim-5g-upgrade|airtel alert.*?sim card)",
        ]
    },
    {
        "id": "RULE_INCOME_TAX_REFUND",
        "family": "govt_refund",
        "weight": 0.85,
        "en_reason": "Fake tax refund or government relief grant order soliciting bank credentials",
        "ta_reason": "வருமான வரி ரீஃபண்ட் அல்லது அரசு நிதி வந்துள்ளதாக ஆசைகாட்டி வங்கி விவரங்களை திருடுகிறது",
        "patterns": [
            r"(?i)(income tax|வருமான வரித்துறை).*?(refund of rs|வரி ரீஃபண்ட்).*?(approved|pending|click|update bank)",
            r"(?i)(tax refund order of rs).*?(confirm your bank|credit your bank)",
            r"(?i)(pm subsidy|பிரதமர் நிவாரண நிதி).*?(grant of rs|claim|பதிவு செய்யவும்)",
        ]
    },
    {
        "id": "RULE_SHORT_URL",
        "family": "short_url",
        "weight": 0.65,
        "en_reason": "Uses a link shortener (e.g. bit.ly, tinyurl) to obscure the true website destination",
        "ta_reason": "உண்மையான இணையதள முகவரியை மறைக்க சுருக்கப்பட்ட லிங்கைப் பயன்படுத்துகிறது",
        "patterns": [
            r"(?i)https?://(bit\.ly|tinyurl\.com|is\.gd|cutt\.ly|t\.ly|t\.co|rb\.gy|shorturl\.at)/[a-zA-Z0-9_\-]+",
        ]
    },
    {
        "id": "RULE_SUSPICIOUS_TLD",
        "family": "suspicious_tld",
        "weight": 0.72,
        "en_reason": "Link points to an unusual or high-risk domain extension (.xyz, .top, .click, etc.)",
        "ta_reason": "மோசடிகளில் அதிகம் பயன்படுத்தப்படும் ஆபத்தான டொமைன் (.xyz, .top, .click) லிங்க் உள்ளது",
        "patterns": [
            r"(?i)https?://[a-zA-Z0-9\-\.]+\.(xyz|top|click|buzz|club|vip|work|site|online|live|loan|icu|stream)/[^\s]*",
            r"(?i)https?://[a-zA-Z0-9\-\.]+\.(xyz|top|click|buzz|club|vip|work|site|online|live|loan|icu|stream)\b",
        ]
    },
    {
        "id": "RULE_PAN_AADHAAR_MANDATORY_LINK",
        "family": "kyc",
        "weight": 0.82,
        "en_reason": "Urgent pressure to link PAN/Aadhaar via external link under threat of deactivation",
        "ta_reason": "சேவை முடங்கும் என அச்சுறுத்தி வெளி லிங்க் மூலம் பான்/ஆதார் இணைக்க அவசரப்படுத்துகிறது",
        "patterns": [
            r"(?i)(link pan|link aadhaar|பான் கார்டு இணைக்க|ஆதார் இணைக்க|aathar link).*?(http|click|லிங்க்|இங்கே)",
            r"(?i)(pan card link panna|aadhaar card.*?link).*?(http|link)",
        ]
    },
    {
        "id": "RULE_RAW_IP_URL",
        "family": "raw_ip",
        "weight": 0.88,
        "en_reason": "Link uses a raw numeric IP address instead of a genuine registered domain name",
        "ta_reason": "டொமைன் பெயருக்குப் பதிலாக எண்களாலான ஐபி (IP) முகவரியைப் பயன்படுத்துகிறது",
        "patterns": [
            r"(?i)https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?(/[^\s]*)?",
        ]
    },
    {
        "id": "RULE_URGENT_DEADLINE",
        "family": "urgency",
        "weight": 0.45,
        "en_reason": "Creates intense artificial panic and strict deadlines to rush the victim",
        "ta_reason": "யோசித்து செயல்பட விடாமல் பதற்றத்தை ஏற்படுத்த குறுகிய காலக்கெடு விடுக்கிறது",
        "patterns": [
            r"(?i)(within 24 hours|within 2 hours|within 1 hour|இன்று இரவு 9\.?30|tonight at 9:30|கடைசி நாள் இன்று|expire midnight|today itself)",
            r"(?i)(immediate penalty|immediately|urgent action|அவசரம்|இன்றிரவு)",
        ]
    },
    {
        "id": "RULE_BETTING_CASINO",
        "family": "betting",
        "weight": 0.70,
        "en_reason": "Illegal gambling, casino, or color prediction betting app advertisement",
        "ta_reason": "சட்டவிரோத ஆன்லைன் ரம்மி அல்லது வண்ண கணிப்பு சூதாட்ட செயலிகளை ஊக்குவிக்கிறது",
        "patterns": [
            r"(?i)(online rummy|color prediction|casino|aviator game).*?(bonus|win rs|deposit|sign up)",
            r"(?i)(ஆன்லைன் ரம்மி|கேசினோ).*?(போனஸ்|வெல்லுங்கள்)",
        ]
    }
]

# ==========================================
# SAFE SIGNAL PATTERNS
# ==========================================
SAFE_SIGNALS = [
    {
        "id": "SAFE_OTP_NEVER_SHARE_WARNING",
        "patterns": [
            r"(?i)(never share (this )?otp|do not share (this )?otp|வங்கி ஒருபோதும் otp கேட்காது|யாரிடமும் (ஒருபோதும் )?பகிராதீர்கள்|வங்கியிடம் கூட பகிராதீர்கள்|bank officials never ask for otp|keep your (banking )?credentials private)",
            r"(?i)(banks never ask for your confidential|rbi kehta hai|do not share otp or click)",
        ]
    },
    {
        "id": "SAFE_DELIVERY_RIDE_OTP",
        "patterns": [
            r"(?i)(share (this )?(otp|pin) (with|to) (your )?(delivery partner|delivery executive|driver|captain|agent|swiggy|zomato|ola|uber|rapido|amazon))",
            r"(?i)(டெலிவரி பார்ட்னரிடம்|ஓட்டுநரிடம்).*?(otp|பகிர்ந்து|தெரிவிக்கவும்)",
            r"(?i)(swiggy|zomato|ola|uber).*?(otp \d{4,6}|ride otp|delivery otp)",
        ]
    },
    {
        "id": "SAFE_BANK_TRANSACTION_ALERT",
        "patterns": [
            r"(?i)(debited (from|by)|credited (to|under)|பற்று வைக்கப்பட்டது|வரவு வைக்கப்பட்டது).*?(a/c xx\d+|avl bal|available balance)",
            r"(?i)(rs \d+[\d,\.]* (debited|credited)).*?(avl bal|balance rs)",
        ]
    },
    {
        "id": "SAFE_OFFICIAL_CONFIRMATION",
        "patterns": [
            r"(?i)(bill payment of rs \d+ received|payment of rs \d+ received successfully|டிக்கெட் pnr \d+ உறுதி செய்யப்பட்டது|appointment with dr\..*?is confirmed|pm-kisan: \d+th installment)",
            r"(?i)(campus drive|interview is scheduled|offer letter has been generated)",
        ]
    },
    {
        "id": "SAFE_NORMAL_CHAT_TRANSACTION",
        "patterns": [
            r"(?i)(movie ticket|room rent|lunch bill|dinner|groceries|காய்கறி|மருந்து|காலேஜ் பீஸ்).*?(gpay|phonepe|கூகுள் பே|போன்பே|google pay|anupiten|panren|பண்ணுங்க)",
            r"(?i)(sent you rs \d+|transferred rs \d+ for).*?(gpay|phonepe|google pay|dinner|snacks|bills)",
        ]
    }
]

# ==========================================
# SPECIFIC ADVICE BY SCAM FAMILY
# ==========================================
FAMILY_ADVICE = {
    "digital_arrest": {
        "en": "Law enforcement agencies (Police, CBI, Customs, ED) NEVER conduct 'digital arrest' or interrogate citizens over Skype/WhatsApp video calls. Disconnect immediately.",
        "ta": "காவல்துறை, சிபிஐ அல்லது எந்த அரசு அமைப்பும் வீடியோ காலில் 'டிஜிட்டல் கைது' செய்யாது. உடனடியாக அழைப்பைத் துண்டிக்கவும்."
    },
    "tneb": {
        "en": "TNEB/TANGEDCO never sends personal mobile numbers or threatens same-night power cuts. Check and pay your electricity bill only on the official portal tangedco.gov.in.",
        "ta": "மின்வாரியம் தனிப்பட்ட மொபைல் எண் தந்து இன்றிரவே மின்சாரம் துண்டிக்கப்படும் என குறுஞ்செய்தி அனுப்பாது. அதிகாரப்பூர்வ tangedco.gov.in தளத்தில் மட்டும் சரிபார்க்கவும்."
    },
    "kyc": {
        "en": "Banks never threaten to block accounts within hours via SMS links. Never click links to update KYC/PAN; visit your local branch or use your official bank app directly.",
        "ta": "வங்கி ஒருபோதும் எஸ்எம்எஸ் லிங்க் மூலம் கணக்கை முடக்குவதாக மிரட்டாது. KYC புதுப்பிக்க உங்கள் வங்கிக் கிளைக்கு செல்லவும் அல்லது அதிகாரப்பூர்வ வங்கியை செயலியை மட்டும் பயன்படுத்தவும்."
    },
    "otp_theft": {
        "en": "Bank employees never ask for OTP or PIN under any pretext. Never share or forward any verification code sent to your mobile phone.",
        "ta": "வங்கி அதிகாரிகள் ஒருபோதும் தொலைபேசியில் ஓடிபி (OTP) கேட்க மாட்டார்கள். உங்கள் மொபைலுக்கு வரும் சரிபார்ப்புக் குறியீட்டை யாரிடமும் பகிராதீர்கள்."
    },
    "upi_fraud": {
        "en": "Entering your UPI PIN or scanning a QR code always DEBITS money from your account. You NEVER need to enter your UPI PIN to receive money or refunds.",
        "ta": "UPI PIN போட்டாலோ QR ஸ்கேன் செய்தாலோ உங்கள் பணம்தான் கழியும். பணம் வரவோ ரீஃபண்ட் பெறவோ ஒருபோதும் UPI PIN போடத் தேவையில்லை."
    },
    "job_scam": {
        "en": "No genuine company pays daily money simply for liking YouTube videos or giving hotel reviews. This is a prepaid task trap designed to siphon deposits.",
        "ta": "யூடியூப் லைக் செய்யவோ ஹோட்டல் ரேட்டிங் போடவோ எந்த நிறுவனமும் தினசரி பணம் தராது. முதலீடு செய்ய வைத்து பணத்தை திருடும் பொறி இது."
    },
    "lottery": {
        "en": "You cannot win a lottery or lucky draw you never entered. Genuine contests never require upfront 'processing fees' or taxes to release winnings.",
        "ta": "பங்குபெறாத போட்டிகளில் பரிசு விழ வாய்ப்பில்லை. பரிசுத்தொகைக்கு முன்கூட்டியே கட்டணம் கேட்கும் எந்த அறிவிப்பையும் நம்பாதீர்கள்."
    },
    "remote_app": {
        "en": "Never install AnyDesk, TeamViewer, or RustDesk on the instruction of an unknown caller. They allow scammers to control your phone and drain your bank account.",
        "ta": "அறியாத நபர்களின் பேச்சைக் கேட்டு AnyDesk அல்லது TeamViewer செயலிகளை நிறுவ வேண்டாம். அவை உங்கள் வங்கி கணக்கை காலியாக்கிவிடும்."
    },
    "apk_malware": {
        "en": "Never download or install APK files from SMS links or WhatsApp. Install apps strictly from the official Google Play Store or Apple App Store.",
        "ta": "எஸ்எம்எஸ் அல்லது வாட்ஸ்அப் வழியாக வரும் APK செயலிகளை ஒருபோதும் நிறுவ வேண்டாம். அதிகாரப்பூர்வ கூகுள் பிளே ஸ்டோரில் மட்டுமே செயலிகளை பதிவிறக்கவும்."
    },
    "customs_parcel": {
        "en": "Customs officers never demand money settlements or spot fines via personal UPI or video calls for detained parcels. Hang up immediately.",
        "ta": "பார்சலில் பொருள் பிடிபட்டதாகக் கூறி சுங்கத்துறை தனிப்பட்ட UPI மூலம் பணம் கட்டச் சொல்லாது. உடனடியாக இணைப்பை துண்டிக்கவும்."
    },
    "loan_app": {
        "en": "Instant loan apps that offer loans without KYC or CIBIL checks often harass contacts and demand extortionate interest. Use only RBI-registered NBFC apps.",
        "ta": "ஆவணங்கள் இன்றி உடனடி கடன் தரும் செயலிகள் உங்கள் தொடர்புகளைத் திருடி மிரட்டும் அபாயம் உண்டு. ரிசர்வ் வங்கி அங்கீகரித்த வங்கிகளை மட்டும் அணுகவும்."
    },
    "investment": {
        "en": "Guaranteed 200%-500% returns in stocks or crypto are mathematically impossible. Unregistered Telegram/WhatsApp trading groups are illegal Ponzi schemes.",
        "ta": "பங்குச் சந்தையில் உத்தரவாத அபரிமித லாபம் என்பது சாத்தியமற்றது. டெலிகிராம் வாட்ஸ்அப் முதலீட்டு குழுக்களில் பணத்தைப் போட்டு ஏமாறாதீர்கள்."
    },
    "sextortion": {
        "en": "Do not panic or pay ransom. Paying only invites more extortion demands. Block the caller, preserve screenshots, and immediately call 1930.",
        "ta": "பயந்து பணம் செலுத்தாதீர்கள்; பணம் தந்தால் மீண்டும் மிரட்டுவார்கள். எண்ணை பிளாக் செய்துவிட்டு உடனடியாக 1930 எண்ணில் புகார் அளிக்கவும்."
    },
    "hi_mum": {
        "en": "Call your family member directly on their known original phone number to verify their safety before transferring any emergency money.",
        "ta": "பணம் அனுப்பும் முன் உங்கள் குடும்பத்தினரின் பழைய அசல் எண்ணுக்கு போன் செய்து உண்மையிலேயே அவர்கள்தானா என்பதை உறுதிப்படுத்திக் கொள்ளுங்கள்."
    },
    "olx_army": {
        "en": "Fraudsters frequently impersonate Indian Army personnel on OLX. Remember that scanning a QR code or entering a PIN only SENDS money, never receives it.",
        "ta": "ஓஎல்எக்ஸ் தளத்தில் ராணுவ வீரர் போல் நடித்து ஏமாற்றுவோர் அதிகம். க்யூஆர் ஸ்கேன் செய்து பின் போட்டால் உங்கள் பணம் போய்விடும் என்பதை மறவாதீர்கள்."
    }
}

GENERIC_ADVICE = [
    {
        "en": "Never share your banking password, ATM PIN, or OTP with anyone under any circumstances.",
        "ta": "வங்கி பாஸ்வேர்ட், ஏடிஎம் பின் அல்லது ஓடிபி-யை எந்தக் காரணத்திற்காகவும் யாரிடமும் பகிராதீர்கள்."
    },
    {
        "en": "Do not click on shortened, unsolicited, or unverified links.",
        "ta": "சுருக்கப்பட்ட அல்லது தெரியாத நபர்களிடமிருந்து வரும் லிங்குகளை கிளிக் செய்யாதீர்கள்."
    },
    {
        "en": "Report suspicious SMS and spam senders on the Chakshu Portal (sancharsaathi.gov.in).",
        "ta": "சந்தேகத்திற்கிடமான குறுஞ்செய்திகளை மத்திய அரசின் சக்ஷு போர்ட்டலில் (sancharsaathi.gov.in) புகார் செய்யவும்."
    },
    {
        "en": "If you have suffered a financial loss, immediately call the National Cyber Crime Helpline at 1930 or lodge a complaint at cybercrime.gov.in.",
        "ta": "நிதி இழப்பு ஏற்பட்டிருந்தால் உடனடியாக 1930 என்ற உதவி எண்ணை அழைக்கவும் அல்லது cybercrime.gov.in-ல் புகார் பதிவு செய்யவும்."
    }
]

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def normalize_text(text: str) -> str:
    """Normalize unicode, whitespace, and strip control chars."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    # Collapse multiple spaces but preserve text structure
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    return text.strip()

def detect_language(text: str) -> str:
    """
    Detect whether text is Tamil script ('ta'), Tanglish ('tanglish'), or English ('en').
    """
    if not text:
        return "en"

    # Count Tamil unicode characters (U+0B80 - U+0BFF)
    tamil_chars = len(re.findall(r"[\u0B80-\u0BFF]", text))
    alpha_chars = len(re.findall(r"[a-zA-Z\u0B80-\u0BFF]", text))

    if alpha_chars > 0 and (tamil_chars / alpha_chars) >= 0.15:
        return "ta"

    # Tanglish word markers
    tanglish_markers = [
        r"\bunga(l)?\b", r"\baagum\b", r"\baachu\b", r"\baagiruku\b", r"\bpannu(nga|m)?\b",
        r"\bpanren\b", r"\bpanunga\b", r"\bsolunga\b", r"\bkulla\b", r"\binaiku\b",
        r"\bnaalaiku\b", r"\banupu(nga|ren)?\b", r"\bthappaa\b", r"\biruku\b", r"\bthavirkka\b",
        r"\bvanga\b", r"\bvaravum\b", r"\bpesuren\b", r"\bmachi\b", r"\bmachan\b",
        r"\bdei\b", r"\bseri\b", r"\billa\b", r"\bkedaika\b", r"\bkudunga\b", r"\bkaatunga\b",
        r"\bpudichitanga\b", r"\beduthuko\b", r"\bvarren\b", r"\bthevai\b", r"\bpo(ga|guthu)\b",
        r"\bkadai\b", r"\bvaliya\b"
    ]
    tgl_hits = 0
    text_lower = text.lower()
    for marker in tanglish_markers:
        if re.search(marker, text_lower):
            tgl_hits += 1

    if tgl_hits >= 1:
        return "tanglish"

    return "en"

def extract_urls(text: str):
    """Find all URLs in the text."""
    url_pattern = r"(https?://[^\s]+)"
    return re.findall(url_pattern, text)

def is_official_domain(hostname: str) -> bool:
    """Check if hostname matches or is a subdomain of an official domain."""
    hostname = hostname.lower()
    for official in OFFICIAL_DOMAINS:
        if hostname == official or hostname.endswith("." + official):
            return True
    return False

def analyze_url(url: str):
    """
    Examine URL against shorteners, suspicious TLDs, raw IPs, and lookalike brand domains.
    Returns list of matched rule objects.
    """
    findings = []
    try:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return findings

        # If it's an official domain, it's not a lookalike or malicious link
        if is_official_domain(hostname):
            return findings

        # Check raw IP
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
            findings.append({
                "rule_id": "RULE_RAW_IP_URL",
                "weight": 0.88,
                "en": f"Link uses raw IP address ({hostname}) rather than a registered domain",
                "ta": f"டொமைன் பெயருக்குப் பதிலாக எண்களாலான ஐபி முகவரியைப் ({hostname}) பயன்படுத்துகிறது",
                "span": url
            })

        # Check shorteners
        if hostname in SHORTENER_DOMAINS or any(hostname.endswith("." + s) for s in SHORTENER_DOMAINS):
            findings.append({
                "rule_id": "RULE_SHORT_URL",
                "weight": 0.65,
                "en": f"Link uses URL shortener ({hostname}) to disguise the destination",
                "ta": f"உண்மையான தளத்தை மறைக்க சுருக்கப்பட்ட லிங்கைப் ({hostname}) பயன்படுத்துகிறது",
                "span": url
            })

        # Check suspicious TLDs
        for tld in SUSPICIOUS_TLDS:
            if hostname.endswith(tld):
                findings.append({
                    "rule_id": "RULE_SUSPICIOUS_TLD",
                    "weight": 0.72,
                    "en": f"Link uses high-risk suspicious TLD ({tld})",
                    "ta": f"மோசடிகளில் அதிகம் பயன்படும் ஆபத்தான டொமைன் விரிவாக்கத்தை ({tld}) கொண்டுள்ளது",
                    "span": url
                })
                break

        # Check lookalike brand domains (contains brand keyword but NOT official domain)
        for kw in TARGET_BRAND_KEYWORDS:
            if kw in hostname:
                findings.append({
                    "rule_id": "RULE_LOOKALIKE_DOMAIN",
                    "weight": 0.88,
                    "en": f"Lookalike domain '{hostname}' mimics trusted organization '{kw}'",
                    "ta": f"அங்கீகரிக்கப்படாத போலி தளம் '{hostname}' ('{kw}' போல் நடிக்கிறது)",
                    "span": url
                })
                break

        # Check APK extension
        if parsed.path.lower().endswith(".apk") or ".apk" in url.lower():
            findings.append({
                "rule_id": "RULE_SUSPICIOUS_APK",
                "weight": 0.90,
                "en": f"Link attempts to download an untrusted Android APK file",
                "ta": f"ஆபத்தான APK கோப்பைப் பதிவிறக்கம் செய்ய அழைக்கிறது",
                "span": url
            })

    except Exception:
        pass

    return findings

def check_safe_signals(text: str) -> bool:
    """Determine if message contains strong safe contextual signals."""
    # Check official domain URLs
    for url in extract_urls(text):
        try:
            parsed = urlparse(url)
            if parsed.hostname and is_official_domain(parsed.hostname):
                return True
        except Exception:
            pass

    for sig in SAFE_SIGNALS:
        for p in sig["patterns"]:
            if re.search(p, text):
                return True
    return False

def calculate_sha256(filepath: str) -> str:
    """Calculate SHA256 hash of a file."""
    if not os.path.exists(filepath):
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

# ==========================================
# ML CLASSIFIER WRAPPER
# ==========================================
class KavasamMLModel:
    def __init__(self):
        self.pipeline = None
        self.dataset_hash = None
        self.sklearn_version = sklearn.__version__
        self.version = MODEL_VERSION

    def train(self, texts, labels):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                analyzer="char_wb",
                ngram_range=(2, 5),
                min_df=2,
                sublinear_tf=True
            )),
            ("clf", LogisticRegression(
                C=2.5,
                max_iter=1000,
                random_state=42,
                solver="lbfgs"
            ))
        ])
        # label 1 for scam, 0 for safe
        y = [1 if (lbl == 1 or str(lbl).lower() in ("scam", "1")) else 0 for lbl in labels]
        self.pipeline.fit(texts, y)
        self.dataset_hash = calculate_sha256(MESSAGES_CSV)

    def predict_proba(self, text: str) -> float:
        if self.pipeline is None:
            return 0.5
        probs = self.pipeline.predict_proba([text])[0]
        # Class 1 is 'scam'
        return float(probs[1])

    def save(self, path=MODEL_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {
            "pipeline": self.pipeline,
            "dataset_hash": self.dataset_hash,
            "sklearn_version": self.sklearn_version,
            "version": self.version
        }
        joblib.dump(data, path)

    @classmethod
    def load_or_train(cls, model_path=MODEL_PATH, dataset_path=MESSAGES_CSV):
        instance = cls()
        current_hash = calculate_sha256(dataset_path)

        if os.path.exists(model_path):
            try:
                saved = joblib.load(model_path)
                if (saved.get("dataset_hash") == current_hash and
                    saved.get("sklearn_version") == sklearn.__version__):
                    instance.pipeline = saved["pipeline"]
                    instance.dataset_hash = saved["dataset_hash"]
                    instance.sklearn_version = saved["sklearn_version"]
                    instance.version = saved.get("version", MODEL_VERSION)
                    return instance
            except Exception:
                pass

        # If not valid or missing, train from dataset
        import csv
        texts, labels = [], []
        if os.path.exists(dataset_path):
            with open(dataset_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    texts.append(row["text"])
                    labels.append(row["label"])

            if texts:
                instance.train(texts, labels)
                instance.save(model_path)

        return instance

# Global engine model instance
_GLOBAL_MODEL = None

def get_model():
    global _GLOBAL_MODEL
    if _GLOBAL_MODEL is None:
        _GLOBAL_MODEL = KavasamMLModel.load_or_train()
    return _GLOBAL_MODEL

# ==========================================
# MAIN CHECK FUNCTION
# ==========================================
def check_message(raw_text: str) -> dict:
    """
    Main evaluation pipeline:
    1. Normalization & Language Detection
    2. URL parsing & lookalike/shortener rules
    3. Regex Rule Matching (Noisy-OR aggregation)
    4. Safe Signal discounting
    5. ML character n-gram prediction
    6. Hybrid score (60% rules + 40% ML) with thresholding
    7. Spans, bilingual reasons, and scam-tailored advice
    """
    normalised = normalize_text(raw_text)
    if not normalised:
        return {
            "verdict": "Safe",
            "label": {"en": "Safe", "ta": "பாதுகாப்பானது"},
            "risk": 0,
            "confidence": 100,
            "rule_score": 0.0,
            "ml_score": 0.0,
            "final_score": 0.0,
            "reasons": [],
            "advice": GENERIC_ADVICE,
            "normalised_text": "",
            "highlight_spans": [],
            "detected_language": "en",
            "model_version": MODEL_VERSION
        }

    lang = detect_language(normalised)

    # 1. Match Rules
    matched_rules = []
    highlight_spans = []
    seen_spans = set()

    for rule in RULES:
        rule_hit = False
        for pat in rule["patterns"]:
            for match in re.finditer(pat, normalised):
                start, end = match.span()
                rule_hit = True
                span_key = (start, end)
                if span_key not in seen_spans:
                    seen_spans.add(span_key)
                    highlight_spans.append({
                        "start": start,
                        "end": end,
                        "text": normalised[start:end],
                        "rule_id": rule["id"]
                    })
        if rule_hit:
            matched_rules.append(rule)

    # 2. Analyze embedded URLs
    urls = extract_urls(normalised)
    for url in urls:
        findings = analyze_url(url)
        for f in findings:
            matched_rules.append({
                "id": f["rule_id"],
                "family": "url",
                "weight": f["weight"],
                "en_reason": f["en"],
                "ta_reason": f["ta"]
            })
            # Add highlight for url
            idx = normalised.find(url)
            if idx != -1:
                span_key = (idx, idx + len(url))
                if span_key not in seen_spans:
                    seen_spans.add(span_key)
                    highlight_spans.append({
                        "start": idx,
                        "end": idx + len(url),
                        "text": url,
                        "rule_id": f["rule_id"]
                    })

    # Sort highlight spans by start position
    highlight_spans.sort(key=lambda s: s["start"])

    # 3. Calculate Rule Score using Noisy-OR: score = 1 - product(1 - weight)
    if matched_rules:
        prod = 1.0
        for r in matched_rules:
            w = r.get("weight", 0.5)
            prod *= (1.0 - w)
        rule_score = 1.0 - prod
    else:
        rule_score = 0.0

    # 4. Check Safe Signals
    is_safe = check_safe_signals(normalised)
    # Check if safe warning should suppress low-confidence triggers
    # If safe signal matches and NO high-severity scam pattern fired (> 0.82)
    has_critical_scam = any(r.get("weight", 0) >= 0.85 for r in matched_rules)

    if is_safe and not has_critical_scam:
        # Heavily dampen rule score for legitimate OTPs/receipts/bank alerts
        rule_score = rule_score * 0.15
        if rule_score < 0.20:
            highlight_spans = []
            matched_rules = []

    # 5. ML Scoring
    model = get_model()
    ml_score = model.predict_proba(normalised)

    if is_safe and not has_critical_scam:
        ml_score = min(ml_score, 0.20)

    # 6. Hybrid Score: 60% rules + 40% ML
    final_score = (0.60 * rule_score) + (0.40 * ml_score)

    # Rule overrides: Multiple strong scam rules force Likely Scam
    strong_rule_count = sum(1 for r in matched_rules if r.get("weight", 0) >= 0.80)
    if strong_rule_count >= 2 or rule_score >= 0.80:
        if final_score < 0.65:
            final_score = 0.65

    # Clamp
    final_score = max(0.0, min(1.0, final_score))

    # 7. Verdict
    # Thresholds: < 0.30 Safe, 0.30 - 0.55 Suspicious, >= 0.55 Likely Scam
    if final_score < 0.30:
        verdict = "Safe"
        label = {"en": "Safe", "ta": "பாதுகாப்பானது"}
    elif final_score < 0.55:
        verdict = "Suspicious"
        label = {"en": "Suspicious", "ta": "சந்தேகத்திற்குரியது"}
    else:
        verdict = "Likely Scam"
        label = {"en": "Likely Scam", "ta": "மோசடி சாத்தியம்"}

    # Confidence calculation based on score clarity
    margin = abs(final_score - 0.425)  # distance from boundary midpoint
    confidence = int(min(98, max(65, 60 + margin * 80)))

    # Risk percentage
    risk = int(round(final_score * 100))

    # 8. Reasons: Top 5 matched rules
    # Deduplicate rules by ID
    dedup_rules = {}
    for r in matched_rules:
        rid = r["id"]
        if rid not in dedup_rules or r.get("weight", 0) > dedup_rules[rid].get("weight", 0):
            dedup_rules[rid] = r

    sorted_rules = sorted(dedup_rules.values(), key=lambda x: x.get("weight", 0), reverse=True)[:5]
    reasons = []
    for r in sorted_rules:
        reasons.append({
            "rule_id": r["id"],
            "en": r["en_reason"],
            "ta": r["ta_reason"],
            "weight": round(r.get("weight", 0.5), 2)
        })

    # If Safe, provide reassuring explanation
    if verdict == "Safe":
        if is_safe:
            reasons = [{
                "rule_id": "REASON_SAFE_TRANSACTION",
                "en": "Message exhibits legitimate transactional patterns, official advisory format, or standard conversation.",
                "ta": "இச்செய்தி உண்மையான வங்கி பரிவர்த்தனை, விழிப்புணர்வு அல்லது இயல்பான உரையாடல் அமைப்பைக் கொண்டுள்ளது.",
                "weight": 0.1
            }]
        elif not reasons:
            reasons = [{
                "rule_id": "REASON_NO_SUSPICIOUS_SIGNALS",
                "en": "No known scam patterns, malicious links, or social engineering tactics detected.",
                "ta": "எந்தவொரு சந்தேகத்திற்கிடமான மோசடி வழிகாட்டலோ, போலி இணைப்புகளோ கண்டறியப்படவில்லை.",
                "weight": 0.05
            }]

    # 9. Advice: Specific top family advice + generic guidance
    advice = []
    matched_families = [r.get("family") for r in sorted_rules if r.get("family")]
    top_family = matched_families[0] if matched_families else None

    if top_family and top_family in FAMILY_ADVICE:
        advice.append(FAMILY_ADVICE[top_family])

    # Add generic advice
    for g in GENERIC_ADVICE:
        advice.append(g)

    return {
        "verdict": verdict,
        "label": label,
        "risk": risk,
        "confidence": confidence,
        "rule_score": round(rule_score, 4),
        "ml_score": round(ml_score, 4),
        "final_score": round(final_score, 4),
        "reasons": reasons,
        "advice": advice,
        "normalised_text": normalised,
        "highlight_spans": highlight_spans,
        "detected_language": lang,
        "model_version": MODEL_VERSION
    }
