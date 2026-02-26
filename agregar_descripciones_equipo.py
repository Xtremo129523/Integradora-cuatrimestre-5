import mysql.connector

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': '6382',
    'database': 'emprendedoress'
}

def agregar_descripciones():
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()

        print("📝 Agregando campos de descripcion del equipo...")

        campos = [
            ("alumno_descripcion", "VARCHAR(150)"),
            ("integrante_1_descripcion", "VARCHAR(150)"),
            ("integrante_2_descripcion", "VARCHAR(150)")
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
    agregar_descripciones()
