#!/usr/bin/env python3
"""
Create initial admin user for the application
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Utilizador
from config.database_config import db

def create_admin_user():
    """Create initial admin user if no users exist"""
    try:
        db.connect()
        
        # Check if any users exist
        user_count = Utilizador.select().count()
        
        if user_count == 0:
            print("Creating initial admin user...")
            
            # Create admin user
            admin_user = Utilizador.create(
                nome="Administrador",
                email="admin@reciclagem.pt",
                is_admin=True,
                telefone="000000000",
                documento_identificacao="ADMIN",
                email_validado=True
            )
            admin_user.set_senha("admin123")
            admin_user.save()
            
            print("Admin user created successfully!")
            print("   Email: admin@reciclagem.pt")
            print("   Password: admin123")
            
        else:
            print(f"Database already has {user_count} user(s).")
            
            # Check if admin user exists
            try:
                admin_user = Utilizador.get(Utilizador.email == "admin@reciclagem.pt")
                print("Admin user already exists.")
            except Utilizador.DoesNotExist:
                print("No admin user found.")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
