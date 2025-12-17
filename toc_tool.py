#!/usr/bin/env python3
import os
import sys
# Asumimos que toc_optimize.py y toc_graf.py están en el mismo directorio
import toc_optimize 
import toc_graf 
from toc_read import load_data_from_file

# ----------------------------------------------------------------------
## FUNCIÓN PRINCIPAL DE LA HERRAMIENTA CENTRAL
# ----------------------------------------------------------------------

def run_toc_tool(yaml_file):
    """
    Orquesta el análisis TOC, la graficación, y organiza los archivos de salida.
    Recibe la ruta del archivo YAML como argumento.
    """
    print(f"\n*** Herramienta de Análisis TOC (Teoría de Restricciones) ***")
    print(f"    Archivo de entrada: {yaml_file}")
    
    # 1. Validar entorno y cargar datos para configuración
    
    # Asegurarse de que las librerías necesarias estén disponibles
    try:
        import yaml
        import pandas
        import networkx
        import matplotlib.pyplot
    except ImportError as e:
        print(f"\n❌ Error de dependencia: La librería {e.name} no está instalada.")
        print("   Por favor, ejecute: pip install PyYAML pandas networkx matplotlib")
        return

    # Cargar datos para obtener el nombre de la empresa
    try:
        data = load_data_from_file(yaml_file)
        # Extraer nombre de la empresa de la sección 'generales'
        company_name = data.get("generales", {}).get("empresa", "Empresa_TOC").strip()
        print(f"    Empresa detectada: {company_name}")
        print(f"    Fecha detectada: {data.get('generales', {}).get('fecha', 'YYYY-MM-DD')}")
    except Exception as e:
        print(f"❌ Error al leer datos del archivo '{yaml_file}': {e}")
        return

    # 2. Crear el Directorio de Salida
    
    output_dir = company_name.replace(' ', '_') # Reemplaza espacios por guiones bajos
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"\n📁 Directorio '{output_dir}' creado exitosamente.")
        else:
            print(f"\n⚠️ Directorio '{output_dir}' ya existe. Los archivos serán sobrescritos.")
            
        # Extraer fecha de la sección 'generales' para usar en los nombres de archivo
        analysis_date = str(data.get("generales", {}).get("fecha", "YYYY-MM-DD")).strip()
        
        # Definir rutas de salida
        csv_path = os.path.join(output_dir, f"{analysis_date}_resultados_toc.csv")
        txt_path = os.path.join(output_dir, f"{analysis_date}_resumen.txt")
        png_path = os.path.join(output_dir, f"{analysis_date}_diagrama_toc.png")
        
    except OSError as e:
        print(f"❌ Error al crear el directorio '{output_dir}': {e}. Saliendo.")
        return

    # 3. Ejecutar el Análisis TOC (Lógica de toc_optimize.py)
    
    print("\n--- Ejecutando Análisis de Optimización TOC ---")
    try:
        # Llamada a la función principal de optimización
        # Pasamos los datos cargados y el nombre del archivo para reporte
        toc_optimize.run_toc_analysis(data, csv_path, txt_path, yaml_file)
        print("✅ Análisis TOC completado y archivos CSV/TXT guardados.")
    except Exception as e:
        print(f"❌ Error crítico durante el análisis TOC: {e}")
        # Detenemos si falla el análisis de datos
        return 
    
    # 4. Ejecutar la Graficación (Lógica de toc_graf.py)

    print("\n--- Generando Diagrama de Procesos ---")
    try:
        # Llamada a la función principal de graficación
        toc_graf.run_toc_graph(data, png_path)
        print("✅ Diagrama de Grafo generado y guardado.")
    except Exception as e:
        print(f"❌ Error durante la graficación: {e}")
        # Continuamos, ya que la gráfica es complementaria al informe

    print(f"\n🎉 Tarea finalizada. Revise la carpeta '{output_dir}' para sus resultados.")
    
# ----------------------------------------------------------------------
## EJECUCIÓN DEL PROGRAMA
# ----------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: ./toc_tool.py <archivo_yaml>")
        sys.exit(1)
        
    yaml_file_arg = sys.argv[1]
    
    if not os.path.exists(yaml_file_arg):
        print(f"Error: El archivo '{yaml_file_arg}' no existe.")
        sys.exit(1)
        
    run_toc_tool(yaml_file_arg)