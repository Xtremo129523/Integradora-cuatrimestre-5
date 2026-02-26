#!/usr/bin/env python3
"""
Script para verificar usuarios registrados en la base de datos
y probar la configuración de SMTP
"""
import mysql.connector
import os
from dotenv import load_dotenv
import smtplib

# Cargar variables de entorno
load_dotenv()

# Credenciales de BD
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "6382"
DB_NAME = "emprendedoress"
DB_PORT = 3307

# Credenciales SMTP
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").replace(" ", "").strip()
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

print("=" * 60)
print("🔍 VERIFICACIÓN DE CONFIGURACIÓN")
print("=" * 60)

# 1. Verificar SMTP
print("\n📧 Estado SMTP:")
if SMTP_USER and SMTP_PASS:
    print(f"  ✅ SMTP_USER: {SMTP_USER}")
    print(f"  ✅ SMTP_PASS: Configurada (longitud: {len(SMTP_PASS)} caracteres)")
else:
    print(f"  ❌ SMTP_USER: {'No configurada' if not SMTP_USER else 'OK'}")
    print(f"  ❌ SMTP_PASS: {'No configurada' if not SMTP_PASS else 'OK'}")

# 2. Conectar a la BD y listar usuarios
print("\n📊 Usuarios registrados en la BD:")
try:
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )
    cursor = db.cursor(dictionary=True)
    
    # Obtener usuarios
    cursor.execute("SELECT id, correo, rol, estado, verificado FROM usuarios")
    usuarios = cursor.fetchall()
    
    if usuarios:
        print(f"\n  Total: {len(usuarios)} usuarios\n")
        for u in usuarios:
            verificado = "✅" if u.get("verificado", True) else "❌"
            print(f"  {verificado} ID:{u['id']} | {u['correo']} | Rol:{u['rol']} | Estado:{u['estado']}")
    else:
        print("  ⚠️  No hay usuarios registrados")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"  ❌ Error al conectar a BD: {e}")

print("\n" + "=" * 60)
