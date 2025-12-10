import random
import matplotlib
matplotlib.use('Agg') # Usar backend no interactivo para generar archivos
import matplotlib.pyplot as plt

class Jugador:
    """
    Representa a un jugador en la simulación del juego de dados.
    Cada jugador tiene un dado con un número específico de caras y un
    inventario (recipiente) para las piezas procesadas.
    """

    def __init__(self, nombre: str, caras_dado: int = 6):
        """
        Inicializa un nuevo jugador.

        Args:
            nombre (str): El nombre del jugador (estación de trabajo).
            caras_dado (int, optional): Número de caras del dado. Por defecto es 6.
        """
        if caras_dado < 1:
            raise ValueError("El número de caras del dado no puede ser menor que 1.")
        self.nombre = nombre
        self.caras_dado = caras_dado
        self.inventario = 0
        self.historial_lanzamientos = []
        self.ultimo_lanzamiento = 0

    def lanzar_dado(self) -> int:
        """
        Simula el lanzamiento del dado, guarda el resultado en el historial
        y lo devuelve.

        Returns:
            int: Un número aleatorio entre 1 y el número de caras del dado.
        """
        resultado = random.randint(1, self.caras_dado)
        self.historial_lanzamientos.append(resultado)
        self.ultimo_lanzamiento = resultado
        return resultado

    def __str__(self) -> str:
        """
        Representación en cadena de texto del estado actual del jugador.
        """
        return (f"Estación: {self.nombre} (Capacidad: 1-{self.caras_dado}, "
                f"dado:{self.ultimo_lanzamiento}, Inventario actual: {self.inventario})")

class LineaDeProduccion:
    """
    Gestiona la simulación de la línea de producción completa,
    orquestando a los jugadores y el flujo de inventario.
    """

    def __init__(self, jugadores: list[Jugador]):
        """
        Inicializa la línea de producción con una lista ordenada de jugadores.

        Args:
            jugadores (list[Jugador]): Una lista de objetos Jugador en el orden
                                       en que operan en la línea.
        """
        self.estaciones = jugadores
        self.producto_terminado = 0
        # Usamos un número muy grande para simular un suministro infinito de materia prima
        self.materia_prima = float('inf')
        self.logs = []

    def _log(self, mensaje):
        """Agrega un mensaje al buffer de logs."""
        self.logs.append(mensaje)

    def guardar_reporte(self, nombre_archivo: str):
        """Guarda los logs acumulados en un archivo."""
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.logs))
        print(f"Reporte guardado en: {nombre_archivo}")

    def simular_turno(self):
        """
        Simula un único turno (ej. una hora) para toda la línea de producción.
        """
        inventario_anterior = self.materia_prima

        for i, estacion in enumerate(self.estaciones):
            capacidad_turno = estacion.lanzar_dado()
            
            # La cantidad que se puede procesar es el mínimo entre la capacidad
            # de la estación y el inventario disponible de la estación anterior.
            unidades_a_procesar = min(capacidad_turno, inventario_anterior)

            # La estación actual procesa las unidades, aumentando su propio inventario.
            estacion.inventario += unidades_a_procesar
            
            # Las unidades procesadas se descuentan del inventario anterior.
            if i > 0:
                self.estaciones[i-1].inventario -= unidades_a_procesar
            
            # El inventario disponible para la siguiente estación es el de la actual.
            inventario_anterior = estacion.inventario

        # Al final del turno, el inventario de la última estación pasa a ser producto terminado.
        self.producto_terminado += self.estaciones[-1].inventario
        self.estaciones[-1].inventario = 0

    def simular_jornada(self, numero_de_turnos: int):
        """
        Simula una jornada laboral completa ejecutando varios turnos.

        Args:
            numero_de_turnos (int): El número de turnos que componen la jornada.
        """
        self._log("=== INICIO DE LA JORNADA LABORAL ===")
        for turno in range(numero_de_turnos):
            self.simular_turno()
            self._log(f"--- Fin del Turno {turno + 1} ---")
            self._log(f"Producto Terminado Acumulado: {self.producto_terminado}")
            for estacion in self.estaciones:
                self._log(f"  - {estacion}")
            self._log("-" * 25)
        self._log("=== FIN DE LA JORNADA LABORAL ===")

    def generar_graficas(self, nombre_base: str):
        """Genera las gráficas solicitadas en PDF."""
        # 1. Gráfica de frecuencias (Líneas)
        plt.figure(figsize=(10, 6))
        for estacion in self.estaciones:
            conteo = {}
            for val in estacion.historial_lanzamientos:
                conteo[val] = conteo.get(val, 0) + 1
            
            x_vals = sorted(conteo.keys())
            y_vals = [conteo[k] for k in x_vals]
            plt.plot(x_vals, y_vals, marker='o', label=estacion.nombre)
            
        plt.title(f"Frecuencia de Lanzamientos - {nombre_base}")
        plt.xlabel("Valor del Dado")
        plt.ylabel("Frecuencia")
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{nombre_base}_frecuencias.pdf")
        plt.close()
        self._log(f"Gráfica guardada: {nombre_base}_frecuencias.pdf")

        # 2. Gráfica de inventario (Barras)
        plt.figure(figsize=(10, 6))
        nombres = [e.nombre for e in self.estaciones]
        inventarios = [e.inventario for e in self.estaciones]
        
        plt.bar(nombres, inventarios, color='skyblue')
        plt.title(f"Inventario Final por Estación - {nombre_base}")
        plt.xlabel("Estación")
        plt.ylabel("Inventario (Unidades)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"{nombre_base}_inventario.pdf")
        plt.close()
        self._log(f"Gráfica guardada: {nombre_base}_inventario.pdf")


    def mostrar_resultados_finales(self, nombre_simulacion="simulacion"):
        """
        Muestra un resumen con los resultados al final de la simulación y genera gráficas.
        """
        self.generar_graficas(nombre_simulacion)
        self._log("\n=== RESULTADOS FINALES ===")
        self._log(f"Total de Producto Terminado: {self.producto_terminado}")
        
        self._log("\nInventario final en cada estación (WIP - Work In Process):")
        wip_total = 0
        for estacion in self.estaciones:
            self._log(f"  - {estacion.nombre}: {estacion.inventario}")
            wip_total += estacion.inventario
        self._log(f"Total WIP: {wip_total}")

        self._log("\nCapacidad teórica vs. Real (lanzamientos de dados):")
        for estacion in self.estaciones:
            promedio = sum(estacion.historial_lanzamientos) / len(estacion.historial_lanzamientos)
            self._log(f"  - {estacion.nombre}: Capacidad promedio por turno: {promedio:.2f}")


if __name__ == '__main__':
    # --- Configuración de la Simulación ---
    
    # Escenario 1: Línea "balanceada" donde todos tienen la misma capacidad promedio.
    # Según la intuición, el rendimiento debería ser el promedio de los dados (3.5).
    print(">>> Simulación 1: Línea Balanceada (5 estaciones, dado de 6 caras)")
    
    linea_balanceada = LineaDeProduccion(jugadores=[
        Jugador(nombre="Operario A", caras_dado=6),
        Jugador(nombre="Operario B", caras_dado=6),
        Jugador(nombre="Operario C", caras_dado=6),
        Jugador(nombre="Operario D", caras_dado=6),
        Jugador(nombre="Operario E", caras_dado=6),
    ])
    
    linea_balanceada.simular_jornada(numero_de_turnos=20)
    linea_balanceada.mostrar_resultados_finales("simulacion_balanceada")
    linea_balanceada.guardar_reporte("reporte_balanceada.txt")

    print("\n" + "="*40 + "\n")

    # Escenario 2: Línea con capacidades diferentes y un cuello de botella claro.
    print(">>> Simulación 2: Línea con Cuello de Botella (Operario C es más lento)")

    linea_con_cuello_botella = LineaDeProduccion(jugadores=[
        Jugador(nombre="Operario A", caras_dado=8),
        Jugador(nombre="Operario B", caras_dado=8),
        Jugador(nombre="Operario C (Lento)", caras_dado=4), # Cuello de botella
        Jugador(nombre="Operario D", caras_dado=8),
        Jugador(nombre="Operario E", caras_dado=8),
    ])

    linea_con_cuello_botella.simular_jornada(numero_de_turnos=20)
    linea_con_cuello_botella.mostrar_resultados_finales("simulacion_cuello_botella")
    linea_con_cuello_botella.guardar_reporte("reporte_cuello_botella.txt")
