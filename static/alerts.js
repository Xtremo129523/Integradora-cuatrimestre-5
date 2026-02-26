/**
 * Sistema de Alertas y Notificaciones Mejorado
 * Incluye Toast notifications, validación de respuestas AJAX y manejo de errores
 */

// ================= SISTEMA DE TOAST NOTIFICATIONS =================
class ToastNotification {
    constructor() {
        this.container = this.createContainer();
        document.body.appendChild(this.container);
    }

    createContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 999999;
            max-width: 400px;
        `;
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const toast = this.createToast(message, type);
        this.container.appendChild(toast);

        // Animación de entrada
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto-remove
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        return toast;
    }

    createToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            danger: '🚫'
        };

        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6',
            danger: '#dc2626'
        };

        toast.style.cssText = `
            background: white;
            border-left: 4px solid ${colors[type] || colors.info};
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            display: flex;
            align-items: center;
            gap: 12px;
            opacity: 0;
            transform: translateX(400px);
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
            max-width: 100%;
        `;

        toast.innerHTML = `
            <span style="font-size: 20px;">${icons[type] || icons.info}</span>
            <div style="flex: 1; color: #333; font-size: 14px;">${message}</div>
            <button onclick="this.parentElement.remove()" style="
                background: none;
                border: none;
                font-size: 20px;
                color: #999;
                cursor: pointer;
                padding: 0;
                line-height: 1;
            ">×</button>
        `;

        toast.classList.add('show');
        return toast;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    danger(message, duration) {
        return this.show(message, 'danger', duration);
    }
}

// Instancia global de Toast
const Toast = new ToastNotification();

// Agregar estilos globales para la animación show
const style = document.createElement('style');
style.textContent = `
    .toast.show {
        opacity: 1 !important;
        transform: translateX(0) !important;
    }
`;
document.head.appendChild(style);


// ================= VALIDACIÓN DE RESPUESTAS AJAX =================
class AjaxValidator {
    static handleResponse(response) {
        // Detectar tipo de respuesta
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => {
                if (data.error) {
                    Toast.error(data.error);
                    throw new Error(data.error);
                }
                
                if (data.mensaje || data.message) {
                    const msg = data.mensaje || data.message;
                    const tipo = data.tipo || data.type || 'info';
                    Toast.show(msg, tipo);
                }
                
                return data;
            });
        }
        
        return response.text();
    }

    static handleError(error) {
        console.error('Error AJAX:', error);
        
        if (error.message) {
            Toast.error(`Error: ${error.message}`);
        } else {
            Toast.error('Ocurrió un error inesperado');
        }
        
        return Promise.reject(error);
    }

    static async fetch(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    ...options.headers
                }
            });

            // Manejar errores HTTP
            if (!response.ok) {
                if (response.status === 403) {
                    Toast.error('⛔ Acceso prohibido');
                } else if (response.status === 404) {
                    Toast.error('❌ Recurso no encontrado');
                } else if (response.status === 413) {
                    Toast.error('📦 Archivo demasiado grande (máx. 16MB)');
                } else if (response.status === 500) {
                    Toast.error('💥 Error del servidor');
                } else {
                    Toast.error(`Error HTTP ${response.status}`);
                }
                throw new Error(`HTTP ${response.status}`);
            }

            return this.handleResponse(response);
        } catch (error) {
            return this.handleError(error);
        }
    }

    static async post(url, data, options = {}) {
        return this.fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            body: typeof data === 'string' ? data : JSON.stringify(data),
            ...options
        });
    }

    static async get(url, options = {}) {
        return this.fetch(url, {
            method: 'GET',
            ...options
        });
    }

    static async postForm(url, formData, options = {}) {
        return this.fetch(url, {
            method: 'POST',
            body: formData,
            ...options
        });
    }
}


// ================= VALIDACIÓN DE ARCHIVOS EN CLIENTE =================
class FileValidator {
    static validateFile(file, options = {}) {
        const {
            maxSize = 16 * 1024 * 1024, // 16MB por defecto
            allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'],
            allowedExtensions = ['jpg', 'jpeg', 'png', 'gif']
        } = options;

        // Validar existencia
        if (!file) {
            return { valid: false, error: 'No se seleccionó ningún archivo' };
        }

        // Validar tamaño
        if (file.size > maxSize) {
            const maxMB = Math.round(maxSize / (1024 * 1024));
            return { valid: false, error: `El archivo excede el tamaño máximo de ${maxMB}MB` };
        }

        // Validar tamaño mínimo
        if (file.size === 0) {
            return { valid: false, error: 'El archivo está vacío' };
        }

        // Validar tipo MIME
        if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
            return { valid: false, error: `Tipo de archivo no permitido. Solo: ${allowedExtensions.join(', ')}` };
        }

        // Validar extensión
        const extension = file.name.split('.').pop().toLowerCase();
        if (allowedExtensions.length > 0 && !allowedExtensions.includes(extension)) {
            return { valid: false, error: `Extensión no permitida. Solo: ${allowedExtensions.join(', ')}` };
        }

        return { valid: true, error: null };
    }

    static validateImage(file) {
        return this.validateFile(file, {
            allowedTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'],
            allowedExtensions: ['jpg', 'jpeg', 'png', 'gif']
        });
    }

    static validateDocument(file) {
        return this.validateFile(file, {
            allowedTypes: ['application/pdf', 'application/msword', 
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            allowedExtensions: ['pdf', 'doc', 'docx']
        });
    }

    static showValidationError(error) {
        Toast.error(error);
    }
}


// ================= HELPER PARA CONVERTIR FLASH MESSAGES =================
function convertFlashMessages() {
    // Buscar mensajes flash en el DOM y convertirlos a toasts
    const flashMessages = document.querySelectorAll('.flash-message, .alert, .message');
    
    flashMessages.forEach(msg => {
        const text = msg.textContent.trim();
        let type = 'info';
        
        if (msg.classList.contains('success') || msg.classList.contains('alert-success')) {
            type = 'success';
        } else if (msg.classList.contains('error') || msg.classList.contains('alert-error') || msg.classList.contains('alert-danger')) {
            type = 'error';
        } else if (msg.classList.contains('warning') || msg.classList.contains('alert-warning')) {
            type = 'warning';
        } else if (msg.classList.contains('danger')) {
            type = 'danger';
        }
        
        if (text) {
            Toast.show(text, type);
        }
        
        // Ocultar el mensaje original
        msg.style.display = 'none';
    });
}

// ================= AUTO-HIDE FLASH MESSAGES =================
function autoHideFlashMessages() {
    // Buscar todos los mensajes flash que no se han convertido a toasts
    const messages = document.querySelectorAll('.message, .flash-message, .alert');
    
    messages.forEach(msg => {
        // Solo aplicar a mensajes visibles
        if (msg.style.display !== 'none') {
            // Agregar animación de desvanecimiento
            msg.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            // Desaparecer después de 5 segundos
            setTimeout(() => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-20px)';
                
                // Remover del DOM después de la animación
                setTimeout(() => {
                    msg.remove();
                }, 500);
            }, 5000);
        }
    });
}

// Convertir mensajes flash al cargar la página
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        convertFlashMessages();
        autoHideFlashMessages();
    });
} else {
    convertFlashMessages();
    autoHideFlashMessages();
}


// ================= EXPORTAR PARA USO GLOBAL =================
window.Toast = Toast;
window.AjaxValidator = AjaxValidator;
window.FileValidator = FileValidator;
window.convertFlashMessages = convertFlashMessages;
window.autoHideFlashMessages = autoHideFlashMessages;
