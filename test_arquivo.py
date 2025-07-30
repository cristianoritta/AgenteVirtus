#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para verificar a geração de arquivos
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.AgentesController import AgentesController

def test_gerar_arquivo():
    """Testa a geração de arquivos"""
    
    # Conteúdo de teste
    conteudo_teste = """
    Este é um teste de geração de arquivo.
    
    Conteúdo de exemplo:
    - Item 1
    - Item 2
    - Item 3
    
    Resultado da análise:
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    """
    
    print("=== TESTE DE GERAÇÃO DE ARQUIVOS ===")
    print(f"Conteúdo de teste: {len(conteudo_teste)} caracteres")
    
    # Testar diferentes formatos
    formatos = ['texto', 'word', 'csv', 'markdown', 'json']
    
    for formato in formatos:
        try:
            print(f"\n--- Testando formato: {formato} ---")
            
            nome_arquivo = f"teste_{formato}"
            arquivo_output, nome_arquivo_final, content_type = AgentesController.gerar_arquivo_saida(
                conteudo_teste, formato, nome_arquivo, None
            )
            
            # Verificar se o arquivo foi gerado
            conteudo_gerado = arquivo_output.getvalue()
            print(f"✅ Arquivo gerado: {nome_arquivo_final}")
            print(f"   Content-Type: {content_type}")
            print(f"   Tamanho: {len(conteudo_gerado)} bytes")
            
            # Para arquivos de texto, mostrar os primeiros caracteres
            if content_type.startswith('text/'):
                try:
                    texto = conteudo_gerado.decode('utf-8')
                    print(f"   Primeiros 100 chars: {texto[:100]}...")
                except:
                    print("   Erro ao decodificar conteúdo")
                    
        except Exception as e:
            print(f"❌ Erro ao gerar arquivo {formato}: {e}")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_gerar_arquivo() 