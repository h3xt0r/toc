import networkx as nx
import matplotlib.pyplot as plt
import os
import yaml
from yaml.loader import SafeLoader

# ----------------------------------------------------------------------
## FUNCIÓN DE CARGA (COPIA DE toc_optimize.py)
# ----------------------------------------------------------------------

def load_data_from_file(file_path):
    """
    Carga los datos de recursos y productos desde un archivo YAML.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: El archivo no fue encontrado en la ruta especificada: {file_path}")

    # print(f"⏳ Cargando datos desde {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            # Usar SafeLoader para seguridad al cargar el contenido YAML
            datos = yaml.load(file, Loader=SafeLoader)
        
        except Exception as e:
            raise e
            
    # Validación de estructura esencial
    if "recursos" not in datos or "productos" not in datos:
        raise ValueError("La estructura del archivo es incorrecta.")
        
    return datos

# ----------------------------------------------------------------------
## EJECUCIÓN DEL GRÁFICO
# ----------------------------------------------------------------------

# 0. Cargar los datos desde el archivo YAML
YAML_FILE = 'procesos.yml' 
try:
    datos = load_data_from_file(YAML_FILE)
    print(f"✅ Datos cargados desde {YAML_FILE} para la graficación.")
except Exception as e:
    print(f"❌ No se pudo cargar la data. Saliendo. Razón: {e}")
    exit()

# 1. Inicializar el grafo
G = nx.DiGraph()
resource_consumption = {r: 0 for r in datos["recursos"]}
product_nodes = set()
resource_nodes = set()


# 2. Calcular el Consumo Total y Throughput (Tasa de Generación de Ingreso)
for prod_name, prod_data in datos["productos"].items():
    T = prod_data.get("precio", 0) - prod_data["costo_ventas"]
    G.add_node(prod_name, node_type='Product', T=T)
    product_nodes.add(prod_name)

    for res_name, time_per_unit in prod_data["recursos"].items():
        consumed_time = prod_data["demanda"] * time_per_unit
        resource_consumption[res_name] += consumed_time
        resource_nodes.add(res_name)
        
        # Arista: Producto (Origen) -> Recurso (Destino)
        G.add_edge(prod_name, res_name, weight=consumed_time)

# 3. Determinar el tamaño de los Nodos de Recurso (la métrica de la Restricción)
resource_sizes = {}
node_colors = {}
base_size = 2500 # Aumentar el tamaño base para mayor visibilidad

for res_name, capacity in datos["recursos"].items():
    consumed = resource_consumption[res_name]
    factor_carga = consumed / capacity
    
    # El tamaño del nodo será proporcional al Factor de Carga
    node_size = base_size * factor_carga 
    resource_sizes[res_name] = max(base_size / 2, node_size)
    
    # Asignar color: Rojo intenso si es restricción
    color = 'red' if factor_carga > 1.0 else 'skyblue'
    node_colors[res_name] = color
    
    G.add_node(res_name, node_type='Resource', capacity=capacity, 
               consumed=consumed, factor_carga=factor_carga)

# 4. Preparación para la Visualización
node_list = G.nodes()
sizes = [resource_sizes.get(n, base_size * 0.5) for n in node_list] # Nodos de producto más pequeños
colors = [node_colors.get(n, 'lightgreen') if G.nodes[n].get('node_type') == 'Resource' else 'yellow' for n in node_list]

# Definir el layout Bipartito (Clave para una mejor visualización)
# Colocamos los Productos a la izquierda (set 0) y los Recursos a la derecha (set 1)
# Esto simula el flujo de material -> recurso
pos = nx.bipartite_layout(G, product_nodes) 

plt.figure(figsize=(10, 6))

# Dibujar el grafo
nx.draw(G, pos, with_labels=False, node_size=sizes, node_color=colors,
        font_size=10, font_weight='bold', edge_color='gray', arrows=True)

# Añadir etiquetas de Producto (más grandes) y Recurso (con carga)
product_labels = {n: n for n in product_nodes}
resource_labels = {n: f"{n}\nCarga: {G.nodes[n]['factor_carga']:.2f}" 
                  for n in resource_nodes}

nx.draw_networkx_labels(G, pos, labels=product_labels, font_size=12, font_color='black')
nx.draw_networkx_labels(G, pos, labels=resource_labels, font_size=9, font_color='black', verticalalignment='center')


plt.title(f"Diagrama de Procesos (TOC) - Identificación de Restricciones", fontsize=14)
plt.axis('off') # Ocultar ejes
# 5. Guardar la gráfica en un archivo
output_filename = "diagrama_toc_restriccion_bipartito.png"
plt.savefig(output_filename, format="png", dpi=300) 

print(f"✅ Gráfico guardado exitosamente como: {output_filename}")