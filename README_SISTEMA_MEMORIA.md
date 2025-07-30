# Sistema de Memória para Conversas

Este sistema implementa um mecanismo completo de memória em banco de dados para gravar e recuperar conversas com a IA, incluindo chatbot e transcrições de áudio.

## 🗄️ Estrutura do Banco de Dados

### Tabelas Criadas

#### `conversa`
- **id**: Chave primária auto-incremento
- **hash_conversa**: Hash único de 64 caracteres para identificar a conversa
- **titulo**: Título descritivo da conversa
- **tipo_conversa**: Tipo da conversa ('chatbot', 'transcricao', etc.)
- **usuario_id**: ID do usuário (opcional, para futuras implementações)
- **ativa**: Status da conversa (True = ativa, False = encerrada)
- **criada_em**: Data/hora de criação
- **atualizada_em**: Data/hora da última atualização

#### `mensagem_conversa`
- **id**: Chave primária auto-incremento
- **conversa_id**: Chave estrangeira para a conversa
- **role**: Papel da mensagem ('user', 'assistant', 'system')
- **conteudo**: Conteúdo da mensagem
- **timestamp**: Data/hora da mensagem
- **ordem**: Ordem sequencial das mensagens na conversa

## 🔧 Funcionalidades Implementadas

### 1. Gerenciamento de Conversas
- ✅ Criação automática de conversas
- ✅ Geração de hash único para cada conversa
- ✅ Recuperação de conversas por ID ou hash
- ✅ Encerramento de conversas
- ✅ Atualização de títulos

### 2. Sistema de Mensagens
- ✅ Armazenamento sequencial de mensagens
- ✅ Diferenciação entre mensagens do usuário e da IA
- ✅ Manutenção do contexto histórico
- ✅ Limite configurável de mensagens para contexto

### 3. Integração com IA
- ✅ Chatbot com memória de conversa
- ✅ Transcrição de áudio com armazenamento
- ✅ Contexto histórico enviado para a IA
- ✅ Respostas da IA automaticamente salvas

### 4. Interface de Gerenciamento
- ✅ Listagem de conversas ativas
- ✅ Visualização detalhada de conversas
- ✅ Edição de títulos
- ✅ Encerramento de conversas
- ✅ Interface responsiva e moderna

## 🚀 Como Usar

### 1. Inicialização do Banco de Dados

Execute o script de inicialização:

```bash
python init_db.py
```

### 2. Acessando o Sistema

#### Via Interface Web
- Acesse `/conversas` para gerenciar conversas
- Use `/ferramentas/chatbot` para conversar com IA
- Use `/ferramentas/transcrever` para transcrições

#### Via API REST

**Listar conversas:**
```bash
GET /api/conversas
```

**Obter conversa específica:**
```bash
GET /api/conversa?conversa_id=1
GET /api/conversa?hash_conversa=abc123...
```

**Criar nova conversa:**
```bash
POST /api/conversa/criar
Content-Type: application/x-www-form-urlencoded

titulo=Nova Conversa&tipo_conversa=chatbot
```

**Atualizar título:**
```bash
POST /api/conversa/atualizar-titulo
Content-Type: application/x-www-form-urlencoded

conversa_id=1&titulo=Novo Título
```

**Encerrar conversa:**
```bash
POST /api/conversa/encerrar
Content-Type: application/x-www-form-urlencoded

conversa_id=1
```

### 3. Uso no Chatbot

O sistema automaticamente:
1. Cria uma nova conversa se não for fornecida
2. Armazena a mensagem do usuário
3. Envia o histórico para a IA
4. Armazena a resposta da IA
5. Retorna o ID e hash da conversa

**Exemplo de uso:**
```javascript
// Primeira mensagem (cria nova conversa)
fetch('/ferramentas/chatbot', {
    method: 'POST',
    body: new FormData(form)
})
.then(response => response.json())
.then(data => {
    // data.conversa_id e data.hash_conversa disponíveis
    console.log('Conversa ID:', data.conversa_id);
    console.log('Hash:', data.hash_conversa);
});

// Mensagens subsequentes (continua conversa)
const formData = new FormData();
formData.append('mensagem', 'Olá novamente');
formData.append('conversa_id', conversaId); // ou hash_conversa
```

### 4. Uso na Transcrição

Similar ao chatbot, mas para transcrições de áudio:

```javascript
const formData = new FormData();
formData.append('arquivo', audioFile);
formData.append('conversa_id', conversaId); // opcional

fetch('/ferramentas/transcrever', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Transcrição:', data.transcricao);
    console.log('Conversa ID:', data.conversa_id);
});
```

## 📊 Vantagens do Sistema

### 1. Persistência
- Todas as conversas são salvas permanentemente
- Recuperação de conversas antigas
- Histórico completo de interações

### 2. Contexto Inteligente
- A IA recebe o histórico da conversa
- Respostas mais contextualizadas
- Continuidade de conversas longas

### 3. Identificação Única
- Hash único para cada conversa
- ID numérico para referência interna
- Fácil compartilhamento de conversas

### 4. Flexibilidade
- Suporte a diferentes tipos de conversa
- Estrutura extensível para novos recursos
- API REST completa

### 5. Gerenciamento
- Interface web para administração
- Encerramento de conversas
- Edição de metadados

## 🔮 Próximas Melhorias

1. **Autenticação de Usuários**: Associar conversas a usuários específicos
2. **Exportação**: Exportar conversas em diferentes formatos
3. **Busca**: Buscar por conteúdo nas conversas
4. **Tags**: Sistema de tags para organizar conversas
5. **Backup**: Sistema de backup automático
6. **Limpeza**: Limpeza automática de conversas antigas
7. **Analytics**: Métricas e estatísticas de uso

## 🛠️ Arquivos Principais

- `models/models.py`: Definição das tabelas
- `services/ConversaService.py`: Lógica de negócio
- `controllers/ConversaController.py`: Controlador da API
- `controllers/IaController.py`: Integração com IA
- `controllers/FerramentasController.py`: Integração com ferramentas
- `templates/conversas/index.html`: Interface de gerenciamento
- `routes.py`: Definição das rotas
- `init_db.py`: Script de inicialização

## 📝 Exemplo de Uso Completo

```python
from services.ConversaService import ConversaService

# Criar nova conversa
conversa = ConversaService.criar_conversa(
    tipo_conversa='chatbot',
    titulo='Conversa sobre Python'
)

# Adicionar mensagens
ConversaService.adicionar_mensagem(conversa.id, 'user', 'Como usar list comprehensions?')
ConversaService.adicionar_mensagem(conversa.id, 'assistant', 'List comprehensions são...')

# Obter histórico para IA
historico = ConversaService.obter_mensagens_para_ia(conversa.id)

# Buscar conversa por hash
conversa = ConversaService.buscar_conversa_por_hash('abc123...')

# Encerrar conversa
ConversaService.encerrar_conversa(conversa.id)
```

O sistema está pronto para uso e pode ser facilmente estendido conforme necessário! 