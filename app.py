import streamlit as st
import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="🌬️",
    layout="centered"
)

# --- التنسيق البصري (الألوان والهوية) ---
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #ffffff; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1e1e1e !important; color: white !important;
        border: 1px solid #8ff48f !important; border-radius: 10px;
    }
    .stButton>button {
        background-color: #8ff48f !important; color: #000000 !important;
        border-radius: 25px !important; font-weight: bold; width: 100%; height: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #8ff48f;'>نسمة | Nesma</h1>", unsafe_allow_html=True)

# --- نموذج الحجز ---
with st.container():
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    
    cleaner = st.selectbox(
        "اختر العاملة المختصة:",
        ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"]
    )

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 التاريخ", min_value=datetime.date.today())
    with col2:
        time = st.time_input("⏰ الوقت")

    if st.button("تأكيد البيانات"):
        if name and phone:
            # 1. صياغة الرسالة التلقائية
            message_text = (
                f"مرحباً نسمة، لدي طلب حجز جديد:\n"
                f"👤 الاسم: {name}\n"
                f"📞 الجوال: {phone}\n"
                f"🧹 العاملة: {cleaner}\n"
                f"📅 الموعد: {date} الساعة {time}"
            )
            
            # 2. تشفير الرسالة (Encoding)
            encoded_msg = urllib.parse.quote(message_text)
            admin_number = "962777278329"
            wa_url = f"https://wa.me/{admin_number}?text={encoded_msg}"
            
            # 3. الرسالة التنبيهية
            st.success(f"إتم تجهيز طلبك يا {name}.. جاري فتح واتساب...")
            
            # 4. السحر البرمجي (فتح الواتساب تلقائياً في صفحة جديدة)
            js = f"window.open('{wa_url}')"
            st.markdown(f'<img src="x" onerror="{js}" style="display:none;">', unsafe_allow_html=True)
            
        else:
            st.warning("الرجاء تعبئة الاسم ورقم الجوال أولاً.")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
