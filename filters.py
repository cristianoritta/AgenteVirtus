from flask import Flask
import json
import re
from datetime import datetime

app = Flask(__name__)

# Registrar filtro customizado para quebras de linha
@app.template_filter('linebreaks')
def linebreaks_filter(text):
    """Converte quebras de linha em <br> tags"""
    if text is None:
        return ""
    return text.replace('\n', '<br>')

# Registrar filtro customizado para JSON
@app.template_filter('from_json')
def from_json_filter(text):
    """Converte string JSON em objeto Python"""
    if text is None or text == "":
        return {}
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return {}

# Registrar filtro customizado para formatação de data
@app.template_filter('strftime')
def strftime_filter(date_value, format_string='%d/%m/%Y'):
    """Formata uma data usando strftime"""
    if date_value is None:
        return ""
    
    try:
        # Se for string, tentar converter para datetime
        if isinstance(date_value, str):
            # Tentar diferentes formatos de data
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%d/%m/%Y', '%d/%m/%Y %H:%M']:
                try:
                    date_value = datetime.strptime(date_value, fmt)
                    break
                except ValueError:
                    continue
            else:
                return date_value  # Se não conseguir converter, retorna o valor original
        
        # Se já for datetime, usar diretamente
        if isinstance(date_value, datetime):
            return date_value.strftime(format_string)
        
        return str(date_value)
    except Exception:
        return str(date_value)

# Registrar filtro customizado para slugify
@app.template_filter('slugify')
def slugify_filter(text):
    """Converte texto em formato slug (lowercase, sem acentos, com hífens)"""
    if text is None:
        return ""
    
    # Converter para string se não for
    text = str(text)
    
    # Converter para minúsculas
    text = text.lower()
    
    # Remover acentos (simplificado)
    import unicodedata
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    
    # Substituir espaços por hífens
    text = re.sub(r'[\s-]+', '-', text)
    
    # Remover hífens no início e fim
    text = text.strip('-')
    
    return text

def register_filters(app):
    """Registra todos os filtros customizados na aplicação Flask"""
    app.template_filter('linebreaks')(linebreaks_filter)
    app.template_filter('from_json')(from_json_filter)
    app.template_filter('strftime')(strftime_filter)
    app.template_filter('slugify')(slugify_filter)
