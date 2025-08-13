from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

# Configuração do banco de dados - fixo em instance/agente_virtus.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agente_virtus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de timeout e retry para APIs de IA
app.config['API_TIMEOUT'] = 120  # 2 minutos
app.config['API_RETRY_ATTEMPTS'] = 3
app.config['API_RETRY_DELAY'] = 2  # segundos entre tentativas
app.config['API_BACKOFF_FACTOR'] = 2  # multiplicador para delay exponencial

# Inicialização do banco de dados
db = SQLAlchemy(app) 