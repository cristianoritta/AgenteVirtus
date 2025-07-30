# Sistema de Formulários Dinâmicos

## Visão Geral

O sistema de formulários dinâmicos permite aos usuários criar, configurar e gerenciar formulários personalizados com campos de diferentes tipos, validações e layouts responsivos.

## Funcionalidades Principais

### 1. Criação de Formulários
- **Nome e Descrição**: Defina o nome e descrição do formulário
- **Status**: Ative ou desative formulários
- **Interface Intuitiva**: Criação através de formulário simples

### 2. Configuração de Campos
- **Tipos de Campo Suportados**:
  - `text`: Campo de texto simples
  - `email`: Campo de email com validação
  - `password`: Campo de senha
  - `number`: Campo numérico
  - `date`: Seletor de data
  - `datetime`: Seletor de data e hora
  - `textarea`: Área de texto multilinhas
  - `select`: Lista suspensa
  - `checkbox`: Caixas de seleção múltipla
  - `radio`: Botões de opção única

- **Configurações de Campo**:
  - **Label**: Nome exibido para o usuário
  - **Nome do Campo**: Identificador único (HTML name)
  - **Placeholder**: Texto de exemplo
  - **Valor Padrão**: Valor inicial do campo
  - **Obrigatório**: Campo obrigatório ou opcional
  - **Tamanho da Coluna**: Layout responsivo (col-lg-12, col-lg-6, etc.)
  - **Opções**: Para campos select, radio e checkbox
  - **Validação**: Regex personalizada

### 3. Interface de Gerenciamento
- **Drag & Drop**: Reordene campos arrastando
- **Edição Inline**: Clique para editar campos
- **Visualização em Tempo Real**: Veja como o formulário ficará

### 4. Execução de Formulários
- **Interface Responsiva**: Adapta-se a diferentes tamanhos de tela
- **Validação Automática**: Validação HTML5 e customizada
- **Salvamento de Dados**: Dados salvos em JSON no banco

### 5. Visualização de Registros
- **DataTable**: Lista paginada e pesquisável
- **Detalhes Completos**: Modal com todos os dados
- **Exportação**: Funcionalidade de exportação (futuro)

## Estrutura do Banco de Dados

### Tabela: `formulario`
```sql
- id (Primary Key)
- nome (String, 200 chars)
- descricao (Text)
- ativo (Boolean, default True)
- usuario_id (Foreign Key)
- criado_em (DateTime)
- atualizado_em (DateTime)
```

### Tabela: `campo_formulario`
```sql
- id (Primary Key)
- formulario_id (Foreign Key)
- label (String, 200 chars)
- tipo (String, 50 chars)
- nome_campo (String, 100 chars)
- placeholder (String, 200 chars)
- valor_padrao (String, 500 chars)
- obrigatorio (Boolean, default False)
- tamanho_coluna (String, 20 chars)
- ordem (Integer)
- opcoes (Text - JSON)
- validacao (String, 200 chars)
- ativo (Boolean, default True)
```

### Tabela: `registro_formulario`
```sql
- id (Primary Key)
- formulario_id (Foreign Key)
- dados (Text - JSON)
- usuario_id (Foreign Key)
- criado_em (DateTime)
- atualizado_em (DateTime)
```

## Rotas da API

### Formulários
- `GET /formularios` - Lista todos os formulários
- `GET /formularios/novo` - Página de criação
- `POST /formularios/novo` - Criar formulário
- `GET /formularios/<id>/editar` - Página de edição
- `POST /formularios/<id>/editar` - Atualizar formulário
- `POST /formularios/<id>/excluir` - Excluir formulário

### Campos
- `GET /formularios/<id>/campos` - Gerenciar campos
- `POST /formularios/<id>/campos/adicionar` - Adicionar campo
- `POST /formularios/campos/<id>/editar` - Editar campo
- `POST /formularios/campos/<id>/excluir` - Excluir campo
- `POST /formularios/campos/reordenar` - Reordenar campos

### Execução
- `GET /formularios/<id>/executar` - Executar formulário
- `POST /formularios/<id>/salvar` - Salvar registro

### Registros
- `GET /formularios/<id>/registros` - Listar registros
- `POST /formularios/registros/<id>/excluir` - Excluir registro

### APIs
- `GET /api/formularios/<id>/campos` - API campos
- `GET /api/formularios/<id>/registros` - API registros

## Como Usar

### 1. Criar um Formulário
1. Acesse `/formularios`
2. Clique em "Novo Formulário"
3. Preencha nome, descrição e status
4. Clique em "Criar Formulário"

### 2. Configurar Campos
1. Na lista de formulários, clique no ícone de engrenagem
2. Clique em "Adicionar Campo"
3. Configure o tipo, label, validações, etc.
4. Salve o campo
5. Repita para todos os campos necessários

### 3. Executar Formulário
1. Na lista de formulários, clique no ícone de play
2. Preencha os campos
3. Clique em "Salvar Registro"

### 4. Ver Registros
1. Na lista de formulários, clique no ícone de banco de dados
2. Visualize todos os registros salvos
3. Clique em "Ver Dados" para detalhes

## Tecnologias Utilizadas

- **Backend**: Flask, SQLAlchemy
- **Frontend**: Bootstrap 5, JavaScript, DataTables
- **Drag & Drop**: SortableJS
- **Validação**: HTML5 + JavaScript
- **Banco**: MySQL/SQLite

## Recursos Avançados

### Validação Customizada
```javascript
// Exemplo de validação regex para CPF
pattern="^[0-9]{11}$"
```

### Layout Responsivo
- `col-lg-12`: Largura total
- `col-lg-6`: Meia largura
- `col-lg-4`: Um terço
- `col-lg-3`: Um quarto
- `col-lg-2`: Um sexto

### Opções para Campos Select/Radio/Checkbox
```
Opção 1
Opção 2
Opção 3
```

## Próximas Funcionalidades

- [ ] Exportação de dados (CSV, Excel)
- [ ] Templates de formulários
- [ ] Validação condicional
- [ ] Campos calculados
- [ ] Upload de arquivos
- [ ] Assinatura digital
- [ ] Notificações por email
- [ ] Relatórios avançados

## Manutenção

### Atualizar Banco de Dados
```bash
python update_db_formularios.py
```

### Verificar Tabelas
```sql
SHOW TABLES LIKE '%formulario%';
```

### Backup de Dados
```sql
-- Backup dos formulários
SELECT * FROM formulario;

-- Backup dos campos
SELECT * FROM campo_formulario;

-- Backup dos registros
SELECT * FROM registro_formulario;
``` 