"""
Database configuration for the application
"""

import os
from peewee import *
from dotenv import load_dotenv

load_dotenv()

# Get the directory of this config file
config_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the eventpy-main directory
project_dir = os.path.dirname(config_dir)
# Construct absolute path to database
db_path = os.path.join(project_dir, os.getenv("DB_PATH", "data/reciclagem_reee.db"))

os.makedirs(os.path.dirname(db_path), exist_ok=True)

db = SqliteDatabase(db_path)
