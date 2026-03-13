"""
Database configuration for the application
"""

import os
from peewee import *
from dotenv import load_dotenv

load_dotenv()

# SQLite database configuration
db_path = os.getenv("DB_PATH", "data/reciclagem_reee.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)

db = SqliteDatabase(db_path)
