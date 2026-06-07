from database.db import get_db_connection


class FuncionarioModel:
    """Modelo para la tabla Funcionarios."""

    @staticmethod
    def listar(solo_activos=True):
        """Listar funcionarios."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            where = "WHERE activo = 1" if solo_activos else ""
            cursor.execute(f"""
                SELECT id, nombre, cargo, departamento, activo, fecha_creacion, fecha_modificacion
                FROM Funcionarios {where} ORDER BY nombre
            """)
            rows = cursor.fetchall()
            return [{
                'id': r.id,
                'nombre': r.nombre,
                'cargo': r.cargo,
                'departamento': r.departamento,
                'activo': r.activo,
                'fecha_creacion': str(r.fecha_creacion),
                'fecha_modificacion': str(r.fecha_modificacion)
            } for r in rows]
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(func_id):
        """Obtener un funcionario por ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, cargo, departamento, activo, fecha_creacion
                FROM Funcionarios WHERE id = ?
            """, (func_id,))
            r = cursor.fetchone()
            if r:
                return {
                    'id': r.id, 'nombre': r.nombre, 'cargo': r.cargo,
                    'departamento': r.departamento, 'activo': r.activo,
                    'fecha_creacion': str(r.fecha_creacion)
                }
            return None
        finally:
            conn.close()

    @staticmethod
    def crear(data):
        """Crear un nuevo funcionario."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Funcionarios (nombre, cargo, departamento)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?)
            """, (data['nombre'], data.get('cargo', ''), data.get('departamento', '')))
            row = cursor.fetchone()
            conn.commit()
            return row[0] if row else None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def actualizar(func_id, data):
        """Actualizar un funcionario."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Funcionarios 
                SET nombre = ?, cargo = ?, departamento = ?, fecha_modificacion = GETDATE()
                WHERE id = ?
            """, (data['nombre'], data.get('cargo', ''), data.get('departamento', ''), func_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def eliminar(func_id):
        """Desactivar un funcionario (baja lógica)."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Funcionarios SET activo = 0, fecha_modificacion = GETDATE()
                WHERE id = ?
            """, (func_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def crear_defaults():
        """Crear funcionarios de ejemplo si no existen."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Funcionarios")
            count = cursor.fetchone()[0]
            if count == 0:
                funcionarios = [
                    ('Lic. Juan Pérez García', 'Delegado', 'Dirección General'),
                    ('Lic. María López Hernández', 'Subdelegada', 'Subdirección'),
                    ('C.P. Roberto Sánchez Díaz', 'Jefe de Área', 'Registro Público'),
                ]
                for f in funcionarios:
                    cursor.execute("""
                        INSERT INTO Funcionarios (nombre, cargo, departamento) VALUES (?, ?, ?)
                    """, f)
                conn.commit()
                print("Funcionarios de ejemplo creados.")
        except Exception as e:
            conn.rollback()
            print(f"Nota: {e}")
        finally:
            conn.close()
