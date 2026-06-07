-- ============================================
-- SANO - Sistema de Asignación de Números de Oficio
-- Script de creación de Base de Datos
-- ============================================

-- Crear la base de datos
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SANO_DB')
BEGIN
    CREATE DATABASE SANO_DB;
END
GO

USE SANO_DB;
GO

-- ============================================
-- Tabla: Usuarios
-- ============================================
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
GO

-- ============================================
-- Tabla: Funcionarios
-- ============================================
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
GO

-- ============================================
-- Tabla: Oficios
-- ============================================
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
GO

-- ============================================
-- Tabla: AuditLog
-- ============================================
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
GO

-- ============================================
-- Insertar usuario administrador por defecto
-- Password: admin123 (hash bcrypt)
-- ============================================
IF NOT EXISTS (SELECT * FROM Usuarios WHERE username = 'admin')
BEGIN
    INSERT INTO Usuarios (username, password_hash, nombre_completo, rol)
    VALUES ('admin', 'PLACEHOLDER_HASH', 'Administrador del Sistema', 'Administrador');
END
GO

-- ============================================
-- Insertar algunos funcionarios de ejemplo
-- ============================================
IF NOT EXISTS (SELECT * FROM Funcionarios WHERE nombre = 'Lic. Juan Pérez García')
BEGIN
    INSERT INTO Funcionarios (nombre, cargo, departamento)
    VALUES 
        ('Lic. Juan Pérez García', 'Delegado', 'Dirección General'),
        ('Lic. María López Hernández', 'Subdelegada', 'Subdirección'),
        ('C.P. Roberto Sánchez Díaz', 'Jefe de Área', 'Registro Público');
END
GO

PRINT 'Base de datos SANO_DB creada exitosamente.';
GO
