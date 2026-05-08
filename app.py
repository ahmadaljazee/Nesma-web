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

# --- 2. إعداد Firebase (الحل المعدل لـ Render) ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            # أولاً: محاولة القراءة من Environment Variables (رندر)
            firebase_key = os.environ.get("FIREBASE_KEYS")
            
            # ثانياً: إذا لم يجدها، يجرب البحث في st.secrets (المحلي)
            if not firebase_key and "FIREBASE_KEYS" in st.secrets:
                firebase_key = st.secrets["FIREBASE_KEYS"]

            if firebase_key:
                key_dict = json.loads(firebase_key)
                creds = credentials.Certificate(key_dict)
                return firebase_admin.initialize_app(creds)
            else:
                st.error("لم يتم العثور على مفتاح FIREBASE_KEYS. تأكد من إضافته في Render Environment Variables.")
                return None
        except Exception as e:
            st.error(f"خطأ في معالجة المفاتيح: {e}")
            return None
    return firebase_admin.get_app()

# استدعاء دالة الاتصال
app = init_firebase()

# التحقق من نجاح الاتصال قبل تعريف db
if app:
    db = firestore.client()
else:
    st.warning("⚠️ التطبيق يعمل بدون قاعدة بيانات حالياً. تأكد من إعدادات المفاتيح.")
    st.stop() # إيقاف التنفيذ لتجنب الخطأ الأحمر الكبير

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
    /* ... باقي تنسيقات الـ CSS الجميلة التي أضفتها ... */
    </style>
    """, unsafe_allow_html=True)

# --- 4. واجهة المستخدم (تكملة الكود السابق) ---
st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)

with st.container():
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"])
    
    col_d, col_t = st.columns(2)
    with col_d: date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_t: time = st.time_input("⏰ وقت الحجز")

    if st.button("تأكيد الحجز وإرسال عبر واتساب"):
        if name and phone:
            try:
                # الحفظ في Firestore
                db.collection("bookings").add({
                    "name": name, "phone": phone, "cleaner": cleaner,
                    "date": str(date), "time": str(time),
                    "timestamp": datetime.datetime.now(), "status": "جديد"
                })
                
                # إرسال الواتساب
                msg = f"حجز جديد: {name} - {cleaner} - {date}"
                encoded_msg = urllib.parse.quote(msg)
                wa_url = f"https://wa.me/962777278329?text={encoded_msg}"
                st.components.v1.html(f"<script>window.open('{wa_url}', '_blank');</script>", height=0)
                st.success("تم الحجز بنجاح!")
            except Exception as e:
                st.error(f"فشل الحفظ في قاعدة البيانات: {e}")

st.markdown("<p style='text-align: center; font-weight: bold;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
