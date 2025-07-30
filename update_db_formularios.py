#!/usr/bin/env python3
"""
Script para atualizar o banco de dados e adicionar o campo menu_ordem aos formulários
"""

from config import app, db
from models.models import Formulario

def atualizar_formularios():
    """Atualiza os formulários existentes com menu_ordem"""
    with app.app_context():
        try:
            # Busca todos os formulários
            formularios = Formulario.query.all()
            
            print(f"Encontrados {len(formularios)} formulários")
            
            # Atualiza cada formulário com menu_ordem baseado no ID
            for i, formulario in enumerate(formularios, 1):
                if formulario.menu_ordem is None:
                    formulario.menu_ordem = i
                    print(f"Atualizando formulário '{formulario.nome}' com menu_ordem = {i}")
            
            # Commit das alterações
            db.session.commit()
            print("✅ Banco de dados atualizado com sucesso!")
            
            # Lista os formulários atualizados
            print("\n📋 Formulários no menu:")
            formularios_menu = Formulario.query.filter(
                Formulario.ativo == True,
                Formulario.menu_ordem > 0
            ).order_by(Formulario.menu_ordem).all()
            
            for formulario in formularios_menu:
                print(f"  {formulario.menu_ordem}. {formulario.nome}")
                
        except Exception as e:
            print(f"❌ Erro ao atualizar banco de dados: {e}")
            db.session.rollback()

if __name__ == '__main__':
    atualizar_formularios() 