from database.db import get_db_connection
import json


class AuditModel:
    """Modelo para la tabla AuditLog."""

    @staticmethod
    def registrar(usuario_id, accion, tabla_afectada, registro_id=None, detalles=None):
        """Registrar una acción en el log de auditoría."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            detalles_str = json.dumps(detalles, ensure_ascii=False) if isinstance(detalles, dict) else detalles
            cursor.execute("""
                INSERT INTO AuditLog (usuario_id, accion, tabla_afectada, registro_id, detalles)
                VALUES (?, ?, ?, ?, ?)
            """, (usuario_id, accion, tabla_afectada, registro_id, detalles_str))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error en auditoría: {e}")
        finally:
            conn.close()

    @staticmethod
    def listar(limit=50):
        """Listar últimos registros de auditoría."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT TOP {limit} a.*, u.nombre_completo AS usuario_nombre
                FROM AuditLog a
                LEFT JOIN Usuarios u ON a.usuario_id = u.id
                ORDER BY a.fecha DESC
            """)
            rows = cursor.fetchall()
            return [{
                'id': r.id,
                'usuario_id': r.usuario_id,
                'usuario_nombre': r.usuario_nombre,
                'accion': r.accion,
                'tabla_afectada': r.tabla_afectada,
                'registro_id': r.registro_id,
                'detalles': r.detalles,
                'fecha': str(r.fecha)
            } for r in rows]
        finally:
            conn.close()
