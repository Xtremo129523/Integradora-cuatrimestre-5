#!/usr/bin/env python3
"""
Script para normalizar todos los correos a minúsculas en la BD
Ejecutar: python normalizar_correos.py
"""

import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "6382"
DB_NAME = "emprendedoress"
DB_PORT = 3307

def normalizar_correos():
    try:
        db = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        
        cursor = db.cursor()
        
        print("📧 Normalizando correos en tabla 'usuarios'...")
        cursor.execute("UPDATE usuarios SET correo = LOWER(correo)")
        usuarios_actualizados = cursor.rowcount
        
        print("👨‍💼 Normalizando correos en tabla 'administradores'...")
        cursor.execute("UPDATE administradores SET correo = LOWER(correo)")
        admins_actualizados = cursor.rowcount
        
        db.commit()
        
        print(f"\n✅ Total de registros actualizados:")
        print(f"   - Usuarios: {usuarios_actualizados}")
        print(f"   - Administradores: {admins_actualizados}")
        
        # Mostrar algunos ejemplos
        print("\n📋 Ejemplos de correos normalizados:")
        cursor.execute("SELECT id, correo FROM usuarios LIMIT 5")
        for row in cursor.fetchall():
            print(f"   - ID {row[0]}: {row[1]}")
        
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
    if normalizar_correos():
        print("\n✅ Normalización completada exitosamente")
    else:
        print("\n❌ Error durante la normalización")
