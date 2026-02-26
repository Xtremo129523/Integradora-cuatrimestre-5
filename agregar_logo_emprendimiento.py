#!/usr/bin/env python3
"""
Script para agregar la columna logo_emprendimiento a la tabla solicitudes
Ejecutar: python agregar_logo_emprendimiento.py
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos (misma que en app.py)
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "6382"
DB_NAME = "emprendedoress"
DB_PORT = 3307

def agregar_columna_logo():
    try:
        # Conexión a la base de datos
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        
        cursor = db.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='solicitudes' AND COLUMN_NAME='logo_emprendimiento'
        """)
        
        if cursor.fetchone():
            print("✓ La columna 'logo_emprendimiento' ya existe en la tabla 'solicitudes'")
            cursor.close()
            db.close()
            return True
        
        # Agregar la columna
        print("Agregando columna 'logo_emprendimiento' a la tabla 'solicitudes'...")
        cursor.execute("""
            ALTER TABLE solicitudes 
            ADD COLUMN logo_emprendimiento VARCHAR(255) 
            AFTER nombre_proyecto
        """)
        
        db.commit()
        print("✓ Columna 'logo_emprendimiento' agregada exitosamente")
        
        # Verificar que se agregó correctamente
        cursor.execute("""
            SELECT COLUMN_NAME, COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='solicitudes' AND COLUMN_NAME='logo_emprendimiento'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✓ Tipo de datos: {result[1]}")
        
        cursor.close()
        db.close()
        return True
        
    except Error as err:
        print(f"❌ Error en la base de datos: {err}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

if __name__ == "__main__":
    if agregar_columna_logo():
        print("\n✓ Migración completada exitosamente")
    else:
        print("\n❌ Error durante la migración")
