from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

# Configuração do banco de dados - usa o caminho correto
# O banco está em instance/agente_virtus.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agente_virtus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de timeout e retry para APIs de IA
app.config['API_TIMEOUT'] = 120  # 2 minutos
app.config['API_RETRY_ATTEMPTS'] = 3
app.config['API_RETRY_DELAY'] = 2  # segundos entre tentativas
app.config['API_BACKOFF_FACTOR'] = 2  # multiplicador para delay exponencial

# Inicialização do banco de dados
db = SQLAlchemy(app)

def configure_database_uri():
    """
    Configura dinamicamente a URI do banco de dados baseado nas configurações do sistema
    Esta função deve ser chamada após a inicialização do banco de dados
    """
    try:
        # Importar aqui para evitar importação circular
        from models.models import SystemConfig
        
        # Tentar obter a configuração do banco de dados
        config = SystemConfig.query.filter_by(chave='database_path').first()
        
        if config and config.valor:
            # Converter caminho do arquivo para URI do SQLAlchemy
            db_path = config.valor
            
            # Se o caminho não começar com 'sqlite:///', adicionar
            if not db_path.startswith('sqlite:///'):
                # Se o caminho contém 'instance/', remover para o SQLAlchemy
                if 'instance/' in db_path:
                    # Extrair apenas o nome do arquivo
                    db_filename = db_path.split('/')[-1]
                    db_uri = f'sqlite:///{db_filename}'
                else:
                    # Usar o caminho como está
                    db_uri = f'sqlite:///{db_path}'
                
                app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
                print(f"✅ Banco de dados configurado para: {db_uri}")
        
    except Exception as e:
        print(f"⚠️ Erro ao configurar banco dinamicamente: {e}")
        print("📁 Usando configuração padrão: sqlite:///agente_virtus.db") 