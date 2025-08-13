#!/usr/bin/env python3
"""
Script de inicialização da aplicação
Configura o banco de dados e executa migrations necessárias
"""

import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import app, db

def init_app():
    """Inicializa a aplicação com configurações corretas"""
    
    with app.app_context():
        try:
            print("🚀 Inicializando AgenteVirtus...")
            
            # Criar todas as tabelas se não existirem
            db.create_all()
            print("✅ Tabelas do banco de dados criadas/verificadas")
            
            print("✅ Aplicação inicializada com sucesso!")
            print("📁 Banco de dados configurado para: sqlite:///agente_virtus.db")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar aplicação: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_app()
