from app import app
from config import db
from models.models import *

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()
        print("✅ Banco de dados inicializado com sucesso!")
        print("📋 Tabelas criadas:")
        
        # Lista as tabelas criadas
        inspector = db.inspect(db.engine)
        for table_name in inspector.get_table_names():
            print(f"   - {table_name}")
        
        # Cria usuário inicial se não existir
        try:
            criar_usuario_inicial()
            print("👤 Usuário inicial criado/verificado")
        except Exception as e:
            print(f"⚠️  Erro ao criar usuário inicial: {e}")

if __name__ == '__main__':
    init_database() 