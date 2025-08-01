import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Kiểm tra admin đã tồn tại chưa
user = c.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()

if user:
    c.execute("UPDATE users SET balance = 999999 WHERE username = 'admin'")
    print("✅ Admin đã tồn tại – đã reset tiền về 999999đ.")
else:
    c.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)", ('admin', 'matkhau', 999999))
    print("✅ Đã tạo tài khoản admin với số dư 999999đ.")

conn.commit()
conn.close()