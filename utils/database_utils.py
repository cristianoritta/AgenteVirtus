import os

def get_database_info():
    """Obtém informações sobre o banco de dados fixo"""
    path = 'instance/agente_virtus.db'
    
    if not os.path.exists(path):
        return {
            'path': path,
            'exists': False,
            'size': 0,
            'size_formatted': '0 B'
        }
    
    size = os.path.getsize(path)
    size_formatted = format_file_size(size)
    
    return {
        'path': path,
        'exists': True,
        'size': size,
        'size_formatted': size_formatted
    }

def format_file_size(size_bytes):
    """Formata o tamanho do arquivo em formato legível"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"
