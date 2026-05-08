import streamlit as st
import datetime
import urllib.parse

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="نسمة | Nesma",
    page_icon="🌬️",
    layout="centered"
)

# --- التنسيق البصري المستوحى من روح "نسمة" الطبيعية ---
st.markdown(f"""
    <style>
    /* تدرج خلفية هادئ يحاكي ألوان الطبيعة والنسمة */
    .stApp {{
        background: linear-gradient(135deg, #fdfcf0 0%, #e8f5e9 50%, #f1f8e9 100%);
        color: #2e4d3b;
    }}
    
    /* تنسيق المدخلات - ألوان زيتونية فاتحة */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{
        background-color: rgba(255, 255, 255, 0.7) !important;
        color: #2e4d3b !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 12px !important;
    }}
    
    /* تنسيق الزر - أخضر ربيعي حيوي */
    .stButton>button {{
        background-color: #8bc34a !important;
        color: white !important;
        border-radius: 30px !important;
        width: 100%;
        font-weight: bold;
        height: 55px;
        border: none !important;
        box-shadow: 0 4px 15px rgba(139, 195, 74, 0.3);
        transition: 0.3s;
    }}
    
    .stButton>button:hover {{
        background-color: #7cb342 !important;
        transform: translateY(-2px);
    }}

    .bio-text {{
        text-align: center;
        color: #558b2f;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 25px;
    }}

    /* تنسيق قسم "تعرف على نسمة" */
    .stExpander {{
        background-color: rgba(255, 255, 255, 0.5) !important;
        border: 1px solid #c5e1a5 !important;
        border-radius: 15px !important;
    }}
    
    .about-section {{
        text-align: right;
        line-height: 1.8;
        direction: rtl;
        color: #33691e;
        padding: 10px;
    }}
    
    h1 {{
        font-family: 'Arial', sans-serif;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }}
    </style>
    """, unsafe_allow_html=True)

# --- العنوان ---
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🍃 نسمة | Nesma</h1>", unsafe_allow_html=True)
st.markdown('<div class="bio-text">نظافة.. راحة.. بلمسة طبيعية ذكية</div>', unsafe_allow_html=True)

# --- قسم نبذة عنا ---
with st.expander("✨ لماذا نسمة؟ (تعرف علينا)"):
    st.markdown("""
    <div class="about-section">
        <strong>نسمة.. أكثر من مجرد خدمة تنظيف.</strong><br>
        استلهمنا اسمنا من "النسمة" الباردة التي تنعش الروح، ليكون عملنا هو إعادة الانتعاش والهدوء لبيتك. 
        نحن فريق يجمع بين دقة الاختيار وسهولة التقنية.
        <br><br>
        <b>ما الذي يميزنا؟</b>
        <ul>
            <li>احترافية عالية: عاملات مدربات لتقديم أفضل جودة.</li>
            <li>ثقة وأمان: نختار فريقنا بعناية لراحتك التامة.</li>
            <li>سرعة الحجز: موعدك مؤكد بضغطة زر عبر الواتساب.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- نموذج الحجز بتصميم نظيف ---
with st.container():
    st.markdown("<div style='text-align: right; color: #2e7d32; font-weight: bold;'>تفاصيل الحجز:</div>", unsafe_allow_html=True)
    
    name = st.text_input("👤 الاسم الكامل", placeholder="أدخل اسمك الكريم")
    phone = st.text_input("📞 رقم الجوال", placeholder="07XXXXXXXX")
    
    cleaner = st.selectbox(
        "🧹 اختر العاملة المختصة:",
        ["سناء م. ⭐ 4.9", "أمل ع. ⭐ 4.7", "ريم س. ⭐ 4.8"]
    )

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col2:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # زر التنفيذ
    if st.button("تأكيد الموعد وإرسال الطلب"):
        if name and phone:
            raw_message = f"طلب حجز جديد من نسمة 🍃\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 العاملة: {cleaner}\n📅 الموعد: {date} الساعة {time}"
            encoded_message = urllib.parse.quote(raw_message)
            admin_phone = "962777278329"
            whatsapp_url = f"https://wa.me/{admin_phone}?text={encoded_message}"
            
            js_code = f"<script>window.location.href = '{whatsapp_url}';</script>"
            st.components.v1.html(js_code, height=0)
            st.info("جاري تحضير "نسمة" النظافة لمنزلك.. يتم التحويل الآن...")
        else:
            st.warning("لطفاً، نحتاج للاسم ورقم الجوال لتأكيد الحجز.")

# --- التذييل ---
st.markdown("<p style='text-align: center; font-size: 12px; color: #999; margin-top: 50px;'>Nesmajo © 2026 | بكل حب من أجل منزلك</p>", unsafe_allow_html=True)
