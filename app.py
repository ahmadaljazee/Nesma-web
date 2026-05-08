import streamlit as st
import datetime
import urllib.parse
import base64
import os

# --- 1. إعدادات الصفحة والأيقونة ---
# تم استخدام logo.png كأيقونة للموقع في المتصفح
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="logo.png", 
    layout="centered"
)

# دالة لتحويل الصور إلى ترميز Base64 لاستخدامها في الخلفية
def get_base64(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except:
            return ""
    return ""

# تحميل صورة الخلفية bg.png وصورة اللوجو logo.png
bg_base64 = get_base64('bg.png')
logo_base64 = get_base64('logo.png')

# --- 2. التنسيق البصري (CSS) ---
# تم تعديل الألوان لتكون داكنة وواضحة وإخفاء الأشرطة العلوية
st.markdown(f"""
    <style>
    /* إخفاء شريط Streamlit الأسود والقوائم تماماً */
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* تثبيت صورة bg.png كخلفية كاملة للصفحة */
    .stApp {{
        background-image: linear-gradient(rgba(253, 252, 240, 0.95), rgba(232, 245, 233, 0.95)), url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* تعديل ألوان الخطوط لتناسب الخلفية الفاتحة */
    label, p, span, h1, h2, h3 {{
        color: #1b5e20 !important; 
        font-weight: 700 !important;
    }}

    /* تحسين شكل صناديق الإدخال وجعل النص بداخلها أسود */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: white !important;
        border: 2px solid #a5d6a7 !important;
        border-radius: 10px !important;
        color: black !important;
    }}

    /* تصميم زر الحجز الأخضر */
    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 25px !important;
        font-weight: bold;
        height: 50px;
        width: 100%;
        border: none !important;
        font-size: 18px !important;
        box-shadow: 0 4px 10px rgba(0,200,83,0.3);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. واجهة المستخدم ---

# عرض logo.png في أعلى الصفحة بشكل موسط
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", use_container_width=True)

st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>نظافة.. راحة.. بلمسة ذكية</p>", unsafe_allow_html=True)

# حاوية نموذج الطلب
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
    
    # زر إرسال الطلب عبر واتساب
    if st.button("تأكيد الحجز وإرسال عبر واتساب"):
        if name and phone:
            msg = f"طلب حجز جديد من نسمة 🌬️\nالاسم: {name}\nالجوال: {phone}\nالعاملة: {cleaner}\nالموعد: {date} الساعة {time}"
            encoded_msg = urllib.parse.quote(msg)
            # تم تعيين رقم الواتساب الخاص بك
            whatsapp_url = f"https://wa.me/962777278329?text={encoded_msg}"
            
            # فتح الرابط في نافذة جديدة
            st.components.v1.html(f"<script>window.open('{whatsapp_url}', '_blank');</script>", height=0)
            st.success("يتم الآن توجيهك إلى واتساب لتأكيد طلبك...")
        else:
            st.error("يرجى تعبئة الاسم ورقم الهاتف لإتمام الحجز.")

st.markdown("<p style='text-align: center; font-size: 10px; color: #666; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
