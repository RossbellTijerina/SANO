import os

class Config:
    """Configuración principal de la aplicación SANO."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'sano-secret-key-2026-cancun')
    DEBUG = os.environ.get('FLASK_DEBUG', True)
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-sano-super-secret-key-2026')
    JWT_ACCESS_TOKEN_EXPIRES = 28800  # 8 horas en segundos
    
    # SQL Server - Windows Authentication
    SQL_SERVER = os.environ.get('SQL_SERVER', 'localhost')
    SQL_DATABASE = os.environ.get('SQL_DATABASE', 'SANO_DB')
    SQL_DRIVER = os.environ.get('SQL_DRIVER', '{ODBC Driver 17 for SQL Server}')
    
    @staticmethod
    def get_connection_string():
        return (
            f"DRIVER={Config.SQL_DRIVER};"
            f"SERVER={Config.SQL_SERVER};"
            f"DATABASE={Config.SQL_DATABASE};"
            f"Trusted_Connection=yes;"
        )
    
    # Backup
    BACKUP_DIR = r"C:\Temp\sano_backups"
