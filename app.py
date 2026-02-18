from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import re
import mysql.connector
from datetime import datetime
from functools import wraps
import io
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "6382"
DB_NAME = "emprendedoress"
DB_PORT = 3307

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

        # Verificar la contraseña
        if usuario["password"] != password:
            flash("Contraseña incorrecta", "danger")
            cursor.close()
            db.close()
            return redirect(url_for("login"))

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

        db = conexion()
        cursor = db.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE correo=%s", (correo,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return render_template("registro.html", error="Este correo ya está registrado. Inicia sesión.")

        cursor.execute("""
            INSERT INTO usuarios (correo, password, rol, estado)
            VALUES (%s, %s, 'alumno', 'pendiente')
        """, (correo, password))

        db.commit()
        cursor.close()
        db.close()

        flash("✓ Cuenta creada correctamente. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")


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
        cursor.execute("""
            INSERT INTO solicitudes (
                usuario_id,
                nombre,
                edad,
                carrera,
                nivel,
                matricula,
                asesor_academico,
                tutor,
                telefono,
                direccion,
                numero_integrantes,
                descripcion_proyecto,
                ubicacion_emprendimiento,
                fecha_inicio_emprendimiento,
                clientes_clave,
                problema_resuelve,
                producto_servicio,
                innovacion,
                creacion_valor,
                idea_7_palabras,
                nombre_proyecto,
                alta_sat,
                personas_trabajando,
                miembros_incubacion,
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
                %s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,'pendiente'
            )
        """, (
            session["usuario_id"],
            request.form["nombre"],
            request.form["edad"],
            request.form["carrera"],
            request.form["nivel"],
            request.form["matricula"],
            request.form["asesor"],
            request.form["tutor"],
            request.form["telefono"],
            request.form["direccion"],
            request.form["integrantes"],
            request.form["descripcion"],
            request.form["ubicacion"],
            request.form["inicio_emprendimiento"],
            request.form["clientes"],
            request.form["problema"],
            request.form["producto"],
            request.form["innovacion"],
            request.form["valor"],
            request.form["idea7"],
            request.form["nombre_proyecto"],
            request.form["sat"],
            request.form["trabajadores"],
            request.form["incubacion"],
            request.form["convocatoria"],
            request.form["lider_descripcion"],
            request.form["rol"],
            request.form["habilidades"],
            request.form["asombroso"],
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
    
    # Obtener info del usuario (para mostrar en el header del chat)
    cursor.execute("SELECT correo, nombre FROM usuarios WHERE id = %s", (usuario_id,))
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