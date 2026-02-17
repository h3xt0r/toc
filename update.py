#!/usr/bin/python3 -O
# -*- coding: utf-8 -*-
from os import system

# Definimos algunas funciones para dar mantenimiento al sistema con 'apt'

### Actualizacion (Update + Full-Upgrade)
def update():
    acciones=["apt update", "apt full-upgrade -y"] # 'apt update' y 'apt full-upgrade' para actualizar todo. El '-y' confirma la instalación.
    for a in acciones:
        print("\n###  Ejecutando: "+a+"  ###\n\n")
        system(a)
    print("\n El sistema esta actualizado, ¡Chido! ;-)\n\n")
    return

### Limpieza (Clean + Autoremove)
def clean():
    print("\nLimpiando archivos de configuracion viejos y dependencias no usadas\n")
    # 'autoremove' elimina paquetes que se instalaron como dependencias y ya no son necesarios.
    # 'autoclean' y 'clean' limpian el cache de paquetes descargados.
    limpieza=["apt autoremove --purge -y", 
              "apt autoclean", 
              "apt clean",
              "appstreamcli refresh-cache --force", # Mantiene Discover con iconos y descripciones frescas
              "pkcon refresh force"  # Refresca el motor de Discover (PackageKit)] 
             ]                   
    for l in limpieza:
        print("\nEjecutando:",l,"\n")
        system(l)
        
    # Limpieza de caché de usuario para evitar los "Binding loops" que vimos
    system("rm -rf ~/.cache/discover")
    print("\nSistema y Discover limpio de archivos viejos. ¡Órale! ;-)\n\n\n")
    return

# Todas las funciones juntas: Actualizar y Limpiar
def ServicioCompleto():
    print("\n\n### Iniciando Servicio Completo: Actualización y Limpieza ###\n")
    update()
    clean()
    print("\n### Fin del Servicio Completo. ¡Todo chido! ###\n")
    return


### Creamos un menu con las opciones.
ans="0" 
while ans !="4": # Solo '4' sale del programa
    print("\n\n\n###  Menu de Administración de Paquetes (APT) ###\n")
    print("1. **Actualizar el Sistema**: 'apt update' y 'apt full-upgrade'")
    print("2. **Limpiar el Sistema**: 'apt autoremove --purge', 'apt autoclean' y 'apt clean'")
    print("3. **Servicio Completo**: Actualizar y Limpiar (1 y 2)")
    print("4. **Salir**")
    ans=input("\nSu opcion (1, 2, 3, 4): ")
    
    if ans == "1":
        print("\nActualizando el Sistema\n")
        update()
    elif ans == "2":
        print("\nLimpiando el Sistema\n")
        clean()
    elif ans == "3":
        ServicioCompleto()
    elif ans == "4":
        print("\n\nI'll be BACK. ¡Nos vemos, *valedor*!\n\n")
        break
    else: # cualquier otro valor
        print("\n *** ERROR: Opción no reconocida: %s *** \n" % ans)
        print("type:", type(ans), ans)

print("\n\nI'll be BACK. ¡Ya sabes, *carnal*!\n\n")
