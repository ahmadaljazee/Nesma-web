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

# محاولة تحميل خلفية bg.png
bg_base64 = get_base64_of_bin_file('bg.png')

# --- 2. التنسيق البصري الاحترافي (CSS) ---
st.markdown(f"""
    <style>
    /* أ. إخفاء شريط Streamlit العلوي والقائمة الجانبية تماماً لإعطاء مظهر تطبيق خاص */
    header {{visibility: hidden !important;}}
    #MainMenu {{visibility: hidden !important;}}
    footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none !important;}}
    
    /* ب. ضبط خلفية الصفحة بالكامل باستخدام bg.png */
    .stApp {{
        /* تراكب لوني خفيف جداً (White Linear Gradient) فوق الصورة لزيادة وضوح النصوص */
        background-image: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)), 
                          url("data:image/png;base64,{bg_base64}");
        background-size: cover; /* جعل الصورة تغطي كامل الشاشة */
        background-position: center; /* توسيط الصورة */
        background-attachment: fixed; /* منع الصورة من التحرك عند التمرير */
    }}
    
    /* ج. تنسيق النصوص لتكون غامقة جداً وواضحة فوق الخلفية */
    label, p, span, h1, h2, h3 {{
        color: #0a3d0d !important; /* أخضر غامق جداً قريب للأسود */
        font-weight: 800 !important; /* عريض جداً */
        text-shadow: 1px 1px 3px rgba(255,255,255,0.7); /* ظل أبيض خفيف حول النص للتباين */
    }}

    /* د. تحسين شكل حقول الإدخال */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.95) !important; /* بيضاء تقريباً وغير شفافة */
        border: 2px solid #2e7d32 !important; /* حدود خضراء واضحة */
        border-radius: 12px !important;
        color: black !important;
        font-weight: 600 !important;
    }}

    /* هـ. كود توسيط الزر تماماً وتنسيقه */
    .stButton {{
        display: flex;
        justify-content: center; /* توسيط أفقي للحاوية */
        width: 100%;
    }}

    div.stButton > button {{
        background-color: #00c853 !important; /* أخضر زاهي (نسمة) */
        color: white !important;
        border-radius: 30px !important;
        font-weight: bold;
        height: 55px;
        width: 100%;
        max-width: 400px; /* تحديد عرض أقصى للزر ليبقى أنيقاً على الشاشات الكبيرة */
        border: none !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2); /* ظل ناعم */
        font-size: 20px !important;
        transition: 0.3s ease; /* حركة ناعمة عند التأشير */
    }}
    
    div.stButton > button:hover {{
        background-color: #00e676 !important; /* لون أفتح قليلاً عند التأشير */
        transform: scale(1.02); /* تكبير بسيط */
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. واجهة التطبيق ---

# أ. عرض اللوجو الرئيسي موسطاً
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", use_container_width=True)

# ب. العناوين والنصوص الثابتة
st.markdown("<h1 style='text-align: center;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.3rem;'>رعــــاية..جـــودة..أمـــان</p>", unsafe_allow_html=True)

# ج. حاوية نموذج الحجز
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
    
    # د. معالجة زر الحجز (الذي تم توسيعه وتوسيطه عبر الـ CSS)
    if st.button("تأكيد الحجز وإرسال عبر واتساب"):
        if name and phone:
            # تجهيز نص الرسالة
            raw_msg = (
                f"طلب حجز جديد من تطبيق نسمة 🌬️\n"
                f"--------------------------\n"
                f"👤 الاسم: {name}\n"
                f"📞 الهاتف: {phone}\n"
                f"🧹 العاملة: {cleaner}\n"
                f"📅 الموعد: {date} الساعة {time}\n"
                f"--------------------------"
            )
            # ترميز الرسالة لتناسب الروابط
            encoded_msg = urllib.parse.quote(raw_msg)
            # رابط الواتساب المباشر (تأكد من الرقم)
            whatsapp_link = f"https://wa.me/962777278329?text={encoded_msg}"
            
            # فتح الرابط في نافذة جديدة باستخدام JavaScript
            st.components.v1.html(f"<script>window.open('{whatsapp_link}', '_blank');</script>", height=0)
            st.success("جاري تحويلك إلى واتساب لتأكيد طلبك...")
        else:
            st.error("يرجى إدخال الاسم ورقم الهاتف للمتابعة.")

# هـ. التذييل (Footer)
st.markdown("<p style='text-align: center; font-size: 12px; color: #000; margin-top: 50px; font-weight: bold;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
