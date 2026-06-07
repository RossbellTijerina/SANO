from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.usuario import UsuarioModel
from models.audit import AuditModel
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Autenticar usuario y devolver JWT."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Se requieren username y password'}), 400
    
    usuario = UsuarioModel.autenticar(data['username'], data['password'])
    
    if not usuario:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Crear token JWT con claims adicionales
    additional_claims = {
        'rol': usuario['rol'],
        'nombre': usuario['nombre_completo']
    }
    access_token = create_access_token(
        identity=str(usuario['id']),
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=8)
    )
    
    # Registrar en auditoría
    AuditModel.registrar(usuario['id'], 'LOGIN', 'Usuarios', usuario['id'], 'Inicio de sesión exitoso')
    
    return jsonify({
        'access_token': access_token,
        'usuario': usuario
    }), 200


@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil():
    """Obtener perfil del usuario autenticado."""
    user_id = int(get_jwt_identity())
    usuario = UsuarioModel.obtener_por_id(user_id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(usuario), 200
