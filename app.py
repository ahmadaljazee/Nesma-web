import streamlit as st
import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="🌬️",
    layout="centered"
)

# --- التنسيق البصري (الهوية البصرية لنسمة 2026) ---
st.markdown("""
    <style>
    /* خلفية متدرجة منعشة تليق بروح نسمة */
    .stApp {
        background: linear-gradient(135deg, #fdfcf0 0%, #e8f5e9 100%) !important;
        color: #2e4d3b !important;
    }
    
    /* تنسيق حقول الإدخال */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #ffffff !important;
        color: #2e4d3b !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 10px !important;
    }

    /* صندوق النبذة الظاهر دائماً */
    .static-about-box {
        background-color: rgba(255, 255, 255, 0.6);
        border: 1px solid #a5d6a7;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 30px;
        text-align: right;
        direction: rtl;
        line-height: 1.8;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }

    /* تنسيق زر الحجز الأخضر */
    div.stButton > button {
        background-color: #8bc34a !important;
        color: white !important;
        border-radius: 25px !important;
        font-weight: bold;
        height: 55px;
        width: 100%;
        border: none !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    
    div.stButton > button:hover {
        background-color: #7cb342 !important;
        transform: translateY(-2px);
    }

    .main-header {
        text-align: center;
        color: #2e7d32;
        font-weight: bold;
    }
    
    .tagline {
        text-align: center;
        color: #558b2f;
        font-size: 15px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- واجهة المستخدم ---
st.markdown("<h1 class='main-header'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>نظافة.. راحة.. بلمسة ذكية</p>", unsafe_allow_html=True)

# --- قسم النبذة الظاهرة (بدون كبس زر) ---
st.markdown("""
<div class="static-about-box">
    <strong>✨ لماذا نسمة؟</strong><br>
    في <b>نسمة</b>، نؤمن أن نظافة منزلك هي نسمة هدوء ليومك. نوفر لكِ نخبة من العاملات المختصات لضمان أعلى معايير الترتيب والتعقيم بخصوصية تامة.
    <br><br>
    ✅ <b>دقة واحترافية:</b> نلتزم بأعلى معايير الجودة.<br>
    ✅ <b>ثقة وأمان:</b> كادرنا مدرب وموثوق لراحتك.<br>
    ✅ <b>سهولة ذكية:</b> حجز سريع ومباشر عبر الواتساب.
</div>
""", unsafe_allow_html=True)

# --- نموذج الحجز ---
with st.container():
    name = st.text_input("👤 الاسم الكامل", placeholder="أدخل اسمك الكريم")
    phone = st.text_input("📞 رقم الجوال", placeholder="07XXXXXXXX")
    
    cleaner = st.selectbox(
        "🧹 اختر العاملة المختصة:",
        ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"]
    )

    col_date, col_time = st.columns(2)
    with col_date:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_time:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- توسيط زر الحجز تماماً ---
    left_side, center_btn, right_side = st.columns([1, 2, 1])
    
    with center_btn:
        if st.button("تأكيد البيانات وإرسال الحجز"):
            if name and phone:
                raw_msg = f"طلب حجز جديد من نسمة 🌬️\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 المختصة: {cleaner}\n📅 الموعد: {date} الساعة {time}"
                encoded_msg = urllib.parse.quote(raw_msg)
                admin_no = "962777278329"
                whatsapp_link = f"https://wa.me/{admin_no}?text={encoded_msg}"
                
                js = f"<script>window.location.href = '{whatsapp_link}';</script>"
                st.components.v1.html(js, height=0)
                st.info("جاري التحويل إلى واتساب...")
            else:
                st.warning("يرجى إدخال الاسم ورقم الهاتف للمتابعة.")

st.markdown("<p style='text-align: center; font-size: 11px; color: #999; margin-top: 60px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
