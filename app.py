import streamlit as st
import datetime
import urllib.parse
import base64
import os

# --- 1. إعدادات الصفحة والأيقونة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="logo.png", 
    layout="centered"
)

# دالة لتحويل صورة bg.png إلى ترميز Base64 لاستخدامها كخلفية ثابتة
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# استدعاء الخلفية
bin_str = get_base64_of_bin_file('bg.png')

# --- 2. التنسيق البصري (CSS) ---
st.markdown(f"""
    <style>
    /* إخفاء العناصر الافتراضية المزعجة */
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* جعل ملف bg.png هو خلفية الصفحة بالكامل */
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* توضيح الخطوط وتغميقها لتتناسب مع الخلفية */
    label, p, span, h1, h2, h3 {{
        color: #1b5e20 !important; 
        font-weight: 700 !important;
    }}

    /* تصميم صناديق الإدخال */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #a5d6a7 !important;
        border-radius: 12px !important;
        color: black !important;
    }}

    /* زر الحجز */
    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold;
        height: 55px;
        width: 100%;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,200,83,0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. واجهة المستخدم ---

# عرض اللوجو موسطاً
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>نظافة.. راحة.. بلمسة ذكية</p>", unsafe_allow_html=True)

# نموذج الطلب
with st.container():
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"])

    c1, c2 = st.columns(2)
    with c1:
        date = st.date_input("📅 التاريخ", min_value=datetime.date.today())
    with c2:
        time = st.time_input("⏰ الوقت")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("تأكيد الحجز عبر واتساب"):
        if name and phone:
            msg = f"طلب حجز جديد من نسمة 🌬️\nالاسم: {name}\nالجوال: {phone}\nالعاملة: {cleaner}\nالموعد: {date} الساعة {time}"
            encoded_msg = urllib.parse.quote(msg)
            whatsapp_url = f"https://wa.me/962777278329?text={encoded_msg}"
            
            # فتح الواتساب
            st.components.v1.html(f"<script>window.open('{whatsapp_url}', '_blank');</script>", height=0)
            st.success("يتم توجيهك الآن إلى واتساب...")
        else:
            st.error("يرجى تعبئة الحقول المطلوبة.")

st.markdown("<p style='text-align: center; font-size: 10px; color: #444; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
