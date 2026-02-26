#!/usr/bin/env python3
"""
Script para verificar archivos de una solicitud específica
"""
import mysql.connector
import os

DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "6382"
DB_NAME = "emprendedoress"
DB_PORT = 3307

# ID de la solicitud a verificar (la que se ve en la imagen)
SOLICITUD_ID = 5

print("=" * 80)
print(f"🔍 VERIFICACIÓN DE ARCHIVOS PARA SOLICITUD #{SOLICITUD_ID}")
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
        SELECT s.*, u.correo
        FROM solicitudes s
        JOIN usuarios u ON s.usuario_id = u.id
        WHERE s.id = %s
    """, (SOLICITUD_ID,))
    solicitud = cursor.fetchone()
    
    if not solicitud:
        print(f"❌ Solicitud {SOLICITUD_ID} no encontrada")
    else:
        print(f"\n📋 Solicitud: {solicitud['nombre_proyecto']}")
        print(f"👤 Usuario: {solicitud['correo']}")
        print(f"📅 Fecha: {solicitud['fecha_creacion']}")
        print("\n" + "=" * 80)
        print("📁 ARCHIVOS:")
        print("=" * 80)
        
        # Directorio base del proyecto
        base_dir = r"c:\Users\xtrem\OneDrive\Escritorio\proyecto integrador 16-02-2026\proyecto integrador"
        
        # Lista de campos de archivos
        archivos = [
            ('foto_alumno', 'Foto del Alumno'),
            ('logo_emprendimiento', 'Logo del Emprendimiento'),
            ('integrante_1_foto', 'Foto Integrante 1'),
            ('integrante_2_foto', 'Foto Integrante 2'),
            ('integrante_3_foto', 'Foto Integrante 3'),
            ('integrante_4_foto', 'Foto Integrante 4'),
            ('integrante_5_foto', 'Foto Integrante 5'),
        ]
        
        for campo, descripcion in archivos:
            ruta_bd = solicitud.get(campo)
            if ruta_bd:
                # Convertir ruta relativa a absoluta
                ruta_normalizada = ruta_bd.replace('\\', '/').replace('/', os.sep)
                ruta_completa = os.path.join(base_dir, ruta_normalizada)
                
                existe = os.path.exists(ruta_completa)
                estado = "✅ EXISTE" if existe else "❌ NO EXISTE"
                
                print(f"\n{descripcion}:")
                print(f"  Ruta en BD: {ruta_bd}")
                print(f"  Ruta completa: {ruta_completa}")
                print(f"  Estado: {estado}")
                
                if existe:
                    tamaño = os.path.getsize(ruta_completa)
                    print(f"  Tamaño: {tamaño:,} bytes ({tamaño/1024:.1f} KB)")
            else:
                print(f"\n{descripcion}: ⚪ NO ESPECIFICADO EN BD")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 80)
