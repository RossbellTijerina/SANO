from database.db import get_db_connection
from datetime import datetime, date


class OficioModel:
    """Modelo para la tabla Oficios."""

    @staticmethod
    def _row_to_dict(row):
        """Convertir fila de BD a diccionario."""
        return {
            'id': row.id,
            'anio': row.anio,
            'folio': row.folio,
            'expediente': row.expediente,
            'solicitante': row.solicitante,
            'asunto': row.asunto,
            'fecha': str(row.fecha) if row.fecha else None,
            'funcionario_id': row.funcionario_id,
            'funcionario_nombre': row.funcionario_nombre if hasattr(row, 'funcionario_nombre') else None,
            'estado': row.estado,
            'motivo_cancelacion': row.motivo_cancelacion,
            'creado_por': row.creado_por,
            'creado_por_nombre': row.creado_por_nombre if hasattr(row, 'creado_por_nombre') else None,
            'fecha_creacion': str(row.fecha_creacion) if row.fecha_creacion else None,
            'fecha_modificacion': str(row.fecha_modificacion) if row.fecha_modificacion else None
        }

    @staticmethod
    def obtener_siguiente_folio(anio):
        """Obtener el siguiente número de folio para un año dado."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ISNULL(MAX(folio), 0) + 1 AS siguiente_folio
                FROM Oficios WHERE anio = ?
            """, (anio,))
            row = cursor.fetchone()
            return row.siguiente_folio
        finally:
            conn.close()

    @staticmethod
    def crear(data, usuario_id):
        """Crear un nuevo oficio con folio auto-asignado."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            anio = data.get('anio', datetime.now().year)
            
            # Obtener siguiente folio dentro de la transacción
            cursor.execute("""
                SELECT ISNULL(MAX(folio), 0) + 1 AS siguiente_folio
                FROM Oficios WHERE anio = ?
            """, (anio,))
            folio = cursor.fetchone().siguiente_folio
            
            fecha = data.get('fecha', date.today().isoformat())
            funcionario_id = data.get('funcionario_id') or None
            
            cursor.execute("""
                INSERT INTO Oficios (anio, folio, expediente, solicitante, asunto, fecha, funcionario_id, creado_por)
                OUTPUT INSERTED.id, INSERTED.folio
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                anio, folio,
                data.get('expediente', ''),
                data['solicitante'],
                data.get('asunto', ''),
                fecha,
                funcionario_id,
                usuario_id
            ))
            row = cursor.fetchone()
            conn.commit()
            return {'id': row[0], 'folio': row[1], 'anio': anio}
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def listar(anio=None, page=1, per_page=20):
        """Listar oficios con paginación y filtro por año."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            
            where_clause = ""
            params = []
            if anio:
                where_clause = "WHERE o.anio = ?"
                params.append(anio)
            
            # Contar total
            cursor.execute(f"""
                SELECT COUNT(*) FROM Oficios o {where_clause}
            """, params)
            total = cursor.fetchone()[0]
            
            # Obtener registros
            cursor.execute(f"""
                SELECT o.*, 
                       f.nombre AS funcionario_nombre,
                       u.nombre_completo AS creado_por_nombre
                FROM Oficios o
                LEFT JOIN Funcionarios f ON o.funcionario_id = f.id
                LEFT JOIN Usuarios u ON o.creado_por = u.id
                {where_clause}
                ORDER BY o.anio DESC, o.folio DESC
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """, (*params, offset, per_page))
            
            rows = cursor.fetchall()
            oficios = [OficioModel._row_to_dict(r) for r in rows]
            
            return {
                'oficios': oficios,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        finally:
            conn.close()

    @staticmethod
    def buscar(filtros):
        """Búsqueda avanzada multicriterio."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            conditions = []
            params = []
            
            if filtros.get('anio'):
                conditions.append("o.anio = ?")
                params.append(int(filtros['anio']))
            
            if filtros.get('folio'):
                conditions.append("o.folio = ?")
                params.append(int(filtros['folio']))
            
            if filtros.get('expediente'):
                conditions.append("o.expediente LIKE ?")
                params.append(f"%{filtros['expediente']}%")
            
            if filtros.get('solicitante'):
                conditions.append("o.solicitante LIKE ?")
                params.append(f"%{filtros['solicitante']}%")
            
            if filtros.get('asunto'):
                conditions.append("o.asunto LIKE ?")
                params.append(f"%{filtros['asunto']}%")
            
            if filtros.get('fecha_desde'):
                conditions.append("o.fecha >= ?")
                params.append(filtros['fecha_desde'])
            
            if filtros.get('fecha_hasta'):
                conditions.append("o.fecha <= ?")
                params.append(filtros['fecha_hasta'])
            
            if filtros.get('funcionario_id'):
                conditions.append("o.funcionario_id = ?")
                params.append(int(filtros['funcionario_id']))
            
            if filtros.get('estado'):
                conditions.append("o.estado = ?")
                params.append(filtros['estado'])
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            
            cursor.execute(f"""
                SELECT o.*, 
                       f.nombre AS funcionario_nombre,
                       u.nombre_completo AS creado_por_nombre
                FROM Oficios o
                LEFT JOIN Funcionarios f ON o.funcionario_id = f.id
                LEFT JOIN Usuarios u ON o.creado_por = u.id
                {where_clause}
                ORDER BY o.anio DESC, o.folio DESC
            """, params)
            
            rows = cursor.fetchall()
            return [OficioModel._row_to_dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(oficio_id):
        """Obtener un oficio por su ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, 
                       f.nombre AS funcionario_nombre,
                       u.nombre_completo AS creado_por_nombre
                FROM Oficios o
                LEFT JOIN Funcionarios f ON o.funcionario_id = f.id
                LEFT JOIN Usuarios u ON o.creado_por = u.id
                WHERE o.id = ?
            """, (oficio_id,))
            row = cursor.fetchone()
            return OficioModel._row_to_dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def actualizar(oficio_id, data):
        """Actualizar un oficio existente (edición de registros)."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            fields = []
            values = []
            
            editable_fields = ['expediente', 'solicitante', 'asunto', 'funcionario_id']
            for field in editable_fields:
                if field in data:
                    fields.append(f'{field} = ?')
                    val = data[field]
                    if field == 'funcionario_id' and (val == '' or val is None):
                        val = None
                    values.append(val)
            
            if not fields:
                return False
            
            fields.append('fecha_modificacion = GETDATE()')
            values.append(oficio_id)
            
            query = f"UPDATE Oficios SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def cancelar(oficio_id, motivo):
        """Cancelar un oficio (baja lógica, solo Admin)."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Oficios 
                SET estado = 'CANCELADO', motivo_cancelacion = ?, fecha_modificacion = GETDATE()
                WHERE id = ? AND estado = 'ACTIVO'
            """, (motivo, oficio_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def estadisticas(anio=None):
        """Obtener estadísticas para el dashboard."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            current_year = anio or datetime.now().year
            
            # Total de oficios del año
            cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN estado = 'ACTIVO' THEN 1 ELSE 0 END) as activos,
                       SUM(CASE WHEN estado = 'CANCELADO' THEN 1 ELSE 0 END) as cancelados
                FROM Oficios WHERE anio = ?
            """, (current_year,))
            row = cursor.fetchone()
            totales = {
                'total': row.total,
                'activos': row.activos or 0,
                'cancelados': row.cancelados or 0
            }
            
            # Oficios del día
            cursor.execute("""
                SELECT COUNT(*) as hoy FROM Oficios 
                WHERE fecha = CAST(GETDATE() AS DATE) AND anio = ?
            """, (current_year,))
            totales['hoy'] = cursor.fetchone().hoy
            
            # Oficios por mes (para gráfica de barras)
            cursor.execute("""
                SELECT MONTH(fecha) as mes, COUNT(*) as cantidad
                FROM Oficios WHERE anio = ? AND estado = 'ACTIVO'
                GROUP BY MONTH(fecha) ORDER BY mes
            """, (current_year,))
            por_mes = [{'mes': r.mes, 'cantidad': r.cantidad} for r in cursor.fetchall()]
            
            # Últimos 10 oficios
            cursor.execute("""
                SELECT TOP 10 o.*, f.nombre AS funcionario_nombre, u.nombre_completo AS creado_por_nombre
                FROM Oficios o
                LEFT JOIN Funcionarios f ON o.funcionario_id = f.id
                LEFT JOIN Usuarios u ON o.creado_por = u.id
                WHERE o.anio = ?
                ORDER BY o.fecha_creacion DESC
            """, (current_year,))
            ultimos = [OficioModel._row_to_dict(r) for r in cursor.fetchall()]
            
            # Años disponibles
            cursor.execute("SELECT DISTINCT anio FROM Oficios ORDER BY anio DESC")
            anios = [r.anio for r in cursor.fetchall()]
            
            return {
                'totales': totales,
                'por_mes': por_mes,
                'ultimos_oficios': ultimos,
                'anios_disponibles': anios,
                'anio_actual': current_year
            }
        finally:
            conn.close()
