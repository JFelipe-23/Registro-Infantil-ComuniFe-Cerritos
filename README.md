# Registro Infantil ComuniFe

Sistema web para la gestión de registros de ingreso/salida de niños en salones de Comunife.

## Descripción

Esta aplicación permite:
- Registrar la entrada de un niño a un salón con datos del acudiente.
- Generar una credencial o "scarapela" con código de registro.
- Gestionar usuarios de staff, supervisores y administrador.
- Marcar la salida del niño desde el panel de staff.
- Cambiar responsable del salón y actualizar contraseñas.
- Generar reportes descargables en Excel por año o mes.

## Funcionalidades principales

- Registro público de niños por salón.
- Login para staff con roles:
  - Administrador
  - Supervisor
  - Personal de salón
- Creación y eliminación de salones.
- Asignación de supervisor a salones.
- Paneles privados para seguimiento de registros activos.
- Exportación de registros a Excel.

## Tecnologías

- Python 3
- Flask
- Flask-Login
- Flask-WTF
- SQLAlchemy
- PostgreSQL
- Pandas
- openpyxl
- Gunicorn

## Instalación

1. Clona o copia el repositorio en tu máquina.
2. Crea y activa un entorno virtual de Python.
3. Instala dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

La aplicación usa `DATABASE_URL` para conectarse a PostgreSQL. Si no está definida, usa una URL por defecto incluida en `models.py`.

Ejemplo de variable de entorno:

```bash
set DATABASE_URL=postgresql://usuario:contraseña@host:puerto/base_de_datos
```

También se puede cambiar la clave secreta en `models.py` si es necesario.

## Inicializar la base de datos

Ejecuta el script para crear las tablas y, si no existe un administrador, crear el primer usuario admin:

```bash
python init_db.py
```

Sigue las indicaciones para registrar el nombre, usuario y contraseña del administrador.

## Ejecución

### Modo de desarrollo

```bash
python wsgi.py
```

Luego abre en el navegador:

```text
http://127.0.0.1:5000/
```

### Despliegue con Gunicorn

```bash
gunicorn wsgi:app
```

## Estructura del proyecto

- `app.py` - Rutas y controladores principales de Flask.
- `models.py` - Modelos SQLAlchemy y lógica de acceso a datos.
- `forms.py` - Formularios WTForms.
- `init_db.py` - Script de inicialización de la base de datos y creación de admin.
- `wsgi.py` - Punto de entrada para ejecución / despliegue.
- `requirements.txt` - Dependencias del proyecto.
- `templates/` - Vistas Jinja2.
- `static/` - Archivos estáticos.

## Uso

- Visitar `/` para acceder a la página principal y seleccionar un salón.
- `staff/logIn` para acceder al panel de staff.
- Los usuarios admin pueden crear salones y asignar supervisores.
- Los supervisores y staff pueden acceder a sus paneles según su rol.

## Notas

- El proyecto está orientado a registros diarios y marcas de salida.
- Los reportes descargables se generan en formato Excel.
- El sistema usa validación básica en formularios y seguridad con hash de contraseñas.

## Contacto

Para mejoras o configuración, revisa el código de `app.py`, `models.py` y los templates en `templates/`.
