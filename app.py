import streamlit as st
import datetime
import urllib.parse

# --- إعدادات الصفحة والهوية البصرية ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="🌬️",
    layout="centered"
)

# --- تطبيق النسق الداكن والألوان ---
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
    /* تنسيق الزر الرئيسي */
    .stButton>button {{
        background-color: #8ff48f !important;
        color: #000000 !important;
        border-radius: 25px !important;
        width: 100%;
        font-weight: bold;
        height: 50px;
    }}
    /* تنسيق رابط الواتساب ليظهر كأنه زر أخضر مميز */
    .whatsapp-button {{
        display: inline-block;
        padding: 15px 25px;
        background-color: #25D366;
        color: white !important;
        text-decoration: none;
        border-radius: 25px;
        font-weight: bold;
        text-align: center;
        width: 100%;
        font-size: 18px;
        margin-top: 10px;
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
    
    st.subheader("اختر النسمة المختصة")
    cleaner = st.selectbox(
        "العاملات المتاحات في منطقتك:",
        ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"]
    )

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col2:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("تأكيد البيانات"):
        if name and phone:
            # تجهيز الرسالة
            raw_message = f"طلب حجز جديد من موقع نسمة\nالاسم: {name}\nالجوال: {phone}\nالعاملة: {cleaner}\nالموعد: {date} الساعة {time}"
            
            # تشفير الرسالة لتعمل بشكل صحيح في الروابط (عشان المسافات واللغة العربية)
            encoded_message = urllib.parse.quote(raw_message)
            
            admin_phone = "962777278329"
            whatsapp_url = f"https://wa.me/{admin_phone}?text={encoded_message}"
            
            st.success(f"تم تجهيز طلبك يا {name}!")
            
            # إظهار زر "الانتقال للواتساب" بشكل واضح
            # هذا الزر لا يمكن للمتصفح حظره لأنه رابط مباشر
            st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-button">اضغط هنا لإرسال الحجز عبر واتساب 💬</a>', unsafe_allow_html=True)
        else:
            st.warning("الرجاء إدخال الاسم ورقم الجوال لإتمام الحجز.")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
