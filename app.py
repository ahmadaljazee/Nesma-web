import streamlit as st
import datetime
import urllib.parse
import base64
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="نسمة | Nesma", page_icon="logo.png", layout="centered")

# --- 2. إعداد الاتصال بـ Firebase (النسخة المعتمدة لـ default1) ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
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

# تعريف قاعدة البيانات default1 بشكل صحيح
db = None
if firebase_app:
    try:
        # استخدام database_id لضمان الربط بالقاعدة التي ظهرت في صورتك
        db = firestore.client(database_id="default1")
    except Exception as e:
        st.error(f"❌ خطأ في الوصول للقاعدة default1: {e}")

# --- 3. التنسيق البصري (CSS) ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()
    return ""

bg_base64 = get_base64_of_bin_file('bg.png')
st.markdown(f"""
    <style>
    header {{visibility: hidden !important;}}
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)), 
                          url("data:image/png;base64,{bg_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    /* تنسيقات النصوص والحقول والزر كما هي في كودك المعتمد */
    label, p, span, h1, h2, h3 {{ color: #0a3d0d !important; font-weight: 800 !important; }}
    div.stButton > button {{
        background-color: #00c853 !important; color: white !important;
        border-radius: 30px !important; font-weight: bold; height: 55px; width: 100%;
    }}
    .about-section {{ background-color: rgba(255, 255, 255, 0.7); border-radius: 15px; padding: 20px; text-align: right; direction: rtl; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. واجهة التطبيق ---
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2: st.image("logo.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)

# النبذة والمميزات
st.markdown("<div class='about-section'><p>في 'نسمة'، نؤمن أن نظافة منزلك هي نسمة هدوء ليومك.</p></div>", unsafe_allow_html=True)

# --- 5. نموذج الحجز ---
with st.container():
    st.markdown("---")
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"])
    
    col_d, col_t = st.columns(2)
    with col_d: date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_t: time = st.time_input("⏰ وقت الحجز")

    if st.button("تأكيد الحجز وإرسال عبر واتساب"):
        if name and phone:
            try:
                # حفظ في Firestore (قاعدة default1)
                if db:
                    db.collection("bookings").add({
                        "name": name, "phone": phone, "cleaner": cleaner,
                        "date": str(date), "time": str(time),
                        "timestamp": datetime.datetime.now(), "status": "جديد"
                    })

                # تجهيز وفتح الواتساب
                msg = f"حجز جديد من نسمة 🌬️\nالاسم: {name}\nالهاتف: {phone}\nالموعد: {date} {time}"
                wa_url = f"https://wa.me/962777278329?text={urllib.parse.quote(msg)}"
                st.components.v1.html(f"<script>window.open('{wa_url}', '_blank');</script>", height=0)
                st.success("تم تسجيل حجزك في النظام وفتح الواتساب!")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
        else:
            st.error("يرجى إدخال الاسم ورقم الهاتف.")

st.markdown("<p style='text-align: center; font-weight: bold;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
