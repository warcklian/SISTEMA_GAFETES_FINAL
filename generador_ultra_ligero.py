#!/usr/bin/env python3
"""
Generador Ultra Ligero - Anti-Colgada
Versión optimizada para sistemas con poca RAM o problemas de estabilidad
"""

import sys
import os
import gc
import time
from pathlib import Path
import pandas as pd
from datetime import datetime
import contextlib

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

# Importar solo lo esencial
try:
    from generador_pasaportes_masivo import GeneradorPasaportesMasivo
except ImportError as e:
    print(f" Error importando generador principal: {e}")
    sys.exit(1)

class GeneradorUltraLigero:
    """Generador ultra ligero para evitar colgadas"""
    
    def __init__(self, base_path=None):
        """Inicializa el generador ultra ligero"""
        print(" GENERADOR ULTRA LIGERO - ANTI-COLGADA")
        print("=" * 50)
        
        self.base_path = Path(base_path) if base_path else Path(__file__).parent
        self.limite_memoria = 80  # Límite de memoria más estricto
        self.tamano_lote = 5      # Lotes muy pequeños
        self.pausa_entre_lotes = 2  # Pausa entre lotes
        
        # Configurar variables de entorno para optimización
        os.environ['OMP_NUM_THREADS'] = '2'
        os.environ['MKL_NUM_THREADS'] = '2'
        os.environ['OPENBLAS_NUM_THREADS'] = '2'
        
        print(f" Configuración ultra ligera:")
        print(f"   - Límite memoria: {self.limite_memoria}%")
        print(f"   - Tamaño lote: {self.tamano_lote}")
        print(f"   - Pausa entre lotes: {self.pausa_entre_lotes}s")
        
        # Inicializar generador principal con configuración ultra ligera
        self.generador = None
        self._inicializar_generador()
    
    def _inicializar_generador(self):
        """Inicializa el generador principal con configuración ultra ligera"""
        try:
            print(" Inicializando generador ultra ligero...")
            
            # Crear generador con configuración ultra ligera
            self.generador = GeneradorPasaportesMasivo(str(self.base_path))
            
            # Ajustar configuración para ultra ligero
            if hasattr(self.generador, 'gestor_memoria'):
                self.generador.gestor_memoria.liberar_cada = 1  # Liberar cada registro
                self.generador.gestor_memoria.umbral_memoria = self.limite_memoria
            
            # Reducir tamaño de lote
            if hasattr(self.generador, 'tamano_lote'):
                self.generador.tamano_lote = self.tamano_lote
            
            # Verificar fuentes (crítico para funcionamiento)
            print(" Verificando fuentes...")
            if hasattr(self.generador, 'validador_fuentes'):
                if not self.generador.validador_fuentes.verificar_fuentes():
                    print(" ERROR: Faltan fuentes requeridas")
                    self.generador.validador_fuentes.mostrar_estado_fuentes()
                    print(" SOLUCIÓN: Ejecuta 'python3 instalar.py' para instalar fuentes")
                    raise Exception("Fuentes requeridas no disponibles")
                else:
                    print(" Fuentes verificadas correctamente")
            else:
                print("️ Validador de fuentes no encontrado")
            
            print(" Generador ultra ligero inicializado")
            
        except Exception as e:
            print(f" Error inicializando generador: {e}")
            raise
    
    def verificar_memoria(self):
        """Verifica el estado de la memoria"""
        try:
            import psutil
            memoria = psutil.virtual_memory()
            return memoria.percent
        except:
            return 0
    
    def limpiar_memoria_agresiva(self):
        """Limpieza agresiva de memoria"""
        try:
            # Garbage collection múltiple
            for _ in range(3):
                gc.collect()
            
            # Limpiar cache GPU si está disponible
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
            except:
                pass
            
            # Limpiar buffers del generador si existen
            if self.generador and hasattr(self.generador, '_limpiar_buffers_temporales'):
                self.generador._limpiar_buffers_temporales()
            
            print(" Memoria limpiada agresivamente")
            
        except Exception as e:
            print(f"️ Error en limpieza de memoria: {e}")
    
    def procesar_ultra_ligero(self, limite=None, archivo_csv=None):
        """Procesa de forma ultra ligera para evitar colgadas"""
        print(" PROCESAMIENTO ULTRA LIGERO INICIADO")
        print("=" * 50)
        
        try:
            # Verificar memoria inicial
            memoria_inicial = self.verificar_memoria()
            print(f" Memoria inicial: {memoria_inicial:.1f}%")
            
            if memoria_inicial > self.limite_memoria:
                print(f"️ Memoria alta ({memoria_inicial:.1f}%), limpiando...")
                self.limpiar_memoria_agresiva()
                time.sleep(2)
            
            # Cargar datos
            if archivo_csv:
                df = self.generador.cargar_datos_csv(archivo_csv)
            else:
                df = self.generador.cargar_datos_csv()
            
            if df is None:
                print(" No se pudieron cargar los datos")
                return False
            
            total_registros = len(df) if limite is None else min(limite, len(df))
            print(f" Total registros a procesar: {total_registros}")
            
            # Procesar en lotes ultra pequeños
            registros_procesados = []
            lote_actual = 0
            
            for inicio in range(0, total_registros, self.tamano_lote):
                fin = min(inicio + self.tamano_lote, total_registros)
                lote_actual += 1
                
                print(f"\n Procesando lote {lote_actual}: registros {inicio+1}-{fin}")
                
                # Verificar memoria antes del lote
                memoria_antes = self.verificar_memoria()
                if memoria_antes > self.limite_memoria:
                    print(f"️ Memoria alta ({memoria_antes:.1f}%), limpiando...")
                    self.limpiar_memoria_agresiva()
                    time.sleep(3)
                
                # Procesar lote
                lote_registros = []
                for idx in range(inicio, fin):
                    try:
                        registro = df.iloc[idx]
                        datos_pasaporte = self.generador._procesar_registro_simple(idx, registro)
                        
                        if datos_pasaporte:
                            lote_registros.append(datos_pasaporte)
                        
                        # Limpiar memoria cada registro si es necesario
                        if idx % 2 == 0:  # Cada 2 registros
                            memoria_actual = self.verificar_memoria()
                            if memoria_actual > self.limite_memoria:
                                self.limpiar_memoria_agresiva()
                    
                    except Exception as e:
                        print(f" Error en registro {idx + 1}: {e}")
                        continue
                
                # Agregar lote a resultados
                registros_procesados.extend(lote_registros)
                
                # Mostrar progreso
                generados = sum(1 for r in registros_procesados if r.get('estado') == 'generado')
                omitidos = sum(1 for r in registros_procesados if r.get('estado') == 'omitido')
                print(f" Progreso: {fin}/{total_registros} - Generados: {generados}, Omitidos: {omitidos}")
                
                # Limpiar memoria después del lote
                self.limpiar_memoria_agresiva()
                
                # Pausa entre lotes
                if fin < total_registros:
                    print(f"⏸️ Pausa de {self.pausa_entre_lotes}s entre lotes...")
                    time.sleep(self.pausa_entre_lotes)
            
            # Guardar resultados
            print("\n Guardando resultados...")
            self.generador.guardar_datos_procesados(registros_procesados)
            
            # Resumen final
            generados = sum(1 for r in registros_procesados if r.get('estado') == 'generado')
            omitidos = sum(1 for r in registros_procesados if r.get('estado') == 'omitido')
            
            print(f"\n PROCESAMIENTO ULTRA LIGERO COMPLETADO")
            print(f" Total procesados: {len(registros_procesados)}")
            print(f" Pasaportes generados: {generados}")
            print(f"️ Registros omitidos: {omitidos}")
            
            # Verificar memoria final
            memoria_final = self.verificar_memoria()
            print(f" Memoria final: {memoria_final:.1f}%")
            print(f" Diferencia memoria: {memoria_final - memoria_inicial:+.1f}%")
            
            return True
            
        except Exception as e:
            print(f" Error en procesamiento ultra ligero: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def encontrar_archivo_result_mas_reciente(self):
        """Encuentra el archivo RESULT más reciente"""
        try:
            data_dir = self.base_path / 'DATA'
            if not data_dir.exists():
                print(" Directorio DATA no encontrado")
                return None
            
            result_files = list(data_dir.glob('*_RESULT_*.csv'))
            
            if not result_files:
                print(" No se encontraron archivos RESULT")
                return None
            
            archivo_mas_reciente = max(result_files, key=lambda x: x.stat().st_mtime)
            print(f" Archivo RESULT más reciente: {archivo_mas_reciente.name}")
            return archivo_mas_reciente
            
        except Exception as e:
            print(f" Error encontrando archivo RESULT: {e}")
            return None
    
    def procesar_continuacion_ultra_ligera(self):
        """Continúa el procesamiento desde donde se quedó de forma ultra ligera"""
        print(" CONTINUACIÓN ULTRA LIGERA")
        print("=" * 40)
        
        try:
            # Buscar archivo RESULT más reciente
            archivo_mas_reciente = self.encontrar_archivo_result_mas_reciente()
            
            if not archivo_mas_reciente:
                return False
            
            # Cargar archivo RESULT
            df = pd.read_csv(archivo_mas_reciente, dtype=str)
            df = df.fillna("")
            
            # Identificar registros pendientes
            registros_pendientes = df[df['estado'].isna() | (df['estado'] == '') | (df['estado'] == 'nan')]
            print(f" Registros pendientes: {len(registros_pendientes)}")
            
            if len(registros_pendientes) == 0:
                print(" No hay registros pendientes")
                return True
            
            # Procesar solo registros pendientes
            return self.procesar_ultra_ligero(limite=len(registros_pendientes), archivo_csv=str(archivo_mas_reciente))
            
        except Exception as e:
            print(f" Error en continuación ultra ligera: {e}")
            return False

def seleccionar_archivo_csv():
    """Selecciona archivo CSV manualmente"""
    try:
        data_dir = Path('/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL/DATA')
        if not data_dir.exists():
            print(" Directorio DATA no encontrado")
            return None
        
        archivos = list(data_dir.glob('*.csv')) + list(data_dir.glob('*.xlsx'))
        if not archivos:
            print(" No se encontraron archivos CSV/XLSX")
            return None
        
        print("\n ARCHIVOS DISPONIBLES:")
        print("-" * 50)
        
        for i, archivo in enumerate(archivos, 1):
            tamaño = archivo.stat().st_size / (1024 * 1024)  # MB
            fecha = datetime.fromtimestamp(archivo.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            print(f"   {i:2d}. {archivo.name}")
            print(f"        Modificado: {fecha}")
            print(f"        Tamaño: {tamaño:.1f} MB")
            print()
        
        while True:
            try:
                seleccion = input(f"Selecciona archivo (1-{len(archivos)}) o 'q' para salir: ").strip()
                
                if seleccion.lower() == 'q':
                    return None
                
                indice = int(seleccion) - 1
                if 0 <= indice < len(archivos):
                    archivo_seleccionado = archivos[indice]
                    print(f" Archivo seleccionado: {archivo_seleccionado.name}")
                    return archivo_seleccionado
                else:
                    print(f" Número inválido. Ingresa un número entre 1 y {len(archivos)}")
                    
            except ValueError:
                print(" Ingresa un número válido")
            except KeyboardInterrupt:
                print("\n⏹️ Selección cancelada")
                return None
                
    except Exception as e:
        print(f" Error en selección de archivo: {e}")
        return None

def seleccionar_archivo_result():
    """Selecciona archivo RESULT manualmente"""
    try:
        data_dir = Path('/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL/DATA')
        if not data_dir.exists():
            print(" Directorio DATA no encontrado")
            return None
        
        result_files = list(data_dir.glob('*_RESULT_*.csv'))
        if not result_files:
            print(" No se encontraron archivos RESULT")
            return None
        
        # Ordenar por fecha de modificación (más reciente primero)
        result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print("\n ARCHIVOS RESULT DISPONIBLES:")
        print("-" * 50)
        
        for i, archivo in enumerate(result_files, 1):
            tamaño = archivo.stat().st_size / (1024 * 1024)  # MB
            fecha = datetime.fromtimestamp(archivo.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            print(f"   {i:2d}. {archivo.name}")
            print(f"        Modificado: {fecha}")
            print(f"        Tamaño: {tamaño:.1f} MB")
            print()
        
        while True:
            try:
                seleccion = input(f"Selecciona archivo RESULT (1-{len(result_files)}) o 'q' para salir: ").strip()
                
                if seleccion.lower() == 'q':
                    return None
                
                indice = int(seleccion) - 1
                if 0 <= indice < len(result_files):
                    archivo_seleccionado = result_files[indice]
                    print(f" Archivo RESULT seleccionado: {archivo_seleccionado.name}")
                    return archivo_seleccionado
                else:
                    print(f" Número inválido. Ingresa un número entre 1 y {len(result_files)}")
                    
            except ValueError:
                print(" Ingresa un número válido")
            except KeyboardInterrupt:
                print("\n⏹️ Selección cancelada")
                return None
                
    except Exception as e:
        print(f" Error en selección de archivo RESULT: {e}")
        return None

def mostrar_menu_simple():
    """Muestra menú simple sin tkinter"""
    print("\n¿Qué deseas hacer?")
    print("1. Procesar archivo CSV específico")
    print("2. Continuar desde archivo RESULT más reciente")
    print("3. Procesar con límite de registros")
    print("4. Salir")
    
    while True:
        try:
            opcion = input("\nSelecciona opción (1-4): ").strip()
            
            if opcion == "1":
                return "csv"
            elif opcion == "2":
                return "result"
            elif opcion == "3":
                return "limite"
            elif opcion == "4":
                return "salir"
            else:
                print(" Opción no válida. Ingresa 1, 2, 3 o 4")
                
        except KeyboardInterrupt:
            print("\n⏹️ Selección cancelada")
            return "salir"

def solicitar_limite():
    """Solicita límite de registros manualmente"""
    try:
        print("\n LÍMITE DE REGISTROS")
        print("-" * 30)
        print("Ingresa el número máximo de registros a procesar")
        print("(Deja vacío para procesar todos)")
        
        limite_texto = input("\nLímite: ").strip()
        
        if limite_texto == "":
            return None
        
        try:
            limite = int(limite_texto)
            if limite <= 0:
                print(" El límite debe ser mayor que 0")
                return None
            return limite
        except ValueError:
            print(" Ingresa un número válido")
            return None
        
    except KeyboardInterrupt:
        print("\n⏹️ Entrada cancelada")
        return None
    except Exception as e:
        print(f" Error solicitando límite: {e}")
        return None

def main():
    """Función principal con menú simple"""
    print(" GENERADOR ULTRA LIGERO - ANTI-COLGADA")
    print("=" * 50)
    print(" Este generador está optimizado para evitar colgadas")
    print(" Usa lotes muy pequeños y limpieza agresiva de memoria")
    print("=" * 50)
    
    try:
        # Crear generador ultra ligero
        generador = GeneradorUltraLigero()
        
        # Mostrar menú simple
        opcion = mostrar_menu_simple()
        
        if opcion == "csv":
            # Seleccionar archivo CSV
            archivo = seleccionar_archivo_csv()
            if archivo and archivo.exists():
                print(f" Archivo seleccionado: {archivo.name}")
                generador.procesar_ultra_ligero(archivo_csv=str(archivo))
            else:
                print(" No se seleccionó archivo o archivo no encontrado")
        
        elif opcion == "result":
            # Continuar desde archivo RESULT
            archivo = seleccionar_archivo_result()
            if archivo and archivo.exists():
                print(f" Archivo RESULT seleccionado: {archivo.name}")
                generador.procesar_ultra_ligero(archivo_csv=str(archivo))
            else:
                print(" No se seleccionó archivo RESULT")
        
        elif opcion == "limite":
            # Solicitar límite
            limite = solicitar_limite()
            if limite is not None:
                print(f" Límite establecido: {limite} registros")
            generador.procesar_ultra_ligero(limite=limite)
        
        elif opcion == "salir":
            print(" Saliendo del programa")
        
        else:
            print(" Opción no válida")
    
    except KeyboardInterrupt:
        print("\n⏹️ Procesamiento interrumpido por el usuario")
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
