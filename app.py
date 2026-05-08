import streamlit as st
import datetime
import urllib.parse
import base64
import os

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="logo.png",
    layout="centered"
)

# دالة آمنة لتحويل الصورة لترميز CSS
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except Exception:
            return ""
    return ""

# محاولة تحميل الصورة (logo.png)
bin_str = get_base64('logo.png')

# --- التنسيق البصري الاحترافي (CSS) ---
st.markdown(f"""
    <style>
    /* 1. إخفاء الشريط الأسود العلوي والقائمة تماماً */
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* 2. إعدادات الخلفية */
    .stApp {{
        {f'background-image: linear-gradient(rgba(253, 252, 240, 0.95), rgba(232, 245, 233, 0.95)), url("data:image/png;base64,{bin_str}");' if bin_str else 'background-image: linear-gradient(135deg, #fdfcf0 0%, #e8f5e9 100%);'}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* 3. تعديل ألوان الخطوط لتكون واضحة (أخضر داكن جداً) */
    h1, h2, h3, p, span, label {{
        color: #1b5e20 !important;
        font-weight: 600 !important;
    }}

    /* 4. تنسيق حقول الإدخال */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #a5d6a7 !important;
        border-radius: 12px !important;
        color: #000000 !important; /* نص المدخلات بالأسود للوضوح التام */
    }}

    /* 5. تنسيق زر الحجز */
    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold;
        height: 55px;
        width: 100%;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,200,83,0.3) !important;
        font-size: 20px !important;
    }}

    /* تحسين شكل النبذة */
    .static-about-box {{
        background-color: rgba(255, 255, 255, 0.7);
        border: 1px solid #a5d6a7;
        border-radius: 15px;
        padding: 20px;
        text-align: right;
        direction: rtl;
        margin-bottom: 25px;
        color: #1b5e20;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- واجهة المستخدم ---

# عرض الشعار موسطاً إذا وجد
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if bin_str:
        st.image("nesma.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem;'>نظافة.. راحة.. بلمسة ذكية</p>", unsafe_allow_html=True)

# نموذج الحجز
with st.container():
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"])

    col_date, col_time = st.columns(2)
    with col_date:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_time:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("تأكيد البيانات وإرسال الحجز"):
        if name and phone:
            raw_msg = f"طلب حجز جديد من نسمة 🌬️\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 المختصة: {cleaner}\n📅 الموعد: {date} الساعة {time}"
            encoded_msg = urllib.parse.quote(raw_msg)
            whatsapp_link = f"https://wa.me/962777278329?text={encoded_msg}"
            # كود جافا سكريبت للتحويل التلقائي
            st.components.v1.html(f"<script>window.open('{whatsapp_link}', '_blank');</script>", height=0)
            st.success("يتم توجيهك الآن إلى واتساب...")
        else:
            st.error("يرجى ملء الاسم ورقم الهاتف.")

st.markdown("<p style='text-align: center; font-size: 11px; color: #555; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
