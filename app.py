import streamlit as st
import datetime
import os
import sys
import subprocess

# --- إعدادات الصفحة والهوية البصرية ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="🌬️",
    layout="centered"
)

# --- تطبيق النسق الداكن والألوان (الأسود والأخضر #8ff48f) ---
st.markdown(f"""
    <style>
    /* خلفية التطبيق */
    .stApp {{
        background-color: #121212;
        color: #ffffff;
    }}
    /* تنسيق الحقول */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: #1e1e1e !important;
        color: white !important;
        border: 1px solid #8ff48f !important;
        border-radius: 10px;
    }}
    /* تنسيق الزر الأخضر الرئيسي */
    .stButton>button {{
        background-color: #8ff48f !important;
        color: #000000 !important;
        border-radius: 25px !important;
        border: none !important;
        width: 100%;
        font-weight: bold;
        height: 50px;
        font-size: 18px;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #76e076 !important;
        box-shadow: 0 4px 15px rgba(143, 244, 143, 0.4);
    }}
    /* البايو والوصف */
    .bio-text {{
        text-align: center;
        color: #aaaaaa;
        font-size: 14px;
        margin-bottom: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- محتوى الواجهة (النبذة والشعار) ---
st.markdown("<h1 style='text-align: center; color: #8ff48f;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("""
    <div class="bio-text">
        نسمة.. نظافة.. راحة.. بلمسة ذكية. <br>
        تجربتك المتكاملة تبدأ بضغطة زر وتنتهي ببيئة منزلية منعشة.
    </div>
    """, unsafe_allow_html=True)

# --- نموذج الحجز (الخطوات اللوجستية) ---
with st.container():
    name = st.text_input("👤 الاسم الكامل", placeholder="أدخل اسمك هنا")
    phone = st.text_input("📞 رقم الجوال", placeholder="07XXXXXXXX")
    
    st.markdown("<hr style='border: 0.5px solid #333'>", unsafe_allow_html=True)
    
    st.subheader("اختر النسمة المختصة")
    cleaner = st.selectbox(
        "العاملات المتاحات في منطقتك:",
        ["سناء م. ⭐ 4.9 (خبيرة ترتيب)", "أمل ع. ⭐ 4.7 (سريعة الإنجاز)", "ريم س. ⭐ 4.8 (دقة عالية)"]
    )

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col2:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("تأكيد حجز نسمة"):
        if name and phone:
            st.success(f"تم استلام طلبك يا {name}! جاري تحويلك لتأكيد الحجز مع الإدارة...")
            
            message = f"طلب حجز جديد من موقع نسمة\nالاسم: {name}\nالجوال: {phone}\nالعاملة: {cleaner}\nالموعد: {date} الساعة {time}"
            admin_phone = "9627XXXXXXXX" # ضع رقمك هنا
            whatsapp_url = f"https://wa.me/{admin_phone}?text={message.replace(' ', '%20')}"
            
            st.markdown(f'<meta http-equiv="refresh" content="2;url={whatsapp_url}">', unsafe_allow_html=True)
        else:
            st.warning("الرجاء إدخال الاسم ورقم الجوال لإتمام الحجز.")

# --- تذييل الصفحة ---
st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top: 50px;'>Nesmajo © 2026 | Powered by Nesma-Logistics</p>", unsafe_allow_html=True)

# --- الجزء الخاص بتشغيل التطبيق على Vercel (بدون تكرار) ---
def app(environ, start_response):
    # تشغيل ستريمليت كعملية فرعية مرة واحدة فقط
    subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8080",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])
    
    # إرسال استجابة لـ Vercel لمنع الخطأ 500
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    return [b"Loading Nesma App... Please refresh this page in 10 seconds."]
