import streamlit as st
import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="🌬️",
    layout="centered"
)

# --- التنسيق البصري (الهوية البصرية لنسمة) ---
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #121212;
        color: #ffffff;
    }}
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: #1e1e1e !important;
        color: white !important;
        border: 1px solid #8ff48f !important;
        border-radius: 10px;
    }}
    .stButton>button {{
        background-color: #8ff48f !important;
        color: #000000 !important;
        border-radius: 25px !important;
        width: 100%;
        font-weight: bold;
        height: 50px;
        border: none !important;
    }}
    .bio-text {{
        text-align: center;
        color: #aaaaaa;
        font-size: 14px;
        margin-bottom: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #8ff48f;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown('<div class="bio-text">نسمة.. نظافة.. راحة.. بلمسة ذكية.</div>', unsafe_allow_html=True)

# --- نموذج الحجز ---
with st.container():
    name = st.text_input("👤 الاسم الكامل", placeholder="أدخل اسمك هنا")
    phone = st.text_input("📞 رقم الجوال", placeholder="07XXXXXXXX")
    
    cleaner = st.selectbox(
        "اختر العاملة المختصة:",
        ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"]
    )

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col2:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # عند الضغط على الزر
    if st.button("تأكيد البيانات وإرسال الحجز"):
        if name and phone:
            # 1. تجهيز الرسالة
            raw_message = f"طلب حجز جديد من موقع نسمة\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 العاملة: {cleaner}\n📅 الموعد: {date} الساعة {time}"
            encoded_message = urllib.parse.quote(raw_message)
            
            # 2. رابط الواتساب
            admin_phone = "962777278329"
            whatsapp_url = f"https://wa.me/{admin_phone}?text={encoded_message}"
            
            # 3. تنفيذ الفتح التلقائي عبر JavaScript مخفي
            # نستخدم target="_self" لضمان الفتح السلس في بعض المتصفحات
            js_code = f"""
            <script>
                window.location.href = "{whatsapp_url}";
            </script>
            """
            st.components.v1.html(js_code, height=0)
            
            st.info("جاري التحويل إلى واتساب...")
        else:
            st.warning("الرجاء إدخال الاسم ورقم الجوال أولاً.")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
