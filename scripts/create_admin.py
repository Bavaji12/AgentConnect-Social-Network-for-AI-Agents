import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password

def create_admin():
    db = SessionLocal()
    try:
        admin_email = "admin@agentconnect.ai"
        existing = db.query(User).filter(User.email == admin_email).first()
        if existing:
            print(f"[!] Admin user already exists: {admin_email}")
            return existing

        admin = User(
            email=admin_email,
            password_hash=hash_password("Password123!"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"[✓] Created default admin user: {admin_email} (Password: Password123!)")
        return admin
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
