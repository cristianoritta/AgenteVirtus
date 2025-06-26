from flask import Flask
import re

app = Flask(__name__)

# Registrar filtro customizado para quebras de linha
@app.template_filter('linebreaks')
def linebreaks_filter(text):
    """Converte quebras de linha em <br> tags"""
    if text is None:
        return ""
    return text.replace('\n', '<br>')

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
    
    # Substituir caracteres especiais por hífens
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    
    # Substituir espaços por hífens
    text = re.sub(r'[\s-]+', '-', text)
    
    # Remover hífens no início e fim
    text = text.strip('-')
    
    return text

def register_filters(app):
    """Registra todos os filtros customizados na aplicação Flask"""
    app.template_filter('linebreaks')(linebreaks_filter)
    app.template_filter('slugify')(slugify_filter)
