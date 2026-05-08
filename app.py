import streamlit as st
import datetime
import urllib.parse
import base64
import os

# --- 1. إعدادات الصفحة (Amman, Jordan Context) ---
st.set_page_config(
    page_title="نسمة للأعمال المنزلية | Nesma Home Services",
    page_icon="🌬️", # Breeze/Cleanliness icon
    layout="centered"
)

# --- 2. دالة مساعدة للتعامل مع الصور بأمان (تمنع تعطل التطبيق) ---
def get_base64_of_bin_file(bin_file):
    """تحاول تحويل الصورة إلى Base64. تعود بـ None إذا لم يتم العثور على الملف أو حدث خطأ."""
    if not os.path.exists(bin_file):
        return None
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        # فشل بصمت لتجنب توقف التطبيق
        return None

# محاولة تحميل صورة الشعار nesma.png
image_base64 = get_base64_of_bin_file('nesma.png')

# --- 3. تصميم الواجهة (CSS Styling) مع معالجة غياب الصورة ---
# إذا وجدت الصورة، نضع تراكب خفيف فوقها. إذا لم توجد، نستخدم التدرج اللوني الهادئ الذي اقترحته.
if image_base64:
    # تنسيق خلفية تحتوي على الصورة المرفوعة مع تراكب أبيض شبه شفاف للوضوح
    bg_style = f"""
        background-image: linear-gradient(rgba(253, 252, 240, 0.92), rgba(232, 245, 233, 0.92)), 
                          url("data:image/png;base64,{image_base64}");
    """
else:
    # التنسيق الاحتياطي: تدرج لوني هادئ ومريح يرمز للنظافة
    bg_style = """
        background-image: linear-gradient(135deg, #fdfcf0 0%, #e8f5e9 100%);
    """

st.markdown(f"""
    <style>
    .stApp {{
        {bg_style}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* تحسين مظهر حقول الإدخال */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {{
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #a5d6a7 !important;
        border-radius: 10px !important;
    }}

    /* تصميم زر الحجز (لون نسمة الأخضر المريح) */
    div.stButton > button {{
        background-color: #00c853 !important;
        color: white !important;
        border-radius: 25px !important;
        font-weight: bold;
        font-size: 1.1rem;
        height: 50px;
        width: 100%;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,200,83,0.3) !important;
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        background-color: #00e676 !important;
        box-shadow: 0 6px 15px rgba(0,200,83,0.4) !important;
    }}

    /* تنسيق النصوص الرئيسية */
    .header-text {{
        text-align: center;
        color: #1b5e20;
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. محتوى الواجهة (UI Content) ---

# عرض الشعار (فقط إذا نجح تحميله)
if image_base64:
    # توسيط الصورة باستخدام أعمدة
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("nesma.png", use_container_width=True)

# العنوان الرئيسي والشعار اللفظي
st.markdown("<h1 class='header-text'>نسمة للأعمال المنزلية | Nesma</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #558b2f; font-weight: 500;'>خدمات منزلية احترافية في عمان بلمسة ذكية</p>", unsafe_allow_html=True)

# حاوية نموذج الحجز
with st.container():
    st.markdown("<h3 style='text-align: center; color: #1b5e20;'>نموذج حجز خدمة</h3>", unsafe_allow_html=True)
    
    # حقول الإدخال
    name = st.text_input("👤 الاسم الكامل", placeholder="أدخل اسمك")
    phone = st.text_input("📞 رقم الجوال (في عمان)", placeholder="07XXXXXXXX")
    
    # اختيار العاملة (مثال لنوع الخدمة)
    cleaner = st.selectbox("🧹 اختر العاملة المختصة:", [
        "سناء م. ⭐ 4.9", 
        "أمل ع. ⭐ 4.7", 
        "ريم س. ⭐ 4.8"
    ])

    # أعمدة التاريخ والوقت
    col_date, col_time = st.columns(2)
    with col_date:
        date = st.date_input("📅 تاريخ الحجز", min_value=datetime.date.today())
    with col_time:
        time = st.time_input("⏰ وقت الحجز")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # زر إرسال الطلب عبر الواتساب (موسط)
    left_col, center_col, right_col = st.columns([1, 1.5, 1])
    with center_col:
        if st.button("تأكيد البيانات وإرسال الحجز"):
            # تحقق بسيط من البيانات
            if not name or not phone:
                st.warning("يرجى إدخال الاسم ورقم الجوال لتأكيد الحجز.")
            else:
                # تجهيز نص رسالة الواتساب
                message_text = f"طلب حجز جديد من نسمة 🌬️\n---------------\n👤 الاسم: {name}\n📞 الجوال: {phone}\n🧹 المختصة: {cleaner}\n📅 الموعد: {date} الساعة {time}\n---------------\nالرجاء التواصل لتأكيد الحجز."
                
                # ترميز الرسالة لتناسب الرابط
                encoded_message = urllib.parse.quote(message_text)
                
                # إنشاء رابط الواتساب (باستخدام رقم أردني في عمان كمثال)
                whatsapp_number = "962777278329" 
                whatsapp_url = f"https://wa.me/{whatsapp_number}?text={encoded_message}"
                
                # توجيه المستخدم (بسبب قيود Render/Streamlit في فتح الروابط مباشرة)
                st.success("تم تجهيز طلبك! يرجى الضغط على الزر أدناه لفتحه في الواتساب وإرسال الرسالة:")
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">الذهاب إلى الواتساب وإرسال الرسالة</div></a>', unsafe_allow_html=True)
                st.info("⚠️ ملاحظة: ستحتاج إلى الضغط على 'إرسال' داخل تطبيق الواتساب.")

# تذييل الصفحة (Footer) مع سياق محلي
st.markdown("<br><br><p style='text-align: center; font-size: 11px; color: #888;'>نسمة للخدمات المنزلية - عمان، الأردن © 2026</p>", unsafe_allow_html=True)
