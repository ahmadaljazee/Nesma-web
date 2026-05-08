import streamlit as st
import datetime
import urllib.parse
import base64
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. إعدادات الصفحة والأيقونة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="logo.png", 
    layout="centered"
)

# --- 2. إعداد الاتصال بـ Firebase (Firestore) ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            # محاولة جلب المفاتيح من Environment Variables (رندر) أو st.secrets
            firebase_key = os.environ.get("FIREBASE_KEYS")
            if not firebase_key and "FIREBASE_KEYS" in st.secrets:
                firebase_key = st.secrets["FIREBASE_KEYS"]

            if firebase_key:
                key_dict = json.loads(firebase_key)
                creds = credentials.Certificate(key_dict)
                return firebase_admin.initialize_app(creds)
            return None
        except Exception as e:
            st.error(f"⚠️ فشل الاتصال بقاعدة البيانات: {e}")
            return None
    return firebase_admin.get_app()

firebase_app = init_firebase()
if firebase_app:
    db = firestore.client()
else:
    st.warning("⚠️ التطبيق يعمل بدون حفظ في قاعدة البيانات حالياً.")

# --- 3. التنسيق البصري الاحترافي (نفس الكود الأصلي بدون تعديل) ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except: return ""
    return ""

bg_base64 = get_base64_of_bin_file('bg.png')

st.markdown(f"""
    <style>
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)), 
                          url("data:image/png;base64,{bg_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    
    label, p, span, h1, h2, h3 {{
        color: #0a3d0d !important; font-weight: 800 !important;
        text-shadow: 1px 1px 3px rgba(255,255,255,0.7);
    }}

    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #2e7d32 !important; border-radius: 12px !important;
        color: black !important; font-weight: 600 !important;
    }}

    div.stButton > button {{
        background-color: #00c853 !important; color: white !important;
        border-radius: 30px !important; font-weight: bold; height: 55px;
        width: 100%; max-width: 400px; border: none !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2); font-size: 20px !important;
        transition: 0.3s ease;
    }}
    
    .about-section {{
        background-color: rgba(255, 255, 255, 0.7); border-radius: 15px;
        padding: 20px; border: 1px solid #a5d6a7; margin-bottom: 25px;
        text-align: right; direction: rtl;
    }}
    .about-title {{
        color: #1b5e20; font-size: 1.5rem; margin-bottom: 10px;
        border-bottom: 2px solid #00c853; display: inline-block; padding-bottom: 5px;
    }}
    .features-section {{ text-align: right; direction: rtl; margin: 15px 0; }}
    .feature-item {{ font-size: 1.1rem; color: #0a3d0d; font-weight: 700 !important; }}
    .feature-icon {{ color: #00c853; margin-left: 10px; font-size: 1.2rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. واجهة التطبيق (اللوجو، النبذة، المميزات) ---
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2: st.image("logo.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem; margin-bottom: 25px;'>رعــــاية..جـــودة..أمـــان</p>", unsafe_allow_html=True)

st.markdown(f"""
    <div class='about-section'>
        <div class='about-title'>لماذا نسمة؟</div>
        <p class='about-text'>
            في "نسمة"، نؤمن أن نظافة منزلك هي نسمة هدوء ليومك. 
            نوفر لكِ نخبة من العاملات المختصات والمدربات، لضمان أعلى معايير الترتيب والتعقيم.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <div class='features-section'>
        <p class='feature-item'><span class='feature-icon'>✨</span>عاملات مختصات (⭐ 4.9)</p>
        <p class='feature-item'><span class='feature-icon'>🕒</span>حجز سريع وسهل عبر واتساب</p>
        <p class='feature-item'><span class='feature-icon'>🔒</span>خصوصية تامة وأمان مضمون</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. نموذج الحجز ومعالجة البيانات ---
with st.container():
    st.markdown("---")
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"])

    col_d, col_t = st.columns(2)
    with col_d: date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_t: time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("تأكيد الحجز وإرسال عبر واتساب"):
        if name and phone:
            try:
                # أ- حفظ في Firestore
                if firebase_app:
                    db.collection("bookings").add({
                        "name": name, "phone": phone, "cleaner": cleaner,
                        "date": str(date), "time": str(time),
                        "timestamp": datetime.datetime.now(), "status": "جديد"
                    })

                # ب- فتح الواتساب
                raw_msg = (
                    f"طلب حجز جديد من تطبيق نسمة 🌬️\n"
                    f"--------------------------\n"
                    f"👤 الاسم: {name}\n"
                    f"📞 الهاتف: {phone}\n"
                    f"🧹 العاملة: {cleaner}\n"
                    f"📅 الموعد: {date} الساعة {time}\n"
                    f"--------------------------"
                )
                encoded_msg = urllib.parse.quote(raw_msg)
                whatsapp_link = f"https://wa.me/962777278329?text={encoded_msg}"
                
                st.components.v1.html(f"<script>window.open('{whatsapp_link}', '_blank');</script>", height=0)
                st.success("تم الحجز بنجاح! جاري تحويلك لواتساب...")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
        else:
            st.error("يرجى إدخال الاسم ورقم الهاتف.")

st.markdown("<p style='text-align: center; font-size: 12px; color: #000; margin-top: 50px; font-weight: bold;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
