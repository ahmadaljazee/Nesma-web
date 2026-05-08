from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import json
import urllib.parse

app = Flask(__name__)

# --- إعداد Firebase (الربط بقاعدة default1) ---
if not firebase_admin._apps:
    firebase_key = os.environ.get("FIREBASE_KEYS")
    if firebase_key:
        try:
            key_dict = json.loads(firebase_key)
            creds = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(creds)
        except Exception as e:
            print(f"Error initializing Firebase: {e}")

# الاتصال بالقاعدة default1 مباشرة
db = firestore.client(database_id="default1")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book():
    # استلام البيانات من النموذج (Form)
    name = request.form.get('name')
    phone = request.form.get('phone')
    cleaner = request.form.get('cleaner')
    date = request.form.get('date')
    time = request.form.get('time')
    lat = request.form.get('lat')
    lon = request.form.get('lon')

    # بناء رابط الخريطة إذا توفرت الإحداثيات
    map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "غير محدد"

    booking_data = {
        "name": name,
        "phone": phone,
        "cleaner": cleaner,
        "date": date,
        "time": time,
        "location": {"lat": lat, "lon": lon},
        "map_url": map_link,
        "status": "جديد",
        "timestamp": datetime.datetime.now()
    }

    # 1. حفظ البيانات في Firestore
    db.collection("bookings").add(booking_data)
    
    # 2. تجهيز رسالة الواتساب الاحترافية
    raw_msg = (
        f"طلب حجز جديد من نسمة 🌬️\n"
        f"--------------------------\n"
        f"👤 الاسم: {name}\n"
        f"📞 الهاتف: {phone}\n"
        f"🧹 العاملة: {cleaner}\n"
        f"📅 الموعد: {date} الساعة {time}\n"
        f"📍 موقع المنزل: {map_link}\n"
        f"--------------------------"
    )
    
    encoded_msg = urllib.parse.quote(raw_msg)
    whatsapp_url = f"https://wa.me/962777278329?text={encoded_msg}"
    
    return redirect(whatsapp_url)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
