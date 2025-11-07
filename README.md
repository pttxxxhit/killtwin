# Automatización de Tareas

Una aplicación móvil desarrollada con Flet (Python) para automatizar tareas comunes de gestión de archivos.

## Características

- Búsqueda y eliminación de archivos duplicados
- Organización automática de archivos por tipo
- Redimensionamiento de imágenes en lote
- Renombrado de archivos en serie
- Interfaz intuitiva y fácil de usar

## Requisitos

- Python 3.7 o superior
- Flet
- Pillow (para el manejo de imágenes)

## Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/pttxxxhit/killtwin.git
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecuta la aplicación con:
```bash
python main.py
```

## Estructura del Proyecto

- `main.py`: Aplicación principal
- `borrar_duplicados.py`: Módulo para gestionar archivos duplicados
- `organizar_archivos.py`: Módulo para organizar archivos por tipo
- `cambiar_tamaño.py`: Módulo para redimensionar imágenes
- `rename_files.py`: Módulo para renombrar archivos en serie
- `assets/`: Carpeta con recursos de la aplicación