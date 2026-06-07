from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware.auth_middleware import admin_requerido
from models.audit import AuditModel
from config import Config
from datetime import datetime
import os
import subprocess

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('', methods=['POST'])
@admin_requerido
def crear_backup():
    """Crear un respaldo de la base de datos (solo Admin)."""
    try:
        # Crear directorio de backups si no existe
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(Config.BACKUP_DIR, f'SANO_DB_backup_{timestamp}.bak')
        
        # Ejecutar backup usando sqlcmd
        sql_command = f"BACKUP DATABASE [{Config.SQL_DATABASE}] TO DISK = N'{backup_file}' WITH FORMAT, INIT, NAME = N'SANO Backup {timestamp}'"
        
        result = subprocess.run(
            ['sqlcmd', '-S', Config.SQL_SERVER, '-E', '-b', '-Q', sql_command],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode == 0 and os.path.exists(backup_file):
            user_id = int(get_jwt_identity())
            AuditModel.registrar(
                user_id, 'BACKUP', 'Sistema', None,
                f"Respaldo creado: {backup_file}"
            )
            
            # Obtener tamaño del archivo
            size_mb = os.path.getsize(backup_file) / (1024 * 1024)
            
            return jsonify({
                'mensaje': 'Respaldo creado exitosamente',
                'archivo': backup_file,
                'tamano_mb': round(size_mb, 2),
                'fecha': timestamp
            }), 200
        else:
            return jsonify({
                'error': 'Error al crear el respaldo',
                'detalle': result.stderr
            }), 500
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'El respaldo tardó demasiado tiempo'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@backup_bp.route('/listar', methods=['GET'])
@admin_requerido
def listar_backups():
    """Listar los respaldos disponibles."""
    try:
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        backups = []
        for f in os.listdir(Config.BACKUP_DIR):
            if f.endswith('.bak'):
                filepath = os.path.join(Config.BACKUP_DIR, f)
                backups.append({
                    'archivo': f,
                    'tamano_mb': round(os.path.getsize(filepath) / (1024 * 1024), 2),
                    'fecha': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                })
        backups.sort(key=lambda x: x['fecha'], reverse=True)
        return jsonify(backups), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
