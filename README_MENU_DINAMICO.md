# Sistema de Menu Dinâmico - Agente Virtus

## Visão Geral

O sistema de menu dinâmico permite que equipes inteligentes sejam exibidas diretamente no menu lateral da aplicação, facilitando o acesso rápido às funcionalidades mais utilizadas.

## Como Funciona

### 1. Campo `menu_ordem`

O sistema utiliza o campo `menu_ordem` na tabela `EquipeInteligente`:
- **`menu_ordem > 0`**: Equipe aparece no menu dinâmico
- **`menu_ordem = NULL` ou `0`**: Equipe não aparece no menu
- **Ordem crescente**: Equipes são exibidas em ordem crescente do valor de `menu_ordem`

### 2. Carregamento Automático

O sistema carrega automaticamente os menus dinâmicos antes de cada requisição através do decorator `@app.before_request` no arquivo `app.py`.

### 3. Exibição no Menu

As equipes aparecem como submenus dentro da seção "Agentes" no menu lateral, organizadas por ordem.

## Funcionalidades

### Adicionar Equipe ao Menu

1. Acesse a página "Minhas Equipes"
2. Clique no botão "Adicionar" na coluna "Menu"
3. A equipe será automaticamente adicionada ao final da lista do menu

### Remover Equipe do Menu

1. Acesse a página "Minhas Equipes"
2. Clique no botão "Remover" na coluna "Menu"
3. Confirme a remoção
4. A equipe será removida do menu

### Acessar Equipe do Menu

1. No menu lateral, expanda a seção "Agentes"
2. Clique em "Equipes no Menu"
3. Selecione a equipe desejada
4. Você será direcionado para a página de execução da equipe

## Estrutura Técnica

### Arquivos Modificados

- **`app.py`**: Adicionado contexto global para carregar menus
- **`routes.py`**: Novas rotas para gerenciar menu dinâmico
- **`controllers/AgentesController.py`**: Métodos para gerenciar menu
- **`templates/layout/menu.html`**: Template atualizado para exibir menus dinâmicos
- **`templates/agentes/equipes.html`**: Interface para gerenciar menu

### Rotas Disponíveis

- `GET /agentesinteligentes/menu/<id>`: Acessar equipe do menu
- `POST /agentesinteligentes/equipe/<id>/adicionar-menu`: Adicionar ao menu
- `POST /agentesinteligentes/equipe/<id>/remover-menu`: Remover do menu
- `POST /agentesinteligentes/reordenar-menu`: Reordenar menu

### Dados de Teste

O sistema inclui dados de teste que são criados automaticamente na primeira execução:
- "Análise de Documentos" (ordem 1)
- "Relatórios Automáticos" (ordem 2)
- "Análise de Dados" (ordem 3)

## Personalização

### Alterar Ordem do Menu

Para alterar a ordem manualmente, você pode:
1. Editar diretamente no banco de dados o campo `menu_ordem`
2. Usar a API de reordenação (futura implementação)

### Estilo Visual

O menu dinâmico usa as classes CSS do Bootstrap e pode ser personalizado editando:
- `templates/layout/menu.html`
- `static/css/style.css`

## Troubleshooting

### Menu Não Aparece

1. Verifique se existem equipes com `menu_ordem > 0`
2. Verifique os logs da aplicação para erros
3. Confirme se o banco de dados está acessível

### Erro ao Adicionar/Remover

1. Verifique se a equipe existe
2. Confirme se o banco de dados está funcionando
3. Verifique os logs da aplicação

## Próximas Melhorias

- [ ] Interface drag-and-drop para reordenação
- [ ] Categorização de menus
- [ ] Ícones personalizados para cada equipe
- [ ] Permissões por usuário
- [ ] Cache de menus para melhor performance 