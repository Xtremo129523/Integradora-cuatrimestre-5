import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': '6382',
    'database': 'emprendedoress'
}

def agregar_campos_fotos():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        print("📝 Agregando campos de fotos y asesores...")
        
        # Campos a agregar
        campos = [
            ("foto_alumno", "VARCHAR(255)"),
            ("asesor_academico_1", "VARCHAR(150)"),
            ("asesor_academico_2", "VARCHAR(150)"),
            ("integrante_1_nombre", "VARCHAR(150)"),
            ("integrante_1_foto", "VARCHAR(255)"),
            ("integrante_2_nombre", "VARCHAR(150)"),
            ("integrante_2_foto", "VARCHAR(255)"),
        ]
        
        for campo, tipo in campos:
            try:
                cursor.execute(f"ALTER TABLE solicitudes ADD COLUMN {campo} {tipo}")
                print(f"✅ Agregado: {campo}")
            except mysql.connector.Error as e:
                if "Duplicate column name" in str(e):
                    print(f"⚠️  {campo} ya existe")
                else:
                    raise
        
        db.commit()
        print("\n✅ Base de datos actualizada exitosamente")
        
        # Verificar columnas
        cursor.execute("DESCRIBE solicitudes")
        columnas = cursor.fetchall()
        print(f"\n📋 Total de columnas en solicitudes: {len(columnas)}")

        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"❌ Error en la base de datos: {err}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    agregar_campos_fotos()
