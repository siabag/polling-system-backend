# 🌱 Sistema de Encuestas Quincenales (Backend)

Backend de un sistema diseñado para gestionar encuestas quincenales relacionadas con cultivos de café.  
El sistema permite a los usuarios registrar fincas, crear encuestas, responder factores y generar reportes.  
Desarrollado en **Flask** y utiliza una base de datos **MySQL**.

---

## ✨ Características Principales

- **Gestión de Usuarios**: Registro, autenticación JWT y roles (Administrador, Encuestador, Analista)
- **Registro de Fincas**: Asociadas a usuarios, con ubicación geográfica opcional
- **Encuestas Dinámicas**: Soporte para varios tipos de encuesta (P1, P2, P3, P4)
- **Factores Personalizables**: Agrupados por categorías y vinculados a tipos de encuesta
- **Respuestas Estructuradas**: Uso de valores predefinidos o texto libre
- **Base de Datos Relacional**: Modelo bien estructurado con relaciones e índices
- **Datos Iniciales**: Usuarios, roles y tipos de encuesta precargados

---

## 🛠️ Tecnologías Utilizadas

| Capa          | Tecnología                  |
|---------------|-----------------------------|
| Backend       | Flask, Python 3.8+          |
| Base de Datos | MySQL                       |
| ORM           | SQLAlchemy                  |
| Seguridad     | JWT, PBKDF2-SHA256          |
| Entorno       | `.env`, entorno virtual     |

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- [Python 3.8+](https://www.python.org/downloads/) 
- [MySQL Server](https://dev.mysql.com/downloads/mysql/) 
- `pip` (viene con Python)
- Git (opcional)

---

### 1. Clonar el repositorio (si aplica)

```bash
git clone https://github.com/siabag/polling-system-backend
cd polling-system-backend
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
SECRET_KEY=your_secret_key
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/encuestas_cafe_db
JWT_SECRET_KEY=your_jwt_secret_key
FLASK_ENV=development
```

### 5. Ejecutar script SQL
Ejecuta este script en tu servidor MySQL para crear la base de datos, tablas e insertar datos iniciales:

```bash
-- Script de creación de base de datos para Sistema de Encuestas Quincenales
CREATE DATABASE encuestas_cafe_db;
USE encuestas_cafe_db;

-- Tabla de roles
CREATE TABLE rol (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_rol_nombre UNIQUE (nombre)
);

-- Tabla de usuarios
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    rol_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_usuario_correo UNIQUE (correo),
    CONSTRAINT fk_usuario_rol FOREIGN KEY (rol_id) REFERENCES rol(id)
);

-- Tabla de fincas
CREATE TABLE finca (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(255),
    latitud DECIMAL(10, 8),
    longitud DECIMAL(11, 8),
    propietario VARCHAR(100),
    usuario_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_finca_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- Tabla de tipos de encuesta
CREATE TABLE tipo_encuesta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_tipo_encuesta_nombre UNIQUE (nombre)
);

-- Tabla de factores
CREATE TABLE factor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    categoria VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    tipo_encuesta_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_factor_nombre_tipo UNIQUE (nombre, tipo_encuesta_id),
    CONSTRAINT fk_factor_tipo_encuesta FOREIGN KEY (tipo_encuesta_id) REFERENCES tipo_encuesta(id)
);

-- Tabla de valores posibles
CREATE TABLE valor_posible (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factor_id INT NOT NULL,
    valor VARCHAR(100) NOT NULL,
    codigo INT NOT NULL,
    descripcion VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_valor_posible_factor_codigo UNIQUE (factor_id, codigo),
    CONSTRAINT fk_valor_posible_factor FOREIGN KEY (factor_id) REFERENCES factor(id)
);

-- Tabla de encuestas
CREATE TABLE encuesta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha_aplicacion DATE NOT NULL,
    tipo_encuesta_id INT NOT NULL,
    usuario_id INT NOT NULL,
    finca_id INT NOT NULL,
    observaciones TEXT,
    completada BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_encuesta_tipo_encuesta FOREIGN KEY (tipo_encuesta_id) REFERENCES tipo_encuesta(id),
    CONSTRAINT fk_encuesta_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id),
    CONSTRAINT fk_encuesta_finca FOREIGN KEY (finca_id) REFERENCES finca(id)
);

-- Tabla de respuestas a factores
CREATE TABLE respuesta_factor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    encuesta_id INT NOT NULL,
    factor_id INT NOT NULL,
    valor_posible_id INT NOT NULL,
    respuesta_texto TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_respuesta_encuesta_factor UNIQUE (encuesta_id, factor_id),
    CONSTRAINT fk_respuesta_encuesta FOREIGN KEY (encuesta_id) REFERENCES encuesta(id),
    CONSTRAINT fk_respuesta_factor FOREIGN KEY (factor_id) REFERENCES factor(id),
    CONSTRAINT fk_respuesta_valor_posible FOREIGN KEY (valor_posible_id) REFERENCES valor_posible(id)
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_encuesta_fecha_aplicacion ON encuesta(fecha_aplicacion);
CREATE INDEX idx_factor_activo ON factor(activo);
CREATE INDEX idx_valor_posible_activo ON valor_posible(activo);
CREATE INDEX idx_encuesta_finca ON encuesta(finca_id);
CREATE INDEX idx_encuesta_tipo ON encuesta(tipo_encuesta_id);
CREATE INDEX idx_encuesta_usuario ON encuesta(usuario_id);
CREATE INDEX idx_factor_tipo_encuesta ON factor(tipo_encuesta_id);
CREATE INDEX idx_valor_posible_factor ON valor_posible(factor_id);

-- Datos iniciales
INSERT INTO rol (nombre, descripcion) VALUES 
('administrador', 'Acceso completo al sistema'),
('encuestador', 'Puede crear y ver sus propias encuestas'),
('analista', 'Puede ver todas las encuestas y generar reportes');

INSERT INTO tipo_encuesta (nombre, descripcion) VALUES 
('P1', 'Encuesta quincenal tipo P1'),
('P2', 'Encuesta quincenal tipo P2'),
('P3', 'Encuesta quincenal tipo P3'),
('P4', 'Encuesta quincenal tipo P4');

-- Usuario administrador inicial con contraseña en formato PBKDF2-SHA256
-- La contraseña es 'admin123' hasheada usando el formato PBKDF2
INSERT INTO usuario (nombre, apellido, correo, contrasena_hash, rol_id) VALUES 
('Admin', 'Sistema', 'admin@sistema.com', 'pbkdf2:sha256:600000$eHRObfez$ef1d0a39267a884807b217a7a2899c5691a82cf92e787fd7a82008ed64a48960', 1);
```