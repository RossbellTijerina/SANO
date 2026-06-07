from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection


class UsuarioModel:
    """Modelo para la tabla Usuarios."""

    @staticmethod
    def crear(username, password, nombre_completo, rol):
        """Crear un nuevo usuario."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            password_hash = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO Usuarios (username, password_hash, nombre_completo, rol)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?)
            """, (username, password_hash, nombre_completo, rol))
            row = cursor.fetchone()
            conn.commit()
            return row[0] if row else None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def autenticar(username, password):
        """Autenticar un usuario por username y password."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, nombre_completo, rol, activo
                FROM Usuarios WHERE username = ?
            """, (username,))
            row = cursor.fetchone()
            if row and row.activo and check_password_hash(row.password_hash, password):
                return {
                    'id': row.id,
                    'username': row.username,
                    'nombre_completo': row.nombre_completo,
                    'rol': row.rol
                }
            return None
        finally:
            conn.close()

    @staticmethod
    def obtener_por_id(user_id):
        """Obtener usuario por ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, nombre_completo, rol, activo, fecha_creacion
                FROM Usuarios WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row.id,
                    'username': row.username,
                    'nombre_completo': row.nombre_completo,
                    'rol': row.rol,
                    'activo': row.activo,
                    'fecha_creacion': str(row.fecha_creacion)
                }
            return None
        finally:
            conn.close()

    @staticmethod
    def listar():
        """Listar todos los usuarios."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, nombre_completo, rol, activo, fecha_creacion
                FROM Usuarios ORDER BY id
            """)
            rows = cursor.fetchall()
            return [{
                'id': r.id,
                'username': r.username,
                'nombre_completo': r.nombre_completo,
                'rol': r.rol,
                'activo': r.activo,
                'fecha_creacion': str(r.fecha_creacion)
            } for r in rows]
        finally:
            conn.close()

    @staticmethod
    def actualizar(user_id, data):
        """Actualizar datos de un usuario."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            fields = []
            values = []
            if 'nombre_completo' in data:
                fields.append('nombre_completo = ?')
                values.append(data['nombre_completo'])
            if 'rol' in data:
                fields.append('rol = ?')
                values.append(data['rol'])
            if 'activo' in data:
                fields.append('activo = ?')
                values.append(data['activo'])
            if 'password' in data and data['password']:
                fields.append('password_hash = ?')
                values.append(generate_password_hash(data['password']))
            
            fields.append('fecha_modificacion = GETDATE()')
            values.append(user_id)
            
            query = f"UPDATE Usuarios SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def eliminar(user_id):
        """Desactivar un usuario (baja lógica)."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Usuarios SET activo = 0, fecha_modificacion = GETDATE()
                WHERE id = ?
            """, (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def crear_admin_default():
        """Crear usuario admin por defecto si no existe."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE username = 'admin'")
            count = cursor.fetchone()[0]
            if count == 0:
                password_hash = generate_password_hash('admin123')
                cursor.execute("""
                    INSERT INTO Usuarios (username, password_hash, nombre_completo, rol)
                    VALUES ('admin', ?, 'Administrador del Sistema', 'Administrador')
                """, (password_hash,))
                conn.commit()
                print("Usuario admin creado (user: admin, pass: admin123)")
        except Exception as e:
            conn.rollback()
            print(f"Nota: {e}")
        finally:
            conn.close()
