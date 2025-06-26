# AgenteVirtus - Sistema de Agentes Inteligentes

## Descrição
Sistema de agentes inteligentes desenvolvido em Flask para análise e processamento de dados.

## Funcionalidades

### 1. Agentes Inteligentes
- Criação e gerenciamento de equipes de agentes
- Execução de tarefas automatizadas
- Interface visual (Canvas) para configuração de agentes
- Importação e exportação de configurações

### 2. Ferramentas

#### Transcrição de Áudio
- Upload de arquivos de áudio
- Transcrição automática usando IA (Groq)
- Correção automática de pontuação e formatação

#### Chatbot Inteligente
- Interface de chat moderna e responsiva
- Integração com IA para análise de transcrições
- Respostas detalhadas com opções de expandir/colapsar
- Botões de ação (refazer análise, copiar resposta)
- Indicador de digitação em tempo real
- Animações e efeitos visuais

## Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **IA**: Groq API (LLaMA 3.3 70B)
- **Banco de Dados**: SQLite
- **Estilização**: Bootstrap, CSS customizado

## Estrutura do Projeto

```
AgenteVirtus/
├── app.py                 # Aplicação principal Flask
├── config.py             # Configurações da aplicação
├── routes.py             # Definição de rotas
├── filters.py            # Filtros customizados para templates
├── controllers/          # Controladores da aplicação
│   ├── AgentesController.py
│   ├── FerramentasController.py
│   └── IaController.py
├── models/               # Modelos de dados
│   └── models.py
├── templates/            # Templates HTML
│   ├── layout/
│   ├── agentes/
│   └── ferramentas/
│       ├── chatbot.html
│       ├── transcrever.html
│       └── _partials/
│           └── chat_mensagem.html
└── static/              # Arquivos estáticos (CSS, JS, imagens)
```

## Configuração

1. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variáveis de ambiente**:
   Criar arquivo `.env` com:
   ```
   GROQ_API_KEY=sua_chave_api_aqui
   ```

3. **Executar a aplicação**:
   ```bash
   python app.py
   ```

## Funcionalidades do Chatbot

### Interface
- Design moderno com gradientes e animações
- Efeito de ondas no topo da interface
- Indicador de digitação animado
- Scroll automático para novas mensagens

### Funcionalidades
- **Mensagens do usuário**: Envio de perguntas via formulário
- **Respostas da IA**: Processamento via Groq API
- **Detalhes expandíveis**: Análises detalhadas com toggle
- **Ações rápidas**: 
  - Refazer análise
  - Copiar resposta
  - Expandir/colapsar detalhes

### Integração
- Comunicação AJAX com o backend
- Templates parciais para mensagens complexas
- Filtros customizados (slugify, linebreaks)
- Tratamento de erros robusto

## API Endpoints

### Ferramentas
- `GET/POST /ferramentas/transcrever` - Transcrição de áudio
- `GET/POST /ferramentas/chatbot` - Interface do chatbot
- `POST /ferramentas/chat_mensagem_partial` - Template parcial para mensagens

### Agentes
- `GET /agentesinteligentes/equipes` - Listar equipes
- `GET /agentesinteligentes/canva` - Interface de configuração
- `POST /agentesinteligentes/executar_tarefas/<id>` - Executar tarefas

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. 