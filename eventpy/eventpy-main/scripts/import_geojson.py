#!/usr/bin/env python3
"""
Script para importar pontos de recolha do ficheiro GeoJSON para a base de dados
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import PontoRecolha
from config.database_config import db
from datetime import datetime

def mapear_tipo_ponto(tipo_desc):
    """Mapear os tipos do GeoJSON para os tipos do nosso modelo"""
    mapeamento = {
        'EcoIlha': 'ecocentro',
        'Ecoilha Bilateral': 'ecocentro',
        'Ecoilha Ecoponto': 'ecocentro',
        'Ecoilha Subterrânea': 'ecocentro',
        'Ecoponto de superfície': 'ecocentro',
        'Suporte Fixação Contentores Select': 'recolha_municipal',
        'Vidrão': 'centro_rececao',
        'Vidrão subterrâneo': 'centro_rececao'
    }
    return mapeamento.get(tipo_desc, 'recolha_municipal')

def gerar_horario_por_tipo(tipo_desc):
    """Gerar horário padrão baseado no tipo de ponto"""
    if 'subterrânea' in tipo_desc.lower() or 'subterranea' in tipo_desc.lower():
        return '00:00', '23:59', '24/7'
    elif 'ecoponto' in tipo_desc.lower():
        return '08:00', '20:00', 'Todos os dias'
    else:
        return '09:00', '18:00', '2ª a 6ª'

def importar_geojson_para_db():
    """Importar pontos do GeoJSON para a base de dados"""
    
    # Conectar à base de dados
    db.connect()
    
    # Limpar pontos existentes
    print("A limpar pontos existentes...")
    PontoRecolha.delete().execute()
    
    # Ler o ficheiro GeoJSON
    print("A ler ficheiro GeoJSON...")
    geojson_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               'data', 'Amb_Reciclagem_-1582428838483285583.geojson')
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Importar cada feature
    pontos_importados = 0
    erros = 0
    
    for feature in data['features']:
        try:
            props = feature['properties']
            geometry = feature['geometry']
            
            # Extrair coordenadas (GeoJSON usa [longitude, latitude])
            longitude = geometry['coordinates'][0]
            latitude = geometry['coordinates'][1]
            
            # Mapear tipo
            tipo_desc = props.get('TPRS_DESC', 'Desconhecido')
            tipo_ponto = mapear_tipo_ponto(tipo_desc)
            
            # Gerar horário padrão
            horario_abertura, horario_fecho, dias_funcionamento = gerar_horario_por_tipo(tipo_desc)
            
            # Criar o ponto
            ponto = PontoRecolha.create(
                nome=f"Ponto de {tipo_desc}",
                morada=props.get('TOP_MOD_1', 'Endereço não disponível'),
                freguesia=props.get('FRE_AB', 'Freguesia não disponível'),
                bairro=props.get('PRSL_LOCAL', None),
                latitude=latitude,
                longitude=longitude,
                horario_abertura=horario_abertura,
                horario_fecho=horario_fecho,
                dias_funcionamento=dias_funcionamento,
                tipo_ponto=tipo_ponto,
                telefone=None,
                email=None,
                website=None,
                observacoes=f"Tipo: {tipo_desc} | Código: {props.get('COD_SIG', 'N/A')}"
            )
            
            pontos_importados += 1
            
            if pontos_importados % 100 == 0:
                print(f"Importados {pontos_importados} pontos...")
                
        except Exception as e:
            erros += 1
            print(f"Erro ao importar ponto {feature.get('id', 'desconhecido')}: {e}")
    
    print(f"\n=== IMPORTAÇÃO CONCLUÍDA ===")
    print(f"Pontos importados: {pontos_importados}")
    print(f"Erros: {erros}")
    
    # Notificar utilizadores sobre os novos pontos importados
    if pontos_importados > 0:
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from app import notificar_utilizadores_novo_ponto_recolha
            notificar_utilizadores_novo_ponto_recolha(None)  # Notificação genérica sobre importação em massa
            print(f"Notificações enviadas para utilizadores sobre {pontos_importados} novos pontos importados")
        except Exception as e:
            print(f"Erro ao enviar notificações: {e}")
    
    # Verificar estatísticas
    total = PontoRecolha.select().count()
    print(f"Total de pontos na base de dados: {total}")
    
    # Mostrar distribuição por tipo
    print("\nDistribuição por tipo:")
    from peewee import fn
    tipos_query = (PontoRecolha
                  .select(PontoRecolha.tipo_ponto, fn.COUNT(PontoRecolha.id).alias('count'))
                  .group_by(PontoRecolha.tipo_ponto))
    
    for item in tipos_query:
        print(f"  {item.tipo_ponto}: {item.count} pontos")
    
    # Fechar conexão
    db.close()

if __name__ == "__main__":
    importar_geojson_para_db()
