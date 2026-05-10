from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

app = Flask(__name__)
app.secret_key = "NESMA_SECRET_KEY_2026"

# --- إعداد قاعدة البيانات PostgreSQL (رابط رندر الداخلي) ---
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 

# --- تعريف الجداول (Models) ---

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='customer') 
    bookings = db.relationship('Booking', backref='customer', lazy=True)

class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)
    tasks = db.relationship('Booking', backref='assigned_worker', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(100))
    duration = db.Column(db.String(20))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    extra_supplies = db.Column(db.Text)
    status = db.Column(db.String(50), default='جديد')
    
    # حقول الإحداثيات المضافة للخريطة
    lat = db.Column(db.Float) 
    lon = db.Column(db.Float)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- المسارات (Routes) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        name = request.form.get('name')
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(phone=phone, password=hashed_pw, full_name=name)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            flash("رقم الهاتف مسجل مسبقاً")
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        user = User.query.filter_by(phone=phone).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("خطأ في رقم الهاتف أو كلمة السر")
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', bookings=current_user.bookings, name=current_user.full_name)

@app.route('/save_booking', methods=['POST'])
@login_required
def save_booking():
    try:
        extras = request.form.getlist('extra')
        new_booking = Booking(
            service_type=request.form.get('service_type'),
            duration=request.form.get('duration'),
            date=request.form.get('date'),
            time=request.form.get('time'),
            extra_supplies=", ".join(extras) if extras else "لا يوجد",
            
            # استلام وحفظ الإحداثيات من الفورم
            lat=float(request.form.get('lat')) if request.form.get('lat') else None,
            lon=float(request.form.get('lon')) if request.form.get('lon') else None,
            
            user_id=current_user.id 
        )
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('dashboard', status='success'))
    except Exception as e:
        return f"حدث خطأ: {e}"

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "غير مسموح لك بالدخول"
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    return render_template('admin.html', bookings=bookings)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
