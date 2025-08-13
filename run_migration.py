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

def run_migration():
    """Executa a migration para criar a tabela system_config"""
    
    with app.app_context():
        try:
            # Criar a tabela system_config se não existir
            db.create_all()
            
            print("✅ Migration executada com sucesso!")
            print("📁 Banco de dados configurado para: instance/agente_virtus.db")
            
        except Exception as e:
            print(f"❌ Erro ao executar migration: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("🚀 Executando migration de configurações do sistema...")
    run_migration()
