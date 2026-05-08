import streamlit as st
import datetime
import urllib.parse
import base64
import os

# --- إعدادات الصفحة (تم تعيين أيقونة مؤقتة) ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="🌬️", # إيموجي يرمز للنظافة والراحة
    layout="centered"
)

# دالة آمنة لتحويل الصورة لترميز CSS (لا تعطل التطبيق في حال غياب الملف)
def get_base64(bin_file):
    # التحقق أولاً من وجود الملف في المسار المحدد
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            # تحويل البيانات لترميز base64 لتضمينها في CSS
            return base64.b64encode(data).decode()
        except Exception as e:
            # في حال وجود خطأ غير متوقع، لا نعطل التطبيق
            return ""
    # إذا لم يكن الملف موجوداً، نرجع نصاً فارغاً
    return ""

# محاولة تحويل الصورة لاستخدامها كخلفية (يجب أن يكون الملف اسمه nesma.png)
bin_str = get_base64('nesma.png')

# التحقق من وجود الصورة لعرض تحذير أصفر في حال غيابها
if not bin_str:
    st.warning("⚠️ لم يتم العثور على ملف 'nesma.png' في المجلد الرئيسي على GitHub. ستظهر واجهة بسيطة وواضحة.")

# --- التنسيق البصري (الكود الأساسي المطور) ---
# قمنا بجعل الخلفية تتكيف مع وجود الصورة أو غيابها
st.markdown(f"""
    <style>
    .stApp {{
        /* إذا وجدت الخلفية، سيتم تفعيلها مع التدرج اللوني، وإلا سنستخدم تدرجاً لونياً هادئاً كبديل */
        {f'background-image: linear-gradient(rgba(253, 252, 240, 0.92), rgba(232, 245, 233, 0.92)), url("data:image/png;base64,{bin_str}");' if bin_str else 'background-image: linear-gradient(135deg, #fdfcf0 0%, #e8f5e9 100%);'}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* تنسيق حقول الإدخال لتكون واضحة */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 12px !important;
        color: #2e4d3b !important;
    }}

    .static-about-box {{
        background-color: rgba(255, 255, 255, 0.8);
        border: 1px solid #a5d6a7;
        border-radius: 15px;
        padding: 20px;
        text-align: right;
        direction: rtl;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }}

    /* تنسيق زر الحجز */
    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold;
        height: 55px;
        width: 100%;
        border: none !important;
        box-shadow: 0 4px 12px rgba(0,200,83,0.3) !important;
    }}
    
    .main-header {{
        text-align: center;
        color: #1b5e20;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- واجهة المستخدم ---

# عرض الشعار موسطاً في الأعلى إذا تم العثور عليه
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    if bin_str:
        st.image("nesma.png", use_container_width=True)

st.markdown("<h1 class='main-header'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #558b2f; font-weight: 500;'>نظافة.. راحة.. بلمسة ذكية</p>", unsafe_allow_html=True)

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
    
    # توسيط الزر
    left, center, right = st.columns([1, 2, 1])
    with center:
        if st.button("تأكيد البيانات وإرسال الحجز"):
            if name and phone:
                raw_msg = f"طلب حجز جديد من نسمة 🌬️\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 المختصة: {cleaner}\n📅 الموعد: {date} الساعة {time}"
                encoded_msg = urllib.parse.quote(raw_msg)
                # استبدل الرقم برقم الواتساب الخاص بك
                whatsapp_link = f"https://wa.me/962777278329?text={encoded_msg}"
                st.components.v1.html(f"<script>window.location.href = '{whatsapp_link}';</script>", height=0)
            else:
                st.warning("يرجى إدخال البيانات المطلوبة.")

st.markdown("<p style='text-align: center; font-size: 11px; color: #999; margin-top: 60px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
