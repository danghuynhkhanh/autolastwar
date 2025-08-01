import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import hashlib
import pyperclip

# Hàm tạo key bản quyền
def generate_key(machine_id, days_valid):
    expiry_date = (datetime.now() + timedelta(days=days_valid)).strftime('%Y-%m-%d')
    raw_data = f"{machine_id}|{expiry_date}"
    hash_part = hashlib.sha256(raw_data.encode()).hexdigest()[:16].upper()
    return f"{hash_part}-{expiry_date}"

# Khi nhấn nút "Tạo Key"
def create_key():
    machine_id = entry_id.get().strip()
    if not machine_id.isdigit():
        messagebox.showerror("Lỗi", "Mã máy phải là số.")
        return
    
    duration = duration_var.get()
    days = {
        "1 tháng": 30,
        "3 tháng": 90,
        "6 tháng": 180,
        "1 năm": 365
    }.get(duration, 30)

    key = generate_key(machine_id, days)
    entry_key.delete(0, tk.END)
    entry_key.insert(0, key)
    pyperclip.copy(key)
    messagebox.showinfo("Đã tạo key", f"Key đã được copy:\n{key}")

# Tạo cửa sổ GUI
root = tk.Tk()
root.title("Tạo Key Bản Quyền")
root.geometry("400x220")

tk.Label(root, text="🔑 Nhập mã máy:", font=("Arial", 11)).pack(pady=5)
entry_id = tk.Entry(root, font=("Arial", 11))
entry_id.pack(pady=5)

tk.Label(root, text="📆 Chọn thời hạn:", font=("Arial", 11)).pack(pady=5)
duration_var = tk.StringVar(value="1 tháng")
tk.OptionMenu(root, duration_var, "1 tháng", "3 tháng", "6 tháng", "1 năm").pack(pady=5)

tk.Button(root, text="Tạo Key", command=create_key, font=("Arial", 11), bg="green", fg="white").pack(pady=10)

tk.Label(root, text="🔐 Key đã tạo:", font=("Arial", 11)).pack()
entry_key = tk.Entry(root, font=("Arial", 11), width=40)
entry_key.pack(pady=5)

root.mainloop()
