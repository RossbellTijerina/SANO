from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt


def rol_requerido(rol):
    """Decorador para verificar que el usuario tenga el rol especificado."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('rol') != rol:
                return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_requerido(fn):
    """Decorador para verificar que el usuario sea Administrador."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('rol') != 'Administrador':
            return jsonify({'error': 'Se requieren permisos de Administrador'}), 403
        return fn(*args, **kwargs)
    return wrapper
