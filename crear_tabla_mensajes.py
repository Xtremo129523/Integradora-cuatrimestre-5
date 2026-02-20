import mysql.connector

# Configuración de conexión
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': '6382',
    'database': 'emprendedoress'
}

def crear_tabla_mensajes():
    try:
        # Conectar a la base de datos
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor(dictionary=True)

        print("📝 Creando tabla mensajes...")
        
        # Crear tabla mensajes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                remitente_tipo ENUM('usuario','admin') NOT NULL,
                contenido TEXT NOT NULL,
                leido BOOLEAN DEFAULT FALSE,
                fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                CONSTRAINT fk_mensajes_usuario
                    FOREIGN KEY (usuario_id)
                    REFERENCES usuarios(id)
                    ON DELETE CASCADE,
                
                INDEX idx_usuario_id (usuario_id),
                INDEX idx_fecha (fecha_creacion)
            ) ENGINE=InnoDB
        """)
        
        db.commit()
        print("✅ Tabla mensajes creada exitosamente")

        # Verificar que la tabla existe
        cursor.execute("SHOW TABLES LIKE 'mensajes'")
        tabla = cursor.fetchone()
        
        if tabla:
            print("✅ Tabla mensajes confirmada en la base de datos")
            
            # Mostrar estructura
            cursor.execute("DESCRIBE mensajes")
            columnas = cursor.fetchall()
            print("\n📋 Estructura de la tabla:")
            for col in columnas:
                print(f"  - {col['Field']}: {col['Type']}")
        else:
            print("❌ Error: tabla no encontrada")

        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"❌ Error en la base de datos: {err}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    crear_tabla_mensajes()
