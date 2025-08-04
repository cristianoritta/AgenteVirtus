from flask_migrate import Migrate
from config import app, db

migrate = Migrate(app, db)

# Este arquivo configura o Flask-Migrate para gerenciar as migrações do banco de dados
# Para usar, execute os seguintes comandos no terminal:
# 
# 1. Inicializar as migrações (primeira vez):
#    flask db init
#
# 2. Criar uma nova migração:
#    flask db migrate -m "descrição da migração"
#
# 3. Aplicar as migrações:
#    flask db upgrade
#
# 4. Reverter a última migração:
#    flask db downgrade