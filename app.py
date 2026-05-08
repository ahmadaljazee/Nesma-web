from flask import Flask, render_template, request, redirect, session, url_for
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import json
import urllib.parse

app = Flask(__name__)

# --- مفتاح سري لتأمين الجلسة (Session) ---
app.secret_key = "NESMA_SECRET_2026" 

# --- كلمة مرور لوحة التحكم (يمكنك تغييرها) ---
ADMIN_PASSWORD = "123"

# --- إعداد Firebase (قاعدة البيانات default1) ---
if not firebase_admin._apps:
    firebase_key = os.environ.get("FIREBASE_KEYS")
    if firebase_key:
        try:
            key_dict = json.loads(firebase_key)
            creds = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(creds)
        except Exception as e:
            print(f"Error: {e}")

db = firestore.client(database_id="default1")

# --- مسار واجهة الزبائن ---
@app.route('/')
def index():
    return render_template('index.html')

# --- مسار تسجيل الحجز ---
@app.route('/book', methods=['POST'])
def book():
    name = request.form.get('name')
    phone = request.form.get('phone')
    cleaner = request.form.get('cleaner')
    date = request.form.get('date')
    time = request.form.get('time')
    lat = request.form.get('lat')
    lon = request.form.get('lon')

    map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "غير محدد"

    booking = {
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

    db.collection("bookings").add(booking)
    
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

# --- لوحة التحكم (الدخول) ---
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
    return '''
        <div style="text-align:center; margin-top:100px; font-family:sans-serif;">
            <h2>قفل الأمان - لوحة تحكم نسمة</h2>
            <form method="post">
                <input type="password" name="password" placeholder="كلمة المرور" style="padding:10px; border-radius:5px;">
                <button type="submit" style="padding:10px 20px; background:#2e7d32; color:white; border:none; border-radius:5px;">دخول</button>
            </form>
        </div>
    '''

# --- لوحة التحكم (عرض البيانات) ---
@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    # جلب الحجوزات مرتبة من الأحدث إلى الأقدم
    bookings_ref = db.collection("bookings").order_by("timestamp", direction="DESCENDING")
    bookings = [doc.to_dict() for doc in bookings_ref.stream()]
    
    return render_template('admin.html', bookings=bookings)

# --- تسجيل الخروج ---
@app.route('/admin-logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
