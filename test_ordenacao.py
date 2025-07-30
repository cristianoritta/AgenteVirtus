#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de teste para verificar a ordenação baseada nas conexões
"""

def determinar_ordem_execucao(nodes, connections):
    """Determina a ordem correta de execução baseada nas conexões"""
    # Criar um grafo direcionado
    grafo = {}
    nos_entrada = set()
    nos_saida = set()
    
    # Inicializar o grafo
    for node in nodes:
        grafo[node['id']] = {'dependencias': set(), 'dependentes': set()}
    
    # Processar conexões
    for connection in connections:
        start_node = connection['startNode']
        end_node = connection['endNode']
        
        # Adicionar dependência
        grafo[end_node]['dependencias'].add(start_node)
        grafo[start_node]['dependentes'].add(end_node)
        
        nos_entrada.add(start_node)
        nos_saida.add(end_node)
    
    # Encontrar nós iniciais (que não têm dependências)
    nos_iniciais = set()
    for node_id, info in grafo.items():
        if not info['dependencias']:
            nos_iniciais.add(node_id)
    
    # Ordenação topológica
    ordem_execucao = []
    nos_processados = set()
    
    def processar_no(node_id):
        if node_id in nos_processados:
            return
        
        # Verificar se todas as dependências foram processadas
        for dep in grafo[node_id]['dependencias']:
            if dep not in nos_processados:
                return
        
        ordem_execucao.append(node_id)
        nos_processados.add(node_id)
        
        # Processar dependentes
        for dep in grafo[node_id]['dependentes']:
            processar_no(dep)
    
    # Processar todos os nós iniciais
    for node_id in nos_iniciais:
        processar_no(node_id)
    
    # Se ainda há nós não processados, adicionar no final
    for node in nodes:
        if node['id'] not in ordem_execucao:
            ordem_execucao.append(node['id'])
    
    return ordem_execucao

def test_ordenacao():
    """Testa a ordenação com o exemplo fornecido"""
    
    # Layout de exemplo fornecido pelo usuário
    layout = {
        "nodes": [
            {"id": "node-1", "type": "trigger", "x": 101, "y": 93, "config": {"description": "Selecione uma planilha", "type": "planilha"}},
            {"id": "node-2", "type": "agent", "x": 624, "y": 155, "config": {"allowDelegation": True, "backstory": "Você é um analista de dados financeiros. Na planilha a seguir, você deve listar todas as pessoas que são \"Titular\" de uma conta bancária.", "goal": "Liste todos os Titulares", "role": "Analista de Dados"}},
            {"id": "node-3", "type": "formatoSaida", "x": 1356, "y": 196, "config": {"description": "Fim", "type": "texto"}},
            {"id": "node-4", "type": "guardrail", "x": 998, "y": 199, "config": {"name": "Lista", "rules": "A resposta deve conter apenas os nomes, sem NENHUMA explicação, comentário etc. Apenas a lista te nomes", "outputFormat": "Lista"}}
        ],
        "connections": [
            {"endNode": "node-2", "endPort": "in-1", "id": "connection-node-1-out-1-node-2-in-1", "startNode": "node-1", "startPort": "out-1"},
            {"id": "connection-node-2-out-1-node-4-in-1", "startNode": "node-2", "startPort": "out-1", "endNode": "node-4", "endPort": "in-1"},
            {"id": "connection-node-4-out-1-node-3-in-1", "startNode": "node-4", "startPort": "out-1", "endNode": "node-3", "endPort": "in-1"}
        ]
    }
    
    print("=== TESTE DE ORDENAÇÃO BASEADA EM CONEXÕES ===")
    print(f"Nós: {[node['id'] for node in layout['nodes']]}")
    print(f"Conexões: {[(conn['startNode'], conn['endNode']) for conn in layout['connections']]}")
    
    # Determinar ordem de execução
    ordem_execucao = determinar_ordem_execucao(layout['nodes'], layout['connections'])
    
    print(f"\nOrdem de execução: {ordem_execucao}")
    
    # Verificar se a ordem está correta
    ordem_esperada = ["node-1", "node-2", "node-4", "node-3"]
    
    if ordem_execucao == ordem_esperada:
        print("✅ Ordenação CORRETA!")
    else:
        print("❌ Ordenação INCORRETA!")
        print(f"Esperado: {ordem_esperada}")
        print(f"Obtido: {ordem_execucao}")
    
    # Mostrar fluxo de execução
    print(f"\nFluxo de execução:")
    for i, node_id in enumerate(ordem_execucao, 1):
        node = next((n for n in layout['nodes'] if n['id'] == node_id), None)
        if node:
            print(f"{i}. {node_id} ({node['type']})")
    
    return ordem_execucao == ordem_esperada

if __name__ == "__main__":
    test_ordenacao() 