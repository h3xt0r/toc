Hola Dra. buenas tardes, estoy pensando en una herramienta para graficar procesos de negocios, pero con un enfoque en la teoría de restricciones del Dr. Eliyahu M. Goldratt, mi idea inicial es empezar con una especificación de los procesos de la empresa, tal vez en lenguaje YAML o JSON por ejemplo:

```

recursos:{
    maquina_cortar:2400,
    maquina_coser:2400
}

productos:{
    camisa_hombre:{
        costo_ventas:50,
        recursos:{
            maquina_cortar:10,
            maquina_coser:10
                }
        precio:100,
        demanda:120
        },

    camisa_mujer:{
    costo_ventas:45,
    recursos:{
        maquina_cortar:2,
        maquina_coser:15,
        }
    precio_venta:105,
    demanda:120
    }
}

```

donde los recursos son variables y corresponden a las máquinas o empleados de la empresa, el número despues de cada recursos es el número de minutos disponibles por semana para ese recurso.

Los productos son las ventas que realiza una empresa, pueden ser productos o servicios, el costo de ventas, es el dinero en unidades monetarias que la empresa invierte en insumos directos para realizar la venta, el diccionario de recursos hace referencia a los recursos definidos inicialmente, indicando el tiempo en minutos que se consume en la fabricación de cada producto.

El precio de venta es por producto, y es la venta bruta, y la demanda es el número de productos que se vendieron o se espera vender.

La idea es usar esta información para hacer un diagrama de procesos, usando networkx y python, donde los elementos de recursos, costo_ventas, precio_venta y demanda son nodos.

En este caso tendríamos dos procesos, uno por cada producto, la idea es que la gráfica muestre de forma visual el recurso que se está saturando, sumando el tiempo que se utiliza para la fabricación de cada producto por recurso,

Por ejemplo, analicemos el recurso de la máquina de cortar, cada camisa de hombre ocupa 10 minutos, por 120 de la demanda me de 1200 minutos, mas 2 minutos por cada camisa de mujer, es decir 2 por 120, me da 240 minutos, el numero total de minutos es de 1200 + 240, 1440 minutos, este número se debe traducir en el tamaño del nodo usando networkx

Ahora para la máquina de coser, para la camisa de hombre de nuevo son 10 minutos por producto, 10 * 120 nos da 1200 minutos para fabricar las 120 camisas de hombre, más los tiempo de la camisa de mujer, 15 * 120 nos da 1800, cuando sumamos los tiempos 1200 + 1800 nos da un total de 3000 minutos, que excede la capacidad de la máquina de coser, por lo que el nodo debe ser más grande que el nodo de la máquina de cortar.

Mi idea es graficar los dos procesos, usando los recursos de forma compartida, y el tamaño de los nodos es dictado por la suma de los tiempos que cada producto vendido usa de los recursos de la empresa.

La idea es hacer un programa en python  que lea este archivo de entrada, con extensión yml o json y lo traduzca en una gráfica de proceso usando networkx o alguna otra libreria de graficación, los elementos que son nodos pero no llevan tiempo, serán graficados siempre con un mismo tamaño, tales como: costo_ventas, precio_venta, demanda, siendo los tres últimos, producto, precio venta y demanda un solo nodo al final del proceso.
