# 📧 ANÁLISIS DEL SISTEMA DE CORREO ELECTRÓNICO

## 🔴 PROBLEMA PRINCIPAL

**Las credenciales SMTP no están configuradas**, por lo que:
- ❌ Los correos NO se envían
- ❌ Los usuarios NO pueden verificar su cuenta
- ❌ El registro está parcialmente bloqueado

---

## 📊 CONFIGURACIÓN ACTUAL

### Líneas 30-35 de app.py:
```python
INSTITUTION_DOMAIN = "@utacapulco.edu.mx"

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "")  # ⚠️ VACÍO
SMTP_PASS = os.getenv("SMTP_PASS", "")  # ⚠️ VACÍO
```

---

## 🎯 3 OPCIONES DE SOLUCIÓN

### **OPCIÓN 1: Desactivar Verificación por Correo (RÁPIDO)**

✅ **Ventajas:**
- Funciona inmediatamente
- No requiere configuración externa
- Los usuarios pueden registrarse y usar el sistema

❌ **Desventajas:**
- Menos seguro
- No valida correos reales
- Cualquiera puede registrarse con correo falso

**Implementación:**
1. Eliminar verificación de SMTP en registro
2. Crear usuarios con `verificado=1` automáticamente
3. Eliminar rutas `/verificar_correo` y `/reenviar_codigo`

---

### **OPCIÓN 2: Configurar Gmail con App Password (RECOMENDADO)**

✅ **Ventajas:**
- Sistema completo y seguro
- Verificación real de correos
- Gratis (usando cuenta Gmail)

❌ **Desventajas:**
- Requiere crear cuenta Gmail
- Configurar autenticación de 2 factores
- Generar contraseña de aplicación

**Pasos:**
1. Crear cuenta Gmail (o usar existente)
2. Activar verificación en 2 pasos
3. Generar "Contraseña de aplicación"
4. Crear archivo `.env` en la raíz del proyecto:
   ```
   SMTP_USER=tu-correo@gmail.com
   SMTP_PASS=xxxx-xxxx-xxxx-xxxx
   ```
5. Instalar python-dotenv: `pip install python-dotenv`
6. Agregar al inicio de app.py:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

**Guía para Gmail:**
1. https://myaccount.google.com/security
2. Activar "Verificación en 2 pasos"
3. "Contraseñas de aplicaciones" → Generar nueva
4. Seleccionar "Correo" y "Otro"
5. Copiar la contraseña de 16 caracteres

---

### **OPCIÓN 3: Usar SMTP de la UTA (IDEAL)**

✅ **Ventajas:**
- Correos institucionales oficiales
- Más profesional
- Mayor confianza de usuarios

❌ **Desventajas:**
- Requiere contactar con IT de la UTA
- Puede tardar en obtener credenciales
- Depende de políticas institucionales

**Necesitas solicitar a IT:**
- Servidor SMTP de la UTA
- Puerto (usualmente 587 o 465)
- Usuario y contraseña para envío
- Política de uso (límites de envío)

**Ejemplo de configuración (depende de la UTA):**
```python
SMTP_HOST = "smtp.utacapulco.edu.mx"  # O el que te indique IT
SMTP_PORT = 587  # O 465 si usan SSL
SMTP_USER = "sistema@utacapulco.edu.mx"
SMTP_PASS = "contraseña-proporcionada"
```

---

## 🔄 FLUJO ACTUAL DEL SISTEMA

### Registro con Verificación (ACTUAL):
```
Usuario → Ingresa correo + password
    ↓
Valida @utacapulco.edu.mx ✅
    ↓
¿SMTP configurado? ❌
    ↓
Muestra error: "El envio de correos no esta configurado"
```

### Login (ACTUAL):
```
Usuario → Ingresa credenciales
    ↓
Valida en BD
    ↓
¿Verificado? ❌
    ↓
Redirige a /verificar_correo (pero el correo nunca se envió)
```

---

## 📝 CÓDIGO RELEVANTE

### Función enviar_correo (línea 49):
```python
def enviar_correo(destinatario, asunto, cuerpo):
    if not smtp_configurado():
        return False, "SMTP no configurado"

    mensaje = EmailMessage()
    mensaje["Subject"] = asunto
    mensaje["From"] = f"Sistema Emprendedores <{SMTP_USER}>"
    mensaje["To"] = destinatario
    mensaje.set_content(cuerpo)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)  # ❌ Falla aquí
            smtp.send_message(mensaje)
        return True, None
    except Exception as exc:
        return False, str(exc)
```

### Registro (línea 361):
```python
if not smtp_configurado():
    return render_template(
        "registro.html",
        error="El envio de correos no esta configurado. Contacta al administrador."
    )
```

---

## 🎯 RECOMENDACIÓN

**Para desarrollo/pruebas inmediatas:**
→ **OPCIÓN 1** (Desactivar verificación)

**Para producción:**
→ **OPCIÓN 2** (Gmail App Password) mientras gestionas **OPCIÓN 3** (SMTP UTA)

---

## 📌 CAMPOS DE BD RELACIONADOS

Tabla `usuarios`:
- `correo` VARCHAR(100) - Almacena el email
- `verificado` TINYINT(1) - 0: No verificado, 1: Verificado
- `codigo_verificacion` VARCHAR(6) - Código de 6 dígitos
- `codigo_expira` DATETIME - Fecha de expiración (15 min)

---

## ✅ CHECKLIST DE DECISIÓN

¿Qué opción necesitas?

- [ ] **Opción 1** - Solo quiero que funcione ya (desarrollo)
- [ ] **Opción 2** - Quiero verificación real con Gmail
- [ ] **Opción 3** - Contactaré con IT de la UTA

**Dime cuál prefieres y lo implemento inmediatamente.**
