import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': '6382',
    'database': 'emprendedoress'
}

def agregar_campos_integrantes():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        print("📝 Agregando campos extra de integrantes...")

        campos = [
            ("integrante_3_nombre", "VARCHAR(150)"),
            ("integrante_3_foto", "VARCHAR(255)"),
            ("integrante_3_descripcion", "VARCHAR(150)"),
            ("integrante_4_nombre", "VARCHAR(150)"),
            ("integrante_4_foto", "VARCHAR(255)"),
            ("integrante_4_descripcion", "VARCHAR(150)"),
            ("integrante_5_nombre", "VARCHAR(150)"),
            ("integrante_5_foto", "VARCHAR(255)"),
            ("integrante_5_descripcion", "VARCHAR(150)")
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

        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"❌ Error en la base de datos: {err}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    agregar_campos_integrantes()
