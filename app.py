import streamlit as st
import datetime
import urllib.parse
import base64
import os

# --- 1. إعدادات الصفحة والأيقونة (لتظهر في المتصفح) ---
# يجب أن يكون لديك ملف اسمه logo.png في نفس المجلد
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="logo.png", 
    layout="centered"
)

# دالة مساعدة لتحويل ملف الصورة إلى ترميز Base64 لاستخدامه في الـ CSS
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        try:
            with open(bin_file, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except:
            return "" # في حال حدث خطأ لا يتوقف التطبيق
    return ""

# محاولة تحميل خلفية bg.png وصورة اللوجو للاستخدام في النبذة
bg_base64 = get_base64_of_bin_file('bg.png')

# --- 2. التنسيق البصري الاحترافي (CSS) - تم إضافة تنسيقات جديدة للنبذة والمميزات ---
st.markdown(f"""
    <style>
    /* أ. إخفاء شريط Streamlit العلوي والقائمة الجانبية تماماً */
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* ب. ضبط خلفية الصفحة بالكامل باستخدام bg.png */
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)), 
                          url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* ج. تنسيق النصوص الأساسية */
    label, p, span, h1, h2, h3 {{
        color: #0a3d0d !important; 
        font-weight: 800 !important;
        text-shadow: 1px 1px 3px rgba(255,255,255,0.7);
    }}

    /* د. تحسين شكل حقول الإدخال */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 12px !important;
        color: black !important;
        font-weight: 600 !important;
    }}

    /* هـ. كود توسيط وتنسيق زر الحجز تماماً */
    .stButton {
        display: flex !important;
        justify-content: center !important; /* هذا السطر هو المسؤول عن التوسيط الأفقي */
        width: 100% !important;
        margin-top: 20px;
    }

    div.stButton > button {
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold;
        height: 55px;
        width: 100% !important;
        max-width: 400px; /* يحافظ على حجم متناسق للزر في المنتصف */
        border: none !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        font-size: 20px !important;
        transition: 0.3s ease;
    }

    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold;
        height: 55px;
        width: 100%;
        max-width: 400px;
        border: none !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        font-size: 20px !important;
        transition: 0.3s ease;
    }}
    
    div.stButton > button:hover {{
        background-color: #00e676 !important;
        transform: scale(1.02);
    }}

    /* و. [جديد] تنسيق حاوية النبذة التعريفية */
    .about-section {{
        background-color: rgba(255, 255, 255, 0.7); /* خلفية بيضاء شفافة */
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #a5d6a7; /* حدود خضراء فاتحة جداً */
        margin-bottom: 25px;
        text-align: right;
        direction: rtl; /* اتجاه النص من اليمين لليسار */
    }}
    .about-title {{
        color: #1b5e20;
        font-size: 1.5rem;
        margin-bottom: 10px;
        border-bottom: 2px solid #00c853; /* خط تحت العنوان */
        display: inline-block;
        padding-bottom: 5px;
    }}
    .about-text {{
        color: #0a3d0d;
        font-size: 1.1rem;
        line-height: 1.7;
        font-weight: 500 !important;
    }}

    /* ز. [جديد] تنسيق حاوية المميزات سريعاً */
    .features-section {{
        text-align: right;
        direction: rtl;
        margin-top: 15px;
        margin-bottom: 15px;
    }}
    .feature-item {{
        font-size: 1.1rem;
        color: #0a3d0d;
        font-weight: 700 !important;
    }}
    .feature-icon {{
        color: #00c853; /* لون الإيقونة (أخضر نسمة) */
        margin-left: 10px;
        font-size: 1.2rem;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. واجهة التطبيق ---

# أ. عرض اللوجو الرئيسي موسطاً (logo.png)
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", use_container_width=True)

# ب. العناوين والنصوص الثابتة (الـ Bio المقترح)
st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem; margin-bottom: 25px;'>رعــــاية..جـــودة..أمـــان</p>", unsafe_allow_html=True)

# [جديد] ج. إضافة النبذة التعريفية المطولة
st.markdown(f"""
    <div class='about-section'>
        <div class='about-title'>لماذا نسمة؟</div>
        <p class='about-text'>
            في "نسمة"، نؤمن أن نظافة منزلك هي نسمة هدوء ليومك. 
            نوفر لكِ نخبة من العاملات المختصات والمدربات، لضمان أعلى معايير الترتيب والتعقيم، بخصوصية تامة واحترافية تليق بكِ. 
            اختاري المختصة المفضلة لديكِ، وحددي موعدك بلمسة زر، ودعي الباقي علينا لتستمتعي براحة البال التي تستحقينها.
        </p>
    </div>
    """, unsafe_allow_html=True)

# [جديد] د. إضافة قائمة المميزات سريعاً
st.markdown(f"""
    <div class='features-section'>
        <p class='feature-item'><span class='feature-icon'>✨</span>عاملات مختصات (⭐ 4.9)</p>
        <p class='feature-item'><span class='feature-icon'>🕒</span>حجز سريع وسهل عبر واتساب</p>
        <p class='feature-item'><span class='feature-icon'>🔒</span>خصوصية تامة وأمان مضمون</p>
        <p class='feature-item'><span class='feature-icon'>💧</span>جودة وتعقيم بلمسة ذكية</p>
    </div>
    <div style='text-align: center; color: #0a3d0d; font-weight: 700; font-size: 1rem; margin-top: 10px;'>نسمة.. منزلك مشرق دائماً.</div>
    """, unsafe_allow_html=True)


# هـ. حاوية نموذج الحجز
with st.container():
    st.markdown("---") # خط فاصل
    name = st.text_input("👤 الاسم الكامل")
    phone = st.text_input("📞 رقم الجوال")
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", [
        "سناء م. ⭐ 4.9", 
        "أمل ع. ⭐ 4.7", 
        "ريم س. ⭐ 4.8"
    ])

    # تقسيم التاريخ والوقت على عمودين
    col_d, col_t = st.columns(2)
    with col_d:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_t:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True) # مسافة
    
    # و. معالجة زر الحجز
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
            st.success("جاري تحويلك إلى واتساب...")
        else:
            st.error("يرجى إدخال الاسم ورقم الهاتف.")

# ز. التذييل (Footer)
st.markdown("<p style='text-align: center; font-size: 12px; color: #000; margin-top: 50px; font-weight: bold;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
