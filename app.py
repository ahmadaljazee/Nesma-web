import streamlit as st
import datetime
import urllib.parse
import base64
import os

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="logo.png",  # هذا الأمر يضع شعارك مكان أيقونة المتصفح
    layout="centered"
)

# دالة لتحميل الصورة الخلفية إذا وجدت
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except:
            return ""
    return ""

bin_str = get_base64('nesma.png')

# --- التنسيق البصري (CSS) لإخفاء الأشرطة وتعديل الألوان ---
st.markdown(f"""
    <style>
    /* إخفاء الشريط العلوي والقوائم تماماً */
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* إعدادات الخلفية */
    .stApp {{
        {f'background-image: linear-gradient(rgba(253, 252, 240, 0.95), rgba(232, 245, 233, 0.95)), url("data:image/png;base64,{bin_str}");' if bin_str else 'background-color: #fdfcf0;'}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* جعل الخطوط داكنة وواضحة جداً */
    label, p, span, h1, h2, h3 {{
        color: #1b5e20 !important; /* أخضر غامق جداً */
        font-weight: 700 !important;
    }}

    /* تحسين شكل صناديق الإدخال */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: white !important;
        border: 2px solid #a5d6a7 !important;
        border-radius: 10px !important;
        color: black !important;
    }}

    /* تصميم زر الحجز */
    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 25px !important;
        font-weight: bold;
        height: 50px;
        width: 100%;
        border: none !important;
        font-size: 18px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- محتوى التطبيق ---

# عرض الشعار موسطاً إذا كان الملف موجوداً
if bin_str:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("nesma.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>نظافة.. راحة.. بلمسة ذكية</p>", unsafe_allow_html=True)

# نموذج الطلب
with st.container():
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    cleaner = st.selectbox("🧹 اختر العاملة:", ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"])

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 التاريخ", min_value=datetime.date.today())
    with col2:
        time = st.time_input("⏰ الوقت")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("تأكيد الحجز عبر واتساب"):
        if name and phone:
            # تجهيز رسالة الواتساب
            msg = f"طلب حجز جديد من نسمة 🌬️\nالاسم: {name}\nالهاتف: {phone}\nالعاملة: {cleaner}\nالموعد: {date} {time}"
            encoded_msg = urllib.parse.quote(msg)
            whatsapp_url = f"https://wa.me/962777278329?text={encoded_msg}"
            
            # فتح الرابط
            st.components.v1.html(f"<script>window.open('{whatsapp_url}', '_blank');</script>", height=0)
            st.success("يتم الآن توجيهك إلى واتساب...")
        else:
            st.error("يرجى تعبئة كافة الحقول")

st.markdown("<p style='text-align: center; font-size: 10px; color: #666; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
