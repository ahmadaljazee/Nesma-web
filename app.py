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

# --- 2. إعداد Firebase (الربط البرمجي بقاعدة البيانات) ---
if not firebase_admin._apps:
    try:
        # قراءة المفتاح السري من Environment Variables في رندر
        if "FIREBASE_KEYS" in st.secrets:
            key_dict = json.loads(st.secrets["FIREBASE_KEYS"])
            creds = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(creds)
        else:
            st.error("لم يتم العثور على مفاتيح Firebase في إعدادات رندر.")
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")

db = firestore.client()

# --- 3. الدوال المساعدة والتنسيق البصري (CSS) ---
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
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)), 
                          url("data:image/png;base64,{bg_base64}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    label, p, span, h1, h2, h3 {{ color: #0a3d0d !important; font-weight: 800 !important; }}
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #2e7d32 !important; border-radius: 12px !important;
    }}
    div.stButton > button {{
        background-color: #00c853 !important; color: white !important;
        border-radius: 30px !important; font-weight: bold; height: 55px; width: 100%;
        max-width: 400px; font-size: 20px !important; transition: 0.3s ease;
    }}
    .about-section {{ background-color: rgba(255, 255, 255, 0.7); border-radius: 15px; padding: 20px; border: 1px solid #a5d6a7; margin-bottom: 25px; text-align: right; direction: rtl; }}
    .about-title {{ color: #1b5e20; font-size: 1.5rem; border-bottom: 2px solid #00c853; display: inline-block; }}
    .features-section {{ text-align: right; direction: rtl; margin-bottom: 15px; }}
    .feature-item {{ font-size: 1.1rem; color: #0a3d0d; font-weight: 700 !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. واجهة التطبيق ---
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2: st.image("logo.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem; margin-bottom: 25px;'>رعــــاية..جـــودة..أمـــان</p>", unsafe_allow_html=True)

st.markdown(f"""
    <div class='about-section'>
        <div class='about-title'>لماذا نسمة؟</div>
        <p class='about-text'>في "نسمة"، نؤمن أن نظافة منزلك هي نسمة هدوء ليومك. نوفر لكِ نخبة من العاملات المختصات والمدربات.</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. نموذج الحجز وقاعدة البيانات ---
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
                # أ. تخزين البيانات في Firebase Firestore
                doc_ref = db.collection("bookings").document()
                doc_ref.set({
                    "name": name,
                    "phone": phone,
                    "cleaner": cleaner,
                    "date": str(date),
                    "time": str(time),
                    "timestamp": datetime.datetime.now(),
                    "status": "New"
                })

                # ب. تجهيز رسالة الواتساب
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
                
                # ج. الفتح التلقائي للواتساب
                st.components.v1.html(f"<script>window.open('{whatsapp_link}', '_blank');</script>", height=0)
                st.success("تم تسجيل بياناتك في النظام.. جاري تحويلك لواتساب")
                
            except Exception as e:
                st.error(f"عذراً، حدث خطأ في النظام: {e}")
        else:
            st.error("يرجى إدخال الاسم ورقم الهاتف.")

st.markdown("<p style='text-align: center; font-size: 12px; color: #000; margin-top: 50px; font-weight: bold;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
