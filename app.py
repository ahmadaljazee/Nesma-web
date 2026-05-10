from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
import os

app = Flask(__name__)
app.secret_key = "NESMA_SECRET_KEY_2026"

# --- إعداد قاعدة البيانات PostgreSQL (Render) ---
# سيقوم التطبيق بجلب الرابط تلقائياً من الإعدادات التي أظهرتها في الصورة
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- تعريف نموذج البيانات (مطابق تماماً لهيكل حجوزاتك السابق) ---
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    cleaner = db.Column(db.String(100))
    duration = db.Column(db.String(20))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    extra_supplies = db.Column(db.Text)
    lat = db.Column(db.String(50))
    lon = db.Column(db.String(50))
    map_url = db.Column(db.Text)
    status = db.Column(db.String(50), default='جديد')
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# --- إعدادات المدير ---
# جلب كلمة المرور من إعدادات رندر كما في الصورة
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123") 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_booking', methods=['POST'])
def save_booking():
    try:
        # استلام البيانات بنفس المسميات في الكود الأصلي
        name = request.form.get('name')
        phone = request.form.get('phone')
        cleaner = request.form.get('cleaner')
        date = request.form.get('date')
        time = request.form.get('time')
        lat = request.form.get('lat')
        lon = request.form.get('lon')
        duration = request.form.get('duration')

        extras = request.form.getlist('extra')
        extras_str = ", ".join(extras) if extras else "لا يوجد"

        map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else "غير محدد"

        # حفظ البيانات في PostgreSQL (Render)
        new_booking = Booking(
            name=name,
            phone=phone,
            cleaner=cleaner,
            duration=duration,
            date=date,
            time=time,
            extra_supplies=extras_str,
            lat=lat,
            lon=lon,
            map_url=map_link
        )
        
        db.session.add(new_booking)
        db.session.commit()
        
        return redirect(url_for('index', status='success'))

    except Exception as e:
        db.session.rollback()
        return f"حدث خطأ أثناء الحفظ في القاعدة الجديدة: {e}"

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

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    
    # جلب البيانات مرتبة من الأحدث إلى الأقدم لعرضها في الجدول
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    return render_template('admin.html', bookings=bookings)

@app.route('/admin-logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # إنشاء الجداول تلقائياً في قاعدة بيانات رندر عند التشغيل
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
