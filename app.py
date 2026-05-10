from flask import Flask, render_template, request, redirect, session, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import json

app = Flask(__name__)
app.secret_key = "NESMA_SECRET_KEY_2026" # مفتاح الأمان للجلسات

# --- إعداد Firebase (قاعدة البيانات default1) ---
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

# --- إعدادات المدير ---
ADMIN_PASSWORD = "nesma2026" # كلمة المرور للوحة التحكم

# --- 1. واجهة الزبائن الرئيسية ---
@app.route('/')
def index():
    return render_template('index.html')

# --- 2. مسار الحجز (تعديل لاستلام المستلزمات الإضافية ومدة الخدمة) ---
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
        
        # إضافة استلام مدة الخدمة (4 أو 6 ساعات)
        duration = request.form.get('duration')

        # --- الجزء الجديد: استلام الخيارات الأربعة (Checkboxes) ---
        extras = request.form.getlist('extra')
        extras_str = ", ".join(extras) if extras else "لا يوجد"

        map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "غير محدد"

        booking = {
            "name": name,
            "phone": phone,
            "cleaner": cleaner,
            "duration": duration, # إضافة المدة داخل قاموس الحجز
            "date": date,
            "time": time,
            "extra_supplies": extras_str,
            "location": {"lat": lat, "lon": lon},
            "map_url": map_link,
            "status": "جديد",
            "timestamp": datetime.datetime.now()
        }

        # حفظ البيانات في Firestore في مجموعة "bookings"
        db.collection("bookings").add(booking)
        
        # التعديل لضمان عدم ظهور روابط خارجية (Redirect بدلاً من script alert المباشر)
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
    return '''
        <div style="text-align:center; margin-top:100px; font-family:sans-serif; direction:rtl;">
            <h2>قفل الأمان - لوحة تحكم نسمة</h2>
            <form method="post">
                <input type="password" name="password" placeholder="كلمة المرور" style="padding:10px; border-radius:5px;">
                <button type="submit" style="padding:10px 20px; background:#2e7d32; color:white; border:none; border-radius:5px; cursor:pointer;">دخول</button>
            </form>
        </div>
    '''

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
