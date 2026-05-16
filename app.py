from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "nesma_secret_key_2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nesma.db'
db = SQLAlchemy(app)

# --- النماذج (Models) ---
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    admin_password = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True) # حقل التحكم بالحجب

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    duration = db.Column(db.String(100)) 
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    lat = db.Column(db.String(50))
    lon = db.Column(db.String(50))
    extra = db.Column(db.Text) 
    status = db.Column(db.String(20), default="جديد")

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    name = db.Column(db.String(100))
    password = db.Column(db.String(50), default="123456")

with app.app_context():
    db.create_all()

# --- المسارات (Routes) ---

# 1. لوحة السوبر أدمن (إدارة المنصة)
@app.route('/super-admin', methods=['GET', 'POST'])
def super_admin():
    if request.method == 'POST':
        new_co = Company(
            name=request.form['name'],
            slug=request.form['slug'],
            admin_password=request.form['password']
        )
        db.session.add(new_co)
        db.session.commit()
        return redirect(url_for('super_admin'))
    companies = Company.query.all()
    return render_template('super_admin.html', companies=companies)

# 2. مسار الحجب (خاص بالسوبر أدمن فقط)
@app.route('/toggle_status/<int:company_id>', methods=['POST'])
def toggle_status(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_active = not company.is_active
    db.session.commit()
    return redirect(url_for('super_admin'))

# 3. صفحة الحجز (بصمة نسمة) - مع التحقق من الحجب
@app.route('/<slug>')
def index(slug):
    # التحقق من أن الشركة موجودة ونشطة (غير محجوبة)
    company = Company.query.filter_by(slug=slug, is_active=True).first()
    if not company:
        return "<h1>عذراً، هذه الخدمة غير متوفرة حالياً ⚠️</h1><p>يرجى التواصل مع إدارة المنصة لتفعيل الحساب.</p>", 403
    return render_template('index.html', company=company)

# 4. حفظ الحجز (لوجستيات كاملة)
@app.route('/<slug>/save_booking', methods=['POST'])
def save_booking(slug):
    company = Company.query.filter_by(slug=slug).first_or_404()
    selected_extras = request.form.getlist('extra')
    extras_string = ", ".join(selected_extras) if selected_extras else ""
    cleaner_count = request.form.get('cleaner', '1')

    new_b = Booking(
        company_id=company.id,
        name=request.form['name'],
        phone=request.form['phone'],
        duration=request.form['duration'],
        date=request.form['date'],
        time=request.form['time'],
        lat=request.form.get('lat'),
        lon=request.form.get('lon'),
        extra=f"العاملات: {cleaner_count} | المستلزمات: {extras_string}"
    )
    db.session.add(new_b)
    db.session.commit()
    return redirect(url_for('index', slug=slug, status='success'))

# 5. إدارة مدير الشركة
@app.route('/<slug>/admin-login', methods=['GET', 'POST'])
def admin_login(slug):
    company = Company.query.filter_by(slug=slug, is_active=True).first_or_404()
    if request.method == 'POST':
        if request.form['password'] == company.admin_password:
            session[f'admin_{company.id}'] = True
            return redirect(url_for('admin_dashboard', slug=slug))
        else:
            flash("كلمة المرور غير صحيحة")
    return render_template('admin_login.html', company=company)

@app.route('/<slug>/dashboard')
def admin_dashboard(slug):
    company = Company.query.filter_by(slug=slug, is_active=True).first_or_404()
    if not session.get(f'admin_{company.id}'):
        return redirect(url_for('admin_login', slug=slug))
    bookings = Booking.query.filter_by(company_id=company.id).all()
    workers = Worker.query.filter_by(company_id=company.id).all()
    return render_template('admin.html', company=company, bookings=bookings, workers=workers)

# 6. إدارة العاملات (إضافة وتعيين)
@app.route('/<slug>/add_worker', methods=['POST'])
def add_worker(slug):
    company = Company.query.filter_by(slug=slug).first_or_404()
    worker_name = request.form.get('worker_name')
    worker_pass = request.form.get('worker_password', '123456')
    if worker_name:
        new_worker = Worker(name=worker_name, password=worker_pass, company_id=company.id)
        db.session.add(new_worker)
        db.session.commit()
    return redirect(url_for('admin_dashboard', slug=slug))

@app.route('/<slug>/assign_worker/<int:booking_id>', methods=['POST'])
def assign_worker(slug, booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.worker_id = request.form.get('worker_id')
    db.session.commit()
    return redirect(url_for('admin_dashboard', slug=slug))

# 7. لوحة العاملة
@app.route('/<slug>/worker-login', methods=['GET', 'POST'])
def worker_login(slug):
    company = Company.query.filter_by(slug=slug, is_active=True).first_or_404()
    if request.method == 'POST':
        name = request.form.get('worker_name')
        pw = request.form.get('password')
        worker = Worker.query.filter_by(company_id=company.id, name=name, password=pw).first()
        if worker:
            session[f'worker_auth_{worker.id}'] = True
            return redirect(url_for('worker_dashboard', slug=slug, worker_id=worker.id))
        else:
            flash("بيانات الدخول غير صحيحة")
    return render_template('worker_login.html', company=company)

@app.route('/<slug>/worker/<int:worker_id>')
def worker_dashboard(slug, worker_id):
    company = Company.query.filter_by(slug=slug).first_or_404()
    worker = Worker.query.get_or_404(worker_id)
    if not session.get(f'worker_auth_{worker.id}'):
        return redirect(url_for('worker_login', slug=slug))
    bookings = Booking.query.filter_by(company_id=company.id, worker_id=worker_id).all()
    return render_template('worker_view.html', company=company, worker=worker, bookings=bookings)

# 8. تحديث الحالة
@app.route('/<slug>/update_status/<int:id>', methods=['POST'])
def update_status(slug, id):
    booking = Booking.query.get_or_404(id)
    booking.status = request.form['status']
    db.session.commit()
    return "OK"

@app.route('/<slug>/logout')
def logout(slug):
    session.clear()
    return redirect(url_for('index', slug=slug))

if __name__ == '__main__':
    app.run(debug=True)