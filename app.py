from flask import Flask, render_template, redirect, request, session
from datetime import datetime, timedelta
import sqlite3, os
from generate_key import generate_key

app = Flask(__name__)
app.secret_key = "supersecret"

DB_FILE = 'database.db'
if not os.path.exists(DB_FILE):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, balance INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE keys (id INTEGER PRIMARY KEY, user_id INTEGER, key TEXT, created_at TEXT, expired_at TEXT)''')
    c.execute('''CREATE TABLE deposits (id INTEGER PRIMARY KEY, user_id INTEGER, amount INTEGER, note TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE homepage (id INTEGER PRIMARY KEY, title TEXT, guide TEXT, contact TEXT, video_url TEXT)''')
    c.execute("INSERT INTO homepage (id, title, guide, contact, video_url) VALUES (1, 'AutoLastWar', 'Hướng dẫn...', 'Liên hệ admin...', '')")
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT title, guide, contact, video_url FROM homepage WHERE id = 1")
    homepage = c.fetchone()
    conn.close()
    return render_template('index.html', homepage=homepage)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (u, p))
            conn.commit()
            return redirect('/login')
        except:
            return "Tên tài khoản đã tồn tại!"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        user = get_user(u)
        if user and user[2] == p:
            session['username'] = u
            return redirect('/dashboard')
        else:
            return "Sai tài khoản hoặc mật khẩu!"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: return redirect('/login')
    user = get_user(session['username'])
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM keys WHERE user_id = ?", (user[0],))
    keys = c.fetchall()
    c.execute("SELECT title, guide, contact, video_url FROM homepage WHERE id = 1")
    homepage = c.fetchone()
    conn.close()
    return render_template('dashboard.html', user=user, keys=keys, homepage=homepage)

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

        key = generate_key(machine_id, days)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expired = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (price, user[0]))
        c.execute("INSERT INTO keys (user_id, key, created_at, expired_at) VALUES (?, ?, ?, ?)",
                  (user[0], key, now, expired))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('buy.html', user=user)



@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'username' not in session: return redirect('/login')
    user = get_user(session['username'])
    if request.method == 'POST':
        note = request.form['note']
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO deposits (user_id, amount, note, created_at) VALUES (?, ?, ?, ?)",
                  (user[0], 0, note, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        return redirect('/dashboard')
    return render_template('deposit.html', user=user)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Cộng tiền nếu có POST
    if request.method == 'POST':
        username = request.form['user_id']  # Thực chất là username
        amount = int(request.form['amount'])

        # Tìm user theo username
        c.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = c.fetchone()

        if result:
            user_id = result[0]
            c.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
            conn.commit()
        else:
            conn.close()
            return "❌ Tài khoản không tồn tại!"

    # Lấy danh sách người dùng
    c.execute('SELECT * FROM users')
    users = c.fetchall()

    # Tổng số tài khoản
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]

    # Lấy danh sách yêu cầu nạp tiền
    c.execute('SELECT * FROM deposits ORDER BY id DESC')
    deposits = c.fetchall()

    conn.close()
    return render_template('admin.html', users=users, deposits=deposits, total_users=total_users)



@app.route('/admin-settings', methods=['GET', 'POST'])
def admin_settings():
    if session.get('username') != 'admin': return redirect('/')
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        guide = request.form['guide']
        contact = request.form['contact']
        video = request.form['video']
        c.execute("UPDATE homepage SET title=?, guide=?, contact=?, video_url=? WHERE id=1",
                  (title, guide, contact, video))
        conn.commit()

    c.execute("SELECT title, guide, contact, video_url FROM homepage WHERE id=1")
    homepage = c.fetchone()
    conn.close()
    return render_template('admin_settings.html', title=homepage[0], guide=homepage[1], contact=homepage[2], video=homepage[3])

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)

