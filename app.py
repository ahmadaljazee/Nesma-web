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

# --- 2. إعداد Firebase (تعديل حيوي لحل المشكلة) ---
# هذه الدالة تضمن أن التطبيق لا يحاول الاتصال إلا إذا كان المفتاح موجوداً فعلاً
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            # محاولة القراءة من Secrets (في رندر)
            if "FIREBASE_KEYS" in st.secrets:
                key_dict = json.loads(st.secrets["FIREBASE_KEYS"])
            else:
                # إذا كنت تجرب محلياً وتملك الملف
                with open("serviceAccountKey.json") as f:
                    key_dict = json.load(f)
            
            creds = credentials.Certificate(key_dict)
            return firebase_admin.initialize_app(creds)
        except Exception as e:
            st.error(f"خطأ في إعدادات المفاتيح: {e}")
            return None
    return firebase_admin.get_app()

# استدعاء الدالة
app = init_firebase()

# تأكد من أن الاتصال تم قبل تعريف db
if app:
    db = firestore.client()
else:
    st.error("قاعدة البيانات غير متصلة. يرجى التحقق من Environment Variables في Render.")
    st.stop() # إيقاف التطبيق هنا لكي لا يظهر الخطأ الأحمر المزعج

# --- 3. التنسيق البصري (CSS) ---
# (ضع هنا كود الـ CSS الجميل الذي صممناه سابقاً)
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()
    return ""

bg_base64 = get_base64_of_bin_file('bg.png')
st.markdown(f"<style>.stApp {{ background-image: url('data:image/png;base64,{bg_base64}'); background-size: cover; }} </style>", unsafe_allow_html=True)

# --- 4. واجهة المستخدم ---
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
                # حفظ في Firestore
                db.collection("bookings").add({
                    "name": name, "phone": phone, "cleaner": cleaner,
                    "date": str(date), "time": str(time),
                    "timestamp": datetime.datetime.now(), "status": "جديد"
                })
                
                # رسالة واتساب
                msg = f"حجز جديد: {name} - {cleaner} - {date}"
                wa_url = f"https://wa.me/962777278329?text={urllib.parse.quote(msg)}"
                st.components.v1.html(f"<script>window.open('{wa_url}', '_blank');</script>", height=0)
                st.success("تم الحجز بنجاح!")
            except Exception as e:
                st.error(f"فشل الحفظ: {e}")

st.markdown("<p style='text-align: center;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
