from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, timedelta, timezone
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB_FILE = 'database.db'

def generate_key(machine_id, days_valid):
    vn_timezone = timezone(timedelta(hours=7))  # Giờ Việt Nam
    expiry_date = (datetime.now(vn_timezone).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_valid)).strftime('%Y-%m-%d')
    raw_data = f"{machine_id}|{expiry_date}"
    hash_part = hashlib.sha256(raw_data.encode()).hexdigest()[:16].upper()
    return f"{hash_part}-{expiry_date}"

def get_user(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, username, password, balance FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        user = get_user(username)
        if user and user[2] == password:
            session['username'] = username
            return redirect('/dashboard')
        return "Sai tài khoản hoặc mật khẩu."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return "Tài khoản đã tồn tại."
        c.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", (username, password, 0))
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    user = get_user(session['username'])

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT key, created_at, expired_at FROM keys WHERE user_id = ?", (user[0],))
    keys = c.fetchall()
    conn.close()

    return render_template('dashboard.html', user=user, keys=keys)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'username' not in session:
        return redirect('/login')
    user = get_user(session['username'])

    if request.method == 'POST':
        amount = int(request.form['amount'])
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user[0]))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    return render_template('deposit.html', user=user)

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if 'username' not in session:
        return redirect('/login')
    user = get_user(session['username'])

    if request.method == 'POST':
        plan = request.form['plan']
        machine_id = request.form['machine_id'].strip()

        price_table = {
            '1 tháng': (30000, 30),
            '3 tháng': (90000, 90),
            '6 tháng': (180000, 180),
            '12 tháng': (360000, 365),
        }

        if plan not in price_table:
            return "Gói không hợp lệ."

        price, days = price_table[plan]
        if user[3] < price:
            return "Không đủ số dư!"

        # Sử dụng múi giờ Việt Nam giống với phần mềm PC
        vn_tz = timezone(timedelta(hours=7))
        created_at = datetime.now(vn_tz).strftime("%Y-%m-%d %H:%M:%S")
        expired_date = (datetime.now(vn_tz).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days)).strftime("%Y-%m-%d")

        key = generate_key(machine_id, days)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (price, user[0]))
        c.execute("INSERT INTO keys (user_id, key, created_at, expired_at) VALUES (?, ?, ?, ?)",
                  (user[0], key, created_at, expired_date))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('buy.html', user=user)

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/admin-settings', methods=['GET', 'POST'])
def admin_settings():
    # Có thể bỏ qua nếu bạn không cần sửa phần này
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
