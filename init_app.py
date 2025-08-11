#!/usr/bin/env python3
"""
Script de inicialização da aplicação
Configura o banco de dados dinamicamente e executa migrations necessárias
"""

import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import app, db, configure_database_uri
from models.models import SystemConfig

def init_app():
    """Inicializa a aplicação com configurações corretas"""
    
    with app.app_context():
        try:
            print("🚀 Inicializando AgenteVirtus...")
            
            # Criar todas as tabelas se não existirem
            db.create_all()
            print("✅ Tabelas do banco de dados criadas/verificadas")
            
            # Verificar se existe a configuração do banco de dados
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
                print("✅ Configuração padrão do banco de dados criada")
            else:
                print("✅ Configuração do banco de dados já existe")
            
            # Configurar o banco de dados dinamicamente
            configure_database_uri()
            
            print("✅ Aplicação inicializada com sucesso!")
            print("📁 Banco de dados configurado para:", app.config['SQLALCHEMY_DATABASE_URI'])
            
        except Exception as e:
            print(f"❌ Erro ao inicializar aplicação: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_app()
