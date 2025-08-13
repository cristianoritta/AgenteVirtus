from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from utils.database_utils import get_database_path

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

# Configuração do banco de dados - dinâmica baseada no tipo de execução
db_path = get_database_path()

print(f"Banco de dados configurado para: {db_path}")

# Garantir que o diretório do banco existe
db_dir = os.path.dirname(db_path)
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)
    print(f"✅ Diretório do banco criado: {db_dir}")

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de timeout e retry para APIs de IA
app.config['API_TIMEOUT'] = 120  # 2 minutos
app.config['API_RETRY_ATTEMPTS'] = 3
app.config['API_RETRY_DELAY'] = 2  # segundos entre tentativas
app.config['API_BACKOFF_FACTOR'] = 2  # multiplicador para delay exponencial

# Inicialização do banco de dados
db = SQLAlchemy(app) 