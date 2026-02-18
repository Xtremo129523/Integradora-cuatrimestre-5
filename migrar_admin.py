import mysql.connector

# Configuración de conexión
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': '6382',
    'database': 'emprendedoress'
}

def migrar_admin():
    try:
        # Conectar a la base de datos
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor(dictionary=True)

        print("🔄 Iniciando migración de administradores...")

        # 1. Crear tabla administradores si no existe
        print("📝 Creando tabla administradores...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS administradores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(150) NOT NULL,
                correo VARCHAR(150) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                cargo VARCHAR(100),
                estado ENUM('activo','inactivo') DEFAULT 'activo',
                fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_admin_correo (correo)
            ) ENGINE=InnoDB
        """)
        db.commit()
        print("✅ Tabla administradores creada")

        # 2. Verificar si existe admin en usuarios
        print("🔍 Buscando administradores en tabla usuarios...")
        cursor.execute("SELECT * FROM usuarios WHERE rol = 'admin'")
        admins_usuarios = cursor.fetchall()

        # 3. Migrar admins de usuarios a administradores
        if admins_usuarios:
            print(f"📦 Encontrados {len(admins_usuarios)} administradores en tabla usuarios")
            for admin in admins_usuarios:
                # Verificar si ya existe en tabla administradores
                cursor.execute("SELECT * FROM administradores WHERE correo = %s", (admin['correo'],))
                existe = cursor.fetchone()
                
                if not existe:
                    # Insertar en tabla administradores
                    cursor.execute("""
                        INSERT INTO administradores (nombre, correo, password, cargo, estado)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        'Administrador',  # nombre por defecto
                        admin['correo'],
                        admin['password'],
                        'Coordinador General',
                        'activo'
                    ))
                    print(f"✅ Migrado: {admin['correo']}")
                else:
                    print(f"⚠️  Ya existe: {admin['correo']}")
            
            db.commit()
        else:
            print("⚠️  No se encontraron administradores en tabla usuarios")

        # 4. Insertar admin por defecto si no existe
        print("🔍 Verificando admin por defecto...")
        cursor.execute("SELECT * FROM administradores WHERE correo = 'admin@utacapulco.edu.mx'")
        admin_default = cursor.fetchone()
        
        if not admin_default:
            cursor.execute("""
                INSERT INTO administradores (nombre, correo, password, cargo, estado)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                'Administrador Principal',
                'admin@utacapulco.edu.mx',
                'admin123',
                'Coordinador General',
                'activo'
            ))
            db.commit()
            print("✅ Admin por defecto creado: admin@utacapulco.edu.mx / admin123")
        else:
            print("✅ Admin por defecto ya existe")

        # 5. Eliminar admins de tabla usuarios (opcional)
        print("\n⚠️  ¿Deseas eliminar los administradores de la tabla usuarios? (s/n)")
        respuesta = input().strip().lower()
        if respuesta == 's':
            cursor.execute("DELETE FROM usuarios WHERE rol = 'admin'")
            db.commit()
            print("✅ Administradores eliminados de tabla usuarios")
        else:
            print("⏭️  Conservando administradores en tabla usuarios")

        # Mostrar resumen
        print("\n" + "="*50)
        print("📊 RESUMEN DE MIGRACIÓN")
        print("="*50)
        cursor.execute("SELECT COUNT(*) as total FROM administradores")
        total_admins = cursor.fetchone()['total']
        print(f"Total de administradores: {total_admins}")
        
        cursor.execute("SELECT correo, nombre, cargo FROM administradores")
        admins = cursor.fetchall()
        for admin in admins:
            print(f"  - {admin['correo']} | {admin['nombre']} | {admin['cargo']}")
        
        print("="*50)
        print("✅ Migración completada exitosamente")

        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"❌ Error en la base de datos: {err}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    migrar_admin()
