"""
Script de prueba para verificar que las credenciales SMTP funcionan
Ejecuta este archivo ANTES de probar el sistema completo
"""

import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

# Cargar variables del archivo .env
load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

print("=" * 60)
print("🧪 PRUEBA DE CONFIGURACIÓN SMTP")
print("=" * 60)

# Verificar que las variables estén configuradas
print("\n1️⃣ Verificando variables de entorno...")
if not SMTP_USER:
    print("❌ ERROR: SMTP_USER no está configurado en .env")
    print("   Abre el archivo .env y configura: SMTP_USER=tu-correo@gmail.com")
    exit(1)
else:
    print(f"✅ SMTP_USER encontrado: {SMTP_USER}")

if not SMTP_PASS:
    print("❌ ERROR: SMTP_PASS no está configurado en .env")
    print("   Abre el archivo .env y configura: SMTP_PASS=tu-contraseña-de-aplicacion")
    exit(1)
else:
    print(f"✅ SMTP_PASS encontrado: {'*' * len(SMTP_PASS)} ({len(SMTP_PASS)} caracteres)")

# Verificar longitud de contraseña (las de aplicación tienen 16 caracteres)
if len(SMTP_PASS) != 16:
    print(f"⚠️  ADVERTENCIA: La contraseña tiene {len(SMTP_PASS)} caracteres")
    print("   Las contraseñas de aplicación de Gmail tienen 16 caracteres")
    print("   Asegúrate de haber copiado la contraseña SIN ESPACIOS")

# Solicitar correo de prueba
print("\n2️⃣ Preparando correo de prueba...")
correo_destino = input("   Ingresa un correo para enviar prueba (Enter para usar el mismo): ").strip()
if not correo_destino:
    correo_destino = SMTP_USER

print(f"   Enviando a: {correo_destino}")

# Crear mensaje de prueba
mensaje = EmailMessage()
mensaje["Subject"] = "🧪 Prueba de Sistema Emprendedores UTA"
mensaje["From"] = f"Sistema Emprendedores <{SMTP_USER}>"
mensaje["To"] = correo_destino
mensaje.set_content("""
¡Hola!

Este es un correo de prueba del Sistema de Gestión de Emprendedores UTA.

Si recibiste este correo, significa que la configuración SMTP está funcionando correctamente ✅

Detalles de la configuración:
- Servidor: smtp.gmail.com:587
- Método: STARTTLS
- Estado: ✅ FUNCIONANDO

Puedes proceder a usar el sistema de registro con verificación de correo.

--
Sistema de Gestión de Emprendedores
Universidad Tecnológica de Acapulco
""")

# Intentar enviar
print("\n3️⃣ Conectando al servidor SMTP...")
try:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
        print(f"   ✅ Conexión establecida con {SMTP_HOST}:{SMTP_PORT}")
        
        print("   🔐 Iniciando STARTTLS...")
        smtp.starttls()
        print("   ✅ Conexión segura establecida")
        
        print(f"   🔑 Autenticando como {SMTP_USER}...")
        smtp.login(SMTP_USER, SMTP_PASS)
        print("   ✅ Autenticación exitosa")
        
        print("   📧 Enviando correo...")
        smtp.send_message(mensaje)
        print("   ✅ Correo enviado correctamente")
        
    print("\n" + "=" * 60)
    print("🎉 ¡ÉXITO! LA CONFIGURACIÓN SMTP FUNCIONA CORRECTAMENTE")
    print("=" * 60)
    print(f"\n✅ Revisa el correo: {correo_destino}")
    print("✅ Puede tardar unos segundos en llegar")
    print("✅ Si no lo ves, revisa la carpeta de SPAM")
    print("\n✅ El sistema está listo para usar")
    
except smtplib.SMTPAuthenticationError:
    print("\n" + "=" * 60)
    print("❌ ERROR DE AUTENTICACIÓN")
    print("=" * 60)
    print("\nPosibles causas:")
    print("1. La contraseña de aplicación es incorrecta")
    print("2. No has activado la verificación en 2 pasos")
    print("3. Estás usando la contraseña normal en vez de la de aplicación")
    print("\nSoluciones:")
    print("1. Ve a: https://myaccount.google.com/apppasswords")
    print("2. Genera una nueva contraseña de aplicación")
    print("3. Cópiala SIN ESPACIOS en el archivo .env")
    print("4. Guarda el archivo y ejecuta de nuevo este script")
    
except smtplib.SMTPException as e:
    print("\n" + "=" * 60)
    print("❌ ERROR SMTP")
    print("=" * 60)
    print(f"\nDetalles: {e}")
    print("\nRevisa:")
    print("- Que tengas conexión a internet")
    print("- Que Gmail no esté bloqueando el acceso")
    print("- Que el correo en SMTP_USER sea válido")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("❌ ERROR INESPERADO")
    print("=" * 60)
    print(f"\nDetalles: {e}")
    print("\nContacta al administrador del sistema")

print("\n")
