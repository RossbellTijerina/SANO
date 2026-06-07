# -*- coding: utf-8 -*-
import pyodbc
from datetime import datetime
import random

conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=SANO_DB;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Get the admin user ID
cursor.execute("SELECT TOP 1 id FROM Usuarios WHERE username='admin'")
user_id = cursor.fetchone()[0]

# Check if data exists
cursor.execute("SELECT COUNT(*) FROM Oficios")
if cursor.fetchone()[0] == 0:
    print('Inserting demo data...')
    # Funcionario demo
    cursor.execute("INSERT INTO Funcionarios (nombre, cargo, departamento) VALUES ('Lic. Roberto Salazar', 'Director General', 'Registro Publico de la Propiedad')")
    cursor.execute("SELECT id FROM Funcionarios WHERE nombre='Lic. Roberto Salazar'")
    func_id = cursor.fetchone()[0]

    estados = ['ACTIVO', 'ACTIVO', 'ACTIVO', 'CANCELADO']
    # Insert for 2026
    for i in range(1, 41):
        estado = random.choice(estados)
        mes = random.randint(1, 4)
        dia = random.randint(1, 28)
        fecha = f'2026-{mes:02d}-{dia:02d} 10:00:00'
        
        cursor.execute('''
            INSERT INTO Oficios (anio, folio, expediente, solicitante, asunto, fecha, estado, funcionario_id, creado_por)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (2026, i, f'QROO/CAN/RPP/2026/{i:04d}', f'Ciudadano Ejemplo {i}', f'Solicitud de certificacion de libertad de gravamen para el predio {i}.', fecha, estado, func_id, user_id))
    
    conn.commit()
    print('Demo data inserted successfully.')
else:
    print('Data already exists.')

conn.close()
