
import os
import hashlib


def hash_file(filename):
    h = hashlib.md5()
    with open(filename, 'rb') as file:
        while chunk := file.read(8192):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(folder):
    hashes = {}
    duplicates = []
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            try:
                file_hash = hash_file(full_path)
                if file_hash in hashes:
                    duplicates.append((full_path, hashes[file_hash]))
                else:
                    hashes[file_hash] = full_path
            except PermissionError:
                print(f"Permiso denegado para acceder al archivo: {full_path}")
            except Exception as e:
                print(f"Error inesperado con el archivo {full_path}: {e}")
    return duplicates
def delete_file(file_path):
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error al eliminar el archivo {file_path}: {e}")
        return False



