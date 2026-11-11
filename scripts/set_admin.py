from backend.app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("UPDATE users SET is_admin = 1 WHERE email = 'skgounder50@gmail.com';"))
    conn.commit()
    user = conn.execute(text("SELECT id, email, full_name, is_admin FROM users WHERE email = 'skgounder50@gmail.com';")).fetchone()
    print("Primary user updated to admin:", user)

