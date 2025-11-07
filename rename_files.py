import os
import pathlib

def rename_files_in_sequence(files, base_name):
    """
    Renombra una lista de archivos usando un nombre base y agregando números secuenciales.
    
    Args:
        files (list): Lista de rutas de archivos a renombrar
        base_name (str): Nombre base para los archivos (ej: 'Factura julio')
        
    Returns:
        list: Lista de tuplas (éxito, antiguo_nombre, nuevo_nombre)
    """
    results = []
    
    # Ordenar los archivos por nombre para mantener un orden consistente
    files = sorted(files)
    
    for index, file_path in enumerate(files, start=1):
        try:
            # Obtener la extensión del archivo original
            path = pathlib.Path(file_path)
            extension = path.suffix
            
            # Crear el nuevo nombre: base_name + número + extensión original
            new_name = f"{base_name} {index}{extension}"
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            
            # Verificar si el archivo de destino ya existe
            counter = 1
            while os.path.exists(new_path):
                new_name = f"{base_name} {index} ({counter}){extension}"
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                counter += 1
            
            # Renombrar el archivo
            os.rename(file_path, new_path)
            results.append((True, os.path.basename(file_path), new_name))
            
        except Exception as e:
            results.append((False, os.path.basename(file_path), str(e)))
    
    return results