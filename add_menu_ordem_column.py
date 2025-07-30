#!/usr/bin/env python3
"""
Script para adicionar a coluna menu_ordem à tabela formulario
"""

from config import app, db
from sqlalchemy import text

def adicionar_coluna_menu_ordem():
    """Adiciona a coluna menu_ordem à tabela formulario"""
    with app.app_context():
        try:
            # Verificar se a coluna já existe
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('formulario')]
            
            if 'menu_ordem' not in columns:
                print("Adicionando coluna menu_ordem à tabela formulario...")
                
                # Adicionar a coluna
                db.session.execute(text("ALTER TABLE formulario ADD COLUMN menu_ordem INTEGER"))
                db.session.commit()
                
                print("✅ Coluna menu_ordem adicionada com sucesso!")
            else:
                print("✅ Coluna menu_ordem já existe!")
            
            # Agora executar o script de atualização
            from update_db_formularios import atualizar_formularios
            atualizar_formularios()
            
        except Exception as e:
            print(f"❌ Erro ao adicionar coluna: {e}")
            db.session.rollback()

if __name__ == '__main__':
    adicionar_coluna_menu_ordem() 