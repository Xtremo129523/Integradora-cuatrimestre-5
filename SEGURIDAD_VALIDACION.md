# Sistema de Seguridad y Validación Implementado

## ✅ Funcionalidades Implementadas

### 1. **Validación de Permisos** ✓
Se implementaron decoradores para controlar el acceso a rutas:

- `@login_requerido`: Requiere que el usuario esté autenticado
- `@solo_admin`: Solo permite acceso a administradores
- `@solo_aceptado`: Solo permite acceso a usuarios con solicitud aceptada

**Ejemplo de uso:**
```python
@app.route("/panel_admin")
@login_requerido
@solo_admin
def panel_admin():
    # Solo admins autenticados pueden acceder
    pass
```

### 2. **Control de Acceso** ✓
Sistema de control de acceso multinivel:

- Validación automática antes de cada request (`@app.before_request`)
- Verificación de correo institucional en sesión
- Bloqueo de acceso a rutas protegidas
- Mensajes flash informativos sobre restricciones

**Rutas permitidas sin autenticación:**
- `login`
- `registro`
- `verificar_correo`
- `reenviar_codigo`
- `static`

### 3. **Validación de Archivos** ✓
Sistema completo de validación de archivos subidos:

**Funciones implementadas:**
- `allowed_file()`: Verifica extensiones permitidas
- `validar_archivo()`: Validación completa (tipo, tamaño, extensión)
- `sanitizar_filename()`: Limpia nombres de archivo para seguridad

**Extensiones permitidas:**
- **Imágenes:** png, jpg, jpeg, gif
- **Documentos:** pdf, doc, docx

**Límites:**
- Tamaño máximo: 16 MB
- Tamaño mínimo: > 0 bytes

**Ejemplo de uso:**
```python
file = request.files.get('archivo')
es_valido, mensaje = validar_archivo(file, tipo='imagen')
if not es_valido:
    flash(mensaje, "danger")
    return redirect(url_for("inicio"))
```

### 4. **Mostrar Errores** ✓
Manejadores personalizados de errores HTTP:

- **403 Forbidden**: Acceso prohibido
- **404 Not Found**: Página no encontrada
- **413 Request Entity Too Large**: Archivo demasiado grande
- **500 Internal Server Error**: Error del servidor
- **Exception**: Manejador genérico de excepciones

**Características:**
- Detección automática de peticiones AJAX (JSON)
- Mensajes amigables para usuarios
- Redirección apropiada según contexto
- Logging de errores

**Respuesta JSON (AJAX):**
```json
{
    "error": "Descripción del error",
    "status": 404
}
```

**Respuesta HTML:**
- Flash message + redirección a login

### 5. **Detectar Respuesta AJAX** ✓
Sistema completo de manejo de respuestas AJAX:

**API Endpoints implementados:**

#### `/api/validar_archivo` (POST)
Valida archivos antes de subirlos
```javascript
const formData = new FormData();
formData.append('archivo', file);
formData.append('tipo', 'imagen');

AjaxValidator.postForm('/api/validar_archivo', formData)
    .then(data => console.log('Válido:', data))
    .catch(err => console.error('Error:', err));
```

#### `/api/verificar_sesion` (GET)
Verifica si hay sesión activa
```javascript
AjaxValidator.get('/api/verificar_sesion')
    .then(data => {
        if (data.activa) {
            console.log('Usuario:', data.correo);
        }
    });
```

#### `/api/notificaciones/count` (GET)
Obtiene número de notificaciones no leídas
```javascript
AjaxValidator.get('/api/notificaciones/count')
    .then(data => {
        console.log(`Notificaciones: ${data.count}`);
    });
```

#### `/api/marcar_leida/<id>` (POST)
Marca notificación como leída
```javascript
AjaxValidator.post(`/api/marcar_leida/${id}`, {})
    .then(data => Toast.success(data.mensaje));
```

### 6. **Mostrar Alertas** ✓
Sistema avanzado de notificaciones Toast:

**Clase ToastNotification:**
```javascript
// Mostrar toast de éxito
Toast.success('Operación exitosa', 5000);

// Mostrar toast de error
Toast.error('Ocurrió un error', 5000);

// Mostrar toast de advertencia
Toast.warning('Ten cuidado', 5000);

// Mostrar toast de información
Toast.info('Información importante', 5000);

// Mostrar toast de peligro
Toast.danger('Acción peligrosa', 5000);
```

**Características:**
- Diseño moderno tipo toast notification
- Animaciones suaves de entrada/salida
- Posición fija en esquina superior derecha
- Auto-cierre con duración configurable
- Botón para cerrar manualmente
- Conversión automática de Flask flash messages
- Iconos visuales por tipo de alerta
- Colores distintivos por categoría

**Conversión automática de Flash:**
Los mensajes flash de Flask se convierten automáticamente en Toast notifications al cargar la página.

## 🔧 Clase AjaxValidator

Maneja todas las peticiones AJAX con validación automática:

```javascript
// GET request
AjaxValidator.get('/api/endpoint')
    .then(data => console.log(data))
    .catch(err => console.error(err));

// POST request con JSON
AjaxValidator.post('/api/endpoint', { key: 'value' })
    .then(data => console.log(data));

// POST request con FormData
const formData = new FormData();
formData.append('campo', 'valor');
AjaxValidator.postForm('/api/endpoint', formData);

// Fetch personalizado
AjaxValidator.fetch('/api/endpoint', {
    method: 'PUT',
    headers: { 'Custom-Header': 'value' }
});
```

**Manejo automático de:**
- Errores HTTP (403, 404, 413, 500)
- Respuestas JSON vs HTML
- Headers de autenticación AJAX
- Conversión de errores a Toast notifications
- Parsing de respuestas

## 🔍 Clase FileValidator

Validación de archivos en el lado del cliente:

```javascript
// Validar archivo general
const resultado = FileValidator.validateFile(file, {
    maxSize: 16 * 1024 * 1024,
    allowedTypes: ['image/jpeg', 'image/png'],
    allowedExtensions: ['jpg', 'jpeg', 'png']
});

if (!resultado.valid) {
    FileValidator.showValidationError(resultado.error);
    return;
}

// Validar solo imágenes
const validacion = FileValidator.validateImage(file);

// Validar solo documentos
const validacion = FileValidator.validateDocument(file);
```

**Validaciones incluidas:**
- ✅ Tamaño de archivo (mín/máx)
- ✅ Tipo MIME
- ✅ Extensión de archivo
- ✅ Archivo vacío
- ✅ Archivo existente

## 📦 Integración en Templates

Para usar el sistema de alertas, agregar en el `<head>` de tus templates:

```html
<!-- Script de alertas y validaciones -->
<script src="{{ url_for('static', filename='alerts.js') }}"></script>
```

## 🎯 Ejemplo Completo de Uso

```html
<!DOCTYPE html>
<html>
<head>
    <title>Mi Página</title>
    <script src="{{ url_for('static', filename='alerts.js') }}"></script>
</head>
<body>
    <!-- Mensajes flash se convierten automáticamente -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="flash-message {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    <!-- Formulario con validación -->
    <form id="miFormulario">
        <input type="file" id="archivo" name="archivo">
        <button type="submit">Subir</button>
    </form>

    <script>
        document.getElementById('miFormulario').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const file = document.getElementById('archivo').files[0];
            
            // Validar en cliente
            const validacion = FileValidator.validateImage(file);
            if (!validacion.valid) {
                Toast.error(validacion.error);
                return;
            }
            
            // Enviar vía AJAX
            const formData = new FormData();
            formData.append('archivo', file);
            formData.append('tipo', 'imagen');
            
            try {
                const resultado = await AjaxValidator.postForm('/api/validar_archivo', formData);
                Toast.success('Archivo válido!');
            } catch (error) {
                // Error ya mostrado automáticamente por AjaxValidator
            }
        });
    </script>
</body>
</html>
```

## 🚀 Características de Seguridad

1. **Sanitización de nombres de archivo**: Usa `secure_filename()` de Werkzeug
2. **Validación multinivel**: Cliente + Servidor
3. **Límites configurables**: Tamaños y tipos personalizables
4. **Headers de seguridad**: `X-Requested-With` para AJAX
5. **Manejo de excepciones**: Try-catch en todas las operaciones críticas
6. **Logging**: Registro de errores para debugging
7. **Control de acceso**: Decoradores en todas las rutas sensibles
8. **Validación de sesión**: Verificación automática antes de cada request

## 📝 Notas Importantes

- Los Toast notifications tienen z-index 999999 para aparecer sobre todo
- Las validaciones AJAX detectan automáticamente peticiones JSON vs HTML
- Los errores se muestran automáticamente, no es necesario llamar Toast manualmente
- Flash messages se convierten a Toast al cargar la página
- Todos los endpoints API retornan JSON con estructura consistente
- La validación de archivos se hace tanto en cliente como en servidor

## 🎨 Personalización

Para personalizar los colores de los Toast, modifica el objeto `colors` en `alerts.js`:

```javascript
const colors = {
    success: '#10b981',  // Verde
    error: '#ef4444',    // Rojo
    warning: '#f59e0b',  // Naranja
    info: '#3b82f6',     // Azul
    danger: '#dc2626'    // Rojo oscuro
};
```

Para cambiar la duración por defecto de los Toast:

```javascript
Toast.show(message, type, 3000); // 3 segundos en lugar de 5
```
