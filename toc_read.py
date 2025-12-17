import os
import yaml
from yaml.loader import SafeLoader

# ----------------------------------------------------------------------
## FUNCIÓN HELPER: CARGA DE DATOS YAML
# ----------------------------------------------------------------------

def load_data_from_file(file_path):
    """Carga los datos de recursos y productos desde un archivo YAML."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: El archivo no fue encontrado en la ruta especificada: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            datos = yaml.load(file, Loader=SafeLoader)
        except Exception as e:
            raise Exception(f"Error al parsear el archivo YAML. Revise el formato: {e}")
            
    if "recursos" not in datos or "productos" not in datos:
        raise ValueError("La estructura del archivo es incorrecta. Faltan las claves 'recursos' o 'productos'.")
    
    # Asegurar que 'gastos_operacion' existe, si no, inicializarlo como un diccionario vacío
    
    if "gastos_operacion" not in datos:
         datos["gastos_operacion"] = {}

    return datos
