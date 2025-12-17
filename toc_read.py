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
            
    # Validar existencia de secciones principales
    required_sections = ["generales", "recursos", "productos", "gastos_operacion"]
    missing_sections = [sec for sec in required_sections if sec not in datos]
    
    if missing_sections:
        raise ValueError(f"El archivo YAML está incompleto. Faltan las siguientes secciones obligatorias: {', '.join(missing_sections)}")

    # Validar contenido de la sección 'generales'
    generales = datos["generales"]
    if not generales or "empresa" not in generales or "fecha" not in generales:
        raise ValueError("La sección 'generales' debe contener los campos 'empresa' y 'fecha'.")
    
    # Validar que existan datos en 'recursos', 'productos' y 'gastos_operacion'
    if not datos["recursos"]:
         raise ValueError("La sección 'recursos' no puede estar vacía. Debe definir al menos un recurso.")
         
    if not datos["productos"]:
         raise ValueError("La sección 'productos' no puede estar vacía. Debe definir al menos un producto.")
         
    if not datos["gastos_operacion"]:
         raise ValueError("La sección 'gastos_operacion' no puede estar vacía. Debe definir al menos un gasto operativo.")

    return datos
