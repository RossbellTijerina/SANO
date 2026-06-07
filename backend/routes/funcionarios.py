from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.funcionario import FuncionarioModel
from models.audit import AuditModel
from middleware.auth_middleware import admin_requerido

funcionarios_bp = Blueprint('funcionarios', __name__)


@funcionarios_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    """Listar todos los funcionarios activos."""
    solo_activos = request.args.get('activos', 'true').lower() == 'true'
    funcionarios = FuncionarioModel.listar(solo_activos)
    return jsonify(funcionarios), 200


@funcionarios_bp.route('/<int:func_id>', methods=['GET'])
@jwt_required()
def obtener(func_id):
    """Obtener un funcionario por ID."""
    func = FuncionarioModel.obtener_por_id(func_id)
    if not func:
        return jsonify({'error': 'Funcionario no encontrado'}), 404
    return jsonify(func), 200


@funcionarios_bp.route('', methods=['POST'])
@admin_requerido
def crear():
    """Crear un nuevo funcionario (solo Admin)."""
    data = request.get_json()
    if not data or not data.get('nombre'):
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    
    try:
        func_id = FuncionarioModel.crear(data)
        user_id = int(get_jwt_identity())
        AuditModel.registrar(user_id, 'CREAR', 'Funcionarios', func_id, f"Funcionario creado: {data['nombre']}")
        return jsonify({'mensaje': 'Funcionario creado', 'id': func_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funcionarios_bp.route('/<int:func_id>', methods=['PUT'])
@admin_requerido
def actualizar(func_id):
    """Actualizar un funcionario (solo Admin)."""
    data = request.get_json()
    if not data or not data.get('nombre'):
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    
    try:
        user_id = int(get_jwt_identity())
        exito = FuncionarioModel.actualizar(func_id, data)
        if exito:
            AuditModel.registrar(user_id, 'EDITAR', 'Funcionarios', func_id, f"Funcionario editado: {data['nombre']}")
            return jsonify({'mensaje': 'Funcionario actualizado'}), 200
        return jsonify({'error': 'Funcionario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@funcionarios_bp.route('/<int:func_id>', methods=['DELETE'])
@admin_requerido
def eliminar(func_id):
    """Desactivar un funcionario (solo Admin)."""
    try:
        user_id = int(get_jwt_identity())
        exito = FuncionarioModel.eliminar(func_id)
        if exito:
            AuditModel.registrar(user_id, 'ELIMINAR', 'Funcionarios', func_id, 'Funcionario desactivado')
            return jsonify({'mensaje': 'Funcionario desactivado'}), 200
        return jsonify({'error': 'Funcionario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
