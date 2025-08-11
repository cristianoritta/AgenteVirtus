#!/usr/bin/env python3
"""
Script para executar a migration de configurações do sistema
"""

import os
import sys
from datetime import datetime

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import app, db
from models.models import SystemConfig

def run_migration():
    """Executa a migration para criar a tabela system_config"""
    
    with app.app_context():
        try:
            # Criar a tabela system_config se não existir
            db.create_all()
            
            # Verificar se já existe a configuração do banco de dados
            config = SystemConfig.query.filter_by(chave='database_path').first()
            
            if not config:
                # Criar configuração padrão
                config = SystemConfig(
                    chave='database_path',
                    valor='instance/agente_virtus.db',
                    descricao='Caminho do arquivo do banco de dados'
                )
                db.session.add(config)
                db.session.commit()
                print("✅ Configuração padrão do banco de dados criada!")
            else:
                print("✅ Configuração do banco de dados já existe!")
            
            print("✅ Migration executada com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao executar migration: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("🚀 Executando migration de configurações do sistema...")
    run_migration()
