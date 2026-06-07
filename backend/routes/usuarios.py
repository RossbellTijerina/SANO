from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.usuario import UsuarioModel
from models.audit import AuditModel
from middleware.auth_middleware import admin_requerido

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('', methods=['GET'])
@admin_requerido
def listar():
    """Listar todos los usuarios (solo Admin)."""
    usuarios = UsuarioModel.listar()
    return jsonify(usuarios), 200


@usuarios_bp.route('', methods=['POST'])
@admin_requerido
def crear():
    """Crear un nuevo usuario (solo Admin)."""
    data = request.get_json()
    
    campos_requeridos = ['username', 'password', 'nombre_completo', 'rol']
    for campo in campos_requeridos:
        if not data.get(campo):
            return jsonify({'error': f'El campo {campo} es obligatorio'}), 400
    
    if data['rol'] not in ['Administrador', 'Capturista']:
        return jsonify({'error': 'El rol debe ser Administrador o Capturista'}), 400
    
    try:
        user_id_new = UsuarioModel.crear(
            data['username'], data['password'],
            data['nombre_completo'], data['rol']
        )
        admin_id = int(get_jwt_identity())
        AuditModel.registrar(admin_id, 'CREAR', 'Usuarios', user_id_new, f"Usuario creado: {data['username']}")
        return jsonify({'mensaje': 'Usuario creado', 'id': user_id_new}), 201
    except Exception as e:
        if 'UNIQUE' in str(e).upper() or 'duplicate' in str(e).lower():
            return jsonify({'error': 'El nombre de usuario ya existe'}), 409
        return jsonify({'error': str(e)}), 500


@usuarios_bp.route('/<int:user_id>', methods=['PUT'])
@admin_requerido
def actualizar(user_id):
    """Actualizar un usuario (solo Admin)."""
    data = request.get_json()
    try:
        admin_id = int(get_jwt_identity())
        exito = UsuarioModel.actualizar(user_id, data)
        if exito:
            AuditModel.registrar(admin_id, 'EDITAR', 'Usuarios', user_id, 'Usuario editado')
            return jsonify({'mensaje': 'Usuario actualizado'}), 200
        return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@usuarios_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_requerido
def eliminar(user_id):
    """Desactivar un usuario (solo Admin)."""
    try:
        admin_id = int(get_jwt_identity())
        if admin_id == user_id:
            return jsonify({'error': 'No puedes desactivar tu propio usuario'}), 400
        exito = UsuarioModel.eliminar(user_id)
        if exito:
            AuditModel.registrar(admin_id, 'ELIMINAR', 'Usuarios', user_id, 'Usuario desactivado')
            return jsonify({'mensaje': 'Usuario desactivado'}), 200
        return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
