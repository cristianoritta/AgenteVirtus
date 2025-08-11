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

### Transcrição de Áudio
- Upload de arquivos de áudio
- Transcrição automática usando IA (Groq)
- Correção automática de pontuação e formatação

### Chatbot Inteligente
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
- **Banco de Dados**: SQLite com Flask-Migrate para controle de versão do schema
- **Estilização**: Bootstrap, CSS customizado

## Estrutura do Projeto

```
AgenteVirtus/
├── app.py                # Aplicação principal Flask
├── config.py             # Configurações da aplicação
├── routes.py             # Definição de rotas
├── filters.py            # Filtros customizados para templates
├── migrations.py         # Configuração do Flask-Migrate
├── migrations/           # Migrações do banco de dados
│   ├── versions/         # Arquivos de migração
│   ├── alembic.ini       # Configuração do Alembic
│   └── env.py            # Ambiente de migração
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

1. **Instalar o Python (preferencialmente até v. 3.11)**
   Acesse http://python.org/downloads/windows/
   (Versão 3.11.9: https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe)

   Siga os passos da instalação.
   *ATENÇÃO:* O python precisa ser colocado nas variáveis de ambiente do windows.

   Junto com o python, será instalado o gerenciador de pacotes *pip*

2. **Fazer download do código-fonte**
   No material de Aula 01, Módulo 4, da Pós-Graduação em Inteligência Artificial para Agentes da Lei, 
   você encontra o arquivo .zip com o código fonte. Verifique sempre a versão mais atualizada no grupo de alunos.

2.1 **Descompacte em uma pasta do seu computador**

2.2 **Acesse a pasta através do prompt de comando**
   - Abra a pasta no Windows Explorer
   - Na barra de endereço, digite *cmd*
   - Vai abrir o prompt de comando do windows (a janela preta)

2. **Criar um ambiente virtual**
   Crie um ambiente virtual com o python, para evitar conflito de versões das bibliotecas, com outras aplicações que você tenha
   ```bash
   python -m venv venv
   ```

   Isso faz com que uma pasta *venv* seja criada, com todas as versões das bibliotecas.
   No entanto, o ambiente virtual ainda não está ativo. Precisamos ativá-lo cada vez que for iniciar o programa

   ```bash
   venv\Scripts\activate.bat
   ```

   *Resultado:*
   ```bash
   C:\Users\Cristiano\Programação\AgenteVirtus>venv\Scripts\activate.bat
   (venv) C:\Users\Cristiano\Programação\AgenteVirtus>
   ```

   A indicação **(venv)** no início da linha indica que o ambiente virtual está ativo.

3. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente**:
   Criar arquivo `.env` com:
   ```
   GROQ_API_KEY=sua_chave_api_aqui
   ```

5. **Configurar o banco de dados**:
   O sistema utiliza Flask-Migrate para gerenciar as migrações do banco de dados. Execute os seguintes comandos:
   ```bash
   # Inicializar as migrações (primeira vez)
   flask db init

   # Criar uma nova migração após alterar os modelos
   flask db migrate -m "descrição da migração"

   # Aplicar as migrações pendentes
   flask db upgrade

   # Se necessário, reverter a última migração
   flask db downgrade
   ```

5.1 ** Atualização em 11/08/2025 **
   # Executar as migrations de atualização do banco de dados
   ```bash
   python run_migration.py
   ```

6. **Executar a aplicação**:
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

## LICENÇA DE SOFTWARE

### Termos e Condições de Uso

### 1. PROPRIEDADE INTELECTUAL
Este software e todo o código fonte associado são de propriedade exclusiva de Cristiano Ribeiro Ritta. Todos os direitos autorais, marcas registradas e outros direitos de propriedade intelectual permanecem com o proprietário.

### 2. AUTORIZAÇÃO DE USO
O uso deste software é permitido apenas para pessoas ou entidades que possuam autorização expressa do proprietário. A ausência de autorização prévia torna o uso ilegal e sujeito às penalidades da lei.
Estão autorizados, desde já:
- Inscritos com suas obrigações em dia na Pós-Graduação em Inteligência Artificial da DataVirtus;

### 3. DIREITOS CONCEDIDOS
Mediante autorização, os usuários podem:
- Utilizar o software para fins pessoais ou internos
- Realizar customizações e modificações necessárias
- Adaptar o software às suas necessidades específicas

### 4. RESTRIÇÕES DE USO

#### 4.1 Proibição de Comercialização
É **ESTRITAMENTE PROIBIDO**:
- Vender, licenciar ou comercializar este software no todo ou em parte
- Distribuir o software ou suas modificações com fins comerciais
- Oferecer o software como serviço comercial
- Incorporar este software em produtos comerciais
- Extrair partes do código fonte para uso em outros softwares comerciais
- Reutilizar componentes, algoritmos ou estruturas deste software em projetos comerciais
- Adaptar ou derivar código deste software para fins comerciais

### 5. DISTRIBUIÇÃO
A redistribuição deste software só é permitida com autorização expressa do proprietário e deve manter todos os avisos de copyright e esta licença.

### 6. MODIFICAÇÕES
Modificações são permitidas apenas para usuários autorizados e para uso próprio. Modificações não podem ser comercializadas ou distribuídas sem autorização expressa.

### 7. ISENÇÃO DE GARANTIA
Este software é fornecido "como está", sem garantias de qualquer tipo, expressas ou implícitas. O proprietário não se responsabiliza por danos decorrentes do uso deste software.

### 8. VIOLAÇÃO DA LICENÇA
O descumprimento dos termos desta licença resultará em:
- Revogação imediata da autorização de uso
- Ação legal por violação de direitos autorais
- Responsabilização por danos e prejuízos causados

<hr>
**© 2025. Todos os direitos reservados.**