import streamlit as st
import datetime
import urllib.parse
import base64

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="nesma.png",
    layout="centered"
)

# دالة لتحويل الصورة لترميز يمكن استخدامه في CSS
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# تحويل اللوجو لاستخدامه كخلفية
bin_str = get_base64('nesma.png')

# --- التنسيق البصري المحدث (إضافة الخلفية) ---
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(253, 252, 240, 0.9), rgba(232, 245, 233, 0.9)), 
                          url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 10px !important;
    }}

    .static-about-box {{
        background-color: rgba(255, 255, 255, 0.7);
        border: 1px solid #a5d6a7;
        border-radius: 15px;
        padding: 20px;
        text-align: right;
        direction: rtl;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}

    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 25px !important;
        font-weight: bold;
        height: 55px;
        width: 100%;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }}
    
    .main-header {{
        text-align: center;
        color: #2e7d32;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- واجهة المستخدم ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("nesma.png", use_container_width=True)

st.markdown("<h1 class='main-header'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #558b2f;'>نظافة.. راحة.. بلمسة ذكية</p>", unsafe_allow_html=True)

# النبذة الثابتة
st.markdown("""
<div class="static-about-box">
    <strong>✨ لماذا نسمة؟</strong><br>
    في <b>نسمة</b>، نؤمن أن نظافة منزلك هي نسمة هدوء ليومك. نوفر لكِ نخبة من العاملات المختصات لضمان أعلى معايير الترتيب والتعقيم بخصوصية تامة.
</div>
""", unsafe_allow_html=True)

# نموذج الحجز
with st.container():
    name = st.text_input("👤 الاسم الكامل", placeholder="أدخل اسمك الكريم")
    phone = st.text_input("📞 رقم الجوال", placeholder="07XXXXXXXX")
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"])

    col_date, col_time = st.columns(2)
    with col_date:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_time:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    left, center, right = st.columns([1, 2, 1])
    with center:
        if st.button("تأكيد البيانات وإرسال الحجز"):
            if name and phone:
                raw_msg = f"طلب حجز جديد من نسمة 🌬️\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 المختصة: {cleaner}\n📅 الموعد: {date} الساعة {time}"
                encoded_msg = urllib.parse.quote(raw_msg)
                whatsapp_link = f"https://wa.me/962777278329?text={encoded_msg}"
                st.components.v1.html(f"<script>window.location.href = '{whatsapp_link}';</script>", height=0)
            else:
                st.warning("يرجى إدخال البيانات المطلوبة.")

st.markdown("<p style='text-align: center; font-size: 11px; color: #999; margin-top: 60px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
