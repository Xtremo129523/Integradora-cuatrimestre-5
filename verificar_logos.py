#!/usr/bin/env python3
"""
Script para verificar qué imágenes tienen las solicitudes
"""
import mysql.connector

DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "6382"
DB_NAME = "emprendedoress"
DB_PORT = 3307

print("=" * 80)
print("🔍 VERIFICACIÓN DE IMÁGENES EN SOLICITUDES")
print("=" * 80)

try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT s.id, s.nombre_proyecto, s.logo_emprendimiento, s.foto_alumno, u.correo
        FROM solicitudes s
        JOIN usuarios u ON s.usuario_id = u.id
        ORDER BY s.id DESC
    """)
    solicitudes = cursor.fetchall()
    
    if solicitudes:
        print(f"\n📊 Total: {len(solicitudes)} solicitudes\n")
        for sol in solicitudes:
            print(f"ID: {sol['id']}")
            print(f"  Proyecto: {sol['nombre_proyecto'] or 'Sin nombre'}")
            print(f"  Usuario: {sol['correo']}")
            print(f"  Logo Emprendimiento: {sol['logo_emprendimiento'] or '❌ NO TIENE'}")
            print(f"  Foto Alumno: {sol['foto_alumno'] or '❌ NO TIENE'}")
            print("-" * 80)
    else:
        print("  ⚠️  No hay solicitudes")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"  ❌ Error: {e}")

print("=" * 80)
