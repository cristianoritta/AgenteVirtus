#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para verificar a exclusão de execuções
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.models import ExecucaoEquipe, EquipeInteligente
from config import db

def test_exclusao():
    """Testa a exclusão de execuções"""
    
    print("=== TESTE DE EXCLUSÃO DE EXECUÇÕES ===")
    
    try:
        # Listar execuções existentes
        execucoes = ExecucaoEquipe.query.all()
        print(f"Total de execuções no banco: {len(execucoes)}")
        
        if execucoes:
            print("\nExecuções encontradas:")
            for execucao in execucoes[:5]:  # Mostrar apenas as 5 primeiras
                equipe = EquipeInteligente.query.get(execucao.equipe_id)
                print(f"ID: {execucao.id} | Equipe: {equipe.nome if equipe else 'N/A'} | Contexto: {execucao.contexto[:50]}...")
            
            # Testar exclusão da primeira execução
            primeira_execucao = execucoes[0]
            print(f"\nTestando exclusão da execução ID: {primeira_execucao.id}")
            
            # Simular exclusão (sem realmente excluir)
            print(f"Execução seria excluída: {primeira_execucao.id}")
            print(f"Equipe ID: {primeira_execucao.equipe_id}")
            print(f"Contexto: {primeira_execucao.contexto}")
            print(f"Resposta: {primeira_execucao.resposta[:100]}...")
            
            print("✅ Teste de exclusão simulado com sucesso!")
            
        else:
            print("❌ Nenhuma execução encontrada no banco de dados.")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    test_exclusao() 