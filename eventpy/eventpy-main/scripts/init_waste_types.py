#!/usr/bin/env python3
"""
Script to initialize waste types for REEE recycling
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import TipoResiduo
from config.database_config import db

def create_waste_types():
    """Create initial waste types if they don't exist"""
    
    waste_types = [
        {
            "nome": "Equipamentos Informáticos",
            "descricao": "Computadores, portáteis, tablets, monitores, teclados, ratos, impressoras",
            "icone": "fa-laptop",
            "exemplos": "Computador, Portátil, Tablet, Monitor, Teclado, Rato, Impressora, Scanner"
        },
        {
            "nome": "Telemóveis e Smartphones",
            "descricao": "Telemóveis, smartphones, carregadores, acessórios de comunicação",
            "icone": "fa-mobile",
            "exemplos": "Telemóvel, Smartphone, Carregador, Fones de ouvido, Cabo USB"
        },
        {
            "nome": "Equipamentos de Áudio e Vídeo",
            "descricao": "Televisores, rádios, leitores de DVD/CD, sistemas de som, câmaras",
            "icone": "fa-tv",
            "exemplos": "Televisão, Rádio, Leitor DVD, Leitor CD, Coluna, Câmara fotográfica"
        },
        {
            "nome": "Pequenos Eletrodomésticos",
            "descricao": "Aspiradores, máquinas de café, torradeiras, ferros de passar, batedeiras",
            "icone": "fa-blender",
            "exemplos": "Aspirador, Máquina de café, Torradeira, Ferro de passar, Batedeira, Liquidificador"
        },
        {
            "nome": "Grandes Eletrodomésticos",
            "descricao": "Frigoríficos, máquinas de lavar loiça/roupa, fogões, fornos, micro-ondas",
            "icone": "fa-snowflake",
            "exemplos": "Frigorífico, Congelador, Máquina de lavar roupa, Máquina de lavar loiça, Fogão, Forno, Micro-ondas"
        },
        {
            "nome": "Ferramentas Elétricas",
            "descricao": "Furadeiras, serras, lixadeiras, martelos pneumáticos, ferramentas de jardim",
            "icone": "fa-tools",
            "exemplos": "Furadeira, Serra elétrica, Lixadeira, Martelo pneumático, Cortador de relva"
        },
        {
            "nome": "Brinquedos e Equipamentos de Lazer",
            "descricao": "Consolas de videojogos, brinquedos eletrónicos, bicicletas elétricas, drones",
            "icone": "fa-gamepad",
            "exemplos": "PlayStation, Xbox, Nintendo, Brinquedos eletrónicos, Bicicleta elétrica, Drone"
        },
        {
            "nome": "Equipamentos Médicos",
            "descricao": "Termómetros digitais, tensiómetros, aparelhos de medição, equipamentos de saúde",
            "icone": "fa-heartbeat",
            "exemplos": "Termómetro digital, Tensiómetro, Glicómetro, Balança digital, Aparelho de oxigénio"
        },
        {
            "nome": "Lâmpadas e Luminárias",
            "descricao": "Lâmpadas LED, fluorescentes, luminárias, candeeiros, refletores",
            "icone": "fa-lightbulb",
            "exemplos": "Lâmpada LED, Lâmpada fluorescente, Candeeiro, Refletor, Luminária de teto"
        },
        {
            "nome": "Pilhas e Baterias",
            "descricao": "Pilhas, baterias recarregáveis, baterias de lítio, acumuladores",
            "icone": "fa-battery-full",
            "exemplos": "Pilha AA, Pilha AAA, Bateria de telemóvel, Bateria de portátil, Bateria de carro"
        }
    ]
    
    try:
        db.connect()
        
        existing_count = TipoResiduo.select().count()
        print(f"Existing waste types: {existing_count}")
        
        created_count = 0
        for waste_type in waste_types:
            # Check if already exists
            try:
                TipoResiduo.get(TipoResiduo.nome == waste_type["nome"])
                print(f"  - '{waste_type['nome']}' already exists")
            except TipoResiduo.DoesNotExist:
                TipoResiduo.create(**waste_type)
                print(f"  + Created '{waste_type['nome']}'")
                created_count += 1
        
        print(f"\nCreated {created_count} new waste types.")
        print(f"Total waste types: {TipoResiduo.select().count()}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_waste_types()
