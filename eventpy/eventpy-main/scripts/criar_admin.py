import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import *
from config.database_config import db

email = input("Qual o email do admin? ")
try:
    user = Utilizador.get(Utilizador.email == email)
    user.is_admin = True
    user.save()
    print(f"Sucesso! {user.nome} agora é administrador.")
except Utilizador.DoesNotExist:
    print("Utilizador não encontrado.")