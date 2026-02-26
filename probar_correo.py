#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de envío de correos.
Usa las credenciales del archivo .env
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

print_header("PRUEBA DE CONFIGURACIÓN DE CORREO ELECTRÓNICO")

# 1. Verificar si las variables están configuradas
print_info("Paso 1: Verificar configuración de credenciales")

if not SMTP_USER:
    print_error("SMTP_USER no está configurado")
    print("\nPara configurar:")
    print("1. Abre el archivo '.env' en el directorio del proyecto")
    print("2. Agrega tu correo: SMTP_USER=tu_correo@gmail.com")
    print("3. Agrega tu contraseña de app: SMTP_PASS=tu_contraseña_app")
    sys.exit(1)
else:
    print_success(f"SMTP_USER configurado: {SMTP_USER}")

if not SMTP_PASS:
    print_error("SMTP_PASS no está configurado")
    print("\nPara obtener contraseña de app en Gmail:")
    print("1. Ve a https://myaccount.google.com/apppasswords")
    print("2. Selecciona 'Mail' y 'Windows'")
    print("3. Copia la contraseña de 16 caracteres generada")
    print("4. Pégala en el archivo .env como SMTP_PASS")
    sys.exit(1)
else:
    print_success(f"SMTP_PASS configurado: {SMTP_PASS[:4]}...{SMTP_PASS[-4:]}")

# 2. Intentar conexión
print("\n" + "-"*60)
print_info("Paso 2: Probar conexión SMTP")

import smtplib

try:
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
        print_success("Conectado al servidor SMTP")
        
        # Intentar iniciar TLS
        smtp.starttls()
        print_success("TLS iniciado")
        
        # Intentar login
        smtp.login(SMTP_USER, SMTP_PASS)
        print_success("Autenticación exitosa")
        
except smtplib.SMTPAuthenticationError:
    print_error("Error de autenticación. Verifica SMTP_USER y SMTP_PASS")
    print_warning("¿Usaste una contraseña de app de 16 caracteres?")
    sys.exit(1)
except smtplib.SMTPException as e:
    print_error(f"Error SMTP: {str(e)}")
    sys.exit(1)
except Exception as e:
    print_error(f"Error de conexión: {str(e)}")
    sys.exit(1)

# 3. Prueba de envío
print("\n" + "-"*60)
print_info("Paso 3: Enviar correo de prueba")

from email.message import EmailMessage

destinatario = input(f"\n¿A qué correo enviar la prueba? [{SMTP_USER}]: ").strip() or SMTP_USER

try:
    mensaje = EmailMessage()
    mensaje["Subject"] = "🧪 Prueba de Correo - Sistema de Emprendedores"
    mensaje["From"] = f"Sistema Emprendedores <{SMTP_USER}>"
    mensaje["To"] = destinatario
    
    cuerpo_html = """
    <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>✅ Prueba de Correo Exitosa</h2>
                <p>Si ves este correo, el sistema de envío de correos está configurado correctamente.</p>
                <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <p><strong>Información de configuración:</strong></p>
                    <ul>
                        <li>Servidor SMTP: smtp.gmail.com:587</li>
                        <li>Usuario: """ + SMTP_USER + """</li>
                        <li>Fecha: """ + __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</li>
                    </ul>
                </div>
                <p>Por favor, ignora este correo de prueba.</p>
            </div>
        </body>
    </html>
    """
    
    mensaje.add_alternative(cuerpo_html, subtype='html')
    
    print(f"Enviando a: {destinatario}")
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASS)
        smtp.send_message(mensaje)
    
    print_success(f"Correo de prueba enviado a {destinatario}")
    
except Exception as e:
    print_error(f"Error al enviar: {str(e)}")
    sys.exit(1)

# Éxito
print("\n" + "="*60)
print_success("¡TODAS LAS PRUEBAS PASARON! El sistema de correo está listo")
print("="*60 + "\n")

print("Próximos pasos:")
print("1. El sistema ahora enviará correos de verificación en el registro")
print("2. Revisa tu carpeta de spam si no ves los correos")
print("3. Si hay problemas, revisa la consola de Flask para mensajes de error")
