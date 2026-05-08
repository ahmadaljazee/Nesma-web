import streamlit as st
import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="🌬️",
    layout="centered"
)

# --- التنسيق البصري (نسق نسمة الطبيعي) ---
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #fdfcf0 0%, #e8f5e9 100%);
        color: #2e4d3b;
    }}
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: #ffffff !important;
        color: #2e4d3b !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 10px;
    }}
    .stButton>button {{
        background-color: #8bc34a !important;
        color: #ffffff !important;
        border-radius: 25px !important;
        font-weight: bold;
        height: 50px;
        width: 100%;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .bio-text {{
        text-align: center;
        color: #558b2f;
        font-size: 14px;
        margin-bottom: 20px;
    }}
    /* تنسيق صندوق النبذة الظاهر */
    .about-box {{
        background-color: rgba(255, 255, 255, 0.5);
        border: 1px dashed #a5d6a7;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
        text-align: right;
        direction: rtl;
        line-height: 1.6;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #2e7d32;'>نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown('<div class="bio-text">نسمة.. نظافة.. راحة.. بلمسة ذكية.</div>', unsafe_allow_html=True)

# --- قسم نبذة عنا (ظاهر بشكل دائم) ---
st.markdown("""
<div class="about-box">
    <strong>✨ لماذا تختارين نسمة؟</strong><br>
    نحن في <b>نسمة</b> نؤمن أن البيت النظيف هو بداية يوم سعيد. 
    نسعى لإعادة تعريف الراحة المنزلية من خلال نخبة من العاملات المختصات لضمان منزل يفوح بالنظافة والترتيب بلمسة عصرية تضمن لكِ الراحة والخصوصية.
    <br><br>
    • <b>دقة في المواعيد</b> واحترافية عالية.<br>
    • <b>عاملات مدربات</b> وصاحبات خبرة.<br>
    • <b>نظام حجز ذكي</b> وسلس عبر الواتساب.
</div>
""", unsafe_allow_html=True)

# --- نموذج الحجز ---
with st.container():
    name = st.text_input("👤 الاسم الكامل", placeholder="أدخل اسمك هنا")
    phone = st.text_input("📞 رقم الجوال", placeholder="07XXXXXXXX")
    
    cleaner = st.selectbox(
        "اختر العاملة المختصة:",
        ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"]
    )

    col_date, col_time = st.columns(2)
    with col_date:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_time:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- توسيط زر الحجز ---
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        submit_button = st.button("تأكيد البيانات وإرسال الحجز")
        
    if submit_button:
        if name and phone:
            raw_message = f"طلب حجز جديد من موقع نسمة\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 العاملة: {cleaner}\n📅 الموعد: {date} الساعة {time}"
            encoded_message = urllib.parse.quote(raw_message)
            admin_phone = "962777278329"
            whatsapp_url = f"https://wa.me/{admin_phone}?text={encoded_message}"
            
            js_code = f"<script>window.location.href = '{whatsapp_url}';</script>"
            st.components.v1.html(js_code, height=0)
            st.info("جاري التحويل إلى واتساب لتأكيد حجزك...")
        else:
            st.warning("الرجاء إدخال الاسم ورقم الجوال أولاً.")

st.markdown("<p style='text-align: center; font-size: 10px; color: #999; margin-top: 50px;'>Nesmajo © 2026</p>", unsafe_allow_html=True)
