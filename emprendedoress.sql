-- =====================================================
-- CREAR BASE SI NO EXISTE (NO BORRAR)
-- =====================================================
CREATE DATABASE IF NOT EXISTS emprendedoress
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE emprendedoress;

-- =====================================================
-- TABLA USUARIOS
-- =====================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol ENUM('alumno','admin') NOT NULL DEFAULT 'alumno',
    estado ENUM('pendiente','aceptado','rechazado') NOT NULL DEFAULT 'pendiente',
    documentacion_completa BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Índice para acelerar búsquedas por correo
CREATE INDEX idx_correo ON usuarios(correo);


-- =====================================================
-- TABLA SOLICITUDES
-- =====================================================
CREATE TABLE IF NOT EXISTS solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,

    -- INFORMACIÓN PERSONAL
    nombre VARCHAR(150) NOT NULL,
    edad INT CHECK (edad > 0),
    carrera VARCHAR(150) NOT NULL,
    nivel VARCHAR(100),
    matricula VARCHAR(100),
    asesor_academico VARCHAR(150),
    tutor VARCHAR(150),
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    numero_integrantes INT,

    -- EMPRENDIMIENTO
    descripcion_proyecto TEXT NOT NULL,
    ubicacion_emprendimiento VARCHAR(255),
    fecha_inicio_emprendimiento DATE,
    clientes_clave TEXT,
    problema_resuelve TEXT,
    producto_servicio TEXT,
    innovacion TEXT,
    creacion_valor TEXT,
    idea_7_palabras VARCHAR(255),
    nombre_proyecto VARCHAR(150),
    alta_sat ENUM('si','no') DEFAULT 'no',
    personas_trabajando INT,
    miembros_incubacion INT,
    convocatorias_previas TEXT,

    -- LÍDER
    descripcion_lider TEXT,
    rol_emprendimiento VARCHAR(150),
    habilidades TEXT,
    logro_destacado TEXT,

    -- CONTROL
    estado ENUM('pendiente','aceptado','rechazado') NOT NULL DEFAULT 'pendiente',
    motivo_rechazo VARCHAR(255),
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_solicitudes_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_solicitudes_usuario ON solicitudes(usuario_id);


-- =====================================================
-- DOCUMENTOS INSCRIPCIÓN
-- =====================================================
CREATE TABLE IF NOT EXISTS documentos_inscripcion (
    usuario_id INT PRIMARY KEY,
    ruta_archivo VARCHAR(255) NOT NULL,
    estado ENUM('pendiente','entregado') NOT NULL DEFAULT 'pendiente',
    fecha_subida DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_documentos_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================
-- EVENTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS eventos_programa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT,
    fecha DATETIME NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- =====================================================
-- PROYECTOS
-- =====================================================
CREATE TABLE IF NOT EXISTS proyectos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_proyectos_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================
-- AVANCES
-- =====================================================
CREATE TABLE IF NOT EXISTS avances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    proyecto_id INT NOT NULL,
    usuario_id INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    archivo_pdf VARCHAR(255),
    estado ENUM('pendiente','enviado','revisado','aprobado') NOT NULL DEFAULT 'enviado',
    fecha_envio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_avances_proyecto
        FOREIGN KEY (proyecto_id)
        REFERENCES proyectos(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_avances_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;


-- =====================================================
-- COMENTARIOS
-- =====================================================
CREATE TABLE IF NOT EXISTS comentarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    avance_id INT NOT NULL,
    usuario_id INT NOT NULL,
    contenido TEXT NOT NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_comentarios_avance
        FOREIGN KEY (avance_id)
        REFERENCES avances(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_comentarios_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;