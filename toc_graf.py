import networkx as nx
import matplotlib.pyplot as plt
import os

# ----------------------------------------------------------------------
## FUNCIÓN HELPER: CARGA DE DATOS YAML - MOVIDA A toc_read.py
# ----------------------------------------------------------------------
## FUNCIÓN PRINCIPAL: EJECUCIÓN DE LA GRÁFICA
# ----------------------------------------------------------------------

def run_toc_graph(datos, output_filename):
    """Genera y guarda el diagrama de procesos TOC usando networkx y bipartite_layout."""
    
    # 0. Datos ya cargados
    # datos = load_data_from_file(yaml_file)

    # 1. Inicializar el grafo
    G = nx.DiGraph()
    resource_consumption = {r: 0 for r in datos["recursos"]}
    product_nodes = set()
    resource_nodes = set()

    # 2. Construcción del Grafo y cálculo de consumo
    for prod_name, prod_data in datos["productos"].items():
        T = prod_data.get("precio", 0) - prod_data["costo_ventas"]
        G.add_node(prod_name, node_type='Product', T=T)
        product_nodes.add(prod_name)

        for res_name, time_per_unit in prod_data["recursos"].items():
            consumed_time = prod_data["demanda"] * time_per_unit
            resource_consumption[res_name] += consumed_time
            resource_nodes.add(res_name)
            G.add_edge(prod_name, res_name, weight=consumed_time)

    # 3. Determinar el tamaño y color de los Nodos de Recurso
    resource_sizes = {}
    node_colors = {}
    base_size = 2500 
    max_factor_global = 0

    for res_name, capacity in datos["recursos"].items():
        consumed = resource_consumption[res_name]
        factor_carga = consumed / capacity
        
        max_factor_global = max(max_factor_global, factor_carga)
        
        node_size = base_size * factor_carga 
        resource_sizes[res_name] = max(base_size / 2, node_size)
        
        color = 'red' if factor_carga > 1.0 else 'skyblue'
        node_colors[res_name] = color
        
        G.add_node(res_name, node_type='Resource', capacity=capacity, 
                   consumed=consumed, factor_carga=factor_carga)

    # 4. Preparación para la Visualización
    node_list = G.nodes()
    sizes = [resource_sizes.get(n, base_size * 0.5) for n in node_list] 
    colors = [node_colors.get(n, 'lightgreen') if G.nodes[n].get('node_type') == 'Resource' else 'yellow' for n in node_list]

    # Usar el Bipartite Layout para separación clara
    pos = nx.bipartite_layout(G, product_nodes) 

    plt.figure(figsize=(10, 6))

    nx.draw(G, pos, with_labels=False, node_size=sizes, node_color=colors,
            font_size=10, font_weight='bold', edge_color='gray', arrows=True)

    # Añadir etiquetas con información clave
    product_labels = {n: n for n in product_nodes}
    resource_labels = {n: f"{n}\nCarga: {G.nodes[n]['factor_carga']:.2f}" 
                      for n in resource_nodes}

    nx.draw_networkx_labels(G, pos, labels=product_labels, font_size=12, font_color='black')
    nx.draw_networkx_labels(G, pos, labels=resource_labels, font_size=9, font_color='black', verticalalignment='center')


    plt.title(f"Diagrama de Procesos TOC - Restricción (Carga Máxima: {max_factor_global:.2f})", fontsize=14)
    plt.axis('off') 
    
    # 5. Guardar la gráfica en un archivo
    plt.savefig(output_filename, format="png", dpi=300)