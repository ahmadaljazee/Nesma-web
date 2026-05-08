import streamlit as st
import datetime
import urllib.parse
import base64
import os

# --- 1. إعدادات الصفحة والأيقونة (المتصفح) ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="logo.png", 
    layout="centered"
)

# دالة لتحويل ملفات الصور لترميز Base64 لاستخدامها في الخلفية
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

# تحميل الخلفية
bg_base64 = get_base64_of_bin_file('bg.png')

# --- 2. التنسيق البصري الاحترافي (CSS) ---
st.markdown(f"""
    <style>
    /* إخفاء شريط الأدوات العلوي والقائمة الجانبية تماماً */
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* ضبط الخلفية (bg.png) مع شفافية منخفضة لتكون واضحة جداً */
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.3)), url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* تنسيق النصوص لتكون غامقة وواضحة فوق الخلفية */
    label, p, span, h1, h2, h3 {{
        color: #0a3d0d !important; 
        font-weight: 800 !important;
        text-shadow: 1px 1px 3px rgba(255,255,255,0.7);
    }}

    /* تحسين شكل حقول الإدخال */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 12px !important;
        color: black !important;
        font-weight: 600 !important;
    }}

    /* --- كود توسيط الزر تماماً --- */
    .stButton {{
        display: flex;
        justify-content: center;
    }}

    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold;
        height: 55px;
        width: 100%;
        max-width: 400px; /* تحديد عرض أقصى للزر ليبقى متناسقاً */
        border: none !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        font-size: 20px !important;
        transition: 0.3s;
    }}
    
    div.stButton > button:hover {{
        background-color: #00e676 !important;
        transform: scale(1.02);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. واجهة التطبيق ---

# عرض اللوجو الرئيسي (logo.png) موسطاً
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem;'>رعــــاية..جـــودة..أمـــان</p>", unsafe_allow_html=True)

# نموذج الحجز
with st.container():
    st.markdown("---")
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", [
        "سناء م. ⭐ 4.9", 
        "أمل ع. ⭐ 4.7", 
        "ريم س. ⭐ 4.8"
    ])

    col_d, col_t = st.columns(2)
    with col_d:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_t:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # الزر الآن سيظهر في المنتصف تلقائياً بسبب تنسيق CSS المضاف
    if st.button("تأكيد الحجز وإرسال عبر واتساب"):
        if name and phone:
            raw_msg = (
                f"طلب حجز جديد من تطبيق نسمة 🌬️\n"
                f"--------------------------\n"
                f"👤 الاسم: {name}\n"
                f"📞 الهاتف: {phone}\n"
                f"🧹 العاملة: {cleaner}\n"
                f"📅 الموعد: {date} الساعة {time}\n"
                f"--------------------------"
            )
            encoded_msg = urllib.parse.quote(raw_msg)
            whatsapp_link = f"https://wa.me/962777278329?text={encoded_msg}"
            
            st.components.v1.html(f"<script>window.open('{whatsapp_link}', '_blank');</script>", height=0)
            st.success("جاري تحويلك إلى واتساب لتأكيد طلبك...")
        else:
            st.error("يرجى إدخال الاسم ورقم الهاتف للمتابعة.")

# التذييل
st.markdown("<p style='text-align: center; font-size: 12px; color: #000; margin-top: 50px; font-weight: bold;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
