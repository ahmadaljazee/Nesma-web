from flask import Flask, render_template, request, redirect, session, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import json

app = Flask(__name__)
app.secret_key = "NESMA_SECRET_KEY_2026" 

# --- إعداد Firebase ---
if not firebase_admin._apps:
    firebase_key = os.environ.get("FIREBASE_KEYS")
    if firebase_key:
        try:
            key_dict = json.loads(firebase_key)
            creds = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(creds)
        except Exception as e:
            print(f"Firebase Error: {e}")

db = firestore.client(database_id="default1")

ADMIN_PASSWORD = "123" 

# --- 1. واجهة الزبائن الرئيسية ---
@app.route('/')
def index():
    return render_template('index.html')

# --- 2. مسار الحجز (التعديل لإخفاء الرابط) ---
@app.route('/save_booking', methods=['POST'])
def save_booking():
    try:
        name = request.form.get('name')
        phone = request.form.get('phone')
        cleaner = request.form.get('cleaner')
        date = request.form.get('date')
        time = request.form.get('time')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        extras = request.form.getlist('extra')
        extras_str = ", ".join(extras) if extras else "لا يوجد"

        map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "غير محدد"

        booking = {
            "name": name,
            "phone": phone,
            "cleaner": cleaner,
            "date": date,
            "time": time,
            "extra_supplies": extras_str,
            "location": {"lat": lat, "lon": lon},
            "map_url": map_link,
            "status": "جديد",
            "timestamp": datetime.datetime.now()
        }

        db.collection("bookings").add(booking)
        
        # التعديل هنا: إعادة التوجيه للصفحة الرئيسية مع حالة النجاح
        # هذا يمنع ظهور رابط Render في المتصفح
        return redirect(url_for('index', status='success'))

    except Exception as e:
        return f"حدث خطأ أثناء الحفظ: {e}"

# --- 3. لوحة التحكم (الدخول) ---
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "كلمة مرور خاطئة!"
    return render_template('login.html') # يفضل وضع كود الدخول في ملف html منفصل

# --- 4. لوحة التحكم (عرض البيانات) ---
@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    bookings_ref = db.collection("bookings").order_by("timestamp", direction="DESCENDING")
    bookings = [doc.to_dict() for doc in bookings_ref.stream()]
    
    return render_template('admin.html', bookings=bookings)

# --- 5. تسجيل الخروج ---
@app.route('/admin-logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
