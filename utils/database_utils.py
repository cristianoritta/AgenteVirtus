import os
from models.models import SystemConfig

class DatabasePathManager:
    """Gerenciador do caminho do banco de dados"""
    
    DEFAULT_PATH = 'instance/agente_virtus.db'
    
    @classmethod
    def get_database_path(cls):
        """Obtém o caminho atual do banco de dados"""
        # Primeiro tenta buscar da configuração do sistema
        config_path = SystemConfig.get_config('database_path')
        if config_path and os.path.exists(config_path):
            return config_path
        
        # Se não encontrar na configuração, verifica o caminho padrão
        if os.path.exists(cls.DEFAULT_PATH):
            # Salva o caminho padrão na configuração
            SystemConfig.set_config('database_path', cls.DEFAULT_PATH, 'Caminho do arquivo do banco de dados')
            return cls.DEFAULT_PATH
        
        # Se não encontrar em nenhum lugar, retorna o padrão
        return cls.DEFAULT_PATH
    
    @classmethod
    def set_database_path(cls, new_path):
        """Define um novo caminho para o banco de dados"""
        # Verifica se o arquivo existe no novo caminho
        if not os.path.exists(new_path):
            raise FileNotFoundError(f"Arquivo de banco de dados não encontrado em: {new_path}")
        
        # Salva a nova configuração
        SystemConfig.set_config('database_path', new_path, 'Caminho do arquivo do banco de dados')
        return new_path
    
    @classmethod
    def validate_database_path(cls, path):
        """Valida se o caminho do banco de dados é válido"""
        if not path:
            return False, "Caminho não pode estar vazio"
        
        if not os.path.exists(path):
            return False, f"Arquivo não encontrado: {path}"
        
        if not path.endswith('.db'):
            return False, "Arquivo deve ter extensão .db"
        
        return True, "Caminho válido"
    
    @classmethod
    def get_database_info(cls):
        """Obtém informações sobre o banco de dados"""
        path = cls.get_database_path()
        
        if not os.path.exists(path):
            return {
                'path': path,
                'exists': False,
                'size': 0,
                'size_formatted': '0 B'
            }
        
        size = os.path.getsize(path)
        size_formatted = cls.format_file_size(size)
        
        return {
            'path': path,
            'exists': True,
            'size': size,
            'size_formatted': size_formatted
        }
    
    @staticmethod
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
