from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
import os

app = Flask(__name__)
app.secret_key = "NESMA_SECRET_KEY_2026"

# --- تصحيح رابط قاعدة البيانات (لحل مشكلة SQLAlchemy مع Render) ---
uri = os.environ.get("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- تعريف الجدول (لبناء المخزن تلقائياً) ---
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    cleaner = db.Column(db.String(100))
    duration = db.Column(db.String(50))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    extra_supplies = db.Column(db.Text)
    lat = db.Column(db.String(50))
    lon = db.Column(db.String(50))
    map_url = db.Column(db.Text)
    status = db.Column(db.String(50), default='جديد')
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# --- إنشاء الجداول (هذا السطر سيحل مشكلة UndefinedTable فوراً) ---
with app.app_context():
    db.create_all()

# جلب كلمة السر من إعدادات رندر (الصورة التي أرسلتها)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_booking', methods=['POST'])
def save_booking():
    try:
        lat, lon = request.form.get('lat'), request.form.get('lon')
        new_booking = Booking(
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            cleaner=request.form.get('cleaner'),
            duration=request.form.get('duration'),
            date=request.form.get('date'),
            time=request.form.get('time'),
            extra_supplies=", ".join(request.form.getlist('extra')) or "لا يوجد",
            lat=lat, lon=lon,
            map_url=f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "غير محدد"
        )
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('index', status='success'))
    except Exception as e:
        db.session.rollback()
        return f"حدث خطأ أثناء الحفظ: {e}"

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return "كلمة مرور خاطئة!"
    return '''<div style="text-align:center; margin-top:100px; direction:rtl;"><h2>دخول المدير</h2><form method="post"><input type="password" name="password" placeholder="كلمة المرور"><button type="submit">دخول</button></form></div>'''

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    return render_template('admin.html', bookings=bookings)

@app.route('/admin-logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

import pandas as pd
from io import BytesIO
from flask import send_file

@app.route('/download-excel')
def download_excel():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    # جلب جميع الحجوزات من القاعدة
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    
    # تحويل البيانات إلى قائمة مرتبة
    data = []
    for b in bookings:
        data.append({
            "الاسم": b.name,
            "الهاتف": b.phone,
            "العاملة": b.cleaner,
            "نوع الخدمة": b.duration,
            "التاريخ": b.date,
            "الوقت": b.time,
            "المستلزمات": b.extra_supplies,
            "رابط الموقع": b.map_url,
            "الحالة": b.status,
            "وقت الطلب": b.timestamp
        })
    
    # تحويل القائمة إلى ملف إكسل باستخدام Pandas
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hajoozat_Nesma')
    
    output.seek(0)
    
    # إرسال الملف للمتصفح للتحميل
    return send_file(
        output, 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True, 
        download_name=f'Nesma_Bookings_{datetime.datetime.now().strftime("%Y-%m-%d")}.xlsx'
    ) 
    @app.route('/update_status/<int:booking_id>', methods=['POST'])
def update_status(booking_id):
    if not session.get('logged_in'):
        return "Unauthorized", 401
    
    new_status = request.form.get('status')
    booking = Booking.query.get(booking_id)
    
    if booking:
        booking.status = new_status
        db.session.commit()
        return "Success", 200
    return "Error", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
