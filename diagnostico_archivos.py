#!/usr/bin/env python3
"""
Script de diagnóstico para sistema de archivos
"""
import os

base_dir = r"c:\Users\xtrem\OneDrive\Escritorio\proyecto integrador 16-02-2026\proyecto integrador"
uploads_dir = os.path.join(base_dir, "uploads")

print("=" * 80)
print("🔍 DIAGNÓSTICO DEL SISTEMA DE ARCHIVOS")
print("=" * 80)

print(f"\n📁 Directorio del proyecto: {base_dir}")
print(f"📁 Directorio de uploads: {uploads_dir}")

# Verificar si el directorio uploads existe
if os.path.exists(uploads_dir):
    print(f"\n✅ El directorio uploads EXISTE")
    
    # Listar subdirectorios
    subdirs = [d for d in os.listdir(uploads_dir) if os.path.isdir(os.path.join(uploads_dir, d))]
    if subdirs:
        print(f"\n📂 Subdirectorios encontrados: {len(subdirs)}")
        for subdir in sorted(subdirs):
            path = os.path.join(uploads_dir, subdir)
            archivos = os.listdir(path)
            print(f"  - {subdir}/ ({len(archivos)} archivos)")
            for archivo in archivos:
                size = os.path.getsize(os.path.join(path, archivo))
                print(f"      * {archivo} ({size:,} bytes)")
    else:
        print("\n⚠️  No hay subdirectorios (carpetas de usuario)")
else:
    print(f"\n❌ El directorio uploads NO EXISTE")
    print("\nCreando directorio...")
    try:
        os.makedirs(uploads_dir, exist_ok=True)
        print("✅ Directorio creado exitosamente")
    except Exception as e:
        print(f"❌ Error al crear directorio: {e}")

# Verificar permisos de escritura
print(f"\n🔐 Verificando permisos de escritura...")
test_file = os.path.join(uploads_dir, "test.txt")
try:
    with open(test_file, 'w') as f:
        f.write("test")
    os.remove(test_file)
    print("✅ Permisos de escritura OK")
except Exception as e:
    print(f"❌ Error de permisos: {e}")

print("\n" + "=" * 80)
print("📋 RESUMEN:")
print("=" * 80)
print("""
Si todos los checks están en ✅, el sistema debería funcionar correctamente.

Si hay problemas:
1. Asegúrate de que la aplicación Flask esté corriendo desde el directorio correcto
2. Reinicia la aplicación después de hacer cambios
3. Envía un nuevo formulario con imágenes para probar

Para reenviar una solicitud:
- Las solicitudes antiguas no tienen archivos físicos
- Debes llenar y enviar el formulario de nuevo con todas las imágenes
""")
print("=" * 80)
