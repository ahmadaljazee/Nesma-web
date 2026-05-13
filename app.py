from flask import Flask, render_template, request, redirect, session, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime
import os
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.secret_key = "NESMA_SECRET_KEY_2026"

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
    
    # التعديل الصحيح هنا: الحقول يجب أن تكون داخل الكلاس
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
        # تحديث قاعدة البيانات لإضافة الأعمدة الجديدة إذا لم تكن موجودة
        db.session.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS worker_id INTEGER REFERENCES workers(id)"))
        db.session.execute(text("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS workers_count VARCHAR(10)"))
        db.session.commit()
    except Exception as e:
        print(f"Database update log: {e}")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123")

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
            # استلام عدد العاملات من حقل cleaner في الـ HTML
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

# ... (بقية المسارات admin و worker تبقى كما هي في كودك) ...

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
    all_workers = Worker.query.all() 
    return render_template('admin.html', bookings=bookings, workers=all_workers)

@app.route('/assign_worker/<int:booking_id>', methods=['POST'])
def assign_worker(booking_id):
    if not session.get('logged_in'): return "Unauthorized", 401
    worker_id = request.form.get('worker_id')
    booking = Booking.query.get(booking_id)
    if booking:
        booking.worker_id = worker_id if worker_id and worker_id != "" else None
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin-logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/download-excel')
def download_excel():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    data = []
    for b in bookings:
        data.append({
            "الاسم": b.name, "الهاتف": b.phone, "عدد العاملات": b.workers_count,
            "نوع الخدمة": b.duration, "التاريخ": b.date, "الوقت": b.time,
            "المستلزمات": b.extra_supplies, "رابط الموقع": b.map_url,
            "الحالة": b.status, "وقت الطلب": b.timestamp
        })
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hajoozat_Nesma')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=f'Nesma_Bookings_{datetime.datetime.now().strftime("%Y-%m-%d")}.xlsx')

@app.route('/update_status/<int:booking_id>', methods=['POST'])
def update_status(booking_id):
    if not session.get('logged_in'): return "Unauthorized", 401
    new_status = request.form.get('status')
    booking = Booking.query.get(booking_id)
    if booking:
        booking.status = new_status
        db.session.commit()
        return "Success", 200
    return "Error", 404

@app.route('/delete_finished', methods=['POST'])
def delete_finished():
    if not session.get('logged_in'): return "Unauthorized", 401
    Booking.query.filter(Booking.status.in_(['تم الانتهاء', 'تم الإلغاء'])).delete(synchronize_session=False)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

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

@app.route('/worker/update_status/<int:task_id>/<action>', methods=['POST'])
@login_required
def worker_update_status(task_id, action):
    task = Booking.query.get_or_404(task_id)
    if task.worker_id == current_user.id:
        task.status = 'جاري العمل' if action == 'start' else 'تم الانتهاء'
        db.session.commit()
    return redirect(url_for('worker_dashboard'))

@app.route('/worker/logout')
@login_required
def worker_logout():
    logout_user()
    return redirect(url_for('worker_login'))

# مسار عرض وإضافة العاملات (للمدير فقط)
@app.route('/admin/manage-workers', methods=['GET', 'POST'])
def manage_workers():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # التأكد من أن اسم المستخدم غير مكرر
        existing = Worker.query.filter_by(username=username).first()
        if not existing:
            new_worker = Worker(username=username, password=password, name=name)
            db.session.add(new_worker)
            db.session.commit()
            flash(f'تم إضافة العاملة {name} بنجاح!')
        else:
            flash('اسم المستخدم موجود مسبقاً!')
            
    workers = Worker.query.all()
    return render_template('manage_workers.html', workers=workers)

# مسار حذف عاملة
@app.route('/admin/delete-worker/<int:id>')
def delete_worker(id):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    worker = Worker.query.get(id)
    if worker:
        db.session.delete(worker)
        db.session.commit()
        flash('تم حذف العاملة بنجاح')
    return redirect(url_for('manage_workers'))
    
@app.route('/manifest.json')
def manifest():
    # لاحظ الفراغ (4 مسافات) قبل كلمة return
    return {
        "short_name": "Nesma",
        "name": "Nesma Cleaning Services",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ],
        "start_url": "/",
        "display": "standalone",
        "theme_color": "#121212",
        "background_color": "#121212"
    }

# هذا السطر لازم يرجع لأول السطر تماماً (بدون أي مسافة قبله)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
