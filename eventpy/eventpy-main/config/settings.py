"""
Configurações principais da aplicação
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações base"""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Configurações de email
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    
    # Configurações da aplicação
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    TESTING = os.getenv("TESTING", "False").lower() == "true"
    
    # Configurações de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora

class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    DATABASE_NAME = "data/reciclagem_reee_dev.db"

class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    DATABASE_NAME = "data/reciclagem_reee.db"

class TestingConfig(Config):
    """Configurações de teste"""
    TESTING = True
    DATABASE_NAME = "data/reciclagem_reee_test.db"

# Configuração ativa
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
