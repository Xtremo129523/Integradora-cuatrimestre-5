# 📧 Guía de Configuración de Correo Electrónico

## ¿Por qué no funcionan los correos?

El sistema necesita credenciales SMTP para enviar correos. Sigue estos pasos:

---

## 📋 Paso 1: Preparar tu cuenta de Gmail

### Con autenticación de 2 factores (RECOMENDADO):

1. **Habilita 2FA en tu cuenta de Google:**
   - Ve a: https://myaccount.google.com/security
   - Busca "Verificación en dos pasos"
   - Actívala si no está activada

2. **Genera una "Contraseña de App":**
   - Ve a: https://myaccount.google.com/apppasswords
   - Selecciona: **Correo** → **Windows**
   - Google generará una contraseña de 16 caracteres
   - **Copia esta contraseña** (la necesitarás en el siguiente paso)

---

## 🔑 Paso 2: Configurar el archivo `.env`

### Opción A: Usar Gmail (Recomendado)

1. En la carpeta del proyecto, crea o abre el archivo `.env`
2. Agrega estas líneas:

```env
SMTP_USER=tu_correo@gmail.com
SMTP_PASS=xxxx xxxx xxxx xxxx
```

**Ejemplo con credenciales reales:**
```env
SMTP_USER=xtremo446@gmail.com
SMTP_PASS=abcd efgh ijkl mnop
```

> ⚠️ **IMPORTANTE:** 
> - La contraseña tiene espacios, ¡NO los quites!
> - No uses tu contraseña de Gmail normal, usa la contraseña de app que generaste
> - Este archivo contiene credenciales sensibles, nunca lo subas a Git

3. Guarda el archivo `.env`

### Opción B: Usar Outlook/Hotmail

```env
SMTP_USER=tu_correo@outlook.com
SMTP_PASS=tu_contraseña_outlook
```

---

## ✅ Paso 3: Verificar que funciona

Ejecuta el script de prueba:

```bash
python probar_correo.py
```

Este script:
- ✅ Verifica que las credenciales estén configuradas
- ✅ Prueba la conexión a Gmail
- ✅ Intenta autenticarse
- ✅ Envía un correo de prueba

**Si todo funciona, verás:**
```
✅ Conectado al servidor SMTP
✅ TLS iniciado
✅ Autenticación exitosa
✅ Correo de prueba enviado
✅ ¡TODAS LAS PRUEBAS PASARON!
```

---

## 🐛 Solución de problemas

### Error: "SMTP_USER no está configurado"
- Verifica que existe el archivo `.env`
- Asegúrate de que no hay espacios al inicio de las líneas
- Reinicia la aplicación Flask después de agregar el `.env`

### Error: "Error de autenticación"
- ¿Usaste la contraseña de app (16 caracteres)?
- ¿La contraseña tiene espacios? (Es normal, no los quites)
- Verifica que 2FA está habilitado en tu cuenta Google
- Intenta generar una nueva contraseña de app

### Error: "Timeout al conectar"
- Verifica tu conexión a internet
- El servidor SMTP podría estar saturado (intenta de nuevo)
- Algunos firewalls pueden bloquear el puerto 587

### El correo nunca llega
- Revisa la carpeta de SPAM
- Verifica que el correo institucional (@utacapulco.edu.mx) es válido
- Revisa la consola de Flask para mensajes de error

---

## 🧪 Prueba en la aplicación

Una vez configurado:

1. Abre http://localhost:5000 en tu navegador
2. Hace click en "Registrarse"
3. Ingresa un correo institucional (@utacapulco.edu.mx)
4. Ingresa una contraseña
5. Deberías recibir un correo con un código de 6 dígitos

Si no recibir el correo:
- Revisa spam/basura
- Abre la consola de Flask (terminal donde ejecutas `python app.py`)
- Busca mensajes de error entre `📧` y `✅` o `❌`

---

## 🔐 Seguridad

**El archivo `.env` contiene credenciales sensibles:**
- ✅ Está en `.gitignore` (no se sube a GitHub)
- ✅ Solo léelo si necesitas verificar la configuración
- ✅ Nunca compartas este archivo
- ✅ Si lo haces público por accidente, cambia la contraseña de app

---

## 📱 Alternativa: Usar app.py sin correos

Si no quieres configurar correos aún, puedes:

1. Comentar la verificación en `app.py`:

```python
# En el registro, después de crear el usuario:
# flash("✅ Cuenta creada. Inicia sesión.", "success")
# return redirect(url_for("login"))
```

2. **NO RECOMENDADO** para producción

---

## 📞 ¿Necesitas ayuda?

Si los correos siguen sin funcionar:

1. Ejecuta: `python probar_correo.py`
2. Revisa los mensajes de error
3. Verifica que:
   - Gmail tiene 2FA habilitado
   - La contraseña de app se copió correctamente
   - El archivo `.env` existe en la carpeta correcta
   - No hay espacios extras en `.env`

---

## ✨ Una vez funcione

El sistema automáticamente:
- ✅ Enviará código al registrarse
- ✅ Permitirá reenviar código si expira
- ✅ Bloqueará login sin verificación
- ✅ Todo con mensajes HTML bonitos
