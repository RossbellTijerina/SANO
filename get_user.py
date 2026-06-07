import pyodbc
conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=SANO_DB;Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT TOP 1 id, username FROM Usuarios")
user = cursor.fetchone()
if user:
    print(f"User ID: {user[0]}, Username: {user[1]}")
else:
    print("No users found")
conn.close()
