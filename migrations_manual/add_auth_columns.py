"""
Migração para adicionar colunas de autenticação ao modelo Usuario
"""
from config import app, db
from models.models import Usuario
from werkzeug.security import generate_password_hash

def upgrade():
    """Adiciona as colunas de autenticação"""
    with app.app_context():
        # Adiciona as novas colunas
        with db.engine.connect() as connection:
            connection.execute(db.text("""
                ALTER TABLE usuario 
                ADD COLUMN senha VARCHAR(255) NOT NULL DEFAULT ''
            """))
            connection.execute(db.text("""
                ALTER TABLE usuario 
                ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
            """))
            connection.execute(db.text("""
                ALTER TABLE usuario 
                ADD COLUMN temporary_token VARCHAR(255) UNIQUE
            """))
            connection.execute(db.text("""
                ALTER TABLE usuario 
                ADD COLUMN token_expira_em DATETIME
            """))
            connection.commit()
        
        # Atualiza o usuário admin existente
        admin = Usuario.query.filter_by(email='admin@admin.com').first()
        if admin:
            admin.senha = generate_password_hash('admin123')
            admin.is_admin = True
            db.session.commit()
        
        print("Migração concluída: colunas de autenticação adicionadas")

def downgrade():
    """Remove as colunas de autenticação"""
    with app.app_context():
        with db.engine.connect() as connection:
            connection.execute(db.text("""
                ALTER TABLE usuario 
                DROP COLUMN senha
            """))
            connection.execute(db.text("""
                ALTER TABLE usuario 
                DROP COLUMN is_admin
            """))
            connection.execute(db.text("""
                ALTER TABLE usuario 
                DROP COLUMN temporary_token
            """))
            connection.execute(db.text("""
                ALTER TABLE usuario 
                DROP COLUMN token_expira_em
            """))
            connection.commit()
        print("Migração revertida: colunas de autenticação removidas")

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'down':
        downgrade()
    else:
        upgrade() 