from flask import Flask, render_template, request, redirect, session, url_for, send_file, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime
import os
import pandas as pd
from io import BytesIO

app = Flask(__name__)
# سحب مفتاح التشفير من Render أو استخدام قيمة افتراضية للمطور
app.secret_key = os.environ.get("NESMA_SECRET_KEY", "default_secret_key_for_local")

# --- تصحيح رابط قاعدة البيانات ---
uri = os.environ.get("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///nesma_main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- إعداد نظام الدخول للعاملات ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'worker_login'

# --- تعريف الجداول (Models) ---

class Worker(UserMixin, db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100))
    bookings = db.relationship('Booking', backref='worker', lazy=True)

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
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'))
    workers_count = db.Column(db.String(10), default='1') 

@login_manager.user_loader
def load_user(user_id):
    return Worker.query.get(int(user_id))

# --- إنشاء وتحديث الجداول ---
with app.app_context():
    db.create_all()
    try:
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS worker_id INTEGER REFERENCES workers(id)"))
        db.session.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS workers_count VARCHAR(10)"))
        db.session.commit()
    except Exception as e:
        print(f"Database update log: {e}")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123")

# --- مسار الـ Service Worker (ضروري للتثبيت) ---
@app.route('/sw.js')
def serve_sw():
    return app.send_static_file('sw.js')

# --- مسارات الـ Manifest (هويات التطبيقات الثلاثة) ---

@app.route('/manifest.json')
def manifest():
    return {
        "id": "/customer-app",
        "short_name": "نسمة-حجز",
        "name": "نسمة لخدمات التنظيف",
        "icons": [{"src": "/static/logo.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
        "start_url": "/",
        "display": "standalone",
        "scope": "/",
        "theme_color": "#121212",
        "background_color": "#121212"
    }

@app.route('/worker_manifest.json')
def worker_manifest():
    return {
        "id": "/worker-app",
        "short_name": "نسمة-ميدان",
        "name": "نسمة - لوحة العاملات",
        "icons": [{"src": "/static/logo.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
        "start_url": "/worker/login",
        "display": "standalone",
        "scope": "/worker/",
        "theme_color": "#121212",
        "background_color": "#121212"
    }

@app.route('/admin_manifest.json')
def admin_manifest():
    return {
        "id": "/admin-app",
        "short_name": "نسمة-إدارة",
        "name": "نسمة - لوحة المدير",
        "icons": [{"src": "/static/logo.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
        "start_url": "/admin-login",
        "display": "standalone",
        "scope": "/",
        "theme_color": "#121212",
        "background_color": "#121212"
    }

# --- مسارات الزبائن والأدمن ---

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
            workers_count=request.form.get('cleaner') or '1',
            worker_id=None,
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
    return render_template('admin_login.html') # يفضل استدعاء ملف HTML بدلاً من نص ثابت

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    all_workers = Worker.query.all() 
    return render_template('admin.html', bookings=bookings, workers=all_workers)

# ... (تكملة بقية مسارات الحذف والتحديث و Excel والعمال كما هي في كودك الأصلي) ...
# سأضع لك الختام لضمان عمل السيرفر

@app.route('/worker/login', methods=['GET', 'POST'])
def worker_login():
    if request.method == 'POST':
        user = Worker.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('worker_dashboard'))
        flash('اسم المستخدم أو كلمة المرور غير صحيحة')
    return render_template('worker_login.html')

@app.route('/worker/dashboard')
@login_required
def worker_dashboard():
    user_tasks = Booking.query.filter_by(worker_id=current_user.id).order_by(Booking.timestamp.desc()).all()
    return render_template('worker_dashboard.html', worker=current_user, tasks=user_tasks)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
