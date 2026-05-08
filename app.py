import streamlit as st
import datetime
import urllib.parse
import base64
import os
import json
import pandas as pd # أضفنا pandas لعرض الجداول باحترافية
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
        db = firestore.client(database_id="default1")
    except Exception as e:
        st.error(f"❌ خطأ في الوصول للقاعدة default1: {e}")

# --- 3. نظام حماية لوحة التحكم ---
def check_password():
    """إرجاع True إذا كانت كلمة المرور صحيحة"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.sidebar.subheader("🔐 دخول الإدارة")
        # يمكنك تغيير كلمة السر هنا (Nesma2026)
        pwd = st.sidebar.text_input("أدخل كلمة المرور", type="password")
        if st.sidebar.button("دخول"):
            if pwd == "Nesma2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.sidebar.error("❌ كلمة المرور خاطئة")
        return False
    return True

# --- 4. التنسيق البصري (CSS) ---
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
    label, p, span, h1, h2, h3 {{ color: #0a3d0d !important; font-weight: 800 !important; }}
    div.stButton > button {{
        background-color: #00c853 !important; color: white !important;
        border-radius: 30px !important; font-weight: bold; height: 55px; width: 100%;
    }}
    .about-section {{ background-color: rgba(255, 255, 255, 0.7); border-radius: 15px; padding: 20px; text-align: right; direction: rtl; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. منطق التنقل بين الواجهة والداشبورد ---
st.sidebar.title("🌬️ نسمة - Nesma")
page = st.sidebar.radio("انتقل إلى:", ["واجهة الحجز", "لوحة التحكم 📊"])

if page == "لوحة التحكم 📊":
    if check_password():
        st.markdown("<h2 style='text-align: center;'>📊 لوحة إدارة الحجوزات</h2>", unsafe_allow_html=True)
        
        if db:
            try:
                # جلب البيانات من Firestore
                docs = db.collection("bookings").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
                data = [doc.to_dict() for doc in docs]
                
                if data:
                    df = pd.DataFrame(data)
                    
                    # إحصائيات سريعة
                    st.columns(3)[0].metric("إجمالي الحجوزات", len(df))
                    
                    # تنسيق الجدول للعرض
                    st.write("### قائمة الحجوزات الأخيرة:")
                    st.dataframe(df[['name', 'phone', 'cleaner', 'date', 'time', 'status']], use_container_width=True)
                    
                    # خيار تحميل البيانات كملف CSV
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 تحميل سجل الحجوزات CSV", csv, "bookings.csv", "text/csv")
                else:
                    st.info("لا توجد حجوزات مسجلة حتى الآن.")
            except Exception as e:
                st.error(f"خطأ في جلب البيانات: {e}")
    
    # زر خروج من الإدارة
    if st.session_state.get("password_correct"):
        if st.sidebar.button("تسجيل خروج"):
            st.session_state["password_correct"] = False
            st.rerun()

else:
    # --- واجهة الزبائن الأصلية ---
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: st.image("logo.png", use_container_width=True)

    st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
    st.markdown("<div class='about-section'><p>في 'نسمة' نؤمن أن نظافة منزلك هي نسمة هدوء ليومك.</p></div>", unsafe_allow_html=True)

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
                    if db:
                        db.collection("bookings").add({
                            "name": name, "phone": phone, "cleaner": cleaner,
                            "date": str(date), "time": str(time),
                            "timestamp": datetime.datetime.now(), "status": "جديد"
                        })

                    msg = f"حجز جديد من نسمة 🌬️\nالاسم: {name}\nالهاتف: {phone}\nالموعد: {date} {time}"
                    wa_url = f"https://wa.me/962777278329?text={urllib.parse.quote(msg)}"
                    st.components.v1.html(f"<script>window.open('{wa_url}', '_blank');</script>", height=0)
                    st.success("تم تسجيل حجزك في النظام وفتح الواتساب!")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
            else:
                st.error("يرجى إدخال الاسم ورقم الهاتف.")

st.markdown("<p style='text-align: center; font-weight: bold; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
