import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import *
from config.database_config import db

try:
    db.connect()
    db.create_tables([
        Utilizador, 
        TipoResiduo, 
        PontoRecolha, 
        PontoRecolhaTiposResiduo,
        Notificacao, 
        Contato
    ])
    print("Tables created/verified successfully!")
except Exception as e:
    print(f"Note: {e}")
finally:
    db.close()
