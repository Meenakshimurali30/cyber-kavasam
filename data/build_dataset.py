"""
build_dataset.py: Generates training messages.csv (3000+ rows, 135+ template groups)
and gold_test.csv (75 hand-crafted benchmark messages) for Cyber Kavasam.
"""

import os
import random
import csv

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

BANKS = ["SBI", "HDFC", "ICICI", "Axis Bank", "Canara Bank", "Indian Bank", "IOB", "Kotak", "PNB", "Bank of Baroda", "Union Bank"]
BANKS_TA = ["எஸ்பிஐ", "ஹெச்டிஎஃப்சி", "ஐசிஐசிஐ", "இந்தியன் வங்கி", "கனரா வங்கி", "கோடக் வங்கி", "பரோடா வங்கி"]
AMOUNTS = ["499", "999", "1,250", "2,499", "5,000", "9,999", "15,000", "25,000", "50,000", "1,00,000", "2,50,000"]
AMOUNTS_NUM = ["350", "500", "850", "1200", "2400", "5000", "10000", "25000", "50000"]
OTPS = ["4829", "8391", "2048", "9182", "5512", "1092", "7381", "3491", "8823"]
ACCOUNTS = ["XX4829", "XX1092", "XX8471", "XX3920", "XX5512", "XX9182", "XX7364"]
PHONES = ["9840123456", "9876543210", "9444012345", "8939012345", "7358012345", "9150012345", "9841029384", "9445019283"]
NAMES = ["Ramesh", "Karthik", "Priya", "Anand", "Suresh", "Murugan", "Selvi", "Kavitha", "Dinesh", "Vijay", "Saravanan", "Lakshmi"]
COMPANIES = ["Amazon", "Flipkart", "Telegram", "YouTube", "FedEx", "DHL", "BlueDart", "Delhivery"]
DATES = ["24-Oct", "25-Oct", "26-Oct", "12-Nov", "15-Nov"]

SCAM_URLS = [
    "http://bit.ly/sbi-kyc-quick",
    "https://tinyurl.com/tneb-bill-pay",
    "http://is.gd/axis-update-2026",
    "https://cutt.ly/claim-refund-it",
    "http://sbi-netbanking-verify.xyz/login",
    "https://tneb-online-service.top/pay",
    "http://income-tax-refund.click/claim",
    "https://icici-reward-portal.club/redeem",
    "http://hdfc-kyc-alert.buzz/update",
    "https://pm-kisan-claim.vip/login",
    "http://192.168.1.105/apk/sbi.apk",
    "http://45.33.32.156/ebill/tneb.apk",
    "https://anydesk-support.top/dl",
    "http://fastag-recharge-failed.work/pay",
    "https://echallan-traffic-fine.vip/view",
    "http://loan-approval-quick.site/apply",
    "https://aadhaar-update-portal.online/pan",
    "http://sim-5g-upgrade.top/sim",
    "https://olx-army-pay.click/qr",
    "http://lic-bonus-claim.xyz/bonus",
]

OFFICIAL_URLS = [
    "https://www.onlinesbi.sbi",
    "https://netbanking.hdfcbank.com",
    "https://www.icicibank.com",
    "https://www.tangedco.gov.in",
    "https://www.tnebnet.org",
    "https://incometax.gov.in",
    "https://pmkisan.gov.in",
    "https://sancharsaathi.gov.in",
    "https://cybercrime.gov.in",
]

TEMPLATES = []

def t(gid, label, lang, template_strs):
    """Register a template group with variations."""
    TEMPLATES.append({
        "group": gid,
        "label": label,
        "lang": lang,
        "templates": template_strs
    })

# ==========================================
# 1. SCAM TEMPLATES - TAMIL SCRIPT (28 groups)
# ==========================================
t("scam_kyc_ta_01", "scam", "ta", [
    "அன்புள்ள வாடிக்கையாளரே, உங்கள் {bank} கணக்கு இன்று முடக்கப்படும். உடனே KYC புதுப்பிக்க {scam_url} கிளிக் செய்யவும்.",
    "எச்சரிக்கை! உங்கள் வங்கி கணக்கு KYC காலாவதியானது. 24 மணி நேரத்தில் முடக்கப்படாமல் இருக்க {scam_url} சென்று புதுப்பிக்கவும்.",
])
t("scam_kyc_ta_02", "scam", "ta", [
    "உங்கள் பான் கார்டு வங்கி கணக்குடன் இணைக்கப்படவில்லை. உடனே அப்டேட் செய்ய {scam_url} பார்க்கவும் அல்லது கணக்கு பிளாக் செய்யப்படும்.",
    "அவசரம்! பான் கார்டு இணைக்க கடைசி நாள் இன்று. அப்டேட் செய்ய {scam_url} தொடவும்.",
])
t("scam_tneb_ta_01", "scam", "ta", [
    "அன்புள்ள நுகர்வோரே, உங்கள் முந்தைய மாத மின் கட்டணம் செலுத்தப்படாததால் இன்று இரவு 9.30 மணிக்கு மின்சாரம் துண்டிக்கப்படும். உடனே {phone} எண்ணில் மின் அதிகாரியை தொடர்பு கொள்ளவும்.",
    "TNEB எச்சரிக்கை: உங்கள் EB பில் அப்டேட் ஆகவில்லை. இன்றிரவு மின் இணைப்பு துண்டிக்கப்படும். சரிசெய்ய {phone} அழைக்கவும் அல்லது {scam_url} கிளிக் செய்யவும்.",
])
t("scam_tneb_ta_02", "scam", "ta", [
    "மின்சார வாரியம்: உங்கள் மின் கட்டண பாக்கி ரூ {amount_num}. உடனடியாக செலுத்த {scam_url} கிளிக் செய்க, இல்லையெனில் மின் இணைப்பு துண்டிக்கப்படும்.",
    "TNEB உதவி மையம்: உங்கள் வீட்டின் மின் இணைப்பு துண்டிப்பை தவிர்க்க உடனடியாக மின் அலுவலரை {phone} தொடர்பு கொள்ளவும்.",
])
t("scam_otp_theft_ta_01", "scam", "ta", [
    "வங்கி அதிகாரி பேசுகிறேன்: உங்கள் கணக்கில் ரூ {amount} கிரெடிட் ஆக வந்துள்ளது. பெற உங்கள் மொபைலுக்கு வந்த OTP எண்ணை {phone} எண்ணுக்கு அனுப்பவும்.",
    "வங்கி சரிபார்ப்பு: உங்கள் கணக்கு பாதுகாப்புக்காக அனுப்பப்பட்ட OTP எண்ணை உடனடியாக தெரிவிக்கவும்.",
])
t("scam_upi_ta_01", "scam", "ta", [
    "தவறுதலாக உங்கள் Google Pay கணக்கிற்கு ரூ {amount} அனுப்பிவிட்டேன். தயவுசெய்து இந்த லிங்க் {scam_url} கிளிக் செய்து பணத்தை திருப்பி அனுப்பவும்.",
    "சார் ரூ {amount} தவறுதலாக உங்கள் PhonePe-க்கு வந்துவிட்டது. Refund பெற UPI PIN போட்டு ஏற்கவும்: {scam_url}",
])
t("scam_digital_arrest_ta_01", "scam", "ta", [
    "மும்பை சைபர் கிரைம் போலீஸ்: உங்கள் ஆதார் எண் சட்டவிரோத பணப் பரிவர்த்தனையில் பயன்படுத்தப்பட்டுள்ளது. டிஜிட்டல் கைது தவிர்க்க உடனடியாக ஸ்கைப்/வாட்ஸ்அப் காலில் {phone} வரவும்.",
    "சிபிஐ தலைமை அலுவலகம்: உங்கள் பெயரில் தடைசெய்யப்பட்ட போதைப்பொருள் பார்சல் பிடிபட்டுள்ளது. பிடிவாரண்ட் தவிர்க்க {phone} தொடர்பு கொள்ளவும்.",
])
t("scam_job_ta_01", "scam", "ta", [
    "வீட்டிலிருந்தே வேலை! யூடியூப் வீடியோக்களுக்கு லைக் செய்து தினமும் ரூ {amount_num} முதல் ரூ 5000 வரை சம்பாதிக்கலாம். வாட்ஸ்அப் {phone} தொடர்பு கொள்ளவும்.",
    "பார்ட் டைம் வேலை வாய்ப்பு: தினமும் 1-2 மணி நேரம் மொபைலில் பணிபுரிந்து ரூ {amount} ஈட்டலாம். உடனே சேர {scam_url}",
])
t("scam_lottery_ta_01", "scam", "ta", [
    "வாழ்த்துக்கள்! உங்கள் மொபைல் எண் KBC அகில இந்திய லக்கி டிராவில் ரூ 25,00,000 வென்றுள்ளது. பரிசுத்தொகையை பெற {phone} அழைக்கவும்.",
    "நீங்கள் புதிய டாடா காரை பரிசாக வென்றுள்ளீர்கள்! பதிவு கட்டணம் ரூ 2500 செலுத்த {scam_url} கிளிக் செய்யவும்.",
])
t("scam_parcel_ta_01", "scam", "ta", [
    "FedEx கூரியர் அறிவிப்பு: உங்கள் வெளிநாட்டு பார்சலில் தடைசெய்யப்பட்ட மருந்துகள் மற்றும் போலி பாஸ்போர்ட் உள்ளன. சுங்கத்துறை நடவடிக்கை எடுக்காமல் இருக்க {phone} அழைக்கவும்.",
])
t("scam_loan_ta_01", "scam", "ta", [
    "உடனடி தனிநபர் கடன் ரூ {amount}! ஆவணங்கள் தேவையில்லை, 5 நிமிடத்தில் வங்கி கணக்கில் பணம். உடனடியாக பெற இந்த APK செயலியை டவுன்லோட் செய்யவும்: {scam_url}",
    "ரூ {amount} உடனடி கடன் ஒப்புதல் அளிக்கப்பட்டது. வட்டி 0%. உடனடியாக பெற {scam_url} தொடவும்.",
])
t("scam_investment_ta_01", "scam", "ta", [
    "பங்குச் சந்தை மற்றும் கிரிப்டோ முதலீட்டில் தினமும் 200% லாபம்! எங்கள் விஐபி டெலிகிராம் குரூப்பில் இணைய {scam_url} கிளிக் செய்யவும்.",
    "ரூ 1000 முதலீடு செய்து ஒரே நாளில் ரூ 10,000 சம்பாதிக்கலாம். அரசு அங்கீகாரம் பெற்ற திட்டம்: {scam_url}",
])
t("scam_apk_ta_01", "scam", "ta", [
    "உங்கள் {bank} ரிவார்டு பாயிண்ட்ஸ் ரூ {amount} பணமாக மாற்ற இந்த செயலியை இன்ஸ்டால் செய்யவும்: {scam_url}",
    "வங்கி பாதுகாப்பு அப்டேட்: உடனடியாக புதிய {bank}_Support.apk செயலியை பதிவிறக்கம் செய்து இன்ஸ்டால் செய்யவும்: {scam_url}",
])
t("scam_govt_refund_ta_01", "scam", "ta", [
    "வருமான வரித்துறை: உங்கள் வங்கிக் கணக்கிற்கு ரூ {amount} வரி ரீஃபண்ட் அனுமதிக்கப்பட்டுள்ளது. பெற உங்கள் வங்கி விவரங்களை {scam_url} உள்ளிடவும்.",
    "பிரதமர் நிவாரண நிதி ரூ {amount} உங்கள் கணக்கில் சேர உடனே {scam_url} பதிவு செய்யவும்.",
])
t("scam_sextortion_ta_01", "scam", "ta", [
    "உங்கள் அந்தரங்க வீடியோ எங்களிடம் உள்ளது. 2 மணி நேரத்தில் ரூ {amount} செலுத்தாவிட்டால் உங்கள் குடும்பத்தினர் மற்றும் நண்பர்களுக்கு அனுப்புவோம். வாட்ஸ்அப் {phone}",
])
t("scam_himum_ta_01", "scam", "ta", [
    "அம்மா, என் போன் உடைந்துவிட்டது. இது என் புதிய வாட்ஸ்அப் எண். உடனடியாக எனக்கு ரூ {amount} அவசரமாக தேவைப்படுகிறது, அனுப்பவும்: {phone}",
])
t("scam_betting_ta_01", "scam", "ta", [
    "ஆன்லைன் ரம்மி மற்றும் கேசினோவில் முதல் டெபாசிட்டுக்கு 500% போனஸ்! ரூ 500 செலுத்தி ரூ {amount} வெல்லுங்கள்: {scam_url}",
])
t("scam_credit_limit_ta_01", "scam", "ta", [
    "உங்கள் {bank} கிரெடிட் கார்டு வரம்பு ரூ {amount} வரை இலவசமாக உயர்த்தப்பட்டுள்ளது. செயல்படுத்த {scam_url} கிளிக் செய்க.",
])
t("scam_fastag_ta_01", "scam", "ta", [
    "உங்கள் பாஸ்டேக் (FASTag) கணக்கு முடக்கப்பட்டுள்ளது. அபராதம் தவிர்க்க உடனே ரீசார்ஜ் செய்து KYC முடிக்க: {scam_url}",
])
t("scam_donation_ta_01", "scam", "ta", [
    "கோவில் திருப்பணி மற்றும் ஏழைக் குழந்தைகள் மருத்துவ உதவிக்கு அவசர நிதி தேவை. நன்கொடை அளிக்க இந்த லிங்கை கிளிக் செய்யவும்: {scam_url}",
])
t("scam_insurance_ta_01", "scam", "ta", [
    "உங்கள் எல்ஐசி பாலிசியில் ரூ {amount} போனஸ் நிலுவையில் உள்ளது. உரிமை கோர உங்கள் பாலிசி விவரங்களை {scam_url} பதிவிடவும்.",
])
t("scam_olx_ta_01", "scam", "ta", [
    "நான் ராணுவ அதிகாரி. உங்கள் பழைய பைக்கை வாங்க விரும்புகிறேன். முன்பணம் ரூ {amount} அனுப்ப இந்த க்யூஆர் கோடை ஸ்கேன் செய்து பின் போடவும்: {scam_url}",
])
t("scam_sim_ta_01", "scam", "ta", [
    "ஏர்டெல்/ஜியோ வாடிக்கையாளரே: உங்கள் 4G சிம் இன்று இரவு முடக்கப்படும். 5G சிம்முக்கு இலவசமாக மாற {scam_url} கிளிக் செய்யவும்.",
])
t("scam_support_ta_01", "scam", "ta", [
    "கூகுள் பே வாடிக்கையாளர் சேவை எண்: பணப் பரிவர்த்தனை தோல்வியடைந்தால் தீர்வு காண எங்கள் அதிகாரியை {phone} அழைக்கவும்.",
])
t("scam_anydesk_ta_01", "scam", "ta", [
    "வங்கி கணக்கு சரிபார்ப்பிற்கு AnyDesk செயலியை டவுன்லோட் செய்து 9 இலக்க குறியீட்டை {phone} எண்ணுக்கு தெரிவிக்கவும்.",
])
t("scam_police_challan_ta_01", "scam", "ta", [
    "தமிழ்நாடு போக்குவரத்து காவல்துறை: உங்கள் வாகனத்திற்கு ரூ {amount_num} அபராதம் நிலுவையில் உள்ளது. நீதிமன்ற நோட்டீஸை தவிர்க்க உடனே செலுத்த: {scam_url}",
])
t("scam_aadhaar_pan_ta_01", "scam", "ta", [
    "ஆதார் ஆணைய எச்சரிக்கை: உங்கள் ஆதார் பயோமெட்ரிக் காலாவதியானது. உடனடியாக புதுப்பிக்காவிடில் சிம் மற்றும் வங்கி சேவை முடங்கும்: {scam_url}",
])
t("scam_crypto_ta_01", "scam", "ta", [
    "பிட்காயின் மற்றும் எத்திரியம் ஏர்-டிராப்! உடனடியாக பதிவு செய்து இலவசமாக ரூ {amount} பெறுங்கள்: {scam_url}",
])

# ==========================================
# 2. SCAM TEMPLATES - TANGLISH (28 groups)
# ==========================================
t("scam_kyc_tanglish_01", "scam", "tanglish", [
    "Dear customer, unga {bank} account block aagum. Udane KYC update panna {scam_url} click pannunga.",
    "Alert! Ungal bank account inaiku suspend aagum. PAN card link panna intha link {scam_url} open panunga.",
])
t("scam_kyc_tanglish_02", "scam", "tanglish", [
    "Aadhaar card bank account la link aagala. 24 hours kulla update panalana fine poduvanga: {scam_url}",
])
t("scam_tneb_tanglish_01", "scam", "tanglish", [
    "Dear consumer, unga previous month electricity bill update aagala. Inaiku night 9.30 PM power disconnect pannuvanga. Officer {phone} call pannunga udane.",
    "TNEB Power Cut Alert: Unga EB bill pending iruku. Disconnect aagatha iruka intha number {phone} contact panunga.",
])
t("scam_tneb_tanglish_02", "scam", "tanglish", [
    "Electricity office alert: Bill amount Rs {amount_num} pay pannalana current cut. Officer support: {phone} or visit {scam_url}",
])
t("scam_otp_theft_tanglish_01", "scam", "tanglish", [
    "Bank manager pesuren: unga account ku Rs {amount} credit aaga OTP vanthuruku, antha number solunga.",
    "Aadhaar verification kaga unga mobile ku vantha OTP share pannunga sir.",
])
t("scam_upi_tanglish_01", "scam", "tanglish", [
    "Bro thappaa unga GPay ku Rs {amount} anupiten. Intha link {scam_url} click panni UPI pin pottu return anupunga pls.",
    "Sir unga PhonePe ku Rs {amount} cashback vanthuruku. Claim panna UPI PIN enter pannunga: {scam_url}",
])
t("scam_upi_tanglish_02", "scam", "tanglish", [
    "Payment collect request: Rs {amount} unga account la collect panna approve pannunga: {scam_url}",
])
t("scam_digital_arrest_tanglish_01", "scam", "tanglish", [
    "Mumbai Police Cyber Crime: Unga Aadhaar illegal courier parcel la irunthu eduthurukom. Digital arrest thavirkka WhatsApp video call {phone} varavum.",
    "CBI warning: Ungal perla money laundering case register aagiruku. Warrant stop panna contact {phone}.",
])
t("scam_digital_arrest_tanglish_02", "scam", "tanglish", [
    "Delhi Crime Branch: Illegal SIM card and bank accounts registered under your name. Appear on video conference {phone} immediately.",
])
t("scam_job_tanglish_01", "scam", "tanglish", [
    "Part time job! Daily YouTube likes panni Rs {amount_num} to Rs 5000 earn pannalam. Contact HR on WhatsApp: {phone}",
    "Work from home opportunity: No investment. Per day Rs {amount_num} guaranteed. Join Telegram group {scam_url}",
])
t("scam_job_tanglish_02", "scam", "tanglish", [
    "Earn daily Rs 3000 typing and writing reviews online. Register here immediately: {scam_url}",
])
t("scam_lottery_tanglish_01", "scam", "tanglish", [
    "Congratulations! Unga number KBC lucky draw la Rs 25 Lakhs win panniruku. Prize collect panna call {phone}.",
    "Unga number ku New Car prize kedachuruku. Delivery charge Rs 2500 pay panna link {scam_url} click pannunga.",
])
t("scam_parcel_tanglish_01", "scam", "tanglish", [
    "FedEx courier alert: Unga parcel la drugs matrum foreign currency iruku nu customs pidichitanga. Clarify panna call {phone}.",
])
t("scam_loan_tanglish_01", "scam", "tanglish", [
    "Instant loan Rs {amount} approve aaiduchu! CIBIL score thevai illa. Udane panam vanga intha app download pannunga: {scam_url}",
    "Quick personal loan 5 mins la account ku varum. Zero interest. Apply now: {scam_url}",
])
t("scam_invest_tanglish_01", "scam", "tanglish", [
    "Daily share market tips & crypto trading. Rs 5000 invest panna weekly Rs 50,000 profit. Join WhatsApp {scam_url}",
])
t("scam_apk_tanglish_01", "scam", "tanglish", [
    "Unga {bank} reward points expire aaga poguthu. Cash ah convert panna intha APK install pannunga: {scam_url}",
    "Bank safe login kaga puthiya app install pannavum: {scam_url}",
])
t("scam_govt_tanglish_01", "scam", "tanglish", [
    "Income tax refund Rs {amount} unga bank ku transfer panna details update pannunga: {scam_url}",
    "PM Kisan Samman Nidhi Rs {amount} unga account la poda aathar link panna {scam_url} click pannunga.",
])
t("scam_sextortion_tanglish_01", "scam", "tanglish", [
    "Unga nude video call record pannitom. 2 hours la Rs {amount} pay pannalana Facebook la post panniduvom. WhatsApp {phone}",
])
t("scam_himum_tanglish_01", "scam", "tanglish", [
    "Amma en phone damaged aaiduchu. Ithu en new WhatsApp number. Urgent ah hospital bill ku Rs {amount} GPay pannu ma: {phone}",
])
t("scam_betting_tanglish_01", "scam", "tanglish", [
    "Color prediction game la daily Rs 5000 win pannalam. Sign up bonus Rs 500. Link {scam_url}",
])
t("scam_card_tanglish_01", "scam", "tanglish", [
    "Unga {bank} credit card limit Rs {amount} varaikum increase aagiruku. Activate panna click {scam_url}",
])
t("scam_challan_tanglish_01", "scam", "tanglish", [
    "Traffic police e-challan: Unga vandi ku pending fine Rs {amount_num}. Court summons thavirkka pay online: {scam_url}",
])
t("scam_fastag_tanglish_01", "scam", "tanglish", [
    "FASTag blacklisted notice: Toll booth block thavirkka udane KYC complete pannunga: {scam_url}",
])
t("scam_olx_tanglish_01", "scam", "tanglish", [
    "Naan Army Officer Chennai camp. Unga bike ku advance Rs {amount} anupuren. Scanner scan panni UPI pin podunga: {scam_url}",
])
t("scam_sim_tanglish_01", "scam", "tanglish", [
    "Airtel alert: Unga SIM card e-KYC pending. Tonight block aagum. Renew panna call {phone} or click {scam_url}",
])
t("scam_support_tanglish_01", "scam", "tanglish", [
    "GPay customer support: Transaction stuck aana help kaga call pannunga {phone}. 24x7 available.",
])
t("scam_anydesk_tanglish_01", "scam", "tanglish", [
    "Sir refund process panna Play Store la RustDesk app download panni screen share pannunga.",
])
t("scam_insur_tanglish_01", "scam", "tanglish", [
    "LIC un-claimed bonus Rs {amount} unga bank ku claim panna details register pannunga: {scam_url}",
])

# ==========================================
# 3. SCAM TEMPLATES - ENGLISH (28 groups)
# ==========================================
t("scam_kyc_en_01", "scam", "en", [
    "Dear customer, your {bank} account will be blocked within 24 hours due to pending KYC. Click here to verify: {scam_url}",
    "URGENT: Your bank account has been suspended. Please update your PAN & Aadhaar details immediately at {scam_url} to avoid deactivation.",
])
t("scam_kyc_en_02", "scam", "en", [
    "Notice: Your netbanking access is on hold. Complete verification immediately at {scam_url} to prevent permanent closure.",
])
t("scam_tneb_en_01", "scam", "en", [
    "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM because your previous month bill was not updated. Please contact officer at {phone}.",
    "TNEB Alert: Power supply disconnection scheduled today. Call electricity helpline {phone} immediately or visit {scam_url}",
])
t("scam_tneb_en_02", "scam", "en", [
    "Electricity Bill Notice: Bill of Rs {amount_num} pending. Electricity will be cut off tonight. Call {phone} immediately.",
])
t("scam_otp_en_01", "scam", "en", [
    "Bank customer care: To unblock your debit card, share the 6-digit OTP received on your mobile with representative {phone}.",
    "Security verification: Please forward the verification code to {phone} to validate your transaction of Rs {amount}.",
])
t("scam_upi_en_01", "scam", "en", [
    "I have mistakenly transferred Rs {amount} to your UPI ID. Please click {scam_url} and enter UPI PIN to refund the money.",
    "You have received a cashback request of Rs {amount}. Click here and approve collect request: {scam_url}",
])
t("scam_upi_en_02", "scam", "en", [
    "Payment collect alert: Enter your UPI PIN to claim cashback of Rs {amount} credited to your Google Pay wallet: {scam_url}",
])
t("scam_digital_arrest_en_01", "scam", "en", [
    "MUMBAI POLICE CRIME BRANCH: A parcel containing narcotics and fake passports under your Aadhaar has been seized. Connect to Skype video call immediately at {phone} to prevent digital arrest.",
    "CBI Notice: Non-bailable arrest warrant issued against your name for financial fraud. Connect with investigation officer {phone} now.",
])
t("scam_digital_arrest_en_02", "scam", "en", [
    "Narcotics Control Bureau (NCB): 500g illegal drugs found in courier package sent from Taiwan in your name. Join interrogation video room {phone}.",
])
t("scam_job_en_01", "scam", "en", [
    "Part Time Job Offer: Earn Rs 2000 to Rs 8000 daily by simply reviewing hotels and liking YouTube videos. Contact HR on WhatsApp: {phone}",
    "Amazon Work From Home: Earn Rs {amount_num} per day. No skills required. Start earning today: {scam_url}",
])
t("scam_job_en_02", "scam", "en", [
    "Telegram Task Scam: Get paid Rs 500 per task. Earn up to Rs {amount} per day working 2 hours from home. Join: {scam_url}",
])
t("scam_lottery_en_01", "scam", "en", [
    "Congratulations! You have won Rs 25,00,000 in Kaun Banega Crorepati WhatsApp Lucky Draw 2026. Call manager {phone} to claim your prize.",
    "Lucky winner! Your mobile number won a Brand New SUV in Indian Mega Draw. Claim prize before deadline: {scam_url}",
])
t("scam_parcel_en_01", "scam", "en", [
    "Delhi Customs & FedEx: Your overseas shipment has been detained due to illegal contraband. Immediate penalty required. Contact customs agent {phone}.",
])
t("scam_loan_en_01", "scam", "en", [
    "Instant Loan Approved! Get up to Rs {amount} credited directly to your bank account in 2 minutes without CIBIL. Download APK: {scam_url}",
    "Pre-approved personal loan of Rs {amount} waiting. Zero processing fee. Apply here: {scam_url}",
])
t("scam_invest_en_01", "scam", "en", [
    "Guaranteed 300% weekly returns in Crypto and Stock Trading. Join our VIP insider group: {scam_url}",
    "Earn Rs 25,000 daily with AI automated algorithmic trading. Minimum investment Rs 1000. Start here: {scam_url}",
])
t("scam_apk_en_01", "scam", "en", [
    "Dear customer, your {bank} netbanking session expired. Install {bank}_Security.apk to restore access: {scam_url}",
    "Redeem your accumulated reward points worth Rs {amount}. Download our rewards app: {scam_url}",
])
t("scam_govt_en_01", "scam", "en", [
    "Income Tax Department: Tax refund of Rs {amount} has been approved. Confirm your bank account details at {scam_url} within 48 hours.",
    "PM Subsidy Scheme: Grant of Rs {amount} released for your account. Register immediately at {scam_url}",
])
t("scam_sextortion_en_01", "scam", "en", [
    "We have recorded your compromise video. Pay Rs {amount} within 1 hour or we will upload it to all your contacts and social media. Contact {phone}",
])
t("scam_himum_en_01", "scam", "en", [
    "Hi Mom, I dropped my phone in water and this is my temporary number. I urgently need Rs {amount} to clear my repair bill. Please transfer to {phone}",
])
t("scam_betting_en_01", "scam", "en", [
    "Win real cash daily playing online casino and Aviator games. 100% deposit bonus up to Rs {amount}. Play now: {scam_url}",
])
t("scam_card_en_01", "scam", "en", [
    "Your {bank} Credit Card reward points {amount_num} will expire today. Convert to cash Rs {amount_num} by clicking {scam_url}",
])
t("scam_challan_en_01", "scam", "en", [
    "Traffic Police Notice: Unpaid e-challan against vehicle. Pay Rs {amount_num} immediately to avoid court proceedings: {scam_url}",
])
t("scam_fastag_en_01", "scam", "en", [
    "FASTag Alert: Your FASTag is deactivated due to low balance and unverified KYC. Recharge now to avoid 2x toll fee: {scam_url}",
])
t("scam_olx_en_01", "scam", "en", [
    "I am an Indian Army officer posted at Chennai cantonment. I want to buy your item on OLX. Scan this QR code and input UPI PIN to receive payment of Rs {amount}: {scam_url}",
])
t("scam_sim_en_01", "scam", "en", [
    "Jio / Airtel Notice: Your SIM card will be deactivated today due to incomplete verification. Complete biometric KYC: {scam_url}",
])
t("scam_support_en_01", "scam", "en", [
    "Official PhonePe Support: Transaction failed? Call our 24/7 helpline number {phone} for instant refund.",
])
t("scam_anydesk_en_01", "scam", "en", [
    "Dear customer, install AnyDesk or TeamViewer QuickSupport from this link {scam_url} to assist in recovering your lost funds.",
])
t("scam_insurance_en_01", "scam", "en", [
    "LIC Policy Alert: Unclaimed maturity bonus of Rs {amount} is waiting. Fill form at {scam_url} before forfeiture.",
])

# ==========================================
# 4. HARD SAFE TEMPLATES - TAMIL SCRIPT (20 groups)
# ==========================================
t("safe_bank_debit_ta_01", "safe", "ta", [
    "உங்கள் {bank} கணக்கு {account}-லிருந்து ரூ {amount_num} பற்று வைக்கப்பட்டது (debited). மீதி இருப்பு ரூ {amount}. பரிவர்த்தனை எண் 91823.",
    "கணக்கு {account}-ல் ரூ {amount_num} ATM மூலம் எடுக்கப்பட்டது. இருப்பு ரூ {amount}. நீங்கள் செய்யவில்லை என்றால் வங்கியிடம் புகார் செய்யவும்.",
])
t("safe_bank_credit_ta_01", "safe", "ta", [
    "உங்கள் கணக்கு {account}-ல் ரூ {amount} வரவு வைக்கப்பட்டது (credited). UPI பரிவர்த்தனை ஐடி 49102847. மீதி இருப்பு ரூ {amount}.",
    "{bank}: கணக்கு {account}-ல் மாதச் சம்பளம் ரூ {amount} வரவு வைக்கப்பட்டுள்ளது. தற்போதைய இருப்பு ரூ {amount}.",
])
t("safe_bank_otp_ta_01", "safe", "ta", [
    "{bank} வங்கி பரிவர்த்தனைக்கான OTP எண் {otp}. இதை வங்கி ஊழியர் உட்பட யாரிடமும் ஒருபோதும் பகிராதீர்கள். ரகசியமாக வைக்கவும்.",
    "ரூ {amount_num} பரிவர்த்தனைக்கான OTP: {otp}. வங்கி ஒருபோதும் OTP கேட்காது. யாரிடமும் பகிர வேண்டாம்.",
])
t("safe_delivery_otp_ta_01", "safe", "ta", [
    "உங்கள் Swiggy உணவு ஆர்டர் டெலிவரி ஆவதற்கு வந்துவிட்டது. டெலிவரி பார்ட்னரிடம் இந்த OTP {otp} பகிரவும்.",
    "Zomato: உங்கள் உணவு டெலிவரி செய்ய வந்துள்ள பார்ட்னரிடம் OTP {otp}-ஐ தெரிவிக்கவும். சுவையான உணவை அனுபவிக்கவும்!",
])
t("safe_ride_otp_ta_01", "safe", "ta", [
    "Ola சவாரி OTP: {otp}. ஓட்டுநரிடம் இந்த OTP எண்ணை பகிர்ந்து உங்கள் பயணத்தைத் தொடங்கவும்.",
    "Uber: உங்கள் ஓட்டுநரிடம் OTP {otp} பகிரவும். பாதுகாப்பான பயணத்தை வாழ்த்துகிறோம்.",
])
t("safe_bank_warning_ta_01", "safe", "ta", [
    "{bank} விழிப்புணர்வு: வங்கி ஒருபோதும் OTP, கடவுச்சொல் அல்லது கார்டு விவரங்களை தொலைபேசி அல்லது எஸ்எம்எஸ் மூலம் கேட்காது. எச்சரிக்கையாக இருக்கவும்.",
    "பாதுகாப்பு குறிப்பு: தெரியாத நபர்களிடம் வங்கி ரகசிய எண்களை பகிராதீர்கள். மோசடிகளில் இருந்து பாதுகாப்பாக இருங்கள்.",
])
t("safe_tneb_official_ta_01", "safe", "ta", [
    "TNEB நுகர்வோர் எண் 09281729-க்கான மின் கட்டணம் ரூ {amount_num} வெற்றிகரமாக செலுத்தப்பட்டது. ரசீது எண் 48291. அதிகாரப்பூர்வ இணையதளம்: https://www.tangedco.gov.in",
])
t("safe_pmkisan_ta_01", "safe", "ta", [
    "பிரதமர் கிசான் சம்மான் நிதி திட்டத்தின் 16வது தவணை ரூ 2,000 உங்கள் வங்கிக் கணக்கில் நேரடியாக வரவு வைக்கப்பட்டுள்ளது. https://pmkisan.gov.in",
])
t("safe_chat_ta_01", "safe", "ta", [
    "அம்மா, காய்கறி வாங்க கடைக்கு போறேன். வர அரை மணி நேரம் ஆகும்.",
    "தம்பி, அப்பாவுக்கு மருந்து வாங்கிட்டேன், ஈவினிங் வீட்டுக்கு எடுத்துட்டு வரேன்.",
])
t("safe_money_chat_ta_01", "safe", "ta", [
    "அண்ணா, காலேஜ் பீஸ் கட்ட 2000 ரூபாய் கூகுள் பே பண்ணுங்க. நாளைக்கு கடைசி தேதி.",
    "சரவணன், மளிகைக் கடைக்கு 850 ரூபாய் அனுப்பிட்டேன். செக் பண்ணிக்கோ.",
    "அம்மா உன் அக்கவுண்ட்க்கு 5000 ரூபாய் போட்டிருக்கேன், செலவுக்கு வச்சுக்கோ.",
])
t("safe_money_chat_ta_02", "safe", "ta", [
    "கார்த்திக், நேத்து சாப்பிட்ட ஹோட்டல் பில்லில் என் பங்கு 350 ரூபாய் கூகுள் பே-யில் அனுப்பிட்டேன்.",
    "தம்பி, வீட்டு வாடகைக்கு 8000 ரூபாய் உன் அக்கவுண்ட்ல போட்டுட்டேன், ஓனரிடம் கொடுத்துடு.",
])
t("safe_appointment_ta_01", "safe", "ta", [
    "டாக்டர் சந்திப்பு உறுதி செய்யப்பட்டது. அப்பல்லோ மருத்துவமனை, சென்னை. நேரம்: மாலை 5.30 மணி. முன்பதிவு எண் 4829.",
])
t("safe_college_ta_01", "safe", "ta", [
    "அண்ணா பல்கலைக்கழகம்: செமஸ்டர் தேர்வு முடிவுகள் அதிகாரப்பூர்வ இணையதளத்தில் வெளியிடப்பட்டுள்ளன. மாணவர்கள் சரிபார்க்கவும்.",
])
t("safe_train_ta_01", "safe", "ta", [
    "IRCTC: உங்கள் ரயில் டிக்கெட் PNR 4829104829 உறுதி செய்யப்பட்டது. ரயில் எண் 12637 பாண்டியன் எக்ஸ்பிரஸ். பெட்டி S3 இருக்கை 42.",
])
t("safe_telecom_ta_01", "safe", "ta", [
    "ஜியோ: உங்கள் தினசரி 1.5 GB டேட்டா பேக் இன்றுடன் முடிவடைகிறது. ரீசார்ஜ் செய்ய MyJio செயலியை பயன்படுத்தவும்.",
])
t("safe_gas_ta_01", "safe", "ta", [
    "பாரத் கேஸ்: உங்கள் சிலிண்டர் முன்பதிவு எண் 91829 உறுதி செய்யப்பட்டது. 2 நாட்களில் டெலிவரி செய்யப்படும்.",
])
t("safe_courier_ta_01", "safe", "ta", [
    "ப்ளூடார்ட் கூரியர்: உங்கள் பார்சல் இன்று மாலை 6 மணிக்குள் டெலிவரி செய்யப்படும். டெலிவரி பாய் எண் 9840112233.",
])
t("safe_grocery_ta_01", "safe", "ta", [
    "பிக் பாஸ்கெட்: உங்கள் மளிகைப் பொருட்கள் பேக்கிங் செய்யப்பட்டு டெலிவரிக்கு புறப்பட்டுள்ளது.",
])
t("safe_greeting_ta_01", "safe", "ta", [
    "இனிய தீபாவளி மற்றும் பொங்கல் நல்வாழ்த்துகள்! உங்கள் குடும்பத்தில் மகிழ்ச்சி பொங்கட்டும்.",
])
t("safe_work_ta_01", "safe", "ta", [
    "நாளை காலை 10 மணிக்கு அலுவலகக் கூட்டம் தொடங்கும். அனைவரும் சரியான நேரத்திற்கு வரவும்.",
])

# ==========================================
# 5. HARD SAFE TEMPLATES - TANGLISH (19 groups)
# ==========================================
t("safe_bank_debit_tanglish_01", "safe", "tanglish", [
    "Unga {bank} A/c {account} la irunthu Rs {amount_num} debit aagiruku. Avl Bal Rs {amount}. If not done by you call bank.",
    "A/c {account} debited by Rs {amount_num} at ATM Chennai. Balance Rs {amount}.",
])
t("safe_bank_credit_tanglish_01", "safe", "tanglish", [
    "Unga {bank} account ku Rs {amount} credit aagiruku through NEFT/UPI. Avl balance Rs {amount}.",
])
t("safe_bank_otp_tanglish_01", "safe", "tanglish", [
    "{bank} OTP for transaction Rs {amount_num} is {otp}. Never share this OTP with anyone, including bank staff.",
    "Do not share your secret OTP {otp} with anyone. Bank officials never ask for OTP.",
])
t("safe_delivery_otp_tanglish_01", "safe", "tanglish", [
    "Swiggy: Share OTP {otp} with delivery partner {name} when food arrives. Enjoy your meal!",
    "Zomato delivery order: Please share OTP {otp} with your delivery partner.",
])
t("safe_ride_otp_tanglish_01", "safe", "tanglish", [
    "Ola ride OTP is {otp}. Share with driver {name} to start your ride.",
    "Rapido bike taxi: Share PIN {otp} with captain to start ride.",
])
t("safe_bank_warn_tanglish_01", "safe", "tanglish", [
    "{bank} Awareness: Bank staff or managers never call asking for PIN or OTP. Stay vigilant.",
])
t("safe_tneb_tanglish_01", "safe", "tanglish", [
    "TNEB Consumer No 482910: Payment of Rs {amount_num} received successfully. Thank you for using https://www.tangedco.gov.in",
])
t("safe_money_chat_tanglish_01", "safe", "tanglish", [
    "Machi naan 500 Rs Gpay panren, movie ticket book pannidu.",
    "Bro phone pay la 1200 anupiten da, hotel bill split panniko.",
    "Akka unga account ku 3000 transfer panniten, dress eduthuko.",
    "Dei Suresh, room rent 4500 Gpay pannu da inaiku evening kulla.",
])
t("safe_money_chat_tanglish_02", "safe", "tanglish", [
    "Appa medicine ku 750 Google Pay la anupiten, shop la kaatunga.",
    "Naan petrol bunk la iruken da, Gpay la 200 send pannu urgent.",
])
t("safe_chat_tanglish_01", "safe", "tanglish", [
    "Enge da iruka? Naan bus stand ku reach aaiten, seekiram vaa.",
    "Amma naalaiku morning train la Trichy varren ma.",
])
t("safe_interview_tanglish_01", "safe", "tanglish", [
    "TCS campus drive: Your interview is scheduled tomorrow at 10 AM. All the best!",
])
t("safe_travel_tanglish_01", "safe", "tanglish", [
    "RedBus booking confirmed: Chennai to Madurai bus departs at 9.30 PM from Koyambedu. Seat no 14.",
])
t("safe_recharge_tanglish_01", "safe", "tanglish", [
    "Airtel recharge successful for Rs 299. 1.5GB/day data credited.",
])
t("safe_friends_tanglish_01", "safe", "tanglish", [
    "Sunday cricket match ku ground book pannitom, kalaila 6.30 ku vanthudu da.",
])
t("safe_study_tanglish_01", "safe", "tanglish", [
    "Semester notes WhatsApp group la share panniruken, exam ku prepare pannunga.",
])
t("safe_gym_tanglish_01", "safe", "tanglish", [
    "Gym membership renewal successful. Validity till next month.",
])
t("safe_office_tanglish_01", "safe", "tanglish", [
    "Manager approved your leave request for Friday. Enjoy your weekend.",
])
t("safe_shopping_tanglish_01", "safe", "tanglish", [
    "Amazon: Unga order out for delivery today. Delivery agent {name} will contact you.",
])
t("safe_doctor_tanglish_01", "safe", "tanglish", [
    "Dental clinic appointment fixed today at 6 PM. Pls be on time.",
])

# ==========================================
# 6. HARD SAFE TEMPLATES - ENGLISH (20 groups)
# ==========================================
t("safe_bank_debit_en_01", "safe", "en", [
    "Rs {amount_num} debited from your {bank} A/c {account} on {date}. Avl Bal: Rs {amount}. Ref: UPI/482910482.",
    "Your {bank} A/c {account} has been debited for Rs {amount_num} towards POS purchase at Reliance Retail.",
])
t("safe_bank_credit_en_01", "safe", "en", [
    "Rs {amount} credited to your {bank} A/c {account} through IMPS. Total Available Balance: Rs {amount}.",
    "Salary of Rs {amount} credited to your {bank} account {account} for this month.",
])
t("safe_bank_otp_en_01", "safe", "en", [
    "OTP for login to {bank} NetBanking is {otp}. Do NOT share this OTP with anyone, not even bank employees.",
    "{otp} is your verification code for transaction of Rs {amount_num} at {company}. Never share your OTP with anyone.",
])
t("safe_delivery_otp_en_01", "safe", "en", [
    "Your Swiggy order from Anjappar is arriving! Share OTP {otp} with delivery partner {name}.",
    "Zomato: Share delivery verification code {otp} with your delivery executive upon food arrival.",
    "Amazon: Delivery agent {name} will deliver your package today. Share OTP {otp} at delivery.",
])
t("safe_ride_otp_en_01", "safe", "en", [
    "Ola: Your ride OTP is {otp}. Share this with driver {name} ({phone}) to begin trip.",
    "Uber: Provide OTP {otp} to driver {name} to start trip.",
])
t("safe_bank_warn_en_01", "safe", "en", [
    "{bank} Alert: Banks never ask for your confidential details like CVV, PIN, or OTP. Never click on unverified links.",
    "RBI Kehta Hai: Stay alert! Do not share OTP or click on suspicious links claiming KYC updates.",
])
t("safe_pmkisan_en_01", "safe", "en", [
    "Rs 2,000 credited under PM-Kisan installment to your registered bank account. Official portal: https://pmkisan.gov.in",
])
t("safe_utility_en_01", "safe", "en", [
    "TANGEDCO: Payment of Rs {amount_num} for Consumer No 091823 has been received on 14-Oct. Visit https://www.tangedco.gov.in",
    "Airtel Broadband: Your monthly bill of Rs 825 is due on 28-Oct. Pay via Airtel Thanks App or official site.",
])
t("safe_interview_en_01", "safe", "en", [
    "Dear Candidate, your technical interview for Software Engineer at Zoho Corporation is scheduled on Friday at 10:00 AM.",
    "Infosys Recruitment: Congratulations! Your offer letter has been generated. Check candidate portal.",
])
t("safe_appointment_en_01", "safe", "en", [
    "Your appointment with Dr. Sundaram at Apollo Hospitals Greams Road is confirmed for tomorrow 4:30 PM. Booking ID: AP48291.",
])
t("safe_chat_en_01", "safe", "en", [
    "Hi mom, I reached Chennai Central safely. Taking metro to office now.",
    "Hey Karthik, sent you Rs 500 on GPay for the movie snacks. Check it out.",
    "Sent Rs 2500 for groceries to your Google Pay account.",
])
t("safe_chat_en_02", "safe", "en", [
    "Dad, transferred Rs 3,000 for utility bills to your account. Let me know when received.",
    "Hey bro, I have sent 450 rupees via PhonePe for the coffee bill.",
])
t("safe_flight_en_01", "safe", "en", [
    "IndiGo: Flight 6E-241 Chennai to Delhi is on schedule at 06:15 hrs from Terminal 1. Web check-in open.",
])
t("safe_train_en_01", "safe", "en", [
    "IRCTC: Booking confirmed for PNR 8491028471. Train 12623 Trivandrum Mail, Coach B2 Berth 31.",
])
t("safe_creditcard_stmt_en_01", "safe", "en", [
    "Your {bank} credit card statement for ending {account} is generated. Total due: Rs {amount_num}, Due date: 15-Nov.",
])
t("safe_school_en_01", "safe", "en", [
    "DAV Public School: Annual sports day is organized on Saturday. Parents are cordially invited at 9:00 AM.",
])
t("safe_library_en_01", "safe", "en", [
    "Connemara Public Library: The borrowed book 'Data Science Handbook' is due for return on 30-Oct.",
])
t("safe_hotel_en_01", "safe", "en", [
    "Booking confirmed at Sterling Resort Ooty for 2 nights from 28-Oct. Confirmation ID: ST8491.",
])
t("safe_ecommerce_en_01", "safe", "en", [
    "Flipkart: Your package containing Boat headphones has been delivered. Thank you for shopping with us.",
])
t("safe_dth_en_01", "safe", "en", [
    "Tata Play: Your subscription renewed successfully for 30 days. Balance Rs 340.",
])

def add_noise(text):
    """Add realistic noise while keeping meaning intact."""
    choice = random.random()
    if choice < 0.20:
        emojis = [" ⚠️", " 🚨", " ❗", " 🔴", " ⏳", " 📲", " ⚡"]
        text = text + random.choice(emojis)
    elif choice < 0.35:
        text = text.replace(" ", "  ", 1)
    return text.strip()

def generate_instances_for_template(template_info, count=38):
    instances = []
    gid = template_info["group"]
    label = template_info["label"]
    lang = template_info["lang"]
    t_list = template_info["templates"]

    for _ in range(count):
        raw_t = random.choice(t_list)
        filled = raw_t.format(
            bank=random.choice(BANKS_TA if lang == "ta" else BANKS),
            amount=random.choice(AMOUNTS),
            amount_num=random.choice(AMOUNTS_NUM),
            otp=random.choice(OTPS),
            account=random.choice(ACCOUNTS),
            phone=random.choice(PHONES),
            name=random.choice(NAMES),
            company=random.choice(COMPANIES),
            scam_url=random.choice(SCAM_URLS),
            official_url=random.choice(OFFICIAL_URLS),
            date=random.choice(DATES)
        )
        filled = add_noise(filled)
        instances.append((label, lang, gid, filled))
    return instances

# ==========================================
# 75 SEPARATE HAND-WRITTEN GOLD TEST MESSAGES
# ==========================================
GOLD_TEST_SET = [
    # --- SCAM: TAMIL SCRIPT (13) ---
    ("scam", "ta", "gold_ta_01", "எஸ்பிஐ வாடிக்கையாளர் கவனத்திற்கு: உங்கள் வங்கி கணக்கு இன்றோடு முடக்கப்படும். உடனே பான் கார்டு அப்டேட் செய்ய http://sbi-kyc-verify.xyz பார்க்கவும்."),
    ("scam", "ta", "gold_ta_02", "மின்சார வாரியம் எச்சரிக்கை: உங்கள் முந்தைய மாத மின் கட்டணம் செலுத்தப்படாததால் இன்று இரவு 9.30 மணிக்கு மின் இணைப்பு துண்டிக்கப்படும். உடனே 9840184712 அழைக்கவும்."),
    ("scam", "ta", "gold_ta_03", "மும்பை சைபர் கிரைம் போலீஸ்: உங்கள் ஆதார் எண் பண மோசடி வழக்கில் சிக்கியுள்ளது. டிஜிட்டல் கைதை தவிர்க்க உடனடியாக ஸ்கைப் வீடியோ காலில் 8939012345 வரவும்."),
    ("scam", "ta", "gold_ta_04", "அன்புள்ள வாடிக்கையாளரே, தவறுதலாக உங்கள் கணக்கிற்கு ரூ 5,000 வந்துவிட்டது. இந்த லிங்க் http://bit.ly/refund-gpay கிளிக் செய்து UPI PIN போட்டு திருப்பி அனுப்பவும்."),
    ("scam", "ta", "gold_ta_05", "வாழ்த்துக்கள்! உங்கள் எண் KBC அகில இந்திய லக்கி டிராவில் ரூ 25 லட்சம் வென்றுள்ளது. பரிசுத்தொகையை பெற மேலாளரை 9444012345 அழைக்கவும்."),
    ("scam", "ta", "gold_ta_06", "வீட்டிலிருந்தே பணிபுரியுங்கள்! யூடியூப் வீடியோக்களுக்கு லைக் செய்து தினமும் ரூ 3000 சம்பாதிக்கலாம். வாட்ஸ்அப் 7358012345 தொடர்பு கொள்ளவும்."),
    ("scam", "ta", "gold_ta_07", "FedEx கூரியர் தகவல்: உங்கள் வெளிநாட்டு பார்சலில் தடை செய்யப்பட்ட மருந்துகள் உள்ளன. சுங்கத்துறை கைது செய்யாமல் இருக்க உடனே 9150012345 அழைக்கவும்."),
    ("scam", "ta", "gold_ta_08", "உடனடி தனிநபர் கடன் ரூ 5,00,000 ஒப்புதல் அளிக்கப்பட்டது. ஆவணம் இன்றி உடனே பெற http://192.168.1.105/loan.apk பதிவிறக்கம் செய்க."),
    ("scam", "ta", "gold_ta_09", "பங்குச் சந்தை விஐபி குரூப்: தினசரி 500% லாபம் நிச்சயம். எங்கள் டெலிகிராம் குரூப்பில் இணைய http://tinyurl.com/crypto-tamil கிளிக் செய்க."),
    ("scam", "ta", "gold_ta_10", "உங்கள் ஹெச்டிஎஃப்சி கார்டு ரிவார்டு பாயிண்ட்ஸ் ரூ 9,500 பணமாக மாற்ற இந்த செயலியை இன்ஸ்டால் செய்க: http://hdfc-reward.club/apk"),
    ("scam", "ta", "gold_ta_11", "வருமான வரித்துறை ரீஃபண்ட் ரூ 18,500 உங்கள் கணக்கில் வரவு வைக்க உங்கள் வங்கி விவரங்களை http://income-tax-refund.click பதிவிடவும்."),
    ("scam", "ta", "gold_ta_12", "உங்கள் அந்தரங்க வீடியோ எங்களிடம் உள்ளது. 2 மணி நேரத்தில் ரூ 25,00,000 தராவிட்டால் குடும்பத்தாருக்கு அனுப்புவோம். 9840123456"),
    ("scam", "ta", "gold_ta_13", "அம்மா என் போன் தொலைந்துவிட்டது, இது புதிய நம்பர். அவசரமாக மருத்துவமனைக்கு ரூ 10000 அனுப்பவும் 9876543210."),

    # --- SCAM: TANGLISH (13) ---
    ("scam", "tanglish", "gold_tgl_01", "Dear customer unga Canara Bank account block aagiruku. Udane KYC renew panna http://cutt.ly/canara-kyc click panunga."),
    ("scam", "tanglish", "gold_tgl_02", "TNEB Power Cut Alert: Unga previous bill pay aagala. Tonight 9.30 PM current cut pannuvanga. Officer number 9840192837."),
    ("scam", "tanglish", "gold_tgl_03", "Delhi Police Cyber Cell: Unga perla drugs parcel seize pannirukom. Arrest warrant stop panna WhatsApp video call 9876541230 varavum."),
    ("scam", "tanglish", "gold_tgl_04", "Sir mistake ah unga GPay ku Rs 4500 anupiten. Intha link http://is.gd/refund-pin click panni UPI pin pottu return anupunga."),
    ("scam", "tanglish", "gold_tgl_05", "Congratulations! KBC Lucky draw la unga mobile number ku 25 Lakhs prize. Claim panna call 9444098765."),
    ("scam", "tanglish", "gold_tgl_06", "Part time job: Daily YouTube video likes panni Rs 2500 earn pannalam. Contact HR on WhatsApp 8939019283."),
    ("scam", "tanglish", "gold_tgl_07", "DHL Customs: Unga UK parcel la illegal gold bar iruku. Case file aagatha iruka call customs officer 7358091823."),
    ("scam", "tanglish", "gold_tgl_08", "Instant 50000 loan approved within 2 mins no CIBIL check. Download app now: http://45.33.32.156/instantloan.apk"),
    ("scam", "tanglish", "gold_tgl_09", "Share market WhatsApp group: Guaranteed 200% return in 3 days. Join here: http://tinyurl.com/stock-rich"),
    ("scam", "tanglish", "gold_tgl_10", "Unga SBI credit card points expire aaga poguthu. Cash ah convert panna intha app install panunga: http://sbi-point.top"),
    ("scam", "tanglish", "gold_tgl_11", "Income tax refund of Rs 14,200 pending. Update bank details at http://tax-refund.buzz/login"),
    ("scam", "tanglish", "gold_tgl_12", "Unga video call record pannitom. 1 hour la Rs 15000 GPAY pannalana social media la leak panniduvom 9150029384."),
    ("scam", "tanglish", "gold_tgl_13", "Amma en phone damaged. New number la irunthu msg panren. Urgent hostel fees ku Rs 5000 anupu ma 9840102938."),

    # --- SCAM: ENGLISH (12) ---
    ("scam", "en", "gold_en_01", "Dear customer, your SBI bank account has been deactivated due to incomplete KYC. Please reactivate by visiting http://sbi-kyc-portal.xyz/login"),
    ("scam", "en", "gold_en_02", "TNEB Alert: Electricity power disconnection scheduled tonight at 9:30 PM due to unpaid bill. Contact electricity officer immediately at 9840123456."),
    ("scam", "en", "gold_en_03", "CBI CYBER CRIME CELL: Arrest warrant issued under PMLA for money laundering parcel sent via FedEx. Join video call immediately 9876501234."),
    ("scam", "en", "gold_en_04", "I accidentally sent Rs 10,000 to your PhonePe account. Kindly click http://bit.ly/phonepe-reverse and enter your UPI PIN to refund."),
    ("scam", "en", "gold_en_05", "You have won a brand new Tata Harrier car in Jio Mega Lucky Draw! Pay delivery registration charges at http://cutt.ly/jio-car-claim"),
    ("scam", "en", "gold_en_06", "Work From Home: Earn Rs 3,000 - Rs 8,000 daily by rating Google Maps places. Message manager on WhatsApp at 9444081920."),
    ("scam", "en", "gold_en_07", "Mumbai Customs: Parcel addressed to your name contains contraband substances. To settle dispute without legal case contact 8939028192."),
    ("scam", "en", "gold_en_08", "Pre-approved personal loan of Rs 2,50,000 waiting for you. Zero documentation. Download APK: http://192.168.1.10/loan.apk"),
    ("scam", "en", "gold_en_09", "Make 10x profit daily on crypto trading signals. Join our Telegram VIP channel: http://tinyurl.com/crypto-signals-vip"),
    ("scam", "en", "gold_en_10", "Your ICICI Credit Card points worth Rs 7,850 will expire midnight. Redeem to cash immediately: http://icici-points.top/redeem"),
    ("scam", "en", "gold_en_11", "Income Tax Dept: Tax refund order of Rs 26,450 approved. Click http://incometax-refund.click to credit your bank account."),
    ("scam", "en", "gold_en_12", "Army Officer transfer to Chennai. Interested in buying your sofa. Scan QR code and enter UPI PIN to receive advance Rs 12000 http://olx-army.buzz"),

    # --- SAFE: TAMIL SCRIPT (12) ---
    ("safe", "ta", "gold_safe_ta_01", "உங்கள் எஸ்பிஐ கணக்கு XX4829-லிருந்து ரூ 1,500 பற்று வைக்கப்பட்டது (debited). மீதி இருப்பு ரூ 18,450. பரிவர்த்தனை எண் 91823901."),
    ("safe", "ta", "gold_safe_ta_02", "உங்கள் இந்தியன் வங்கி கணக்கு XX1092-ல் ரூ 25,000 சம்பளம் வரவு வைக்கப்பட்டது (credited). தற்போதைய இருப்பு ரூ 32,400."),
    ("safe", "ta", "gold_safe_ta_03", "ஹெச்டிஎஃப்சி வங்கி OTP எண் 482910. இந்த எண்ணை யாரிடமும் ஒருபோதும் பகிராதீர்கள். வங்கி ஊழியர்கள் ஒருபோதும் OTP கேட்க மாட்டார்கள்."),
    ("safe", "ta", "gold_safe_ta_04", "Swiggy: உங்கள் உணவு டெலிவரி செய்ய வந்துவிட்டது. டெலிவரி பார்ட்னரிடம் OTP 3819-ஐ பகிர்ந்து உணவை பெற்றுக்கொள்ளவும்."),
    ("safe", "ta", "gold_safe_ta_05", "Ola சவாரி OTP 8192. உங்கள் ஓட்டுநர் கார்த்திக்கிடம் இந்த எண்ணைப் பகிர்ந்து பயணத்தைத் தொடங்கவும்."),
    ("safe", "ta", "gold_safe_ta_06", "எஸ்பிஐ விழிப்புணர்வு: வங்கி ஒருபோதும் உங்கள் கடவுச்சொல், ஏடிஎம் பின் அல்லது ஓடிபி-யை போனில் கேட்காது. விழிப்புடன் இருக்கவும்."),
    ("safe", "ta", "gold_safe_ta_07", "TNEB நுகர்வோர் எண் 0928172-க்கான மின்கட்டணம் ரூ 1,240 பெறப்பட்டது. ரசீது பார்க்க அதிகாரப்பூர்வ தளம்: https://www.tangedco.gov.in"),
    ("safe", "ta", "gold_safe_ta_08", "பிரதமர் கிசான் தவணை ரூ 2,000 உங்கள் கணக்கில் நேரடியாக வரவு வைக்கப்பட்டது. https://pmkisan.gov.in"),
    ("safe", "ta", "gold_safe_ta_09", "அம்மா, நான் கடைக்கு போய் மளிகை சாமான் வாங்கிட்டு ஒரு அரை மணி நேரத்துல வீட்டுக்கு வந்திடுறேன்."),
    ("safe", "ta", "gold_safe_ta_10", "அண்ணா, காலேஜ் எக்ஸாம் பீஸ் கட்ட 1500 ரூபாய் கூகுள் பே பண்ணுங்க. இன்னைக்கு சாயங்காலம் கட்டணும்."),
    ("safe", "ta", "gold_safe_ta_11", "செல்வி, காய்கறி கடைக்கு 450 ரூபாய் போன்பே-ல அனுப்பிட்டேன். செக் பண்ணிக்கோ."),
    ("safe", "ta", "gold_safe_ta_12", "அப்பல்லோ மருத்துவமனை: டாக்டர் ரமேஷ் சந்திப்பு இன்று மாலை 5 மணிக்கு உறுதி செய்யப்பட்டது. முன்பதிவு எண் AP8471."),

    # --- SAFE: TANGLISH (12) ---
    ("safe", "tanglish", "gold_safe_tgl_01", "Unga HDFC A/c XX3920 la irunthu Rs 750 debit aagiruku towards Swiggy. Avl Bal Rs 14,250."),
    ("safe", "tanglish", "gold_safe_tgl_02", "Unga Indian Bank account ku Rs 10000 credit aagiruku through NEFT from Ramesh. Bal Rs 15400."),
    ("safe", "tanglish", "gold_safe_tgl_03", "Axis Bank OTP for online purchase of Rs 1200 is 581902. Do not share this OTP with anyone for security."),
    ("safe", "tanglish", "gold_safe_tgl_04", "Zomato: Share delivery OTP 9182 with delivery partner Murugan. Enjoy your food!"),
    ("safe", "tanglish", "gold_safe_tgl_05", "Ola ride OTP is 4019. Driver Selvam will pick you up shortly. Share OTP to start ride."),
    ("safe", "tanglish", "gold_safe_tgl_06", "Bank security alert: Never share OTP, CVV or password with anyone. Stay alert against fraud."),
    ("safe", "tanglish", "gold_safe_tgl_07", "TNEB: Rs 890 payment received for consumer no 381920. Thank you https://www.tangedco.gov.in"),
    ("safe", "tanglish", "gold_safe_tgl_08", "Machi naan movie tickets book panniten, unga share 350 GPay pannidu da."),
    ("safe", "tanglish", "gold_safe_tgl_09", "Akka unga account ku 2000 Google Pay la anupiten, check pannitu sollunga."),
    ("safe", "tanglish", "gold_safe_tgl_10", "Appa train ticket confirm aaiduchu, evening 7 PM ku Chennai Central station reach aaganum."),
    ("safe", "tanglish", "gold_safe_tgl_11", "Dei Karthik, lunch bill 620 split panniko da, naan already hotel la card thechuten."),
    ("safe", "tanglish", "gold_safe_tgl_12", "TCS campus placement: Technical interview round scheduled tomorrow 10.30 AM via Microsoft Teams."),

    # --- SAFE: ENGLISH (13) ---
    ("safe", "en", "gold_safe_en_01", "Rs 2,450.00 debited from your SBI A/c XX8471 on 24-Oct. Avl Bal: Rs 42,109. Ref: UPI/29182049182."),
    ("safe", "en", "gold_en_02", "Rs 45,000 credited to your HDFC A/c XX1092 towards monthly salary from Infosys Ltd. Avl Bal Rs 58,230."),
    ("safe", "en", "gold_safe_en_03", "Your ICICI Bank OTP for transaction of Rs 3,500 at Flipkart is 839201. Do not share this OTP with anyone, including bank officials."),
    ("safe", "en", "gold_safe_en_04", "Share OTP 9204 with your Swiggy delivery partner to receive order from Saravana Bhavan."),
    ("safe", "en", "gold_safe_en_05", "Your Ola ride OTP is 6192. Please share with driver Vijay to start your trip."),
    ("safe", "en", "gold_safe_en_06", "SBI Security Alert: Banks never call or message asking for your password, ATM PIN, or OTP. Keep your banking credentials private."),
    ("safe", "en", "gold_safe_en_07", "PM-Kisan: 16th installment of Rs 2000 has been credited to your Aadhaar linked bank account. Details at https://pmkisan.gov.in"),
    ("safe", "en", "gold_safe_en_08", "TANGEDCO: Bill payment of Rs 1,450 received for Consumer No 09182391 on 22-Oct. Official portal: https://www.tangedco.gov.in"),
    ("safe", "en", "gold_safe_en_09", "Your appointment with Dr. Sundaram at Apollo Hospitals is confirmed for Thursday at 4:30 PM. Booking ID: AP9281."),
    ("safe", "en", "gold_safe_en_10", "Hi Dad, I have transferred Rs 5,000 to your bank account for electricity and water bills."),
    ("safe", "en", "gold_safe_en_11", "Hey Priya, sent you Rs 450 on Google Pay for yesterday's dinner. Thanks!"),
    ("safe", "en", "gold_safe_en_12", "Zoho Corporation: Your second round interview for Software Developer is confirmed on Monday at 11 AM."),
    ("safe", "en", "gold_safe_en_13", "Amazon: Delivery associate will deliver your package today. Share OTP 4829 with agent at delivery.")
]

def build():
    data_dir = os.path.dirname(os.path.abspath(__file__))
    messages_path = os.path.join(data_dir, "messages.csv")
    gold_path = os.path.join(data_dir, "gold_test.csv")

    print(f"Number of template groups defined: {len(TEMPLATES)}")

    # 1. Write gold_test.csv
    print(f"Writing {len(GOLD_TEST_SET)} benchmark messages to gold_test.csv...")
    with open(gold_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "lang", "group", "text"])
        for label, lang, gid, text in GOLD_TEST_SET:
            writer.writerow([label, lang, gid, text.strip()])

    gold_texts = set(t[3].strip() for t in GOLD_TEST_SET)

    # 2. Generate training dataset from 135+ template groups
    raw_rows = []
    for template_info in TEMPLATES:
        instances = generate_instances_for_template(template_info, count=36)
        for label, lang, gid, text in instances:
            if text.strip() not in gold_texts:
                raw_rows.append((label, lang, gid, text.strip()))

    # De-duplicate by normalized text
    seen = set()
    deduped_rows = []
    for label, lang, gid, text in raw_rows:
        norm = " ".join(text.split())
        if norm not in seen:
            seen.add(norm)
            deduped_rows.append((label, lang, gid, text))

    print(f"Total deduplicated training messages: {len(deduped_rows)}")

    # Write messages.csv
    with open(messages_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "lang", "group", "text"])
        for label, lang, gid, text in deduped_rows:
            writer.writerow([label, lang, gid, text])

    print(f"Saved {len(deduped_rows)} messages to {messages_path}")

    # Summary
    counts = {}
    for label, lang, gid, text in deduped_rows:
        key = f"{label}_{lang}"
        counts[key] = counts.get(key, 0) + 1
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")

if __name__ == "__main__":
    build()
