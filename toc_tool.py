import os
import sys
# Asumimos que toc_optimize.py y toc_graf.py están en el mismo directorio
import toc_optimize 
import toc_graf 

# ----------------------------------------------------------------------
## FUNCIÓN PRINCIPAL DE LA HERRAMIENTA CENTRAL
# ----------------------------------------------------------------------

def run_toc_tool():
    """
    Orquesta el análisis TOC, la graficación, y organiza los archivos de salida.
    """
    print("\n*** Herramienta de Análisis TOC (Teoría de Restricciones) ***")
    
    # 1. Solicitar datos de entrada
    
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

    # Solicitar nombre de la empresa para el directorio
    company_name = input("▶️ Ingrese el nombre del Análisis/Empresa (ej. 'TextilesAlfa'): ").strip()
    if not company_name:
        print("❌ Nombre de análisis inválido. Saliendo.")
        return

    # Solicitar nombre del archivo de datos YAML
    yaml_file = input("▶️ Ingrese el nombre del archivo YAML (ej. 'procesos.yml'): ").strip()
    if not yaml_file:
        print("❌ Nombre de archivo inválido. Saliendo.")
        return
    
    # 2. Crear el Directorio de Salida

    output_dir = company_name.replace(' ', '_') # Reemplaza espacios por guiones bajos
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"\n📁 Directorio '{output_dir}' creado exitosamente.")
        else:
            print(f"\n⚠️ Directorio '{output_dir}' ya existe. Los archivos serán sobrescritos.")
            
        # Definir rutas de salida
        csv_path = os.path.join(output_dir, f"{output_dir}_resultados_toc.csv")
        txt_path = os.path.join(output_dir, f"{output_dir}_resumen.txt")
        png_path = os.path.join(output_dir, f"{output_dir}_diagrama_toc.png")
        
    except OSError as e:
        print(f"❌ Error al crear el directorio '{output_dir}': {e}. Saliendo.")
        return

    # 3. Ejecutar el Análisis TOC (Lógica de toc_optimize.py)
    
    # La función run_toc_analysis de toc_optimize debe devolver el df_final y total_throughput
    # Para la orquestación, modificamos la firma de la función en toc_optimize.py
    # para que acepte las rutas de salida.
    print("\n--- Ejecutando Análisis de Optimización TOC ---")
    try:
        # Llamada a la función principal de optimización
        toc_optimize.run_toc_analysis(yaml_file, csv_path, txt_path)
        print("✅ Análisis TOC completado y archivos CSV/TXT guardados.")
    except Exception as e:
        print(f"❌ Error crítico durante el análisis TOC: {e}")
        # Detenemos si falla el análisis de datos
        return 
    
    # 4. Ejecutar la Graficación (Lógica de toc_graf.py)

    print("\n--- Generando Diagrama de Procesos ---")
    try:
        # Llamada a la función principal de graficación
        # Hacemos que la función en toc_graf.py acepte la ruta de salida.
        toc_graf.run_toc_graph(yaml_file, png_path)
        print("✅ Diagrama de Grafo generado y guardado.")
    except Exception as e:
        print(f"❌ Error durante la graficación: {e}")
        # Continuamos, ya que la gráfica es complementaria al informe

    print(f"\n🎉 Tarea finalizada. Revise la carpeta '{output_dir}' para sus resultados.")
    
# ----------------------------------------------------------------------
## EJECUCIÓN DEL PROGRAMA
# ----------------------------------------------------------------------

if __name__ == "__main__":
    run_toc_tool()