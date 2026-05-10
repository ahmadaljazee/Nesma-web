from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
import os

app = Flask(__name__)
app.secret_key = "NESMA_SECRET_KEY_2026"

# الربط مع قاعدة بيانات رندر عبر المتغير البيئي DATABASE_URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# تعريف الجدول (هذا الجزء هو الذي سيحل مشكلة UndefinedTable)
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

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_booking', methods=['POST'])
def save_booking():
    try:
        # استلام البيانات من الفورم
        new_booking = Booking(
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            cleaner=request.form.get('cleaner'),
            duration=request.form.get('duration'),
            date=request.form.get('date'),
            time=request.form.get('time'),
            extra_supplies=", ".join(request.form.getlist('extra')) or "لا يوجد",
            lat=request.form.get('lat'),
            lon=request.form.get('lon'),
            map_url=f"https://www.google.com/maps?q={request.form.get('lat')},{request.form.get('lon')}"
        )
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('index', status='success'))
    except Exception as e:
        db.session.rollback()
        return f"حدث خطأ أثناء الحفظ: {e}"

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    return render_template('admin.html', bookings=bookings)

# ... (باقي المسارات admin-login و admin-logout تبقى كما هي)

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # هذا السطر هو "السحر" الذي سيقوم بإنشاء الجدول المفقود
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
