from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify, abort
import re
import os
import random
import smtplib
import mysql.connector
from datetime import datetime, timedelta
from functools import wraps
from email.message import EmailMessage
import io
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = "clave_super_secreta"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Extensiones permitidas para archivos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx'}

DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "6382"
DB_NAME = "emprendedoress"
DB_PORT = 3307

INSTITUTION_DOMAIN = "@utacapulco.edu.mx"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()

def es_correo_institucional(correo):
    return bool(correo) and correo.lower().endswith(INSTITUTION_DOMAIN)


def generar_codigo_verificacion():
    return "".join(random.choice("0123456789") for _ in range(6))


def smtp_configurado():
    return bool(SMTP_USER and SMTP_PASS)


def enviar_correo(destinatario, asunto, cuerpo, html=False):
    """
    Envía un correo electrónico usando SMTP de Gmail
    
    Args:
        destinatario: Email del destinatario
        asunto: Asunto del correo
        cuerpo: Cuerpo del correo
        html: Si True, envía como HTML
    
    Returns:
        tupla (éxito: bool, mensaje: str)
    """
    
    if not smtp_configurado():
        error = "❌ SMTP no configurado. Por favor, establecer SMTP_USER y SMTP_PASS en el archivo .env"
        print(f"Error de correo: {error}")
        return False, error
    
    if not destinatario or '@' not in destinatario:
        error = "❌ Dirección de correo inválida"
        print(f"Error de correo: {error}")
        return False, error

    try:
        # Crear mensaje
        mensaje = EmailMessage()
        mensaje["Subject"] = asunto
        mensaje["From"] = f"Sistema Emprendedores <{SMTP_USER}>"
        mensaje["To"] = destinatario
        
        # Agregar contenido
        if html:
            mensaje.add_alternative(cuerpo, subtype='html')
        else:
            mensaje.set_content(cuerpo)
        
        # Enviar email
        print(f"📧 Intentando enviar correo a: {destinatario}")
        print(f"   Asunto: {asunto}")
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(mensaje)
        
        print(f"✅ Correo enviado exitosamente a: {destinatario}")
        return True, "Correo enviado exitosamente"
        
    except smtplib.SMTPAuthenticationError:
        error = "❌ Error de autenticación SMTP. Verifica SMTP_USER y SMTP_PASS en .env"
        print(f"Error de correo: {error}")
        return False, error
        
    except smtplib.SMTPException as e:
        error = f"❌ Error SMTP: {str(e)}"
        print(f"Error de correo: {error}")
        return False, error
        
    except TimeoutError:
        error = "❌ Timeout al conectar con servidor SMTP"
        print(f"Error de correo: {error}")
        return False, error
        
    except Exception as e:
        error = f"❌ Error al enviar correo: {str(e)}"
        print(f"Error de correo: {error}")
        return False, error


# ================= VALIDACIÓN DE ARCHIVOS =================
def allowed_file(filename, allowed_extensions=None):
    """Verifica si el archivo tiene una extensión permitida"""
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validar_archivo(file, tipo='imagen'):
    """Valida archivos subidos por tipo, extensión y tamaño"""
    if not file:
        return False, "No se proporcionó ningún archivo"
    
    if file.filename == '':
        return False, "Nombre de archivo vacío"
    
    # Validar extensión según tipo
    if tipo == 'imagen':
        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return False, f"Tipo de archivo no permitido. Solo se permiten: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    elif tipo == 'documento':
        if not allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
            return False, f"Tipo de archivo no permitido. Solo se permiten: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"
    else:
        if not allowed_file(file.filename):
            return False, f"Tipo de archivo no permitido. Solo se permiten: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Validar tamaño (ya manejado por MAX_CONTENT_LENGTH, pero agregamos validación adicional)
    file.seek(0, 2)  # Ir al final del archivo
    size = file.tell()
    file.seek(0)  # Volver al inicio
    
    max_size = 16 * 1024 * 1024  # 16 MB
    if size > max_size:
        return False, f"El archivo es demasiado grande. Tamaño máximo: {max_size // (1024*1024)}MB"
    
    if size == 0:
        return False, "El archivo está vacío"
    
    return True, "Archivo válido"


def sanitizar_filename(filename):
    """Sanitiza el nombre del archivo para evitar problemas de seguridad"""
    return secure_filename(filename)

# ================= CONEXIÓN =================
def conexion():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )


def verificar_base_datos():
    db = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME=%s",
            (DB_NAME,)
        )
        if not cursor.fetchone():
            raise RuntimeError(
                "La base de datos no existe. Importa emprendedoress.sql antes de ejecutar Flask."
            )
    finally:
        cursor.close()
        db.close()

# ================= DECORADORES =================
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def solo_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("rol") != "admin":
            flash("No tienes permiso para acceder aquí.", "danger")
            return redirect(url_for("inicio"))
        return f(*args, **kwargs)
    return decorated_function


def solo_aceptado(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("estado") != "aceptado":
            flash("⚠️ Acceso restringido: Solo usuarios con solicitud ACEPTADA pueden acceder a esta función.", "warning")
            return redirect(url_for("inicio"))
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def validar_correo_institucional_en_sesion():
    ruta_actual = request.endpoint or ""
    rutas_permitidas = {
        "login",
        "registro",
        "verificar_correo",
        "reenviar_codigo",
        "static",
    }

    if ruta_actual in rutas_permitidas:
        return None

    if "usuario_id" in session and session.get("rol") != "admin":
        correo_sesion = session.get("correo", "")
        if not es_correo_institucional(correo_sesion):
            flash("Debes usar un correo institucional para acceder al sistema.", "danger")
            return redirect(url_for("login"))


# ================= MANEJADORES DE ERRORES =================
@app.errorhandler(403)
def forbidden(e):
    """Manejador de errores 403 - Acceso prohibido"""
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({"error": "Acceso prohibido", "status": 403}), 403
    flash("⛔ Acceso prohibido. No tienes permiso para acceder a este recurso.", "danger")
    return render_template("login.html"), 403


@app.errorhandler(404)
def not_found(e):
    """Manejador de errores 404 - Página no encontrada"""
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({"error": "Recurso no encontrado", "status": 404}), 404
    flash("❌ Página no encontrada. Verifica la URL.", "warning")
    return render_template("login.html"), 404


@app.errorhandler(413)
def request_entity_too_large(e):
    """Manejador de errores 413 - Archivo demasiado grande"""
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({"error": "Archivo demasiado grande", "status": 413, "max_size": "16MB"}), 413
    flash("📦 El archivo es demasiado grande. Tamaño máximo permitido: 16MB", "danger")
    return redirect(request.referrer or url_for("inicio"))


@app.errorhandler(500)
def internal_server_error(e):
    """Manejador de errores 500 - Error interno del servidor"""
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({"error": "Error interno del servidor", "status": 500}), 500
    flash("💥 Ocurrió un error interno. Por favor, intenta de nuevo más tarde.", "danger")
    return render_template("login.html"), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Manejador genérico de excepciones"""
    # Si es un error HTTP conocido, dejarlo pasar
    if hasattr(e, 'code'):
        return e
    
    # Log del error (en producción usar logging apropiado)
    print(f"Error no controlado: {str(e)}")
    
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({"error": "Error inesperado", "status": 500}), 500
    
    flash("⚠️ Ocurrió un error inesperado. Por favor, contacta al administrador.", "danger")
    return redirect(url_for("login"))


# ================= SERVIR ARCHIVOS SUBIDOS =================
@app.route("/uploads/<path:filepath>")
def descargar_archivo(filepath):
    """Servir archivos subidos (fotos)"""
    try:
        return send_file(filepath, mimetype='image/jpeg')
    except:
        return "Archivo no encontrado", 404


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "").strip()

        # Validación de campos vacíos
        if not correo or not password:
            flash("Por favor, completa todos los campos", "danger")
            return redirect(url_for("login"))

        db = conexion()
        cursor = db.cursor(dictionary=True)

        # Primero verificar si es un administrador
        cursor.execute("SELECT * FROM administradores WHERE correo=%s", (correo,))
        admin = cursor.fetchone()

        if admin:
            # Es un administrador
            if admin["password"] != password:
                flash("Contraseña incorrecta", "danger")
                cursor.close()
                db.close()
                return redirect(url_for("login"))
            
            if admin["estado"] != "activo":
                flash("Tu cuenta de administrador está inactiva. Contacta al responsable.", "danger")
                cursor.close()
                db.close()
                return redirect(url_for("login"))

            # Login de administrador exitoso
            session["usuario_id"] = admin["id"]
            session["correo"] = admin["correo"]
            session["nombre"] = admin["nombre"]
            session["rol"] = "admin"
            session["estado"] = "aceptado"
            session["es_admin"] = True

            cursor.close()
            db.close()

            flash(f"🔔 Sesión iniciada - Bienvenido, {admin['nombre']}", "success")
            return redirect(url_for("panel_admin"))

        # Si no es admin, verificar si es usuario regular
        cursor.execute("SELECT * FROM usuarios WHERE correo=%s", (correo,))
        usuario = cursor.fetchone()

        if not usuario:
            flash("El correo ingresado no está registrado", "danger")
            cursor.close()
            db.close()
            return redirect(url_for("login"))

        # Verificar correo institucional
        if not es_correo_institucional(usuario["correo"]):
            flash("Debes usar un correo institucional (@utacapulco.edu.mx)", "danger")
            cursor.close()
            db.close()
            return redirect(url_for("login"))

        # Verificar la contraseña
        if usuario["password"] != password:
            flash("Contraseña incorrecta", "danger")
            cursor.close()
            db.close()
            return redirect(url_for("login"))

        # Verificar si el correo ya fue confirmado
        if not usuario.get("verificado", True):
            cursor.close()
            db.close()
            flash("Debes verificar tu correo antes de iniciar sesión.", "warning")
            return redirect(url_for("verificar_correo", correo=correo))

        # Credenciales correctas - Usuario regular
        session["usuario_id"] = usuario["id"]
        session["correo"] = usuario["correo"]
        session["rol"] = usuario["rol"]
        session["estado"] = usuario["estado"]
        session["es_admin"] = False

        cursor.close()
        db.close()

        flash(f"🔔 Sesión iniciada - Bienvenido, {correo}", "success")
        return redirect(url_for("inicio"))

    return render_template("login.html")


# ================= REGISTRO =================
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "").strip()

        # Validación de campos vacíos
        if not correo or not password:
            return render_template("registro.html", error="Por favor, completa todos los campos")

        # Validación de correo institucional
        if not re.search(r"@utacapulco\.edu\.mx$", correo):
            return render_template("registro.html", error="Debes usar tu correo institucional (@utacapulco.edu.mx)")

        # Validación de longitud de contraseña
        if len(password) < 6:
            return render_template("registro.html", error="La contraseña debe tener al menos 6 caracteres")

        if not smtp_configurado():
            return render_template(
                "registro.html",
                error="El envio de correos no esta configurado. Contacta al administrador."
            )

        db = conexion()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE correo=%s", (correo,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return render_template("registro.html", error="Este correo ya está registrado. Inicia sesión.")

        codigo = generar_codigo_verificacion()
        expira = datetime.now() + timedelta(minutes=15)

        cursor.execute("""
            INSERT INTO usuarios (correo, password, rol, estado, verificado, codigo_verificacion, codigo_expira)
            VALUES (%s, %s, 'alumno', 'pendiente', 0, %s, %s)
        """, (correo, password, codigo, expira))

        asunto = "🔐 Código de Verificación - Sistema de Emprendedores"
        cuerpo_html = f"""
        <html>
            <body style="font-family: 'Poppins', Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #0f5a8a 0%, #0f3460 100%); padding: 20px; border-radius: 10px; color: white; text-align: center;">
                        <h1 style="margin: 0;">Sistema de Emprendedores</h1>
                    </div>
                    
                    <div style="background: #f9f9f9; padding: 20px; margin-top: 20px; border-radius: 5px;">
                        <h2>¡Bienvenido!</h2>
                        <p>Para completar tu registro en el Sistema de Gestión de Emprendedores, necesitas verificar tu correo electrónico.</p>
                        
                        <div style="background: white; padding: 20px; border-left: 4px solid #0f5a8a; margin: 20px 0;">
                            <p style="margin: 0 0 10px 0; color: #666;">Tu código de verificación es:</p>
                            <h1 style="margin: 0; font-size: 36px; letter-spacing: 5px; color: #0f5a8a; text-align: center;">{codigo}</h1>
                        </div>
                        
                        <div style="background: #fff3cd; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 5px;">
                            <p style="margin: 0; color: #856404;">
                                ⏱️ <strong>Este código expira en 15 minutos.</strong><br>
                                Si no solicitaste este registro, ignora este correo.
                            </p>
                        </div>
                        
                        <p style="margin-top: 20px; color: #666; font-size: 12px;">
                            Este es un mensaje automático. Por favor no respondas a este correo.
                        </p>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; color: #999; font-size: 12px;">
                        <p>© 2026 Sistema de Gestion de Emprendedores - Universidad Tecnológica de Acapulco</p>
                    </div>
                </div>
            </body>
        </html>
        """

        enviado, error_envio = enviar_correo(correo, asunto, cuerpo_html, html=True)
        if not enviado:
            db.rollback()
            cursor.close()
            db.close()
            flash(f"Error al enviar correo: {error_envio}", "danger")
            return render_template("registro.html", correo=correo)

        db.commit()
        cursor.close()
        db.close()

        flash("✅ Se envió un código de verificación a tu correo. Revisa tu bandeja de entrada.", "success")
        return redirect(url_for("verificar_correo", correo=correo))


    return render_template("registro.html")


# ================= VERIFICACION CORREO =================
@app.route("/verificar_correo", methods=["GET", "POST"])
def verificar_correo():
    correo = request.args.get("correo") or request.form.get("correo") or ""

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()

        if not correo or not codigo:
            return render_template("verificar_correo.html", error="Completa todos los campos", correo=correo)

        db = conexion()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, codigo_verificacion, codigo_expira, verificado
            FROM usuarios
            WHERE correo = %s
        """, (correo,))
        usuario = cursor.fetchone()

        if not usuario:
            cursor.close()
            db.close()
            return render_template("verificar_correo.html", error="Usuario no encontrado", correo=correo)

        if usuario.get("verificado"):
            cursor.close()
            db.close()
            flash("Tu correo ya estaba verificado. Inicia sesion.", "info")
            return redirect(url_for("login"))

        if not usuario.get("codigo_verificacion") or codigo != usuario.get("codigo_verificacion"):
            cursor.close()
            db.close()
            return render_template("verificar_correo.html", error="Codigo incorrecto", correo=correo)

        if usuario.get("codigo_expira") and datetime.now() > usuario["codigo_expira"]:
            cursor.close()
            db.close()
            return render_template("verificar_correo.html", error="El codigo ya expiro", correo=correo)

        cursor.execute("""
            UPDATE usuarios
            SET verificado = 1, codigo_verificacion = NULL, codigo_expira = NULL
            WHERE id = %s
        """, (usuario["id"],))
        db.commit()
        cursor.close()
        db.close()

        flash("Correo verificado correctamente. Ya puedes iniciar sesion.", "success")
        return redirect(url_for("login"))

    return render_template("verificar_correo.html", correo=correo)


@app.route("/reenviar_codigo", methods=["POST"])
def reenviar_codigo():
    correo = request.form.get("correo", "").strip()

    if not correo:
        return render_template("verificar_correo.html", error="Ingresa tu correo", correo=correo)

    db = conexion()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, verificado
        FROM usuarios
        WHERE correo = %s
    """, (correo,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        db.close()
        return render_template("verificar_correo.html", error="Usuario no encontrado", correo=correo)

    if usuario.get("verificado"):
        cursor.close()
        db.close()
        flash("Tu correo ya esta verificado. Inicia sesion.", "info")
        return redirect(url_for("login"))

    codigo = generar_codigo_verificacion()
    expira = datetime.now() + timedelta(minutes=15)

    cursor.execute("""
        UPDATE usuarios
        SET codigo_verificacion = %s, codigo_expira = %s
        WHERE id = %s
    """, (codigo, expira, usuario["id"]))
    db.commit()
    cursor.close()
    db.close()

    asunto = "Codigo de verificacion"
    cuerpo = (
        "Hola,\n\n"
        "Tu codigo de verificacion es: " + codigo + "\n\n"
        "Este codigo expira en 15 minutos.\n\n"
        "Sistema de Gestion de Emprendedores"
    )

    enviado, _ = enviar_correo(correo, asunto, cuerpo)
    if not enviado:
        return render_template(
            "verificar_correo.html",
            error="No se pudo reenviar el codigo. Intenta mas tarde.",
            correo=correo
        )

    flash("Se envio un nuevo codigo a tu correo.", "success")
    return redirect(url_for("verificar_correo", correo=correo))


# ================= PANEL ADMIN =================
@app.route("/panel_admin")
@login_requerido
@solo_admin
def panel_admin():

    db = conexion()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.*, u.correo, u.password 
        FROM solicitudes s
        JOIN usuarios u ON s.usuario_id = u.id
        WHERE u.rol = 'alumno'
    """)
    solicitudes = cursor.fetchall()

    return render_template("panel_admin.html", solicitudes=solicitudes)


# ================= VER DETALLE SOLICITUD =================
@app.route("/solicitud/<int:id>")
@login_requerido
@solo_admin
def ver_solicitud(id):

    db = conexion()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.*, u.correo
        FROM solicitudes s
        JOIN usuarios u ON s.usuario_id = u.id
        WHERE s.id=%s
    """, (id,))
    solicitud = cursor.fetchone()

    return render_template("detalle_solicitud_Admin.html", solicitud=solicitud)


# ================= APROBAR =================
@app.route("/aprobar/<int:id>")
@login_requerido
@solo_admin
def aprobar(id):

    db = conexion()
    cursor = db.cursor(dictionary=True)

    try:
        # Obtener info de la solicitud
        cursor.execute("SELECT usuario_id FROM solicitudes WHERE id=%s", (id,))
        solicitud = cursor.fetchone()
        
        if not solicitud:
            flash("Solicitud no encontrada", "danger")
            return redirect(url_for("panel_admin"))
        
        usuario_id = solicitud["usuario_id"]
        
        # Actualizar estado de solicitud
        cursor.execute("UPDATE solicitudes SET estado='aceptado' WHERE id=%s", (id,))
        
        # Actualizar estado de usuario
        cursor.execute("""
            UPDATE usuarios 
            SET estado='aceptado' 
            WHERE id=%s
        """, (usuario_id,))

        db.commit()
        
        # Crear notificación de aprobación
        crear_notificacion(
            usuario_id=usuario_id,
            tipo="estado_cambio",
            titulo="Solicitud Aceptada",
            mensaje="Tu solicitud de inscripción ha sido ACEPTADA. Ahora puedes acceder a todas las funciones.",
            solicitud_id=id,
            enlace="estado_solicitud"
        )
        
        flash("Solicitud aprobada exitosamente", "success")
    
    except Exception as e:
        db.rollback()
        flash(f"Error al aprobar la solicitud: {str(e)}", "danger")
    
    finally:
        cursor.close()
        db.close()

    return redirect(url_for("panel_admin"))


# ================= RECHAZAR =================
@app.route("/rechazar/<int:id>")
@login_requerido
@solo_admin
def rechazar(id):

    db = conexion()
    cursor = db.cursor(dictionary=True)

    try:
        # Obtener info de la solicitud
        cursor.execute("SELECT usuario_id FROM solicitudes WHERE id=%s", (id,))
        solicitud = cursor.fetchone()
        
        if not solicitud:
            flash("Solicitud no encontrada", "danger")
            return redirect(url_for("panel_admin"))
        
        usuario_id = solicitud["usuario_id"]
        
        # Actualizar estado de solicitud
        cursor.execute("UPDATE solicitudes SET estado='rechazado' WHERE id=%s", (id,))
        
        # Actualizar estado de usuario
        cursor.execute("""
            UPDATE usuarios 
            SET estado='rechazado' 
            WHERE id=%s
        """, (usuario_id,))

        db.commit()
        
        # Crear notificación de rechazo
        crear_notificacion(
            usuario_id=usuario_id,
            tipo="estado_cambio",
            titulo="Solicitud Rechazada",
            mensaje="Tu solicitud de inscripción ha sido RECHAZADA. Puedes enviar una nueva solicitud más adelante.",
            solicitud_id=id,
            enlace="estado_solicitud"
        )
        
        flash("Solicitud rechazada exitosamente", "success")
    
    except Exception as e:
        db.rollback()
        flash(f"Error al rechazar la solicitud: {str(e)}", "danger")
    
    finally:
        cursor.close()
        db.close()

    return redirect(url_for("panel_admin"))


# ================= INICIO ALUMNO =================
@app.route("/inicio")
@login_requerido
def inicio():

    db = conexion()
    cursor = db.cursor(dictionary=True)

    # Actualizar el estado del usuario desde la BD
    cursor.execute("SELECT estado FROM usuarios WHERE id=%s", (session["usuario_id"],))
    usuario = cursor.fetchone()
    
    # Actualizar estado en la sesión
    session["estado"] = usuario["estado"]

    # Redirigir según el estado
    if usuario["estado"] == "aceptado":
        cursor.close()
        db.close()
        return render_template("aceptado.html")

    if usuario["estado"] == "rechazado":
        cursor.close()
        db.close()
        return render_template("rechazado.html")

    # Estado pendiente - verificar si ya envió el formulario
    cursor.execute("""
        SELECT id FROM solicitudes 
        WHERE usuario_id=%s 
        ORDER BY fecha_creacion DESC 
        LIMIT 1
    """, (session["usuario_id"],))
    solicitud_existente = cursor.fetchone()
    
    cursor.close()
    db.close()

    if not usuario:
        flash("Error al obtener información del usuario", "danger")
        return redirect(url_for("logout"))

    # Si ya tiene una solicitud, mostrar página de espera
    if solicitud_existente:
        return render_template("en_revision.html")
    
    # Si no ha enviado formulario, mostrarlo
    return render_template("formulario.html")


# ================= GUARDAR FORMULARIO =================

def guardar_archivo(file, usuario_id, tipo="foto"):
    """Guardar archivo subido y retornar la ruta relativa con validación"""
    if not file or file.filename == '':
        return None, "No se proporcionó archivo"
    
    # Validar el archivo según tipo
    tipo_validacion = 'imagen' if tipo == 'foto' else 'general'
    es_valido, mensaje = validar_archivo(file, tipo_validacion)
    
    if not es_valido:
        return None, mensaje
    
    # Crear carpeta de uploads si no existe
    upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(usuario_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Sanitizar y generar nombre único para el archivo
    filename_seguro = sanitizar_filename(file.filename)
    ext = os.path.splitext(filename_seguro)[1]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{tipo}_{timestamp}{ext}"
    
    filepath = os.path.join(upload_dir, filename)
    
    try:
        file.save(filepath)
        return filepath, "Archivo guardado exitosamente"
    except Exception as e:
        return None, f"Error al guardar archivo: {str(e)}"


@app.route("/guardar_formulario", methods=["POST"])
@login_requerido
def guardar_formulario():

    # Validar que el usuario tenga estado pendiente
    if session.get("estado") != "pendiente":
        flash("⚠️ No puedes enviar una nueva solicitud. Tu estado actual es: " + session.get("estado", "desconocido"), "warning")
        return redirect(url_for("inicio"))

    db = conexion()
    cursor = db.cursor()

    try:
        # Obtener usuario_id de sesión con mejor manejo de error
        usuario_id = session.get("usuario_id")
        if not usuario_id:
            flash("❌ Error: No se encontró tu ID de usuario. Por favor, inicia sesión de nuevo.", "danger")
            cursor.close()
            db.close()
            return redirect(url_for("login"))

        numero_integrantes = request.form.get("integrantes")
        if numero_integrantes:
            try:
                num_int = int(numero_integrantes)
                if num_int > 5:
                    flash("❌ El máximo de integrantes permitidos es 5.", "danger")
                    cursor.close()
                    db.close()
                    return redirect(url_for("inicio"))
            except ValueError:
                flash("❌ El número de integrantes debe ser un número válido.", "danger")
                cursor.close()
                db.close()
                return redirect(url_for("inicio"))
        
        # Guardar archivos con validación
        foto_alumno, msg1 = guardar_archivo(request.files.get('foto_alumno'), usuario_id, "alumno")
        if not foto_alumno and request.files.get('foto_alumno'):
            flash(f"Error en foto principal: {msg1}", "danger")
            cursor.close()
            db.close()
            return redirect(url_for("inicio"))
        
        logo_emprendimiento, msg2 = guardar_archivo(request.files.get('logo_emprendimiento'), usuario_id, "logo_emprendimiento")
            
        integrante_1_foto, _ = guardar_archivo(request.files.get('integrante_1_foto'), usuario_id, "integrante_1")
        integrante_2_foto, _ = guardar_archivo(request.files.get('integrante_2_foto'), usuario_id, "integrante_2")
        integrante_3_foto, _ = guardar_archivo(request.files.get('integrante_3_foto'), usuario_id, "integrante_3")
        integrante_4_foto, _ = guardar_archivo(request.files.get('integrante_4_foto'), usuario_id, "integrante_4")
        integrante_5_foto, _ = guardar_archivo(request.files.get('integrante_5_foto'), usuario_id, "integrante_5")
        
        cursor.execute("""
            INSERT INTO solicitudes (
                usuario_id,
                nombre,
                edad,
                carrera,
                nivel,
                matricula,
                asesor_academico_1,
                asesor_academico_2,
                telefono,
                direccion,
                numero_integrantes,
                foto_alumno,
                alumno_descripcion,
                integrante_1_nombre,
                integrante_1_foto,
                integrante_1_descripcion,
                integrante_2_nombre,
                integrante_2_foto,
                integrante_2_descripcion,
                integrante_3_nombre,
                integrante_3_foto,
                integrante_3_descripcion,
                integrante_4_nombre,
                integrante_4_foto,
                integrante_4_descripcion,
                integrante_5_nombre,
                integrante_5_foto,
                integrante_5_descripcion,
                nombre_proyecto,
                logo_emprendimiento,
                descripcion_proyecto,
                ubicacion_emprendimiento,
                fecha_inicio_emprendimiento,
                clientes_clave,
                problema_resuelve,
                producto_servicio,
                innovacion,
                creacion_valor,
                idea_7_palabras,
                personas_trabajando,
                convocatorias_previas,
                descripcion_lider,
                rol_emprendimiento,
                habilidades,
                logro_destacado,
                fecha_creacion,
                estado
            )
            VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,'pendiente'
            )
        """, (
            usuario_id,
            request.form.get("nombre"),
            request.form.get("edad"),
            request.form.get("carrera"),
            request.form.get("nivel"),
            request.form.get("matricula"),
            request.form.get("asesor_1"),
            request.form.get("asesor_2"),
            request.form.get("telefono"),
            request.form.get("direccion"),
            numero_integrantes or None,
            foto_alumno,
            request.form.get("alumno_descripcion"),
            request.form.get("integrante_1_nombre"),
            integrante_1_foto,
            request.form.get("integrante_1_descripcion"),
            request.form.get("integrante_2_nombre"),
            integrante_2_foto,
            request.form.get("integrante_2_descripcion"),
            request.form.get("integrante_3_nombre"),
            integrante_3_foto,
            request.form.get("integrante_3_descripcion"),
            request.form.get("integrante_4_nombre"),
            integrante_4_foto,
            request.form.get("integrante_4_descripcion"),
            request.form.get("integrante_5_nombre"),
            integrante_5_foto,
            request.form.get("integrante_5_descripcion"),
            request.form.get("descripcion"),
            request.form.get("ubicacion"),
            request.form.get("inicio_emprendimiento"),
            request.form.get("clientes"),
            request.form.get("problema"),
            request.form.get("producto"),
            request.form.get("innovacion"),
            request.form.get("valor"),
            request.form.get("idea7"),
            request.form.get("nombre_proyecto"),
            logo_emprendimiento,
            request.form.get("trabajadores"),
            request.form.get("convocatoria"),
            request.form.get("lider_descripcion"),
            request.form.get("rol"),
            request.form.get("habilidades"),
            request.form.get("asombroso"),
            datetime.now()
        ))

        db.commit()
        flash("✓ ¡Formulario enviado exitosamente! Tu solicitud está en espera de revisión por parte del administrador.", "success")
    
    except Exception as e:
        db.rollback()
        flash(f"❌ Error al guardar la solicitud: {str(e)}", "danger")
    
    finally:
        cursor.close()
        db.close()

    return redirect(url_for("inicio"))


# ================= ESTADO SOLICITUD =================
@app.route("/estado_solicitud")
@login_requerido
def estado_solicitud():
    db = conexion()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM solicitudes 
        WHERE usuario_id=%s 
        ORDER BY fecha_creacion DESC 
        LIMIT 1
    """, (session["usuario_id"],))
    
    solicitud = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template("estado_solicitud.html", solicitud=solicitud)


# ================= DESCARGAR DOCUMENTO =================
@app.route("/descargar_documento/<int:id>")
@login_requerido
@solo_aceptado
def descargar_documento(id):
    db = conexion()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.*, u.correo 
        FROM solicitudes s
        JOIN usuarios u ON s.usuario_id = u.id
        WHERE s.id=%s AND s.usuario_id=%s AND s.estado='aceptado'
    """, (id, session["usuario_id"]))
    
    solicitud = cursor.fetchone()
    cursor.close()
    db.close()

    if not solicitud:
        flash("No tienes permiso para descargar este documento", "danger")
        return redirect(url_for("inicio"))

    # Generar PDF
    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)
    
    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 800, "SOLICITUD DE INSCRIPCIÓN - EMPRENDEDORES")
    
    # Contenido
    pdf.setFont("Helvetica", 10)
    y = 770
    
    campos = [
        ("Nombre:", solicitud.get("nombre", "N/A")),
        ("Email:", solicitud.get("correo", "N/A")),
        ("Edad:", str(solicitud.get("edad", "N/A"))),
        ("Carrera:", solicitud.get("carrera", "N/A")),
        ("Nivel:", solicitud.get("nivel", "N/A")),
        ("Matrícula:", solicitud.get("matricula", "N/A")),
        ("Teléfono:", solicitud.get("telefono", "N/A")),
        ("Proyecto:", solicitud.get("nombre_proyecto", "N/A")),
        ("Descripción:", solicitud.get("descripcion_proyecto", "N/A")[:80] + "..."),
        ("Estado:", solicitud.get("estado", "N/A").upper()),
    ]
    
    for campo, valor in campos:
        pdf.drawString(50, y, f"{campo} {valor}")
        y -= 20
    
    pdf.drawString(50, y - 20, f"Fecha de solicitud: {solicitud.get('fecha_creacion', 'N/A')}")
    
    pdf.showPage()
    pdf.save()
    
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"solicitud_{id}.pdf",
        mimetype="application/pdf"
    )


# ================= SISTEMA DE MENSAJES =================
@app.route("/chat")
@login_requerido
def chat():
    """Página de chat entre usuario y admin"""
    # Si es admin, debe pasar un usuario_id como parámetro
    if session.get("rol") == "admin":
        usuario_id_target = request.args.get("usuario_id")
        if not usuario_id_target:
            flash("Debes especificar un usuario", "danger")
            return redirect(url_for("panel_admin"))
        usuario_id = int(usuario_id_target)
    else:
        usuario_id = session["usuario_id"]
    
    db = conexion()
    cursor = db.cursor(dictionary=True)
    
    # Obtener mensajes ordenados por fecha
    cursor.execute("""
        SELECT m.*, 
               CASE 
                   WHEN m.remitente_tipo = 'usuario' THEN u.correo
                   WHEN m.remitente_tipo = 'admin' THEN a.nombre
               END as nombre_remitente
        FROM mensajes m
        LEFT JOIN usuarios u ON m.usuario_id = u.id AND m.remitente_tipo = 'usuario'
        LEFT JOIN administradores a ON m.remitente_tipo = 'admin'
        WHERE m.usuario_id = %s
        ORDER BY m.fecha_creacion ASC
    """, (usuario_id,))
    
    mensajes = cursor.fetchall()
    
    # Formatear fecha de los mensajes
    for msg in mensajes:
        if msg['fecha_creacion']:
            if isinstance(msg['fecha_creacion'], str):
                # Si ya es string, dejarla como está
                pass
            else:
                # Si es datetime, convertir a string
                msg['fecha_creacion'] = msg['fecha_creacion'].strftime('%d/%m/%Y %H:%M')
    
    # Obtener info del usuario (para mostrar en el header del chat)
    # El nombre está en solicitudes, no en usuarios
    cursor.execute("""
        SELECT u.correo, s.nombre 
        FROM usuarios u 
        LEFT JOIN solicitudes s ON u.id = s.usuario_id 
        WHERE u.id = %s
    """, (usuario_id,))
    usuario_info = cursor.fetchone()
    
    # Contar mensajes no leídos
    cursor.execute("""
        SELECT COUNT(*) as no_leidos FROM mensajes 
        WHERE usuario_id = %s AND leido = FALSE AND remitente_tipo = 'admin'
    """, (usuario_id,))
    
    no_leidos = cursor.fetchone()["no_leidos"]
    
    cursor.close()
    db.close()
    
    # Validar que el usuario no intente ver chats de otros usuarios
    if session.get("rol") != "admin" and usuario_id != session["usuario_id"]:
        flash("No tienes permiso para ver este chat", "danger")
        return redirect(url_for("inicio"))
    
    return render_template("chat.html", mensajes=mensajes, no_leidos=no_leidos, 
                         usuario_id=usuario_id, usuario_info=usuario_info)


@app.route("/enviar_mensaje", methods=["POST"])
@login_requerido
def enviar_mensaje():
    """Guardar mensaje del usuario o admin"""
    contenido = request.form.get("contenido", "").strip()
    usuario_id_target = request.form.get("usuario_id")
    
    if not contenido:
        flash("El mensaje no puede estar vacío", "danger")
        return redirect(request.referrer or url_for("chat"))
    
    # Si es admin, usar el usuario_id del formulario; si no, usar su propia ID
    if session.get("rol") == "admin":
        if not usuario_id_target:
            flash("Debes especificar un usuario", "danger")
            return redirect(url_for("panel_admin"))
        usuario_id = int(usuario_id_target)
    else:
        usuario_id = session["usuario_id"]
    
    db = conexion()
    cursor = db.cursor()
    
    try:
        # Determinar si es admin o usuario
        es_admin = session.get("rol") == "admin"
        remitente_tipo = "admin" if es_admin else "usuario"
        
        cursor.execute("""
            INSERT INTO mensajes (usuario_id, remitente_tipo, contenido, fecha_creacion)
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, remitente_tipo, contenido, datetime.now()))
        
        db.commit()
        
        # Si es admin enviando mensaje, crear notificación
        if es_admin:
            cursor.execute("""
                INSERT INTO notificaciones 
                (usuario_id, tipo, titulo, mensaje, enlaces_a, fecha_creacion)
                VALUES (%s, 'respuesta', 'Nuevo mensaje', %s, 'chat', %s)
            """, (usuario_id, contenido, datetime.now()))
            db.commit()
        
        flash("Mensaje enviado correctamente", "success")
    
    except Exception as e:
        db.rollback()
        flash(f"Error al enviar mensaje: {str(e)}", "danger")
    
    finally:
        cursor.close()
        db.close()
    
    # Redirigir al chat del usuario específico
    if session.get("rol") == "admin":
        return redirect(url_for("chat", usuario_id=usuario_id))
    else:
        return redirect(url_for("chat"))


@app.route("/marcar_mensajes_leidos", methods=["POST"])
@login_requerido
def marcar_mensajes_leidos():
    """Marcar mensajes como leídos"""
    db = conexion()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            UPDATE mensajes 
            SET leido = TRUE
            WHERE usuario_id = %s AND remitente_tipo = 'admin'
        """, (session["usuario_id"],))
        
        db.commit()
    
    except Exception as e:
        db.rollback()
    
    finally:
        cursor.close()
        db.close()
    
    return "", 204


# ================= SISTEMA DE NOTIFICACIONES =================
@app.route("/notificaciones")
@login_requerido
def notificaciones():
    """Página de notificaciones"""
    db = conexion()
    cursor = db.cursor(dictionary=True)
    
    # Obtener notificaciones del usuario ordenadas por fecha descendente
    cursor.execute("""
        SELECT * FROM notificaciones
        WHERE usuario_id = %s
        ORDER BY fecha_creacion DESC
        LIMIT 50
    """, (session["usuario_id"],))
    
    notificaciones_list = cursor.fetchall()
    
    # Contar no leídas
    cursor.execute("""
        SELECT COUNT(*) as total FROM notificaciones
        WHERE usuario_id = %s AND leido = FALSE
    """, (session["usuario_id"],))
    
    total_no_leidas = cursor.fetchone()["total"]
    
    cursor.close()
    db.close()
    
    return render_template("notificaciones.html", 
                         notificaciones=notificaciones_list, 
                         total_no_leidas=total_no_leidas)


@app.route("/marcar_notificacion_leida/<int:id>", methods=["POST"])
@login_requerido
def marcar_notificacion_leida(id):
    """Marcar una notificación como leída"""
    db = conexion()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            UPDATE notificaciones 
            SET leido = TRUE
            WHERE id = %s AND usuario_id = %s
        """, (id, session["usuario_id"]))
        
        db.commit()
        flash("Notificación marcada como leída", "info")
    
    except Exception as e:
        db.rollback()
        flash(f"Error: {str(e)}", "danger")
    
    finally:
        cursor.close()
        db.close()
    
    return redirect(url_for("notificaciones"))


@app.route("/obtener_notificaciones_no_leidas")
@login_requerido
def obtener_notificaciones_no_leidas():
    """API para obtener cantidad de notificaciones no leídas (para el navbar)"""
    db = conexion()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT COUNT(*) as total FROM notificaciones
        WHERE usuario_id = %s AND leido = FALSE
    """, (session["usuario_id"],))
    
    resultado = cursor.fetchone()
    cursor.close()
    db.close()
    
    return {"total_no_leidas": resultado["total"]}


def crear_notificacion(usuario_id, tipo, titulo, mensaje, solicitud_id=None, enlace=None):
    """Función auxiliar para crear notificaciones"""
    db = conexion()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO notificaciones 
            (usuario_id, solicitud_id, tipo, titulo, mensaje, enlaces_a, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (usuario_id, solicitud_id, tipo, titulo, mensaje, enlace, datetime.now()))
        
        db.commit()
    
    except Exception as e:
        db.rollback()
        print(f"Error al crear notificación: {str(e)}")
    
    finally:
        cursor.close()
        db.close()


# ================= API PARA VALIDACIÓN AJAX =================
@app.route("/api/validar_archivo", methods=["POST"])
@login_requerido
def api_validar_archivo():
    """Endpoint para validar archivos vía AJAX antes de subirlos"""
    if 'archivo' not in request.files:
        return jsonify({"error": "No se proporcionó archivo", "status": 400}), 400
    
    file = request.files['archivo']
    tipo = request.form.get('tipo', 'general')
    
    tipo_validacion = 'imagen' if tipo in ['foto', 'imagen'] else 'general'
    es_valido, mensaje = validar_archivo(file, tipo_validacion)
    
    if es_valido:
        return jsonify({
            "mensaje": "Archivo válido",
            "tipo": "success",
            "valido": True,
            "nombre": file.filename,
            "tamano": file.tell()
        }), 200
    else:
        return jsonify({
            "error": mensaje,
            "tipo": "error",
            "valido": False
        }), 400


@app.route("/api/verificar_sesion", methods=["GET"])
def api_verificar_sesion():
    """Endpoint para verificar si hay sesión activa vía AJAX"""
    if "usuario_id" in session:
        return jsonify({
            "activa": True,
            "usuario_id": session["usuario_id"],
            "correo": session.get("correo"),
            "rol": session.get("rol"),
            "estado": session.get("estado")
        }), 200
    else:
        return jsonify({
            "activa": False,
            "mensaje": "No hay sesión activa"
        }), 401


@app.route("/api/notificaciones/count", methods=["GET"])
@login_requerido
def api_notificaciones_count():
    """Obtener cantidad de notificaciones no leídas vía AJAX"""
    db = conexion()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM notificaciones
            WHERE usuario_id = %s AND leido = FALSE
        """, (session["usuario_id"],))
        
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        return jsonify({
            "count": count,
            "mensaje": f"Tienes {count} notificaciones sin leer" if count > 0 else "No tienes notificaciones",
            "tipo": "info"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": f"Error al obtener notificaciones: {str(e)}",
            "tipo": "error"
        }), 500
    
    finally:
        cursor.close()
        db.close()


@app.route("/api/marcar_leida/<int:id>", methods=["POST"])
@login_requerido
def api_marcar_leida(id):
    """Marcar notificación como leída vía AJAX"""
    db = conexion()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            UPDATE notificaciones 
            SET leido = TRUE
            WHERE id = %s AND usuario_id = %s
        """, (id, session["usuario_id"]))
        
        db.commit()
        
        return jsonify({
            "mensaje": "Notificación marcada como leída",
            "tipo": "success",
            "success": True
        }), 200
    
    except Exception as e:
        db.rollback()
        return jsonify({
            "error": f"Error: {str(e)}",
            "tipo": "error",
            "success": False
        }), 500
    
    finally:
        cursor.close()
        db.close()


# ================= LOGOUT =================
@app.route("/logout")
@login_requerido
def logout():
    usuario_correo = session.get("correo", "Usuario")
    
    # Eliminar solo las claves del usuario, no los mensajes flash
    session.pop("usuario_id", None)
    session.pop("correo", None)
    session.pop("rol", None)
    session.pop("estado", None)
    
    flash(f"Sesión cerrada - Hasta pronto, {usuario_correo}", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    verificar_base_datos()
    app.run(debug=True)