import streamlit as st
import datetime
import urllib.parse
import base64
import os

# --- إعدادات الصفحة (تعيين الأيقونة) ---
# تم تعديل الاسم ليكون logo.png بناءً على مجلد GitHub الخاص بك
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="logo.png",
    layout="centered"
)

# دالة آمنة لتحويل الصورة لترميز CSS (لا تعطل التطبيق)
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except Exception:
            return "" # في حال وجود خطأ في القراءة
    return "" # إذا لم يكن الملف موجوداً

# محاولة تحويل الصورة لاستخدامها كخلفية (تأكد أن الملف اسمه bg.png)
bin_str = get_base64('bg.png')

# التحقق من وجود الصورة لعرض تحذير
if not bin_str:
    st.warning("⚠️ لم يتم العثور على ملف 'bg.png' في المجلد الرئيسي. يرجى التأكد من رفعه على GitHub للحصول على الخلفية.")

# --- التنسيق البصري (الكود الأساسي المطور) ---
st.markdown(f"""
    <style>
    .stApp {{
        /* تعيين صورة الخلفية مع التدرج اللوني لضمان وضوح النص */
        background-image: linear-gradient(rgba(253, 252, 240, 0.92), rgba(232, 245, 233, 0.92)), url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 12px !important;
        color: #2e4d3b !important;
    }}

    .stDateInput>div>div>input, .stTimeInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 12px !important;
        color: #2e4d3b !important;
    }}

    .static-about-box {{
        background-color: rgba(255, 255, 255, 0.8);
        border: 1px solid #a5d6a7;
        border-radius: 15px;
        padding: 20px;
        text-align: right;
        direction: rtl;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }}

    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold;
        height: 55px;
        width: 100%;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,200,83,0.3) !important;
    }}
    
    .main-header {{
        text-align: center;
        color: #1b5e20;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- واجهة المستخدم ---

# عرض الشعار موسطاً (تم تعديل الاسم إلى logo.png)
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)

st.markdown("<h1 class='main-header'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #558b2f; font-weight: 500;'>نظافة.. راحة.. بلمسة ذكية</p>", unsafe_allow_html=True)

# النبذة الثابتة
st.markdown("""
<div class="static-about-box">
    <strong>✨ لماذا نسمة؟</strong><br>
    في <b>نسمة</b>، نؤمن أن نظافة منزلك هي نسمة هدوء ليومك. نوفر لكِ نخبة من العاملات المختصات لضمان أعلى معايير الترتيب والتعقيم بخصوصية تامة.
</div>
""", unsafe_allow_html=True)

# نموذج الحجز
with st.container():
    st.markdown("<h3 style='text-align: center; color: #1b5e20;'>نموذج طلب الخدمة</h3>", unsafe_allow_html=True)
    
    name = st.text_input("👤 الاسم الكامل", placeholder="أدخل اسمك الكريم")
    phone = st.text_input("📞 رقم الجوال", placeholder="07XXXXXXXX")
    
    # اختيار العاملة (مثال)
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", ["سناء ⭐ 4.9", "أمل ⭐ 4.7", "ريم ⭐ 4.8"])

    col_date, col_time = st.columns(2)
    with col_date:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_time:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # توسيط زر الحجز
    left, center, right = st.columns([1, 2, 1])
    with center:
        if st.button("تأكيد البيانات وإرسال الحجز"):
            if name and phone:
                # تجهيز رسالة الواتساب
                raw_msg = f"طلب حجز جديد من نسمة 🌬️\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 المختصة: {cleaner}\n📅 الموعد: {date} الساعة {time}"
                encoded_msg = urllib.parse.quote(raw_msg)
                # استبدل الرقم برقم الواتساب الخاص بك (مثلاً: 962777278329)
                whatsapp_link = f"https://wa.me/962XXXXXXXXX?text={encoded_msg}"
                
                # استخدام HTML لفتح الرابط لتجنب فتح نافذة بيضاء
                st.components.v1.html(f"<script>window.location.href = '{whatsapp_link}';</script>", height=0)
            else:
                st.warning("يرجى إدخال البيانات المطلوبة.")

st.markdown("<p style='text-align: center; font-size: 11px; color: #999; margin-top: 60px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
