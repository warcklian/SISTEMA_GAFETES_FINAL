#!/usr/bin/env python3
"""
Diagnóstico de Hardware - Identificar problemas de estabilidad
"""

import os
import sys
import psutil
import time
from pathlib import Path

def diagnostico_memoria():
    """Diagnostica el uso de memoria"""
    print(" DIAGNÓSTICO DE MEMORIA")
    print("=" * 40)
    
    # Memoria total
    memoria = psutil.virtual_memory()
    print(f" Memoria total: {memoria.total / (1024**3):.1f} GB")
    print(f" Memoria disponible: {memoria.available / (1024**3):.1f} GB")
    print(f" Memoria usada: {memoria.percent:.1f}%")
    
    # Swap
    swap = psutil.swap_memory()
    print(f" Swap total: {swap.total / (1024**3):.1f} GB")
    print(f" Swap usado: {swap.percent:.1f}%")
    
    # Recomendaciones
    if memoria.percent > 80:
        print("️ ADVERTENCIA: Uso de memoria alto")
    if swap.percent > 50:
        print("️ ADVERTENCIA: Swap en uso - puede causar lentitud")
    
    return memoria.percent < 80

def diagnostico_cpu():
    """Diagnostica el uso de CPU"""
    print("\n DIAGNÓSTICO DE CPU")
    print("=" * 40)
    
    # Información de CPU
    print(f"️ CPUs físicos: {psutil.cpu_count(logical=False)}")
    print(f"️ CPUs lógicos: {psutil.cpu_count(logical=True)}")
    
    # Frecuencia de CPU
    try:
        frecuencias = psutil.cpu_freq()
        if frecuencias:
            print(f"️ Frecuencia actual: {frecuencias.current:.0f} MHz")
            print(f"️ Frecuencia mínima: {frecuencias.min:.0f} MHz")
            print(f"️ Frecuencia máxima: {frecuencias.max:.0f} MHz")
    except:
        print("️ Frecuencia: No disponible")
    
    # Uso de CPU durante 5 segundos
    print("️ Midiendo uso de CPU (5 segundos)...")
    uso_cpu = psutil.cpu_percent(interval=5)
    print(f"️ Uso promedio de CPU: {uso_cpu:.1f}%")
    
    if uso_cpu > 90:
        print("️ ADVERTENCIA: CPU muy cargado")
    
    return uso_cpu < 90

def diagnostico_disco():
    """Diagnostica el uso de disco"""
    print("\n DIAGNÓSTICO DE DISCO")
    print("=" * 40)
    
    # Disco principal
    disco = psutil.disk_usage('/')
    print(f" Espacio total: {disco.total / (1024**3):.1f} GB")
    print(f" Espacio usado: {disco.used / (1024**3):.1f} GB")
    print(f" Espacio libre: {disco.free / (1024**3):.1f} GB")
    print(f" Porcentaje usado: {(disco.used / disco.total) * 100:.1f}%")
    
    # Velocidad de disco (test simple)
    print(" Probando velocidad de disco...")
    test_file = Path('/tmp/test_disk_speed.txt')
    start_time = time.time()
    
    try:
        with open(test_file, 'w') as f:
            f.write('x' * (1024 * 1024))  # 1MB
        write_time = time.time() - start_time
        
        start_time = time.time()
        with open(test_file, 'r') as f:
            f.read()
        read_time = time.time() - start_time
        
        test_file.unlink()
        
        print(f" Velocidad escritura: {1/write_time:.1f} MB/s")
        print(f" Velocidad lectura: {1/read_time:.1f} MB/s")
        
        if write_time > 1 or read_time > 1:
            print("️ ADVERTENCIA: Disco lento")
            return False
        
    except Exception as e:
        print(f"️ Error probando disco: {e}")
        return False
    
    return True

def diagnostico_gpu():
    """Diagnostica el estado de la GPU"""
    print("\n DIAGNÓSTICO DE GPU")
    print("=" * 40)
    
    # Verificar CUDA
    try:
        import torch
        if torch.cuda.is_available():
            print(f" CUDA disponible: {torch.cuda.device_count()} GPU(s)")
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                print(f" GPU {i}: {props.name}")
                print(f" Memoria: {props.total_memory / (1024**3):.1f} GB")
                
                # Verificar memoria GPU
                memoria_reservada = torch.cuda.memory_reserved(i)
                memoria_allocada = torch.cuda.memory_allocated(i)
                print(f" Memoria reservada: {memoria_reservada / (1024**3):.1f} GB")
                print(f" Memoria allocada: {memoria_allocada / (1024**3):.1f} GB")
        else:
            print(" CUDA no disponible")
    except ImportError:
        print(" PyTorch no instalado")
    except Exception as e:
        print(f" Error con GPU: {e}")
    
    # Verificar OpenCV
    try:
        import cv2
        print(f" OpenCV: {cv2.__version__}")
        if cv2.cuda.getCudaEnabledDeviceCount() > 0:
            print(" OpenCV con soporte CUDA")
        else:
            print(" OpenCV sin soporte CUDA")
    except ImportError:
        print(" OpenCV no instalado")
    except Exception as e:
        print(f" Error con OpenCV: {e}")

def diagnostico_temperatura():
    """Diagnostica la temperatura del sistema"""
    print("\n DIAGNÓSTICO DE TEMPERATURA")
    print("=" * 40)
    
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                print(f"️ {name}:")
                for entry in entries:
                    if entry.current:
                        print(f"   {entry.label or 'Sensor'}: {entry.current:.1f}°C")
                        if entry.current > 80:
                            print("   ️ ADVERTENCIA: Temperatura alta")
        else:
            print("️ Información de temperatura no disponible")
    except Exception as e:
        print(f"️ Error obteniendo temperatura: {e}")

def test_estabilidad():
    """Prueba de estabilidad del sistema"""
    print("\n PRUEBA DE ESTABILIDAD")
    print("=" * 40)
    
    print(" Ejecutando prueba de carga...")
    
    # Simular carga de procesamiento
    start_time = time.time()
    for i in range(1000):
        # Simular procesamiento
        data = [j for j in range(1000)]
        result = sum(data)
        
        # Liberar memoria cada 100 iteraciones
        if i % 100 == 0:
            import gc
            gc.collect()
    
    end_time = time.time()
    print(f" Tiempo de prueba: {end_time - start_time:.2f} segundos")
    
    # Verificar memoria después de la prueba
    memoria = psutil.virtual_memory()
    print(f" Memoria después de prueba: {memoria.percent:.1f}%")
    
    if memoria.percent > 90:
        print("️ ADVERTENCIA: Sistema puede ser inestable bajo carga")
        return False
    
    return True

def main():
    """Función principal de diagnóstico"""
    print(" DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("=" * 50)
    
    # Ejecutar todos los diagnósticos
    resultados = []
    
    resultados.append(("Memoria", diagnostico_memoria()))
    resultados.append(("CPU", diagnostico_cpu()))
    resultados.append(("Disco", diagnostico_disco()))
    diagnostico_gpu()
    diagnostico_temperatura()
    resultados.append(("Estabilidad", test_estabilidad()))
    
    # Resumen
    print("\n RESUMEN DEL DIAGNÓSTICO")
    print("=" * 50)
    
    problemas = []
    for nombre, ok in resultados:
        if ok:
            print(f" {nombre}: OK")
        else:
            print(f" {nombre}: PROBLEMA")
            problemas.append(nombre)
    
    if problemas:
        print(f"\n️ PROBLEMAS DETECTADOS: {', '.join(problemas)}")
        print("\n RECOMENDACIONES:")
        if "Memoria" in problemas:
            print("   • Cerrar aplicaciones innecesarias")
            print("   • Considerar aumentar RAM")
        if "CPU" in problemas:
            print("   • Reducir carga de procesamiento")
            print("   • Verificar procesos en segundo plano")
        if "Disco" in problemas:
            print("   • Verificar espacio en disco")
            print("   • Considerar SSD si usa HDD")
        if "Estabilidad" in problemas:
            print("   • El sistema puede colgarse bajo carga")
            print("   • Usar procesamiento más conservador")
    else:
        print("\n SISTEMA ESTABLE - No se detectaron problemas críticos")
    
    print("\n RECOMENDACIONES PARA EL GENERADOR:")
    print("   • Usar generador_simple.py (sin paralelismo)")
    print("   • Procesar en lotes pequeños (10-20 registros)")
    print("   • Hacer pausas entre lotes")
    print("   • Monitorear temperatura y memoria")

if __name__ == "__main__":
    main()
