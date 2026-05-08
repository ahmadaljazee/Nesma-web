import streamlit as st
import datetime
import urllib.parse
import base64
import os
import json
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="نسمة | Nesma", page_icon="logo.png", layout="centered")

# --- 2. إعداد الاتصال بـ Firebase ---
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
db = None
if firebase_app:
    try:
        # الربط المباشر بقاعدتك default1 التي نجحنا في تفعيلها
        db = firestore.client(database_id="default1")
    except Exception as e:
        st.error(f"❌ خطأ في الوصول للقاعدة default1: {e}")

# --- 3. نظام حماية لوحة التحكم ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.sidebar.markdown("### 🔐 منطقة الإدارة")
        # جلب كلمة المرور من إعدادات رندر أو استخدام الافتراضية
        ADMIN_PWD = os.environ.get("ADMIN_PASSWORD", "Nesma2026")
        pwd = st.sidebar.text_input("أدخل كلمة المرور", type="password")
        if pwd == ADMIN_PWD:
            st.session_state["password_correct"] = True
            st.sidebar.success("تم تسجيل الدخول")
            return True
        elif pwd != "":
            st.sidebar.error("كلمة المرور خاطئة")
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
        border: none !important; box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    .about-section {{ background-color: rgba(255, 255, 255, 0.7); border-radius: 15px; padding: 20px; text-align: right; direction: rtl; border: 1px solid #a5d6a7; }}
    .about-title {{ color: #1b5e20; font-size: 1.5rem; border-bottom: 2px solid #00c853; display: inline-block; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. منطق التنقل بين الصفحات ---
st.sidebar.image("logo.png", width=100) if os.path.exists("logo.png") else None
page = st.sidebar.radio("الانتقال إلى:", ["واجهة الزبائن", "لوحة الإدارة 📊"])

if page == "لوحة الإدارة 📊":
    if check_password():
        st.markdown("<h2 style='text-align: center;'>📊 سجل حجوزات نسمة</h2>", unsafe_allow_html=True)
        try:
            # جلب البيانات من Firestore
            docs = db.collection("bookings").order_by("timestamp", direction=firestore.Query.DESCENDING).stream()
            data = []
            for doc in docs:
                item = doc.to_dict()
                # تنسيق الوقت ليكون مقروءاً أكثر في الجدول
                if 'timestamp' in item:
                    item['تسجيل الطلب'] = item['timestamp'].strftime('%Y-%m-%d %H:%M')
                data.append(item)
            
            if data:
                df = pd.DataFrame(data)
                # إحصائيات سريعة في لوحة التحكم
                c1, c2 = st.columns(2)
                c1.metric("إجمالي الحجوزات", len(df))
                c2.metric("حجوزات اليوم", len(df[df['date'] == str(datetime.date.today())]))
                
                # ترتيب الأعمدة للعرض
                cols_to_show = ['name', 'phone', 'cleaner', 'date', 'time', 'تسجيل الطلب']
                st.dataframe(df[cols_to_show], use_container_width=True)
                
                # خيار لتحميل البيانات كملف Excel/CSV
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 تحميل سجل الحجوزات", data=csv, file_name='nesma_bookings.csv', mime='text/csv')
            else:
                st.info("لا توجد حجوزات مسجلة في قاعدة البيانات حتى الآن.")
        except Exception as e:
            st.error(f"خطأ في جلب البيانات: {e}")

else:
    # --- واجهة الزبائن الأصلية ---
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: st.image("logo.png", use_container_width=True)

    st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>رعــــاية..جـــودة..أمـــان</p>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class='about-section'>
            <div class='about-title'>لماذا نسمة؟</div>
            <p style='font-size: 1.1rem; line-height: 1.7;'>
                في "نسمة"، نؤمن أن نظافة منزلك هي نسمة هدوء ليومك. 
                نوفر لكِ نخبة من العاملات المختصات والمدربات، لضمان أعلى معايير الترتيب والتعقيم بخصوصية تامة واحترافية تليق بكِ.
            </p>
        </div>
        """, unsafe_allow_html=True)

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
                            "timestamp": datetime.datetime.now()
                        })
                    # تجهيز رسالة الواتساب
                    raw_msg = f"طلب حجز جديد من تطبيق نسمة 🌬️\n---\n👤 الاسم: {name}\n📞 الهاتف: {phone}\n🧹 العاملة: {cleaner}\n📅 الموعد: {date} {time}"
                    encoded_msg = urllib.parse.quote(raw_msg)
                    wa_url = f"https://wa.me/962777278329?text={encoded_msg}"
                    
                    st.components.v1.html(f"<script>window.open('{wa_url}', '_blank');</script>", height=0)
                    st.success("تم تسجيل حجزك بنجاح! جاري تحويلك لواتساب...")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء معالجة الطلب: {e}")
            else:
                st.error("يرجى إكمال الاسم ورقم الهاتف.")

st.markdown("<p style='text-align: center; font-size: 12px; color: #000; margin-top: 50px; font-weight: bold;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
