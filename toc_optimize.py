import os
import yaml
import pandas as pd
from yaml.loader import SafeLoader

# ----------------------------------------------------------------------
## 1. FUNCIÓN DE CARGA DE DATOS (PARSER YAML)
# ----------------------------------------------------------------------

def load_data_from_file(file_path):
    """
    Carga los datos de recursos y productos desde un archivo YAML.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: El archivo no fue encontrado en la ruta especificada: {file_path}")

    print(f"⏳ Cargando datos desde {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            # Usar SafeLoader para seguridad al cargar el contenido YAML
            datos = yaml.load(file, Loader=SafeLoader)
        
        except Exception as e:
            print(f"❌ Error al parsear el archivo {file_path}. Revise el formato YAML.")
            raise e
            
    # Validación de estructura esencial
    if "recursos" not in datos or "productos" not in datos:
        raise ValueError("La estructura del archivo es incorrecta. Debe contener las claves 'recursos' y 'productos' a nivel superior.")
        
    print("✅ Estructura de datos validada.")
    return datos

# ----------------------------------------------------------------------
## 2. BLOQUE PRINCIPAL DE ANÁLISIS Y OPTIMIZACIÓN TOC
# ----------------------------------------------------------------------

def run_toc_analysis(file_to_load):
    """Ejecuta el análisis TOC completo: Carga, Identificación, Explotación y Exportación."""
    
    # Intenta cargar los datos, sale si hay un error crítico
    try:
        datos = load_data_from_file(file_to_load)
    except Exception as e:
        print(f"Deteniendo la ejecución del análisis. Razón: {e}")
        return

    # Inicialización de métricas y identificación de la restricción
    resource_consumption = {r: 0 for r in datos["recursos"]}
    resource_factors = {}
    max_factor = 0

    # Calcular consumo total para identificar el cuello de botella
    for prod_name, prod_data in datos["productos"].items():
        # Consistencia de nombres: precio o precio_venta
        precio = prod_data.get("precio") or prod_data.get("precio_venta", 0) 
        
        for res_name, time_per_unit in prod_data["recursos"].items():
            consumed_time = prod_data["demanda"] * time_per_unit
            resource_consumption[res_name] += consumed_time

    # Determinar el recurso con la mayor Carga (Factor > 1.0)
    for res_name, capacity in datos["recursos"].items():
        consumed = resource_consumption[res_name]
        factor_carga = consumed / capacity
        resource_factors[res_name] = factor_carga
        
        if factor_carga > max_factor:
            max_factor = factor_carga
            global_bottleneck = res_name
            
    # Determinar si hay restricción global
    has_bottleneck = max_factor > 1.0
    global_bottleneck = global_bottleneck if has_bottleneck else "N/A"
    
    # ----------------------------------------------------------------------
    # 3. PREPARACIÓN DEL DATAFRAME y ASIGNACIÓN INICIAL
    # ----------------------------------------------------------------------

    optimization_data = []
    total_throughput = 0

    for prod_name, prod_data in datos["productos"].items():
        precio = prod_data.get("precio") or prod_data.get("precio_venta", 0)
        T = precio - prod_data["costo_ventas"]
        
        # Tiempo en la restricción (C)
        C = prod_data["recursos"].get(global_bottleneck, 0) if has_bottleneck else 1 
        T_C = T / C if C > 0 else 0 
        
        # Asignación de producción inicial (Si no hay restricción, es igual a la demanda)
        units_to_produce = prod_data["demanda"] if not has_bottleneck else 0
        T_generado = units_to_produce * T
        total_throughput += T_generado

        optimization_data.append({
            'Producto': prod_name,
            'Throughput_Unitario (T)': T,
            'Tiempo_Restriccion (C)': C,
            'T_por_C (Prioridad)': T_C,
            'Demanda': prod_data["demanda"],
            'Produccion_Optima': units_to_produce,
            'Throughput_Generado': T_generado
        })

    df_opt = pd.DataFrame(optimization_data)

    # ----------------------------------------------------------------------
    # 4. ALGORITMO DE EXPLOTACIÓN (SOLO SI HAY RESTRICCIÓN)
    # ----------------------------------------------------------------------
    
    if has_bottleneck:
        print(f"\n⚠️ Restricción Crítica Identificada: {global_bottleneck} (Factor de Carga: {max_factor:.2f})")
        bottleneck_capacity = datos["recursos"][global_bottleneck]
        remaining_capacity = bottleneck_capacity
        total_throughput = 0 # Resetear para recalcular con la asignación TOC
        
        # 4a. Reordenar y Asignar por T/C (Explotación)
        df_opt = df_opt.sort_values(by='T_por_C (Prioridad)', ascending=False).reset_index(drop=True)

        print(f"⏳ Asignando producción óptima mediante T/C. Capacidad: {remaining_capacity} minutos...")
        
        for index, row in df_opt.iterrows():
            demand = row['Demanda']
            time_per_unit = row['Tiempo_Restriccion (C)']
            T_unit = row['Throughput_Unitario (T)']
            
            # Unidades que la capacidad permite
            capacity_units = int(remaining_capacity // time_per_unit) if time_per_unit > 0 else demand
            # Producir el mínimo entre lo permitido y la demanda
            units_to_produce = min(demand, capacity_units)

            # Actualizar el DataFrame y las métricas
            df_opt.loc[index, 'Produccion_Optima'] = units_to_produce
            df_opt.loc[index, 'Throughput_Generado'] = units_to_produce * T_unit
            
            # Actualizar capacidad restante
            time_used = units_to_produce * time_per_unit
            remaining_capacity -= time_used
            total_throughput += df_opt.loc[index, 'Throughput_Generado']
            
            print(f"-> Producto {row['Producto']}: Producir {units_to_produce} (Usado: {time_used} min)")
            if remaining_capacity <= 0:
                remaining_capacity = 0
                break
                
        print(f"\n✨ Throughput Total Máximo (Optimizado): {total_throughput:.2f}")
    
    else:
        # Caso sin restricción: remaining_capacity del recurso más cargado
        most_loaded_resource = max(resource_factors, key=resource_factors.get)
        bottleneck_capacity = datos["recursos"][most_loaded_resource]
        remaining_capacity = bottleneck_capacity - resource_consumption[most_loaded_resource]
        
        print("\n✅ Todos los recursos tienen capacidad suficiente.")
        print(f"El Throughput máximo es el potencial de ventas (T: {total_throughput:.2f})")

    # ----------------------------------------------------------------------
    # 5. EXPORTAR RESULTADOS (Común para ambos casos)
    # ----------------------------------------------------------------------

    df_final = df_opt[['Producto', 'T_por_C (Prioridad)', 'Demanda', 'Produccion_Optima', 'Throughput_Generado']]
    output_csv_file = "resultados_toc_optimizacion.csv"
    output_txt_file = "resumen.txt"

    # Exportar CSV
    df_final.to_csv(output_csv_file, index=False, float_format='%.2f')

    # Crear archivo de texto con el resumen
    with open(output_txt_file, "w") as f:
        f.write(f"*** RESULTADOS DEL MODELO DE OPTIMIZACIÓN TOC ***\n")
        f.write(f"Datos de Entrada: {file_to_load}\n")
        f.write(f"---------------------------------------------------\n")
        
        if has_bottleneck:
            f.write(f"Restricción Global (Cuello de Botella): {global_bottleneck}\n")
            f.write(f"Capacidad de Restricción (min/semana): {bottleneck_capacity}\n")
            f.write(f"Factor de Carga Original: {max_factor:.2f}\n")
            f.write(f"Capacidad de Restricción Residual: {remaining_capacity:.2f} minutos\n\n")
            f.write("Instrucción de Subordinación: Todos los recursos NO restringidos deben limitar su producción al mix óptimo de la tabla para evitar acumulación de inventario (Drum-Buffer-Rope).\n\n")
        else:
            f.write(f"¡NO HAY RESTRICCIONES DE CAPACIDAD! (Uso Máximo: {max_factor:.2f})\n")
            f.write(f"El recurso más cargado ({most_loaded_resource}) tiene una capacidad sobrante de: {remaining_capacity:.2f} minutos.\n\n")
            f.write("Instrucción: Producir la Demanda Completa. Enfocarse en reducir Costos de Operación o aumentar Demanda.\n\n")

        f.write(f"Throughput Total Máximo Alcanzado: {total_throughput:.2f}\n\n")
        f.write("Mezcla de Producción Óptima:\n")
        f.write(df_final.to_string(index=False, float_format='%.2f') + "\n")

    print(f"\n💾 Análisis TOC completado. Archivos generados:\n - {output_csv_file}\n - {output_txt_file}")


# ----------------------------------------------------------------------
## EJECUCIÓN DEL PROGRAMA
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Nombre del archivo YAML que debe estar en el mismo directorio
    YAML_FILE = 'procesos.yml' 
    run_toc_analysis(YAML_FILE)