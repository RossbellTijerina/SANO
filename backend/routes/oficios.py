from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.oficio import OficioModel
from models.audit import AuditModel
from middleware.auth_middleware import admin_requerido

oficios_bp = Blueprint('oficios', __name__)


@oficios_bp.route('', methods=['GET'])
@jwt_required()
def listar():
    """Listar oficios con paginación y filtro por año."""
    anio = request.args.get('anio', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    resultado = OficioModel.listar(anio=anio, page=page, per_page=per_page)
    return jsonify(resultado), 200


@oficios_bp.route('/buscar', methods=['GET'])
@jwt_required()
def buscar():
    """Búsqueda avanzada multicriterio."""
    filtros = {
        'anio': request.args.get('anio'),
        'folio': request.args.get('folio'),
        'expediente': request.args.get('expediente'),
        'solicitante': request.args.get('solicitante'),
        'asunto': request.args.get('asunto'),
        'fecha_desde': request.args.get('fecha_desde'),
        'fecha_hasta': request.args.get('fecha_hasta'),
        'funcionario_id': request.args.get('funcionario_id'),
        'estado': request.args.get('estado'),
    }
    # Eliminar filtros vacíos
    filtros = {k: v for k, v in filtros.items() if v}
    
    resultados = OficioModel.buscar(filtros)
    return jsonify({'oficios': resultados, 'total': len(resultados)}), 200


@oficios_bp.route('/siguiente-folio', methods=['GET'])
@jwt_required()
def siguiente_folio():
    """Obtener el siguiente número de folio para un año."""
    from datetime import datetime
    anio = request.args.get('anio', datetime.now().year, type=int)
    folio = OficioModel.obtener_siguiente_folio(anio)
    return jsonify({'anio': anio, 'siguiente_folio': folio}), 200


@oficios_bp.route('', methods=['POST'])
@jwt_required()
def crear():
    """Crear un nuevo oficio con folio auto-asignado."""
    data = request.get_json()
    
    if not data or not data.get('solicitante'):
        return jsonify({'error': 'El campo solicitante es obligatorio'}), 400
    
    user_id = int(get_jwt_identity())
    
    try:
        resultado = OficioModel.crear(data, user_id)
        
        # Registrar en auditoría
        AuditModel.registrar(
            user_id, 'CREAR', 'Oficios', resultado['id'],
            f"Oficio {resultado['anio']}-{resultado['folio']} creado"
        )
        
        return jsonify({
            'mensaje': f"Oficio creado exitosamente. Folio: {resultado['anio']}-{resultado['folio']}",
            'oficio': resultado
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@oficios_bp.route('/<int:oficio_id>', methods=['GET'])
@jwt_required()
def obtener(oficio_id):
    """Obtener un oficio por ID."""
    oficio = OficioModel.obtener_por_id(oficio_id)
    if not oficio:
        return jsonify({'error': 'Oficio no encontrado'}), 404
    return jsonify(oficio), 200


@oficios_bp.route('/<int:oficio_id>', methods=['PUT'])
@jwt_required()
def actualizar(oficio_id):
    """Actualizar un oficio existente (edición de registros)."""
    data = request.get_json()
    user_id = int(get_jwt_identity())
    
    try:
        exito = OficioModel.actualizar(oficio_id, data)
        if exito:
            AuditModel.registrar(
                user_id, 'EDITAR', 'Oficios', oficio_id,
                f"Oficio #{oficio_id} editado: {', '.join(data.keys())}"
            )
            return jsonify({'mensaje': 'Oficio actualizado correctamente'}), 200
        return jsonify({'error': 'Oficio no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@oficios_bp.route('/<int:oficio_id>', methods=['DELETE'])
@admin_requerido
def cancelar(oficio_id):
    """Cancelar un oficio (solo Administrador)."""
    data = request.get_json()
    motivo = data.get('motivo', '') if data else ''
    
    if not motivo:
        return jsonify({'error': 'Debe proporcionar un motivo de cancelación'}), 400
    
    user_id = int(get_jwt_identity())
    
    try:
        exito = OficioModel.cancelar(oficio_id, motivo)
        if exito:
            AuditModel.registrar(
                user_id, 'CANCELAR', 'Oficios', oficio_id,
                f"Oficio #{oficio_id} cancelado. Motivo: {motivo}"
            )
            return jsonify({'mensaje': 'Oficio cancelado correctamente'}), 200
        return jsonify({'error': 'Oficio no encontrado o ya cancelado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@oficios_bp.route('/estadisticas', methods=['GET'])
@jwt_required()
def estadisticas():
    """Obtener estadísticas para el dashboard."""
    anio = request.args.get('anio', type=int)
    stats = OficioModel.estadisticas(anio)
    return jsonify(stats), 200
