from datetime import datetime, timedelta
import hashlib

# Hàm tạo key bản quyền
def generate_key(machine_id, days_valid):
    expiry_date = (datetime.now() + timedelta(days=days_valid)).strftime('%Y-%m-%d')
    raw_data = f"{machine_id}|{expiry_date}"
    hash_part = hashlib.sha256(raw_data.encode()).hexdigest()[:16].upper()
    return f"{hash_part}-{expiry_date}"
