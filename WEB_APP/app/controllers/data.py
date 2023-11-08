from app import db
from app.models.user import User
import uuid 
import sys
def create_admin_user():
    # First check if an admin user already exists
    existing_admin = User.query.filter_by(role='admin').first()

    if existing_admin:
        print("Admin user already exists!")
        return

    admin_user = User(username="admin", email="admin@example.com", role="admin")
    admin_user.password = "strongpassword"
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created!")

def add_visitor(unique_id=None):
    
    if not unique_id:
        unique_id = str(uuid.uuid4())  # Generates a random UUID

    # Check if a visitor with this ID already exists
    existing_visitor = User.query.filter_by(username=unique_id).first()
    if existing_visitor:
        print(f"Visitor with ID {unique_id} already exists!")
        return existing_visitor

    visitor = User(username=unique_id, role="visitor")
    db.session.add(visitor)
    db.session.commit()
    print(f"Visitor with ID {unique_id} added!",file=sys.stdout)
    return visitor