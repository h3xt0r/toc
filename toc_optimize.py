import os
import yaml
import pandas as pd
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

# ----------------------------------------------------------------------
## FUNCIÓN PRINCIPAL: EJECUCIÓN DEL ANÁLISIS TOC (VERSION FINAL)
# ----------------------------------------------------------------------

def run_toc_analysis(file_to_load, output_csv_file, output_txt_file):
    """
    Ejecuta el análisis TOC completo, manejando la asignación de recursos
    con y sin la restricción principal para una asignación más precisa.
    """
    
    # 1. Cargar datos
    datos = load_data_from_file(file_to_load)

    # 2. Identificar la Restricción Global (Cálculo de Consumo Total)
    resource_consumption = {r: 0 for r in datos["recursos"]}
    resource_factors = {}
    
    for prod_name, prod_data in datos["productos"].items():
        for res_name, time_per_unit in prod_data["recursos"].items():
            resource_consumption[res_name] += prod_data["demanda"] * time_per_unit

    max_factor = 0
    global_bottleneck = None
    
    for res_name, capacity in datos["recursos"].items():
        consumed = resource_consumption[res_name]
        factor_carga = consumed / capacity
        resource_factors[res_name] = factor_carga
        
        if factor_carga > max_factor:
            max_factor = factor_carga
            global_bottleneck = res_name
            
    has_bottleneck = max_factor > 1.0
    global_bottleneck = global_bottleneck if has_bottleneck else max(resource_factors, key=resource_factors.get)

    # 3. PREPARACIÓN DEL DATAFRAME y CÁLCULO T/C
    optimization_data = []
    
    for prod_name, prod_data in datos["productos"].items():
        precio = prod_data.get("precio") or prod_data.get("precio_venta", 0)
        T = precio - prod_data["costo_ventas"]
        
        # El tiempo C siempre es respecto al RECURSO PRINCIPAL IDENTIFICADO
        C = prod_data["recursos"].get(global_bottleneck, 0)
        # Si C=0 y T>0, T/C debe ser alto para priorizar (usamos T como proxy)
        T_C = T / C if C > 0 else (T if T > 0 else 0) 
        
        # Solución al bug: Inicializar Produccion_Optima con la demanda si NO hay restricción.
        units_to_produce = prod_data["demanda"] if not has_bottleneck else 0 
        
        optimization_data.append({
            'Producto': prod_name,
            'Throughput_Unitario (T)': T,
            'Tiempo_Restriccion (C)': prod_data["recursos"].get(global_bottleneck, 0) if has_bottleneck else 0,
            'T_por_C (Prioridad)': T_C,
            'Demanda': prod_data["demanda"],
            'Produccion_Optima': units_to_produce, 
            'Throughput_Generado': units_to_produce * T
        })

    df_opt = pd.DataFrame(optimization_data)
    total_throughput = df_opt['Throughput_Generado'].sum() # Inicializar T total

    # 4. ALGORITMO DE EXPLOTACIÓN Y SUBORDINACIÓN (Lógica Mejorada)
    
    if has_bottleneck:
        # 4a. Priorizar por T/C y asignar capacidad del Cuello de Botella
        
        # Ordenar: 1. Por T/C (Prioridad), 2. Productos que no usan la restricción (C=0) al final.
        df_opt['Es_Restriccion'] = df_opt['Tiempo_Restriccion (C)'] > 0
        df_opt = df_opt.sort_values(by=['T_por_C (Prioridad)', 'Es_Restriccion'], 
                                    ascending=[False, True]).reset_index(drop=True)
        
        bottleneck_capacity = datos["recursos"][global_bottleneck]
        remaining_capacity = bottleneck_capacity
        
        # Reasignación inicial basada en el Cuello de Botella
        for index, row in df_opt.iterrows():
            demand = row['Demanda']
            time_per_unit = row['Tiempo_Restriccion (C)']
            
            if time_per_unit > 0:
                capacity_units = int(remaining_capacity // time_per_unit)
                units_to_produce = min(demand, capacity_units)
                
                remaining_capacity -= units_to_produce * time_per_unit
            else:
                # Si C=0, asignar demanda total (la limitación vendrá de recursos secundarios)
                units_to_produce = demand
                
            df_opt.loc[index, 'Produccion_Optima'] = units_to_produce
            
        # 4b. Subordinación: Ajustar la Producción por Recursos Secundarios
        subordinate_resource_capacity = datos["recursos"].copy() 
        total_throughput = 0 # Resetear para calcular el valor final

        for index, row in df_opt.iterrows():
            prod_name = row['Producto']
            current_production = row['Produccion_Optima']
            limiting_factor_units = current_production
            
            # Verificar todos los recursos subordinados que consume este producto
            for res_name, time_per_unit in datos['productos'][prod_name]['recursos'].items():
                if time_per_unit > 0: # Solo si el recurso es relevante
                    capacity = subordinate_resource_capacity[res_name]
                    max_units_by_res = int(capacity // time_per_unit)
                    
                    limiting_factor_units = min(limiting_factor_units, max_units_by_res)
            
            # La producción final es el mínimo entre lo ya asignado y lo que permiten los subordinados.
            final_units_to_produce = limiting_factor_units
            
            # Aplicar el ajuste final
            T_unit = row['Throughput_Unitario (T)']
            df_opt.loc[index, 'Produccion_Optima'] = final_units_to_produce
            df_opt.loc[index, 'Throughput_Generado'] = final_units_to_produce * T_unit
            total_throughput += final_units_to_produce * T_unit
            
            # Actualizar la capacidad restante de TODOS los recursos (incluyendo el cuello de botella)
            for res_name, time_per_unit in datos['productos'][prod_name]['recursos'].items():
                 subordinate_resource_capacity[res_name] -= final_units_to_produce * time_per_unit

        # Capacidad Residual Final del Cuello de Botella
        remaining_capacity = subordinate_resource_capacity[global_bottleneck]


    else:
        # CASO SIN RESTRICCIÓN (Bug Corregido):
        # La Producción Óptima ya está en df_opt (igual a la Demanda) desde el Paso 3.
        most_loaded_resource = global_bottleneck # Ya está definido como el recurso más cargado
        bottleneck_capacity = datos["recursos"][most_loaded_resource]
        
        # Calcular consumo real con la demanda completa
        resource_consumption_actual = df_opt['Demanda'].apply(lambda x: x * datos['productos'][df_opt.loc[df_opt['Produccion_Optima'] == x].iloc[0]['Producto']]['recursos'].get(most_loaded_resource, 0)).sum()
        
        # Calcular capacidad sobrante
        remaining_capacity = bottleneck_capacity - resource_consumption[most_loaded_resource]
        most_loaded_resource_name = most_loaded_resource
        
        # total_throughput ya fue calculado correctamente en el Paso 3.
    
    # 4c. CÁLCULO FINAL DE UTILIDAD NETA (Después de que total_throughput se ha calculado)
    # Sumar todos los gastos operativos (OE)
    total_operating_expense = sum(datos["gastos_operacion"].values())
    # Calcular Utilidad Neta
    net_profit = total_throughput - total_operating_expense

    # 5. EXPORTAR RESULTADOS (CSV y TXT)
    
    df_final = df_opt[['Producto', 'T_por_C (Prioridad)', 'Demanda', 'Produccion_Optima', 'Throughput_Generado']]
    
    # Exportar CSV
    df_final.to_csv(output_csv_file, index=False, float_format='%.2f')

    # Crear archivo de texto con el resumen
    with open(output_txt_file, "w") as f:
        f.write(f"*** RESULTADOS DEL MODELO DE OPTIMIZACIÓN TOC ***\n")
        f.write(f"Datos de Entrada: {file_to_load}\n")
        f.write(f"---------------------------------------------------\n")
        
        if has_bottleneck:
            f.write(f"Restricción Global (Cuello de Botella): {global_bottleneck}\n")
            f.write(f"Capacidad de Restricción (unidades): {datos['recursos'][global_bottleneck]}\n") 
            f.write(f"Factor de Carga Original: {max_factor:.2f}\n")
            f.write(f"Capacidad de Restricción Residual: {remaining_capacity:.2f} minutos\n\n")
            f.write("Instrucción de Subordinación: Todos los recursos NO restringidos deben limitar su producción al mix óptimo de la tabla para evitar acumulación de inventario (Drum-Buffer-Rope). La producción ya ha sido ajustada por restricciones secundarias.\n\n")
        else:
            f.write(f"¡NO HAY RESTRICCIONES DE CAPACIDAD! (Uso Máximo: {max_factor:.2f})\n")
            f.write(f"El recurso más cargado ({most_loaded_resource_name}) tiene una capacidad sobrante de: {remaining_capacity:.2f} minutos.\n\n")
            f.write("Instrucción: Producir la Demanda Completa. Enfocarse en reducir Costos de Operación o aumentar Demanda.\n\n")
        # NUEVA SECCIÓN DE FINANZAS TOC
        f.write("--- ANÁLISIS FINANCIERO TOC ---\n")
        f.write(f"Throughput Total Máximo Alcanzado (T): {total_throughput:.2f}\n")
        f.write(f"Gastos Operativos Totales (OE): {total_operating_expense:.2f}\n")
        f.write(f"Utilidad Neta (Net Profit): {net_profit:.2f}\n")
        f.write("----------------------------------------------\n\n")
        f.write(f"Throughput Total Máximo Alcanzado: {total_throughput:.2f}\n\n")
        f.write("Mezcla de Producción Óptima:\n")
        f.write(df_final.to_string(index=False, float_format='%.2f') + "\n")