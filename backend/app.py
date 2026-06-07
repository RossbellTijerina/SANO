"""
SANO - Sistema de Asignación de Números de Oficio
Backend Flask API
"""
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database.db import init_db
from datetime import timedelta
import os

# Importar blueprints
from routes.auth import auth_bp
from routes.oficios import oficios_bp
from routes.funcionarios import funcionarios_bp
from routes.usuarios import usuarios_bp
from routes.reportes import reportes_bp
from routes.backup import backup_bp


def create_app():
    """Crear y configurar la aplicación Flask."""
    # Configurar rutas para servir frontend
    frontend_folder = os.path.join(os.path.dirname(__file__), '../frontend/dist/frontend/browser')
    
    app = Flask(__name__, 
                static_folder=frontend_folder,
                static_url_path='')
    
    # Configuración
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    
    # CORS - permitir peticiones desde cualquier origen en desarrollo
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # JWT
    jwt = JWTManager(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token expirado. Inicie sesión nuevamente.'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Token inválido.'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Token de acceso requerido.'}), 401
    
    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(oficios_bp, url_prefix='/api/oficios')
    app.register_blueprint(funcionarios_bp, url_prefix='/api/funcionarios')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(reportes_bp, url_prefix='/api/reportes')
    app.register_blueprint(backup_bp, url_prefix='/api/backup')
    
    # Ruta de salud
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'ok',
            'sistema': 'SANO - Sistema de Asignación de Números de Oficio',
            'version': '1.0.0'
        }), 200
    
    # Servir archivos estáticos del frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app


if __name__ == '__main__':
    # Inicializar base de datos
    print("=" * 60)
    print("  SANO - Sistema de Asignación de Números de Oficio")
    print("  Iniciando servidor backend...")
    print("=" * 60)
    
    print("\n[1/3] Inicializando base de datos...")
    init_db()
    
    print("[2/2] Creando datos por defecto...")
    from models.usuario import UsuarioModel
    from models.funcionario import FuncionarioModel
    UsuarioModel.crear_admin_default()
    FuncionarioModel.crear_defaults()
    
    print("[3/3] Iniciando servidor Flask...")
    app = create_app()
    print("\n✓ Servidor listo en http://localhost:5000")
    print("  Usuario: admin | Contraseña: admin123")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)