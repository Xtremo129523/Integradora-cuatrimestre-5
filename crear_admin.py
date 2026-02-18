import mysql.connector

# Conexión a la base de datos
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="6382",
    database="emprendedoress",
    port=3307
)

cursor = db.cursor()

# Insertar usuario admin
try:
    cursor.execute("""
        INSERT INTO usuarios (correo, password, rol, estado, documentacion_completa) 
        VALUES ('admin@utacapulco.edu.mx', 'admin123', 'admin', 'aceptado', TRUE)
        ON DUPLICATE KEY UPDATE correo = correo
    """)
    db.commit()
    print("✓ Usuario administrador creado exitosamente")
    print("\n📧 Correo: admin@utacapulco.edu.mx")
    print("🔑 Contraseña: admin123")
except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    db.close()
