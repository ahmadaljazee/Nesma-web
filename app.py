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
        db = firestore.client(database_id="default1")
    except Exception as e:
        st.error(f"❌ خطأ في الوصول للقاعدة default1: {e}")

# --- 3. نظام حماية لوحة التحكم ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        st.sidebar.markdown("### 🔐 منطقة الإدارة")
        ADMIN_PWD = os.environ.get("ADMIN_PASSWORD", "Nesma2026")
        pwd = st.sidebar.text_input("أدخل كلمة المرور", type="password")
        if pwd == ADMIN_PWD:
            st.session_state["password_correct"] = True
            st.sidebar.success("تم تسجيل الدخول")
            st.rerun() # إعادة التشغيل لتنظيف الواجهة فوراً
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
    </style>
    """, unsafe_allow_html=True)

# --- 5. منطق التنقل واللوجو النظيف ---
# إصلاح خطأ اللوجو: عرض مباشر بدون Metadata
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=150)

page = st.sidebar.radio("الانتقال إلى:", ["واجهة الزبائن", "لوحة الإدارة 📊"])

if page == "لوحة الإدارة 📊":
    if check_password():
        st.markdown("<h2 style='text-align: center;'>📊 إدارة عمليات نسمة</h2>", unsafe_allow_html=True)
        try:
            # جلب الحجوزات
            bookings_ref = db.collection("bookings").order_by("timestamp", direction=firestore.Query.DESCENDING)
            docs = list(bookings_ref.stream())
            
            data = []
            for doc in docs:
                d = doc.to_dict()
                d['id'] = doc.id # حفظ الـ ID لتعديل الحالة لاحقاً
                if 'status' not in d: d['status'] = 'جديد' # حالة افتراضية
                data.append(d)
            
            if data:
                df = pd.DataFrame(data)
                
                # إحصائيات سريعة
                st.metric("إجمالي الطلبات", len(df))
                
                # قسم تحديث الحالة
                st.markdown("---")
                st.subheader("📝 تحديث حالة حجز")
                selected_id = st.selectbox("اختر اسم الزبون لتعديل حالته:", 
                                         options=df['id'], 
                                         format_func=lambda x: df[df['id']==x]['name'].values[0])
                
                new_status = st.selectbox("الحالة الجديدة:", ["جديد", "تم التواصل", "تم التنفيذ", "ملغي"])
                if st.button("تحديث الحالة الآن"):
                    db.collection("bookings").document(selected_id).update({"status": new_status})
                    st.success(f"تم تحديث حالة طلب {df[df['id']==selected_id]['name'].values[0]} إلى {new_status}")
                    st.rerun()

                st.markdown("---")
                # عرض الجدول النهائي
                st.dataframe(df[['name', 'phone', 'cleaner', 'date', 'time', 'status']], use_container_width=True)
            else:
                st.info("لا توجد بيانات حالياً.")
        except Exception as e:
            st.error(f"خطأ: {e}")

else:
    # --- واجهة الزبائن (نفس الكود المستقر) ---
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2: st.image("logo.png", use_container_width=True)

    st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='about-section'><p>نظافة منزلك هي نسمة هدوء ليومك.</p></div>", unsafe_allow_html=True)
        st.markdown("---")
        name = st.text_input("👤 الاسم الكامل")
        phone = st.text_input("📞 رقم الجوال")
        cleaner = st.selectbox("🧹 اختر العاملة:", ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"])
        
        col_d, col_t = st.columns(2)
        with col_d: date = st.date_input("📅 التاريخ", min_value=datetime.date.today())
        with col_t: time = st.time_input("⏰ الوقت")

        if st.button("تأكيد الحجز وإرسال عبر واتساب"):
            if name and phone:
                try:
                    db.collection("bookings").add({
                        "name": name, "phone": phone, "cleaner": cleaner,
                        "date": str(date), "time": str(time),
                        "timestamp": datetime.datetime.now(),
                        "status": "جديد"
                    })
                    msg = f"حجز جديد من نسمة\nالاسم: {name}\nالهاتف: {phone}\nالموعد: {date} {time}"
                    wa_url = f"https://wa.me/962777278329?text={urllib.parse.quote(msg)}"
                    st.components.v1.html(f"<script>window.open('{wa_url}', '_blank');</script>", height=0)
                    st.success("تم الحجز بنجاح!")
                except Exception as e:
                    st.error(f"خطأ: {e}")
            else:
                st.error("يرجى إكمال البيانات.")

st.markdown("<p style='text-align: center; font-weight: bold; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
