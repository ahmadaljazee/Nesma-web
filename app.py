import streamlit as st
import datetime
import urllib.parse
import base64
import os
import json
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. إعدادات الصفحة والأيقونة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="logo.png", 
    layout="centered"
)

# --- 2. إعداد الاتصال بـ Firebase (قاعدة بيانات default1) ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            # جلب المفاتيح من Environment Variables في رندر
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
db = None
if firebase_app:
    try:
        # الربط المباشر بقاعدة البيانات default1
        db = firestore.client(database_id="default1")
    except Exception as e:
        st.error(f"❌ خطأ في الوصول للقاعدة default1: {e}")

# --- 3. نظام حماية لوحة التحكم ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.sidebar.subheader("🔐 دخول الإدارة")
        # كلمة السر الافتراضية Nesma2026
        pwd = st.sidebar.text_input("أدخل كلمة المرور", type="password")
        if st.sidebar.button("دخول"):
            if pwd == "Nesma2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.sidebar.error("❌ كلمة المرور خاطئة")
        return False
    return True

# --- 4. التنسيق البصري الاحترافي (CSS) ---
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
    
    label, p, span, h1, h2, h3 {{ color: #0a3d0d !important; font-weight: 800 !important; text-shadow: 1px 1px 3px rgba(255,255,255,0.7); }}

    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #2e7d32 !important; border-radius: 12px !important;
        color: black !important; font-weight: 600 !important;
    }}

    div.stButton > button {{
        background-color: #00c853 !important; color: white !important;
        border-radius: 30px !important; font-weight: bold; height: 55px; width: 100%;
        border: none !important; box-shadow: 0 5px 15px rgba(0,0,0,0.2); font-size: 20px !important;
    }}
    
    .about-section {{
        background-color: rgba(255, 255, 255, 0.7); border-radius: 15px; padding: 20px;
        border: 1px solid #a5d6a7; margin-bottom: 25px; text-align: right; direction: rtl;
    }}
    .about-title {{ color: #1b5e20; font-size: 1.5rem; border-bottom: 2px solid #00c853; display: inline-block; padding-bottom: 5px; }}
    .features-section {{ text-align: right; direction: rtl; margin: 15px 0; }}
    .feature-item {{ font-size: 1.1rem; color: #0a3d0d; font-weight: 700 !important; }}
    .feature-icon {{ color: #00c853; margin-left: 10px; font-size: 1.2rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. منطق التنقل (Sidebar) ---
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=150)

page = st.sidebar.radio("انتقل إلى:", ["واجهة الحجز", "لوحة التحكم 📊"])

if page == "لوحة التحكم 📊":
    if check_password():
        st.markdown("<h2 style='text-align: center;'>📊 إدارة عمليات نسمة</h2>", unsafe_allow_html=True)
        try:
            docs = db.collection("bookings").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
            data = []
            for doc in docs:
                d = doc.to_dict()
                d['id'] = doc.id
                data.append(d)
            
            if data:
                df = pd.DataFrame(data)
                st.metric("إجمالي الطلبات", len(df))
                st.dataframe(df[['name', 'phone', 'cleaner', 'date', 'time', 'status']], use_container_width=True)
                
                # تحديث الحالة
                with st.expander("📝 تحديث حالة الطلب"):
                    selected_id = st.selectbox("اختر طلب الزبون:", options=df['id'], format_func=lambda x: df[df['id']==x]['name'].values[0])
                    new_status = st.selectbox("تغيير الحالة إلى:", ["جديد", "تم التواصل", "تم التنفيذ", "ملغي"])
                    if st.button("تحديث"):
                        db.collection("bookings").document(selected_id).update({"status": new_status})
                        st.success("تم التحديث!")
                        st.rerun()
            else:
                st.info("لا توجد بيانات حالياً.")
        except Exception as e:
            st.error(f"خطأ: {e}")
        
        if st.sidebar.button("تسجيل خروج"):
            st.session_state["password_correct"] = False
            st.rerun()

else:
    # --- واجهة الزبائن الأصلية (مع البيو والمميزات) ---
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: st.image("logo.png", use_container_width=True)

    st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.3rem; margin-bottom: 25px;'>رعــــاية..جـــودة..أمـــان</p>", unsafe_allow_html=True)

    # النبذة التعريفية
    st.markdown(f"""
        <div class='about-section'>
            <div class='about-title'>لماذا نسمة؟</div>
            <p class='about-text'>
                في "نسمة"، نؤمن أن نظافة منزلك هي نسمة هدوء ليومك. 
                نوفر لكِ نخبة من العاملات المختصات والمدربات، لضمان أعلى معايير الترتيب والتعقيم، بخصوصية تامة واحترافية تليق بكِ. 
            </p>
        </div>
        """, unsafe_allow_html=True)

    # قائمة المميزات
    st.markdown(f"""
        <div class='features-section'>
            <p class='feature-item'><span class='feature-icon'>✨</span>عاملات مختصات (⭐ 4.9)</p>
            <p class='feature-item'><span class='feature-icon'>🕒</span>حجز سريع وسهل عبر واتساب</p>
            <p class='feature-item'><span class='feature-icon'>🔒</span>خصوصية تامة وأمان مضمون</p>
            <p class='feature-item'><span class='feature-icon'>💧</span>جودة وتعقيم بلمسة ذكية</p>
        </div>
        """, unsafe_allow_html=True)

    # نموذج الحجز
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
                    msg = f"حجز جديد من نسمة 🌬️\nالاسم: {name}\nالهاتف: {phone}\nالعاملة: {cleaner}\nالموعد: {date} {time}"
                    wa_url = f"https://wa.me/962777278329?text={urllib.parse.quote(msg)}"
                    st.components.v1.html(f"<script>window.open('{wa_url}', '_blank');</script>", height=0)
                    st.success("تم الحجز بنجاح!")
                except Exception as e:
                    st.error(f"خطأ: {e}")
            else:
                st.error("يرجى إدخال الاسم ورقم الهاتف.")

st.markdown("<p style='text-align: center; font-size: 12px; color: #000; margin-top: 50px; font-weight: bold;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
