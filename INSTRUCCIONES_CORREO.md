# 📧 GUÍA: CONFIGURAR CORREO ELECTRÓNICO PARA EL SISTEMA

## ✅ ¿QUÉ SE HA CONFIGURADO?

1. ✅ Instalado `python-dotenv`
2. ✅ Creado archivo `.env` para credenciales
3. ✅ Creado `.gitignore` para proteger credenciales
4. ✅ Modificado `app.py` para cargar variables de entorno
5. ✅ Actualizado `requirements.txt`

---

## 🔐 PASO 1: CREAR/USAR CUENTA DE GMAIL

Necesitas una cuenta de Gmail para enviar correos. Puedes:
- Usar tu cuenta personal
- Crear una cuenta nueva específica para el sistema (recomendado)

**Sugerencia de nombre:** `sistemautac@gmail.com` o similar

---

## 🛡️ PASO 2: ACTIVAR VERIFICACIÓN EN 2 PASOS

1. Ve a: https://myaccount.google.com/security
2. Busca "Verificación en 2 pasos"
3. Haz clic en "Empezar" o "Activar"
4. Sigue el proceso de verificación (SMS o app)

**⚠️ IMPORTANTE:** Sin este paso NO podrás generar contraseñas de aplicación.

---

## 🔑 PASO 3: GENERAR CONTRASEÑA DE APLICACIÓN

1. Ve a: https://myaccount.google.com/apppasswords
   - O busca "Contraseñas de aplicaciones" en la configuración de seguridad
   
2. **Si no ves la opción:**
   - Asegúrate de haber completado el Paso 2
   - Cierra sesión y vuelve a iniciar
   
3. **Crear contraseña:**
   - En "Selecciona la app": Elige "Correo"
   - En "Selecciona el dispositivo": Elige "Otro (nombre personalizado)"
   - Escribe: "Sistema Emprendedores UTA"
   - Haz clic en "Generar"
   
4. **Se mostrará una contraseña de 16 caracteres como:**
   ```
   abcd efgh ijkl mnop
   ```
   
5. **⚠️ COPIA LA CONTRASEÑA INMEDIATAMENTE** (solo se muestra una vez)

---

## ⚙️ PASO 4: CONFIGURAR EL ARCHIVO .env

1. Abre el archivo `.env` en la raíz del proyecto

2. Reemplaza estas líneas:
   ```
   SMTP_USER=tu-correo@gmail.com
   SMTP_PASS=xxxx-xxxx-xxxx-xxxx
   ```

3. **Con tus datos reales:**
   ```
   SMTP_USER=sistemautac@gmail.com
   SMTP_PASS=abcdefghijklmnop
   ```

4. **IMPORTANTE:**
   - La contraseña va **SIN ESPACIOS** (quita los espacios entre grupos)
   - Ejemplo: `abcd efgh ijkl mnop` → `abcdefghijklmnop`
   - NO uses tu contraseña normal de Gmail, usa la de aplicación

---

## 🧪 PASO 5: PROBAR EL SISTEMA

1. **Guarda el archivo .env**

2. **Reinicia el servidor Flask** si estaba corriendo

3. **Prueba el registro:**
   ```
   - Visita: http://127.0.0.1:5000/registro
   - Ingresa un correo institucional: alumno@utacapulco.edu.mx
   - Ingresa una contraseña
   - Haz clic en registrar
   ```

4. **Verifica que:**
   - ✅ No aparece error de "SMTP no configurado"
   - ✅ Aparece mensaje de "Se envió un código de verificación"
   - ✅ Revisa el correo (bandeja de entrada o spam)

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "SMTP no configurado"
- ❌ El archivo `.env` no existe o está mal ubicado
- ❌ Las variables SMTP_USER o SMTP_PASS están vacías
- ✅ Verifica que `.env` esté en `proyecto integrador/`
- ✅ Verifica que no haya espacios extra en las variables

### Error: "No se pudo enviar el correo"
- ❌ Contraseña de aplicación incorrecta
- ❌ No has activado verificación en 2 pasos
- ❌ Usaste la contraseña normal en vez de la de aplicación
- ✅ Genera una nueva contraseña de aplicación
- ✅ Cópiala sin espacios

### Error: "Authentication failed"
- ❌ Credenciales incorrectas
- ✅ Verifica que el correo sea correcto
- ✅ Verifica que la contraseña no tenga espacios
- ✅ Prueba iniciando sesión en Gmail para verificar la cuenta

### El correo no llega
- ⏰ Espera 1-2 minutos
- 📧 Revisa la carpeta de SPAM
- 🔍 Busca "Sistema Emprendedores"
- 📱 Verifica que el correo destino sea correcto

---

## 📋 EJEMPLO COMPLETO DE .env

```env
# Ejemplo funcional (reemplaza con tus datos)
SMTP_USER=sistemautac@gmail.com
SMTP_PASS=abcdefghijklmnop
```

**⚠️ NO compartas este archivo con nadie**
**⚠️ NO lo subas a GitHub (ya está en .gitignore)**

---

## ✅ CHECKLIST FINAL

Antes de probar, asegúrate de:

- [ ] Cuenta de Gmail creada/disponible
- [ ] Verificación en 2 pasos activada
- [ ] Contraseña de aplicación generada
- [ ] Archivo `.env` creado en la carpeta correcta
- [ ] Variables `SMTP_USER` y `SMTP_PASS` configuradas
- [ ] Contraseña copiada SIN espacios
- [ ] Servidor Flask reiniciado

---

## 🎯 RESULTADO ESPERADO

Cuando todo esté configurado:

1. Usuario se registra con correo `@utacapulco.edu.mx`
2. Sistema genera código de 6 dígitos
3. Correo se envía automáticamente
4. Usuario recibe correo con código
5. Usuario ingresa código en `/verificar_correo`
6. Cuenta verificada ✅
7. Usuario puede iniciar sesión ✅

---

## 📞 AYUDA ADICIONAL

**Videos útiles en YouTube:**
- "Como generar contraseña de aplicación Gmail 2024"
- "Verificación en 2 pasos Gmail"
- "App passwords Google"

**Documentación oficial:**
- https://support.google.com/accounts/answer/185833

---

**Si sigues teniendo problemas, verifica:**
1. Que python-dotenv esté instalado: `pip list | findstr dotenv`
2. Que el archivo .env exista: `dir .env`
3. Que las variables se carguen: Agrega `print(os.getenv("SMTP_USER"))` después de `load_dotenv()` en app.py

¡Listo! El sistema de correo está completamente configurado. 📧✅
