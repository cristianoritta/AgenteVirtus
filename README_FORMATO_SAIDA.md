# Formato de Saída - AgenteVirtus

## Visão Geral

O nó **Formato de Saída** é um novo tipo de componente no AgenteVirtus que permite gerar arquivos de saída em diferentes formatos a partir do resultado do processamento dos agentes.

## Tipos de Formato Suportados

### 1. Texto (.txt)
- Arquivo de texto simples
- Codificação UTF-8
- Ideal para saídas em texto puro

### 2. Word (.docx)
- Documento Microsoft Word
- Inclui título e formatação básica
- Compatível com Microsoft Office e LibreOffice

### 3. CSV (.csv)
- Arquivo de valores separados por vírgula
- Cada linha do resultado vira uma linha no CSV
- Ideal para dados estruturados

### 4. PDF (.pdf)
- Documento PDF gerado com matplotlib
- Inclui título e formatação
- Visualização limpa e profissional

### 5. Mapa Mental (.pdf)
- Diagrama visual em formato de mapa mental
- Usa networkx para criar visualização
- Ideal para organizar ideias e conceitos

### 6. Markdown (.md)
- Arquivo Markdown com formatação
- Inclui título e conteúdo estruturado
- Compatível com editores Markdown e GitHub

### 7. JSON (.json)
- Arquivo JSON estruturado
- Se o conteúdo já for JSON válido, mantém a estrutura
- Caso contrário, cria objeto com timestamp

## Como Usar

### 1. Adicionar o Nó
1. Arraste o componente "Formato Saída" da barra lateral para o canvas
2. Configure o tipo de formato desejado no modal
3. Adicione uma descrição opcional

### 2. Conectar
- O nó Formato de Saída possui apenas uma porta de entrada
- Conecte a saída de um agente, tarefa ou guardrail à entrada do Formato de Saída

### 3. Executar
- Execute a equipe normalmente
- Se o Formato de Saída for o último nó, o arquivo será baixado automaticamente
- Se estiver no meio do fluxo, o arquivo estará disponível para download na página de resultados

## Configuração

### Modal de Configuração
- **Tipo de Formato**: Selecione o formato desejado (Texto, Word, CSV, PDF, Mapa Mental, Markdown, JSON)
- **Descrição**: Adicione uma descrição opcional (não será processada por IA)

### Nome do Arquivo
O arquivo gerado terá o nome no formato:
```
resultado_[Nome da Equipe]_[Data_Hora].[extensão]
```

Exemplo: `resultado_Equipe Analise_20241201_143022.pdf`

## Dependências

Para usar todos os formatos, as seguintes bibliotecas são necessárias:

```bash
pip install python-docx==0.8.11
pip install markdown==3.5.1
pip install matplotlib==3.7.2
pip install networkx==3.1
pip install pandas==2.0.3
```

## Exemplos de Uso

### Exemplo 1: Relatório em Word
1. Agente → Analisa dados
2. Guardrail → Formata resultado
3. **Formato de Saída (Word)** → Gera relatório .docx

### Exemplo 2: Dados em CSV
1. Agente → Extrai dados
2. Tarefa → Processa dados
3. **Formato de Saída (CSV)** → Gera arquivo .csv

### Exemplo 3: Mapa Mental
1. Agente → Gera conceitos
2. **Formato de Saída (Mapa Mental)** → Cria diagrama visual

## Limitações

- O nó Formato de Saída não pode ter portas de saída
- Apenas um formato pode ser selecionado por nó
- Para múltiplos formatos, use múltiplos nós Formato de Saída

## Tratamento de Erros

Se houver erro na geração do arquivo:
- O sistema tentará gerar um arquivo de texto com a mensagem de erro
- O conteúdo original será preservado
- Um log de erro será exibido no console

## Suporte

Para dúvidas ou problemas com o Formato de Saída, consulte a documentação completa do AgenteVirtus ou entre em contato com o suporte. 