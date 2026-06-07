import pyodbc
from config import Config

def get_db_connection():
    """Obtener conexión a SQL Server."""
    conn = pyodbc.connect(Config.get_connection_string())
    conn.autocommit = False
    return conn

def init_db():
    """Inicializar la base de datos ejecutando el schema."""
    try:
        # Primero conectar sin base de datos para crearla
        conn_str = (
            f"DRIVER={Config.SQL_DRIVER};"
            f"SERVER={Config.SQL_SERVER};"
            f"Trusted_Connection=yes;"
        )
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        # Crear BD si no existe
        cursor.execute(f"""
            IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{Config.SQL_DATABASE}')
            BEGIN
                CREATE DATABASE {Config.SQL_DATABASE};
            END
        """)
        conn.close()
        
        # Ahora conectar a la BD y crear tablas
        conn = get_db_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Crear tabla Usuarios
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Usuarios')
            BEGIN
                CREATE TABLE Usuarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    username NVARCHAR(50) NOT NULL UNIQUE,
                    password_hash NVARCHAR(255) NOT NULL,
                    nombre_completo NVARCHAR(200) NOT NULL,
                    rol NVARCHAR(20) NOT NULL CHECK (rol IN ('Administrador', 'Capturista')),
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_modificacion DATETIME DEFAULT GETDATE()
                );
            END
        """)
        
        # Crear tabla Funcionarios
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Funcionarios')
            BEGIN
                CREATE TABLE Funcionarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    nombre NVARCHAR(200) NOT NULL,
                    cargo NVARCHAR(200),
                    departamento NVARCHAR(200),
                    activo BIT DEFAULT 1,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_modificacion DATETIME DEFAULT GETDATE()
                );
            END
        """)
        
        # Crear tabla Oficios
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Oficios')
            BEGIN
                CREATE TABLE Oficios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    anio INT NOT NULL,
                    folio INT NOT NULL,
                    expediente NVARCHAR(100),
                    solicitante NVARCHAR(200) NOT NULL,
                    asunto NVARCHAR(500),
                    fecha DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
                    funcionario_id INT NULL,
                    estado NVARCHAR(20) NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'CANCELADO')),
                    motivo_cancelacion NVARCHAR(500) NULL,
                    creado_por INT NOT NULL,
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_modificacion DATETIME DEFAULT GETDATE(),
                    CONSTRAINT FK_Oficios_Funcionario FOREIGN KEY (funcionario_id) REFERENCES Funcionarios(id),
                    CONSTRAINT FK_Oficios_Usuario FOREIGN KEY (creado_por) REFERENCES Usuarios(id),
                    CONSTRAINT UQ_Oficio_Anio_Folio UNIQUE (anio, folio)
                );
            END
        """)
        
        # Crear tabla AuditLog
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AuditLog')
            BEGIN
                CREATE TABLE AuditLog (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    usuario_id INT NOT NULL,
                    accion NVARCHAR(50) NOT NULL,
                    tabla_afectada NVARCHAR(50) NOT NULL,
                    registro_id INT,
                    detalles NVARCHAR(MAX),
                    fecha DATETIME DEFAULT GETDATE(),
                    CONSTRAINT FK_Audit_Usuario FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
                );
            END
        """)
        
        conn.close()
        print("Base de datos inicializada correctamente.")
        return True
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        return False
