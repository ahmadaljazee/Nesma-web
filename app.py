import streamlit as st
import datetime
import urllib.parse
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. إعداد الاتصال بـ Firebase (آمن تماماً) ---
if not firebase_admin._apps:
    try:
        # استدعاء المفتاح من Environment Variables التي أضفتها في رندر
        key_dict = json.loads(st.secrets["FIREBASE_KEYS"])
        creds = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(creds)
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")

db = firestore.client()

# --- 2. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="نسمة | Nesma", page_icon="🌬️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #ffffff; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1e1e1e !important; color: white !important;
        border: 1px solid #8ff48f !important; border-radius: 10px;
    }
    .stButton>button {
        background-color: #8ff48f !important; color: #000000 !important;
        border-radius: 25px !important; width: 100%; font-weight: bold; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #8ff48f;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaa;'>نظافة.. راحة.. بلمسة ذكية</p>", unsafe_allow_html=True)

# --- 3. نموذج الحجز ---
with st.container():
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    cleaner = st.selectbox("اختر النسمة المختصة:", ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"])
    
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 التاريخ", min_value=datetime.date.today())
    with col2:
        time = st.time_input("⏰ الوقت")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("تأكيد الحجز"):
        if name and phone:
            try:
                # أ- حفظ البيانات في Firebase
                doc_ref = db.collection("bookings").document()
                doc_ref.set({
                    "name": name,
                    "phone": phone,
                    "cleaner": cleaner,
                    "date": str(date),
                    "time": str(time),
                    "timestamp": datetime.datetime.now(),
                    "status": "جديد"
                })

                # ب- تجهيز رابط الواتساب
                raw_msg = f"طلب حجز جديد من نسمة:\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 العاملة: {cleaner}\n📅 الموعد: {date} {time}"
                encoded_msg = urllib.parse.quote(raw_msg)
                wa_url = f"https://wa.me/962777278329?text={encoded_msg}"

                # ج- التحويل التلقائي للواتساب عبر JavaScript
                js = f"window.open('{wa_url}', '_blank')"
                st.components.v1.html(f"<script>{js}</script>", height=0)

                st.success(f"تم تسجيل حجزك يا {name}.. جاري فتح واتساب!")
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحفظ: {e}")
        else:
            st.warning("يرجى تعبئة جميع البيانات.")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
