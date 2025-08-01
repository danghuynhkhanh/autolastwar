import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Tạo bảng homepage nếu chưa có
c.execute('''
CREATE TABLE IF NOT EXISTS homepage (
    id INTEGER PRIMARY KEY,
    title TEXT,
    guide TEXT,
    contact TEXT,
    video_url TEXT
)
''')

# Thêm dòng đầu tiên nếu chưa có
c.execute("SELECT * FROM homepage WHERE id = 1")
if not c.fetchone():
    c.execute('''
        INSERT INTO homepage (id, title, guide, contact, video_url)
        VALUES (1, 'AutoLastWar', 'Hướng dẫn sẽ hiển thị ở đây.', 'Liên hệ qua Zalo 0366905470', '')
    ''')

conn.commit()
conn.close()
print("✅ Đã khởi tạo bảng homepage và thêm dữ liệu mẫu.")
