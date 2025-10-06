#!/usr/bin/env python3
"""
Generador Masivo de Pasaportes Venezolanos
Integra datos del Excel con imágenes y genera pasaportes dinámicos
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import random
import re
import shutil
from datetime import datetime, date
import gc  # Garbage collector para liberar memoria
import psutil  # Para monitorear uso de memoria
from pathlib import Path
from PIL import Image
import argparse
import threading
import time
import contextlib
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2  # OPTIMIZACIÓN: OpenCV para procesamiento de imágenes

# =============================================================================
# SUPRIMIR LOGS EXCESIVOS PARA PRODUCCIÓN
# =============================================================================
import os
os.environ['GLOG_minloglevel'] = '3'  # Solo errores críticos
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Solo errores críticos de TensorFlow
os.environ['MEDIAPIPE_GPU'] = '0'  # Deshabilitar MediaPipe GPU

# =============================================================================
# CONFIGURACIÓN GLOBAL - MODIFICAR AQUÍ LOS VALORES DESEADOS
# =============================================================================

# Archivo CSV a procesar (cambiar este valor según necesites)
# Ejemplo: "DATA/Datos_Crear_20251001_043036_001.csv"
ARCHIVO_CSV = None  # None = Seleccionar automáticamente

# Límite de registros a procesar (None = todos)
# Ejemplo: 50, 100, 200, None
LIMITE_REGISTROS = None  # None = procesar todos

# Carpeta para archivos de salida (separada de DATA para evitar confusión)
CARPETA_SALIDA = "OUTPUT/resultados_pasaportes"

# =============================================================================
# CONFIGURACIÓN DE PRODUCCIÓN
# =============================================================================

# Modo de producción (True = optimizado para producción, False = modo desarrollo)
MODO_PRODUCCION = True

# Configuración de memoria para producción
MEMORIA_LIMITE_PORCENTAJE = 85  # Porcentaje de memoria RAM antes de liberar
VRAM_LIMITE_PORCENTAJE = 90     # Porcentaje de VRAM antes de liberar
LIBERAR_MEMORIA_CADA = 500      # Liberar memoria cada X registros

# Configuración de lotes para procesamiento masivo
TAMANO_LOTE_PRODUCCION = 50     # Tamaño de lote para procesamiento paralelo
MAX_WORKERS_PARALELO = 4        # Máximo número de workers paralelos

# Configuración de logging para producción
LOGGING_DETALLADO = False       # True = logs detallados, False = logs mínimos
GUARDAR_LOGS_ERRORES = True     # Guardar logs de errores en archivo

# =============================================================================
# EJEMPLOS DE CONFIGURACIÓN:
# =============================================================================
# Para procesar archivo específico:
# ARCHIVO_CSV = "DATA/Datos_Crear_20251001_043036_001.csv"
# LIMITE_REGISTROS = 50
#
# Para procesar todos los registros:
# ARCHIVO_CSV = "DATA/Datos_Crear_20251001_043036_001.csv"  
# LIMITE_REGISTROS = None
#
# Para seleccionar archivo automáticamente:
# ARCHIVO_CSV = None
# LIMITE_REGISTROS = 100
# =============================================================================

# Sistema de progreso simple sin barras visuales
class ProgresoSimple:
    def __init__(self):
        self.completed_count = 0
        self.total_count = 0
        
    def actualizar_progreso(self, completados, total):
        """Actualiza el progreso de forma simple"""
        self.completed_count = completados
        self.total_count = total
        if total > 0:
            porcentaje = (completados / total) * 100
            print(f"📊 Progreso: {completados}/{total} ({porcentaje:.1f}%)")

# OPTIMIZACIÓN: Configuración GPU con OpenCV (más estable que onnxruntime)
def configurar_gpu_entorno():
    """Configura el entorno GPU optimizado con OpenCV"""
    try:
        import torch
        if torch.cuda.is_available():
            num_gpus = torch.cuda.device_count()
            if num_gpus > 1:
                # Múltiples GPUs disponibles - usar todas
                gpu_ids = ','.join(str(i) for i in range(num_gpus))
                os.environ.setdefault('CUDA_VISIBLE_DEVICES', gpu_ids)
                print(f"🎮 Detectadas {num_gpus} GPUs: {gpu_ids}")
            else:
                os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0')
                print("🎮 GPU única detectada")
        else:
            os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0')
    except ImportError:
        os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0')
    
    # OPTIMIZACIÓN: Configurar OpenCV para GPU (más estable que TensorFlow)
    try:
        import cv2
        if cv2.cuda.getCudaEnabledDeviceCount() > 0:
            print("🎮 OpenCV CUDA detectado")
        else:
            print("⚠️ OpenCV sin soporte CUDA")
    except ImportError:
        print("⚠️ OpenCV no instalado")
    
    # Configuración base
    os.environ.setdefault('__NV_PRIME_RENDER_OFFLOAD', '1')
    os.environ.setdefault('__GLX_VENDOR_LIBRARY_NAME', 'nvidia')
    # OPTIMIZACIÓN: Deshabilitar MediaPipe GPU (causa segmentation faults)
    os.environ.setdefault('MEDIAPIPE_GPU', '0')
    os.environ.setdefault('OPENCV_OPENCL_RUNTIME', 'opencl')
    os.environ.setdefault('OPENCV_OPENCL_DEVICE', ':GPU:0')

# Configurar entorno GPU
configurar_gpu_entorno()

# Importar el script maestro para generar pasaportes visuales (después de setear entorno GPU)
sys.path.append(str(Path(__file__).parent / 'SCRIPTS'))
try:
    from script_maestro_integrado import ScriptMaestroIntegrado
except Exception as e:
    print("⚠️ No se pudo importar script_maestro_integrado.py:", e)
    ScriptMaestroIntegrado = None

class ValidadorFuentes:
    """Validador de fuentes disponibles (sistema o rutas locales del proyecto)"""
    
    def __init__(self):
        self.fuentes_requeridas = [
            # Fuentes básicas del sistema
            "Arial",
            "BrittanySignature.ttf",
            "Pasaport Numbers Front-Regular.ttf",
            "OCR-B10PitchBT Regular.otf",
            
            # Fuentes para firmas adaptativas
            "Thesignature.ttf",
            "Lovtony Script.ttf", 
            "Autography.otf",
            "Amsterdam.ttf",
            "BeautyDemo.ttf",
            "South Brittany FREE.otf",
            "Dear Script (Demo_Font).otf",
            "RetroSignature.otf",
            "Augusthin Beatrice DEMO VERSION.ttf",
            "Augusthin Beatrice Italic DEMO VERSION.ttf",
            "Amalfi Coast.ttf",
            "Hourglass of Shine.otf",
            "Breathing Personal Use Only.ttf",
            "White Sign (DemoVersion).otf",
            "Royalty Free.ttf",
            "lovtony.ttf",
            "Moriyathena.otf"
        ]
        
        self.fuentes_disponibles = []
        self.fuentes_faltantes = []
        # Ruta local del proyecto donde están las fuentes incluidas
        self.fuentes_base_path = (Path(__file__).parent / 'TEMPLATE' / 'Fuentes_Base').resolve()
        self._indice_fuentes_local = None  # cache para búsqueda rápida por nombre (case-insensitive)
    
    def verificar_fuentes(self):
        """Verifica si todas las fuentes requeridas están disponibles (sistema o locales)."""
        print("🔍 Verificando fuentes disponibles...")
        # Limpiar estado previo por reusabilidad
        self.fuentes_disponibles = []
        self.fuentes_faltantes = []
        self._construir_indice_local_si_hace_falta()
        
        for fuente in self.fuentes_requeridas:
            if self._verificar_fuente_individual(fuente):
                self.fuentes_disponibles.append(fuente)
            else:
                self.fuentes_faltantes.append(fuente)
        
        return len(self.fuentes_faltantes) == 0
    
    def _verificar_fuente_individual(self, nombre_fuente):
        """Verifica si una fuente específica está disponible en el sistema o localmente."""
        from PIL import ImageFont
        
        # 1) Intentar cargar desde el sistema por nombre
        try:
            ImageFont.truetype(nombre_fuente, 12)
            print(f"   ✅ {nombre_fuente}")
            return True
        except Exception:
            pass
        
        # 2) Intentar desde carpeta local del proyecto (búsqueda case-insensitive)
        try:
            ruta_local = self._resolver_ruta_local_fuente(nombre_fuente)
            if ruta_local and ruta_local.exists():
                ImageFont.truetype(str(ruta_local), 12)
                print(f"   ✅ {nombre_fuente} (local: {ruta_local.name})")
                return True
        except Exception:
            pass
        
        # 3) Rutas de compatibilidad (antiguas) como fallback
        try:
            rutas_locales = [
                str(self.fuentes_base_path),
                str(Path(__file__).parent / 'TEMPLATE' / 'Mas_Fuentes'),
            ]
            for ruta in rutas_locales:
                ruta_completa = os.path.join(ruta, nombre_fuente)
                if os.path.exists(ruta_completa):
                    ImageFont.truetype(ruta_completa, 12)
                    print(f"   ✅ {nombre_fuente} (compat: {ruta})")
                    return True
        except Exception:
            pass
        
        print(f"   ❌ {nombre_fuente}")
        return False

    def _construir_indice_local_si_hace_falta(self):
        if self._indice_fuentes_local is not None:
            return
        self._indice_fuentes_local = {}
        try:
            if self.fuentes_base_path.exists():
                for p in self.fuentes_base_path.iterdir():
                    if p.is_file():
                        self._indice_fuentes_local[p.name.lower()] = p
        except Exception:
            self._indice_fuentes_local = {}

    def _resolver_ruta_local_fuente(self, nombre_fuente):
        """Devuelve la ruta en `TEMPLATE/Fuentes_Base` que coincide con el nombre (case-insensitive)."""
        self._construir_indice_local_si_hace_falta()
        if not self._indice_fuentes_local:
            return None
        return self._indice_fuentes_local.get(nombre_fuente.lower())
    
    def mostrar_estado_fuentes(self):
        """Muestra el estado de las fuentes"""
        print(f"\n📊 ESTADO DE FUENTES:")
        print(f"   ✅ Disponibles: {len(self.fuentes_disponibles)}")
        print(f"   ❌ Faltantes: {len(self.fuentes_faltantes)}")
        
        if self.fuentes_faltantes:
            print(f"\n⚠️ FUENTES FALTANTES:")
            for fuente in self.fuentes_faltantes:
                print(f"   • {fuente}")
            return False
        else:
            print(f"\n✅ Todas las fuentes están disponibles")
            return True
    
    def obtener_fuentes_disponibles_por_categoria(self):
        """Obtiene fuentes disponibles organizadas por categoría"""
        fuentes_cortas = []
        fuentes_medianas = []
        fuentes_largas = []
        
        for fuente in self.fuentes_disponibles:
            if fuente in ["Breathing Personal Use Only.ttf", "White Sign (DemoVersion).otf", 
                         "Royalty Free.ttf", "lovtony.ttf", "Moriyathena.otf"]:
                fuentes_cortas.append(fuente)
            elif fuente in ["Thesignature.ttf", "Lovtony Script.ttf", "Autography.otf", 
                           "Amsterdam.ttf", "BeautyDemo.ttf", "South Brittany FREE.otf", 
                           "Dear Script (Demo_Font).otf"]:
                fuentes_medianas.append(fuente)
            elif fuente in ["RetroSignature.otf", "Augusthin Beatrice DEMO VERSION.ttf", 
                           "Augusthin Beatrice Italic DEMO VERSION.ttf", "Amalfi Coast.ttf", 
                           "Hourglass of Shine.otf"]:
                fuentes_largas.append(fuente)
        
        return {
            'cortas': fuentes_cortas,
            'medianas': fuentes_medianas,
            'largas': fuentes_largas
        }

class GestorMemoria:
    """Gestor de memoria para liberar recursos periódicamente"""
    
    def __init__(self, liberar_cada=10, umbral_memoria=80, umbral_vram_perc=85):
        self.liberar_cada = liberar_cada  # Liberar cada X registros
        self.umbral_memoria = umbral_memoria  # Umbral de memoria en %
        self.contador_registros = 0
        self.umbral_vram_perc = umbral_vram_perc  # Umbral de VRAM en %
        self.gpu_total_bytes = None
        
    def verificar_memoria(self):
        """Verifica el uso de memoria del sistema"""
        try:
            memoria_actual = psutil.virtual_memory().percent
            return memoria_actual
        except Exception:
            return 0
    
    def liberar_memoria(self, forzar=False):
        """Libera memoria del sistema de forma agresiva para evitar colgadas"""
        memoria_actual = self.verificar_memoria()
        
        # Comprobar VRAM si está disponible
        vram_actual_perc = None
        try:
            import torch
            if torch.cuda.is_available():
                # Inicializar total si no está
                if self.gpu_total_bytes is None:
                    props = torch.cuda.get_device_properties(0)
                    self.gpu_total_bytes = getattr(props, 'total_memory', None)
                reserved = torch.cuda.memory_reserved(0)
                if self.gpu_total_bytes:
                    vram_actual_perc = (reserved / self.gpu_total_bytes) * 100.0
        except Exception:
            pass

        cond_vram = (vram_actual_perc is not None and vram_actual_perc > self.umbral_vram_perc)

        # Solo liberar en casos críticos para no interrumpir el flujo de GPU
        if forzar and memoria_actual > self.umbral_memoria:
            # Liberación mínima de memoria
            gc.collect()
            
            # Limpiar cache de GPU solo si es necesario
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except:
                pass
            
            self.contador_registros = 0
            return True
        
        return False
    
    def incrementar_contador(self):
        """Incrementa contador (sin liberación automática para optimizar GPU)"""
        self.contador_registros += 1
        return False

class GeneradorPasaportesMasivo:
    def __init__(self, base_path=None):
        """Inicializa el generador de pasaportes masivo"""
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.data_path = self.base_path / 'DATA'
        # La carpeta de salida se establecerá dinámicamente basada en el CSV de origen
        self.output_path = None  # Se establecerá cuando se cargue el CSV
        self.pasaportes_visuales_path = self.base_path / 'OUTPUT' / 'pasaportes_visuales'
        self.imagenes_mujeres_path = self.data_path / 'Imagenes_Mujeres'
        
        # Crear directorios de salida de forma robusta
        self._crear_directorios_robustos()
        
        # OPTIMIZACIÓN: Gestor de memoria optimizado para producción
        self.gestor_memoria = GestorMemoria(
            liberar_cada=LIBERAR_MEMORIA_CADA, 
            umbral_memoria=MEMORIA_LIMITE_PORCENTAJE, 
            umbral_vram_perc=VRAM_LIMITE_PORCENTAJE
        )
        
        # Inicializar validador de fuentes
        self.validador_fuentes = ValidadorFuentes()
        
        # Inicializar optimizaciones GPU
        self._inicializar_gpu_optimizaciones()
        
        # Inicializar sistema de recuperación
        self._crear_sistema_recuperacion()
        
        # Sistema para recordar última ubicación de CSV
        self._inicializar_sistema_ubicacion_csv()

        # OPTIMIZACIÓN: Sistema de memoria reservada reutilizable para procesamiento masivo
        self._inicializar_recursos_reservados()
        
        # OPTIMIZACIÓN: Cargar ScriptMaestroIntegrado solo cuando se necesite (lazy loading)
        self.script_maestro_cache = None

        # Modo silencio para reducir I/O en terminal (acelera ejecución)
        self.silencioso = not LOGGING_DETALLADO
        
        # Estados y capitales usados en pasaportes venezolanos (MAYÚSCULAS y sin acentos)
        self.estados_venezuela = {
            'AMAZONAS': 'PUERTO AYACUCHO',
            'ANZOATEGUI': 'BARCELONA',
            'APURE': 'SAN FERNANDO DE APURE',
            'ARAGUA': 'MARACAY',
            'BARINAS': 'BARINAS',
            'BOLIVAR': 'CIUDAD BOLIVAR',
            'CARABOBO': 'VALENCIA',
            'COJEDES': 'SAN CARLOS',
            'DELTA AMACURO': 'TUCUPITA',
            'DISTRITO CAPITAL': 'CARACAS',
            'FALCON': 'CORO',
            'GUARICO': 'SAN JUAN DE LOS MORROS',
            'LARA': 'BARQUISIMETO',
            'MERIDA': 'MERIDA',
            'MIRANDA': 'LOS TEQUES',
            'MONAGAS': 'MATURIN',
            'NUEVA ESPARTA': 'LA ASUNCION',
            'PORTUGUESA': 'GUANARE',
            'SUCRE': 'CUMANA',
            'TACHIRA': 'SAN CRISTOBAL',
            'TRUJILLO': 'TRUJILLO',
            'LA GUAIRA': 'LA GUAIRA',
            'YARACUY': 'SAN FELIPE',
            'ZULIA': 'MARACAIBO'
        }
        
        # Rango de números de pasaporte (simulado, 9 dígitos, límite superior más realista)
        self.rango_pasaporte_min = 100000000
        self.rango_pasaporte_max = 199999999
        
        # Vigencia del pasaporte venezolano (10 años según SAIME)
        self.vigencia_pasaporte_anos = 10
        
        # OPTIMIZACIÓN: Batching optimizado para producción
        self.tamano_lote = TAMANO_LOTE_PRODUCCION
        self.registros_lote = []
        ts_base = datetime.now().strftime("%Y%m%d_%H%M%S")
        # El jsonl_path se establecerá cuando se cargue el CSV
        self.jsonl_path = None
        
        # Directorio de temporales
        self.temp_dir = self.base_path / 'OUTPUT' / 'temp'
        # CSV actualmente usado (si aplica)
        self.csv_path_used = None
        
        # Sistema de barras de progreso múltiples
        self.progress_manager = None
    
    def _determinar_capacidad_paralela(self):
        """OPTIMIZACIÓN: Determina capacidad paralela basada en GPU para máximo rendimiento"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                gpu_name = torch.cuda.get_device_name(0)
                
                # OPTIMIZACIÓN: Paralelización agresiva para máximo uso de GPU
                if gpu_memory >= 24:  # RTX 4090, A100, etc.
                    return 8  # Máximo paralelismo para GPUs de alta gama
                elif gpu_memory >= 16:  # RTX 4080, RTX 3080 Ti, etc.
                    return 6  # Alto paralelismo
                elif gpu_memory >= 12:  # RTX 4070 Ti, RTX 3080, etc.
                    return 4  # Paralelismo medio-alto
                elif gpu_memory >= 8:   # RTX 3070, RTX 4060 Ti, etc.
                    return 3  # Paralelismo medio
                elif gpu_memory >= 6:   # RTX 3060, RTX 2060, etc.
                    return 2  # Paralelismo bajo
                else:
                    return 1  # Secuencial para GPUs pequeñas
            else:
                return 1
        except:
            return 1
    
    def _procesar_lotes_paralelos(self, cola_procesamiento, registros_procesados):
        """OPTIMIZACIÓN: Procesa registros en paralelo con máximo uso de GPU"""
        import concurrent.futures
        
        # OPTIMIZACIÓN: Lotes conservadores para 20K+ registros
        lote_size = self.progress_manager.max_parallel * 1  # Tamaño conservador para estabilidad
        
        for i in range(0, len(cola_procesamiento), lote_size):
            lote = cola_procesamiento[i:i + lote_size]
            
            # OPTIMIZACIÓN: Procesar lote en paralelo con máximo workers
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.progress_manager.max_parallel) as executor:
                futures = []
                
                for j, (idx, registro) in enumerate(lote):
                    passport_id = f"passport_{idx}"
                    name = f"{registro.get('PRIMER_NOMBRE', 'N/A')} {registro.get('PRIMER_APELLIDO', 'N/A')}"
                    
                    # Iniciar barra de progreso
                    if self.progress_manager.start_passport(passport_id, name):
                        future = executor.submit(self._procesar_registro_con_progreso, passport_id, idx, registro)
                        futures.append((passport_id, future))
                
                # Esperar a que terminen todos los pasaportes del lote
                for passport_id, future in futures:
                    try:
                        resultado = future.result()
                        registros_procesados.append(resultado)
                        self.progress_manager.complete_passport(passport_id, success=True)
                    except Exception as e:
                        print(f"\n❌ Error en pasaporte {passport_id}: {e}")
                        self.progress_manager.complete_passport(passport_id, success=False)
            
            # OPTIMIZACIÓN: Limpieza GPU más frecuente para 20K+ registros
            if i % (lote_size * 2) == 0:  # Cada 2 lotes para estabilidad
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    gc.collect()
                except:
                    pass
    
    def _procesar_registro_simple(self, idx, registro):
        """Procesa registro de forma simple sin barras de progreso"""
        try:
            # Procesar datos básicos
            datos_pasaporte = self.procesar_registro(registro)
            
            if datos_pasaporte is None:
                return datos_pasaporte
            
            # Buscar imagen
            ruta_imagen = self.buscar_imagen_por_edad(datos_pasaporte['edad'], datos_pasaporte.get('sexo', 'F'))
            
            if ruta_imagen is None:
                datos_pasaporte['estado'] = 'omitido'
                datos_pasaporte['motivo_no_generado'] = f"Sin imagen adecuada (edad {datos_pasaporte['edad']})"
                return datos_pasaporte
            
            datos_pasaporte['ruta_foto'] = str(ruta_imagen)
            datos_pasaporte['imagen_usada'] = str(ruta_imagen)
            
            # Generar pasaporte visual
            ruta_pasaporte_visual = self.generar_pasaporte_visual_optimizado(datos_pasaporte)
            
            if ruta_pasaporte_visual:
                datos_pasaporte['pasaporte_visual'] = str(ruta_pasaporte_visual)
                datos_pasaporte['estado'] = 'generado'
                
                # Mover imagen usada
                self.mover_imagen_usada(datos_pasaporte['imagen_usada'])
            else:
                datos_pasaporte['estado'] = 'omitido'
                datos_pasaporte['motivo_no_generado'] = "Error en generación de pasaporte visual"
            
            # Limpiar buffers temporales
            self._limpiar_buffers_temporales()
            
            return datos_pasaporte
            
        except Exception as e:
            print(f"❌ Error en registro {idx + 1}: {e}")
            return None

    def _limpieza_previa(self):
        """Limpieza preventiva antes de iniciar una generación masiva."""
        try:
            # Limpieza silenciosa
            # Limpiar temporales previos
            self._cleanup_temporales()
            # Forzar GC
            for _ in range(2):
                gc.collect()
            # Vaciar caché GPU si disponible
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                    torch.cuda.empty_cache()
                    pass
            except Exception:
                pass
            # Reducir consumo de subprocesos BLAS
            os.environ['OMP_NUM_THREADS'] = os.environ.get('OMP_NUM_THREADS', '4')
            os.environ['MKL_NUM_THREADS'] = os.environ.get('MKL_NUM_THREADS', '4')
        except Exception as e:
            pass
    
    def _crear_directorios_robustos(self):
        """Crea todos los directorios necesarios de forma robusta"""
        if LOGGING_DETALLADO:
            print("📁 Creando estructura de directorios...")
        
        directorios_requeridos = [
            self.pasaportes_visuales_path,
            self.imagenes_mujeres_path,
            self.imagenes_mujeres_path / 'usadas',
            self.data_path / 'Imagenes_Hombres',
            self.data_path / 'Imagenes_Hombres' / 'usadas',
            self.base_path / 'OUTPUT' / 'plantillas_integradas',
            self.base_path / 'OUTPUT' / 'logs',
            self.base_path / 'OUTPUT' / 'temp'
        ]
        
        for directorio in directorios_requeridos:
            try:
                directorio.mkdir(parents=True, exist_ok=True)
                if LOGGING_DETALLADO:
                    print(f"   ✅ {directorio}")
            except Exception as e:
                if LOGGING_DETALLADO:
                    print(f"   ❌ Error creando {directorio}: {e}")
                raise Exception(f"No se pudo crear el directorio {directorio}")
        
        if LOGGING_DETALLADO:
            print("✅ Todos los directorios creados correctamente")
    
    def _inicializar_gpu_optimizaciones(self):
        """Inicializa optimizaciones GPU con soporte para múltiples GPUs"""
        if LOGGING_DETALLADO:
            print("🎮 Inicializando optimizaciones GPU...")
        
        self.gpu_disponible = False
        self.device = None
        self.gpu_name = "No detectada"
        self.gpu_total_mb = None
        self.num_gpus = 0
        self.gpu_devices = []
        
        # 1. Verificar CUDA (NVIDIA) con soporte para múltiples GPUs
        try:
            import torch
            if torch.cuda.is_available():
                self.gpu_disponible = True
                self.device = torch.device('cuda')
                self.num_gpus = torch.cuda.device_count()
                
                # Detectar todas las GPUs disponibles
                for i in range(self.num_gpus):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory
                    gpu_memory_mb = int(gpu_memory / (1024*1024))
                    self.gpu_devices.append({
                        'id': i,
                        'name': gpu_name,
                        'memory_mb': gpu_memory_mb
                    })
                
                # Usar la primera GPU como principal
                self.gpu_name = self.gpu_devices[0]['name']
                self.gpu_total_mb = self.gpu_devices[0]['memory_mb']
                
                if LOGGING_DETALLADO:
                    if self.num_gpus > 1:
                        print(f"   ✅ {self.num_gpus} GPUs NVIDIA detectadas:")
                        for gpu in self.gpu_devices:
                            print(f"      GPU {gpu['id']}: {gpu['name']} ({gpu['memory_mb']} MB)")
                        print(f"   🚀 Usando todas las GPUs para procesamiento paralelo")
                    else:
                        print(f"   ✅ GPU NVIDIA detectada: {self.gpu_name}")
                        print(f"   📦 VRAM: {self.gpu_total_mb} MB")
                
                # Optimizaciones CUDA para múltiples GPUs
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                torch.cuda.empty_cache()
                
                # Configurar balanceo de carga para múltiples GPUs
                if self.num_gpus > 1 and LOGGING_DETALLADO:
                    print(f"   ⚖️ Balanceo de carga habilitado para {self.num_gpus} GPUs")
                
        except ImportError:
            if LOGGING_DETALLADO:
                print("   ⚠️ PyTorch no instalado")
        except Exception as e:
            if LOGGING_DETALLADO:
                print(f"   ⚠️ Error con CUDA: {e}")
        
        # 2. Verificar OpenCL (AMD/Intel/otros)
        if not self.gpu_disponible:
            try:
                import pyopencl as cl
                platforms = cl.get_platforms()
                if platforms:
                    self.gpu_disponible = True
                    self.device = "opencl"
                    gpu_info = platforms[0].get_devices()[0].name
                    self.gpu_name = gpu_info
                    if LOGGING_DETALLADO:
                        print(f"   ✅ GPU OpenCL detectada: {gpu_info}")
                        print(f"   🚀 Usando OpenCL para aceleración")
            except ImportError:
                if LOGGING_DETALLADO:
                    print("   ⚠️ PyOpenCL no instalado")
            except Exception as e:
                if LOGGING_DETALLADO:
                    print(f"   ⚠️ Error con OpenCL: {e}")
        
        # 3. Verificar Metal (macOS)
        if not self.gpu_disponible:
            try:
                import torch
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self.gpu_disponible = True
                    self.device = torch.device('mps')
                    self.gpu_name = "Metal Performance Shaders"
                    if LOGGING_DETALLADO:
                        print(f"   ✅ GPU Metal detectada: {self.gpu_name}")
                        print(f"   🚀 Usando Metal para aceleración")
            except Exception as e:
                if LOGGING_DETALLADO:
                    print(f"   ⚠️ Error con Metal: {e}")
        
        # 4. Verificar DirectML (Windows)
        if not self.gpu_disponible:
            try:
                import torch
                if hasattr(torch.backends, 'dml') and torch.backends.dml.is_available():
                    self.gpu_disponible = True
                    self.device = torch.device('dml')
                    self.gpu_name = "DirectML"
                    if LOGGING_DETALLADO:
                        print(f"   ✅ GPU DirectML detectada: {self.gpu_name}")
                        print(f"   🚀 Usando DirectML para aceleración")
            except Exception as e:
                if LOGGING_DETALLADO:
                    print(f"   ⚠️ Error con DirectML: {e}")
        
        # 5. Fallback a CPU optimizado
        if not self.gpu_disponible:
            self.device = "cpu"
            if LOGGING_DETALLADO:
                print("   ⚠️ No se detectó GPU compatible, usando CPU optimizado")
        
        # Configurar variables de entorno para optimización universal
        os.environ['OMP_NUM_THREADS'] = '4'
        os.environ['MKL_NUM_THREADS'] = '4'
        os.environ['OPENBLAS_NUM_THREADS'] = '4'
        os.environ['NUMEXPR_NUM_THREADS'] = '4'
        
        # OPTIMIZACIÓN: Deshabilitar MediaPipe completamente (causa segmentation faults)
        os.environ['MEDIAPIPE_GPU'] = '0'
        os.environ['GLOG_minloglevel'] = '3'  # Solo errores críticos
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Solo errores críticos de TensorFlow
        if LOGGING_DETALLADO:
            print("   ⚠️ MediaPipe deshabilitado (causa segmentation faults)")
            print("✅ Optimizaciones universales configuradas")

    def _inicializar_recursos_reservados(self):
        """OPTIMIZACIÓN: Inicializa recursos reservados reutilizables para procesamiento masivo"""
        if LOGGING_DETALLADO:
            print("🔄 Inicializando recursos reservados reutilizables...")
        
        # 1. Cache de plantilla base (se carga una sola vez)
        self.plantilla_cache = None
        self.plantilla_path = None
        
        # 2. Cache de modelos de IA (MediaPipe, OpenCV, etc.)
        self.mediapipe_cache = None
        self.opencv_models_cache = {}
        
        # 3. Buffers de procesamiento de imágenes (reutilizables)
        self.image_buffers = {
            'original': None,
            'processed': None,
            'resized': None,
            'grayscale': None,
            'final': None
        }
        
        # 4. Configuraciones fijas (se cargan una sola vez)
        self.config_cache = {
            'gpu_disponible': True,  # Asumir GPU disponible
            'opencv_optimizado': True,
            'mediapipe_habilitado': False,  # Deshabilitado por estabilidad
            'batch_size': 50,
            'memoria_limite': 85
        }
        
        # 5. Pool de workers para procesamiento paralelo
        self.worker_pool = None
        
        # 6. Inicializar modelos OpenCV básicos
        self._inicializar_modelos_opencv_basicos()
        
        if LOGGING_DETALLADO:
            print("✅ Recursos reservados reutilizables inicializados")

    def _cargar_script_maestro_lazy(self):
        """OPTIMIZACIÓN: Carga ScriptMaestroIntegrado solo cuando se necesite"""
        if self.script_maestro_cache is None:
            try:
                self.script_maestro_cache = ScriptMaestroIntegrado()
                print("   🎯 Script maestro cargado bajo demanda")
            except Exception as e:
                print(f"   ❌ Error cargando script maestro: {e}")
                return None
        return self.script_maestro_cache

    def _inicializar_modelos_opencv_basicos(self):
        """OPTIMIZACIÓN: Inicializa modelos OpenCV básicos solo cuando se necesiten"""
        try:
            import cv2
            
            # Configurar OpenCV para optimización (ligero)
            cv2.setNumThreads(2)  # Reducir threads para ahorrar memoria
            
            # Solo inicializar cache, cargar modelos bajo demanda
            self.opencv_models_cache = {}
            
            print("   ✅ Modelos OpenCV preparados para carga bajo demanda")
            
        except Exception as e:
            print(f"   ⚠️ Error preparando OpenCV: {e}")
    
    def _cargar_modelo_opencv_bajo_demanda(self, modelo_name):
        """Carga modelos OpenCV solo cuando se necesiten"""
        if modelo_name not in self.opencv_models_cache:
            try:
                import cv2
                
                if modelo_name == 'face_cascade':
                    face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                    if Path(face_cascade_path).exists():
                        self.opencv_models_cache[modelo_name] = cv2.CascadeClassifier(face_cascade_path)
                        print(f"   🔧 {modelo_name} cargado bajo demanda")
                
            except Exception as e:
                print(f"   ⚠️ Error cargando {modelo_name}: {e}")
                return None
        
        return self.opencv_models_cache.get(modelo_name)

    def _cargar_plantilla_base(self, plantilla_path):
        """OPTIMIZACIÓN: Carga plantilla base una sola vez y la reutiliza"""
        if self.plantilla_cache is None or self.plantilla_path != plantilla_path:
            try:
                from PIL import Image
                self.plantilla_cache = Image.open(plantilla_path).copy()
                self.plantilla_path = plantilla_path
                print(f"   📄 Plantilla base cargada: {plantilla_path}")
            except Exception as e:
                print(f"   ❌ Error cargando plantilla: {e}")
                return None
        return self.plantilla_cache

    def _inicializar_modelos_ia(self):
        """OPTIMIZACIÓN: Inicializa modelos de IA una sola vez"""
        if self.mediapipe_cache is None:
            try:
                import mediapipe as mp
                # Inicializar MediaPipe una sola vez
                self.mediapipe_cache = {
                    'face_mesh': mp.solutions.face_mesh.FaceMesh(
                        static_image_mode=True,
                        max_num_faces=1,
                        refine_landmarks=True,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5
                    ),
                    'face_detection': mp.solutions.face_detection.FaceDetection(
                        model_selection=0,
                        min_detection_confidence=0.5
                    )
                }
                print("   🧠 Modelos MediaPipe inicializados")
            except Exception as e:
                print(f"   ⚠️ Error inicializando MediaPipe: {e}")
                self.mediapipe_cache = None
        
        if not self.opencv_models_cache:
            try:
                import cv2
                # Cargar modelos OpenCV una sola vez
                self.opencv_models_cache = {
                    'face_cascade': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'),
                    'eye_cascade': cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
                }
                print("   🔍 Modelos OpenCV inicializados")
            except Exception as e:
                print(f"   ⚠️ Error inicializando OpenCV: {e}")

    def _procesar_imagen_optimizada(self, ruta_imagen):
        """OPTIMIZACIÓN: Procesa imagen usando recursos reservados reutilizables"""
        try:
            # Cargar imagen original
            import cv2
            imagen = cv2.imread(str(ruta_imagen))
            if imagen is None:
                return None
            
            # Usar buffers reutilizables
            self.image_buffers['original'] = imagen
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            
            # Detectar cara usando modelo cacheado
            if 'face_cascade' in self.opencv_models_cache:
                face_cascade = self.opencv_models_cache['face_cascade']
                gray = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                    # Tomar la cara más grande
                    face = max(faces, key=lambda x: x[2] * x[3])
                    x, y, w, h = face
                    
                    # Recortar cara usando buffer
                    self.image_buffers['processed'] = imagen_rgb[y:y+h, x:x+w]
                    
                    # Procesar fondo usando GPU si está disponible
                    cara_recortada = self.image_buffers['processed']
                    
                    # Remover fondo usando OpenCV optimizado
                    hsv = cv2.cvtColor(cara_recortada, cv2.COLOR_RGB2HSV)
                    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
                    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
                    mask = cv2.inRange(hsv, lower_skin, upper_skin)
                    
                    # Aplicar morfología para limpiar la máscara
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    
                    # Aplicar la máscara
                    resultado = cara_recortada.copy()
                    resultado[mask == 0] = [0, 0, 0, 0]  # Transparente
                    
                    # Convertir a PIL usando buffer
                    from PIL import Image
                    self.image_buffers['final'] = Image.fromarray(resultado)
                    return self.image_buffers['final']
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error procesando imagen: {e}")
            return None

    def _limpiar_buffers_temporales(self):
        """OPTIMIZACIÓN: Limpia solo buffers temporales, mantiene recursos reservados"""
        # Limpiar solo buffers de imagen temporal
        for key in ['original', 'processed', 'resized', 'grayscale']:
            self.image_buffers[key] = None
        
        # Forzar garbage collection solo de temporales
        import gc
        gc.collect()
        
        # Limpiar cache GPU si es necesario
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass

    def _liberar_recursos_reservados(self):
        """OPTIMIZACIÓN: Libera todos los recursos reservados al final del procesamiento"""
        print("🧹 Liberando recursos reservados...")
        
        # Limpiar plantilla
        if self.plantilla_cache:
            del self.plantilla_cache
            self.plantilla_cache = None
        
        # Limpiar modelos de IA
        if self.mediapipe_cache:
            for model in self.mediapipe_cache.values():
                if hasattr(model, 'close'):
                    model.close()
            self.mediapipe_cache = None
        
        # Limpiar modelos OpenCV
        self.opencv_models_cache.clear()
        
        # Limpiar todos los buffers
        for key in self.image_buffers:
            self.image_buffers[key] = None
        
        # Limpiar configuraciones
        self.config_cache.clear()
        
        # Limpiar pool de workers
        if self.worker_pool:
            self.worker_pool.shutdown(wait=True)
            self.worker_pool = None
        
        # Limpieza final de memoria
        import gc
        gc.collect()
        
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except:
            pass
        
        print("✅ Recursos reservados liberados")

    def _append_jsonl(self, registros):
        """Añade un lote de registros al archivo JSONL"""
        if not registros:
            return
        try:
            with open(self.jsonl_path, 'a', encoding='utf-8') as fout:
                for r in registros:
                    fout.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
            print(f"💾 Lote guardado en JSONL: +{len(registros)} líneas → {self.jsonl_path.name}")
        except Exception as e:
            print(f"⚠️ Error guardando JSONL por lotes: {e}")

    def _cleanup_temporales(self):
        """Elimina archivos temporales del directorio temp para liberar espacio"""
        try:
            if not self.temp_dir.exists():
                return
            eliminados = 0
            for f in self.temp_dir.iterdir():
                try:
                    if f.is_file():
                        f.unlink()
                        eliminados += 1
                except Exception:
                    continue
            if eliminados:
                print(f"🧽 Temporales eliminados: {eliminados}")
        except Exception as e:
            print(f"⚠️ Error limpiando temporales: {e}")
    
    def _crear_sistema_recuperacion(self):
        """Crea sistema de recuperación para evitar pérdida de progreso"""
        self.archivo_progreso = self.base_path / 'OUTPUT' / 'logs' / 'progreso_actual.json'
        self.archivo_errores = self.base_path / 'OUTPUT' / 'logs' / 'errores.log'
        
        # Crear archivos de seguimiento
        self.archivo_progreso.parent.mkdir(parents=True, exist_ok=True)
        self.archivo_errores.parent.mkdir(parents=True, exist_ok=True)
    
    def _inicializar_sistema_ubicacion_csv(self):
        """Inicializa sistema para recordar última ubicación de CSV"""
        self.archivo_ubicacion_csv = self.base_path / 'OUTPUT' / 'logs' / 'ultima_ubicacion_csv.json'
        self.ultima_ubicacion_csv = None
        
        # Cargar última ubicación si existe
        self._cargar_ultima_ubicacion_csv()
    
    def _cargar_ultima_ubicacion_csv(self):
        """Carga la última ubicación de CSV procesado"""
        try:
            if self.archivo_ubicacion_csv.exists():
                with open(self.archivo_ubicacion_csv, 'r') as f:
                    data = json.load(f)
                    self.ultima_ubicacion_csv = data.get('ultima_ubicacion')
                    if LOGGING_DETALLADO:
                        print(f"📂 Última ubicación CSV: {self.ultima_ubicacion_csv}")
        except Exception as e:
            if LOGGING_DETALLADO:
                print(f"⚠️ Error cargando última ubicación: {e}")
            self.ultima_ubicacion_csv = None
    
    def _guardar_ultima_ubicacion_csv(self, ubicacion):
        """Guarda la última ubicación de CSV procesado"""
        try:
            data = {
                'ultima_ubicacion': str(ubicacion),
                'timestamp': datetime.now().isoformat()
            }
            with open(self.archivo_ubicacion_csv, 'w') as f:
                json.dump(data, f, indent=2)
            self.ultima_ubicacion_csv = str(ubicacion)
            if LOGGING_DETALLADO:
                print(f"💾 Ubicación CSV guardada: {ubicacion}")
        except Exception as e:
            if LOGGING_DETALLADO:
                print(f"⚠️ Error guardando ubicación: {e}")
    
    def _establecer_carpeta_salida(self, archivo_csv):
        """Establece la carpeta de salida en una subcarpeta de la misma ruta del CSV"""
        try:
            # Crear subcarpeta en la misma ruta del CSV
            carpeta_csv = archivo_csv.parent
            subcarpeta_resultados = carpeta_csv / "resultados_pasaportes"
            self.output_path = subcarpeta_resultados
            self.output_path.mkdir(parents=True, exist_ok=True)
            
            # Establecer jsonl_path
            ts_base = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.jsonl_path = self.output_path / f'pasaportes_procesados_{ts_base}.jsonl'
            
        except Exception as e:
            # Fallback a carpeta por defecto
            self.output_path = self.base_path / CARPETA_SALIDA
            self.output_path.mkdir(parents=True, exist_ok=True)
            ts_base = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.jsonl_path = self.output_path / f'pasaportes_procesados_{ts_base}.jsonl'
    
    def _guardar_progreso(self, registro_actual, total_registros):
        """Guarda el progreso actual para recuperación"""
        try:
            progreso = {
                'registro_actual': registro_actual,
                'total_registros': total_registros,
                'timestamp': datetime.now().isoformat(),
                'memoria_actual': self.gestor_memoria.verificar_memoria(),
                'csv_usado': str(self.csv_path_used) if self.csv_path_used else None
            }
            
            with open(self.archivo_progreso, 'w') as f:
                json.dump(progreso, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error guardando progreso: {e}")
    
    def _cargar_progreso(self):
        """Carga el progreso guardado para recuperación"""
        try:
            if self.archivo_progreso.exists():
                with open(self.archivo_progreso, 'r') as f:
                    progreso = json.load(f)
                print(f"📂 Progreso encontrado: {progreso['registro_actual']}/{progreso['total_registros']}")
                return progreso
        except Exception as e:
            print(f"⚠️ Error cargando progreso: {e}")
        return None
    
    def _hay_imagenes_disponibles(self) -> bool:
        """Retorna True si hay imágenes disponibles para procesar (no usadas)."""
        try:
            disponibles = list(self.imagenes_mujeres_path.glob('*.png'))
            return len(disponibles) > 0
        except Exception:
            return False
        
        # Campos requeridos para el pasaporte (extraídos del script maestro)
        self.campos_pasaporte = {
            'imagen': 'ruta_foto',
            'numero_pasaporte_vertical1': 'numero_pasaporte_1',
            'numero_pasaporte_vertical2': 'numero_pasaporte_2', 
            'tipo_documento': 'tipo',
            'pais': 'pais_emisor',
            'nombre': 'nombre_completo',
            'apellido': 'apellido_completo',
            'fecha_nacimiento': 'fecha_nacimiento',
            'numero_documento': 'cedula',
            'fecha_emision': 'fecha_emision',
            'fecha_vencimiento': 'fecha_vencimiento',
            'sexo': 'sexo',
            'nacionalidad': 'nacionalidad',
            'lugar_nacimiento': 'lugar_nacimiento',
            'numero_pasaporte': 'numero_pasaporte',
            'code': 'codigo_verificacion',
            'firma_texto': 'firma',
            'codigo_mrz_linea1': 'mrz_linea1',
            'codigo_mrz_linea2': 'mrz_linea2'
        }
    
    def seleccionar_archivo_csv(self):
        """Abre una ventana para seleccionar el archivo CSV"""
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal
        
        archivo_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV con datos procesados",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            initialdir=str(self.output_path)
        )
        
        root.destroy()
        return archivo_path
    
    def _convertir_xlsx_a_csv(self, archivo_xlsx: Path) -> Path:
        """Convierte XLSX a CSV (UTF-8) en la misma carpeta con timestamp en el nombre y retorna la ruta del CSV."""
        try:
            df = pd.read_excel(archivo_xlsx, dtype=str)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_path = archivo_xlsx.with_name(f"{archivo_xlsx.stem}_{ts}.csv")
            # Guardar en UTF-8 sin index
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"💾 Convertido XLSX→CSV: {csv_path.name}")
            return csv_path
        except Exception as e:
            print(f"⚠️ Error convirtiendo XLSX a CSV: {e}")
            # Fallback: devolver original para intentar lectura directa
            return archivo_xlsx

    def _normalizar_fechas_en_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Elimina HH:MM:SS dejando YYYY-MM-DD en columnas de fecha (sin alterar orden)."""
        try:
            # Columnas candidatas: contienen 'FECHA' en el nombre
            cols_fecha = [c for c in df.columns if 'FECHA' in c.upper()]
            for c in cols_fecha:
                if c in df:
                    df[c] = df[c].astype(str).str.strip()
                    # Si viene como 'YYYY-MM-DD HH:MM:SS', tomar solo la parte de la fecha
                    df[c] = df[c].str.split().str[0]
                    # Asegurar formato YYYY-MM-DD (no cambiar orden)
                    # Si alguna celda no cumple, la dejamos igual para evitar invertir día/mes
            return df
        except Exception:
            return df

    def cargar_datos_csv(self, archivo_path=None):
        """Carga datos desde archivo CSV optimizado (generado por procesador_xlsx.py)"""
        print("📊 Cargando datos desde CSV optimizado...")
        
        if archivo_path is None:
            # SIEMPRE solicitar selección manual del archivo CSV
            print("📂 Seleccionando archivo CSV...")
            archivo_path = self.seleccionar_archivo_csv()
            if not archivo_path:
                print("❌ No se seleccionó archivo CSV")
                return None
        
        # Convertir a Path si es string
        if isinstance(archivo_path, str):
            archivo_path = Path(archivo_path)
        
        try:
            if archivo_path.suffix.lower() == '.csv' and archivo_path.exists():
                # Marcar CSV usado
                self.csv_path_used = archivo_path
                # Establecer carpeta de salida basada en la ubicación del CSV
                self._establecer_carpeta_salida(archivo_path)
                # Guardar ubicación para próxima vez
                self._guardar_ultima_ubicacion_csv(archivo_path)
                # Cargar CSV optimizado (ya procesado por procesador_xlsx.py)
                df = pd.read_csv(archivo_path, dtype=str, keep_default_na=False)
                print(f"✅ Datos cargados (CSV optimizado): {len(df)} registros")
                return df
            else:
                print(f"❌ Archivo CSV no encontrado: {archivo_path}")
                return None
        except Exception as e:
            print(f"❌ Error al cargar CSV: {e}")
            return None
    
    def calcular_edad(self, fecha_nacimiento):
        """Calcula la edad basada en la fecha de nacimiento"""
        # Verificar si es None o NaN
        if fecha_nacimiento is None or pd.isna(fecha_nacimiento):
            return None
        
        try:
            if isinstance(fecha_nacimiento, str):
                # Verificar que no esté vacío
                if not fecha_nacimiento.strip():
                    return None
                fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            elif isinstance(fecha_nacimiento, datetime):
                fecha_nacimiento = fecha_nacimiento.date()
            
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year
            
            # Ajustar si aún no ha cumplido años este año
            if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
                edad -= 1
                
            return edad
        except Exception as e:
            # Si hay cualquier error, retornar None
            return None
    
    def limpiar_texto(self, texto):
        """Limpia y normaliza texto (mayúsculas, sin acentos, sin espacios excesivos)"""
        if pd.isna(texto) or texto == '':
            return ''
        
        # Convertir a string y limpiar
        texto = str(texto).strip()
        
        # Eliminar acentos y caracteres especiales
        texto = texto.replace('á', 'A').replace('é', 'E').replace('í', 'I').replace('ó', 'O').replace('ú', 'U')
        texto = texto.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        texto = texto.replace('ñ', 'N').replace('Ñ', 'N')
        
        # Convertir a mayúsculas
        texto = texto.upper()
        
        # Eliminar espacios excesivos
        texto = ' '.join(texto.split())
        
        return texto
    
    def generar_numero_pasaporte(self):
        """Genera un número de pasaporte aleatorio dentro del rango válido"""
        return random.randint(self.rango_pasaporte_min, self.rango_pasaporte_max)
    
    def seleccionar_lugar_nacimiento(self):
        """Selecciona aleatoriamente un lugar de nacimiento de Venezuela"""
        estado = random.choice(list(self.estados_venezuela.keys()))
        capital = self.estados_venezuela[estado]
        # Normalizar a MAYÚSCULAS y sin acentos para impresión en pasaporte
        capital_norm = self.limpiar_texto(capital)
        return f"{capital_norm} VEN"
    
    def formatear_fecha_pasaporte(self, fecha):
        """Formatea fecha para el pasaporte (DD/MMM/MMM/YYYY)"""
        if pd.isna(fecha):
            return "01/Ene/Jan/2000"
        
        try:
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d')
            elif isinstance(fecha, datetime):
                pass
            elif isinstance(fecha, date):
                # Convertir date a datetime
                fecha = datetime.combine(fecha, datetime.min.time())
            else:
                print(f"⚠️ Tipo de fecha no reconocido: {type(fecha)}")
                return "01/Ene/Jan/2000"
        except Exception as e:
            print(f"⚠️ Error procesando fecha: {e}")
            return "01/Ene/Jan/2000"
        
        # Meses en español (primera letra mayúscula, resto minúsculas)
        meses_es = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }
        
        # Meses en inglés (primera letra mayúscula, resto minúsculas)
        meses_en = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
        
        mes_es = meses_es[fecha.month]
        mes_en = meses_en[fecha.month]
        return f"{fecha.day:02d}/{mes_es}/{mes_en}/{fecha.year}"
    
    def generar_fecha_emision(self, fecha_nacimiento):
        """
        Genera fecha de emisión realista basada en la fecha de nacimiento
        
        Reglas:
        1. La emisión debe ser DESPUÉS de que la persona cumpla 18 años
        2. La emisión debe ser en los últimos 5 años (pasaporte vigente)
        3. La emisión debe ser al menos 3 meses antes de hoy (evitar expiración próxima)
        """
        # Verificar si la fecha es válida
        if fecha_nacimiento is None or pd.isna(fecha_nacimiento):
            # Usar fecha por defecto si no hay fecha de nacimiento
            hoy = date.today()
            return self.formatear_fecha_pasaporte(date(hoy.year - 2, 1, 1))
        
        hoy = date.today()
        
        try:
            # Calcular fecha cuando cumplió 18 años
            if isinstance(fecha_nacimiento, str):
                if not fecha_nacimiento.strip():
                    return self.formatear_fecha_pasaporte(date(hoy.year - 2, 1, 1))
                fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
            else:
                fecha_nac = fecha_nacimiento.date() if hasattr(fecha_nacimiento, 'date') else fecha_nacimiento
            
            fecha_18_anos = date(fecha_nac.year + 18, fecha_nac.month, fecha_nac.day)
        except Exception:
            # Si hay error, usar fecha por defecto
            return self.formatear_fecha_pasaporte(date(hoy.year - 2, 1, 1))
        
        # La emisión debe ser DESPUÉS de cumplir 18 años
        fecha_inicio_emision = max(fecha_18_anos, date(hoy.year - 5, 1, 1))
        
        # La emisión debe ser al menos 3 meses antes de hoy (evitar expiración próxima)
        if hoy.month > 3:
            fecha_limite = date(hoy.year, hoy.month - 3, hoy.day)
        else:
            fecha_limite = date(hoy.year - 1, hoy.month + 9, hoy.day)
        fecha_fin_emision = min(fecha_limite, hoy)
        
        # Asegurar que hay al menos 1 año de diferencia entre inicio y fin
        if fecha_inicio_emision >= fecha_fin_emision:
            # Extender el rango si es necesario
            fecha_fin_emision = date(fecha_inicio_emision.year + 1, fecha_inicio_emision.month, fecha_inicio_emision.day)
        
        # Si no hay rango válido, usar fecha por defecto
        if fecha_inicio_emision >= fecha_fin_emision:
            print(f"⚠️ Rango de fechas inválido. Inicio: {fecha_inicio_emision}, Fin: {fecha_fin_emision}")
            fecha_emision = date(hoy.year - 2, 1, 1)  # 2 años atrás como fallback
        else:
            dias_diferencia = (fecha_fin_emision - fecha_inicio_emision).days
            dias_aleatorios = random.randint(0, dias_diferencia)
            fecha_emision = fecha_inicio_emision + pd.Timedelta(days=dias_aleatorios)
            # Fecha generada silenciosamente
        
        return self.formatear_fecha_pasaporte(fecha_emision)
    
    def generar_fecha_vencimiento(self, fecha_emision):
        """
        Genera fecha de vencimiento (10 años después de emisión según SAIME)
        
        Reglas:
        1. Exactamente 10 años después de la fecha de emisión
        2. Usar la fecha exacta de emisión, no solo el año
        """
        if isinstance(fecha_emision, str):
            # Extraer fecha de la fecha formateada (DD/MMM/MMM/YYYY)
            partes = fecha_emision.split('/')
            dia = int(partes[0])
            año = int(partes[3])
            
            # Mapear mes
            meses = {
                'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6,
                'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12
            }
            mes = meses.get(partes[1], 1)
            
            fecha_emision_obj = date(año, mes, dia)
        else:
            fecha_emision_obj = fecha_emision
        
        # Calcular vencimiento exacto (10 años después)
        try:
            fecha_vencimiento = date(
                fecha_emision_obj.year + self.vigencia_pasaporte_anos,
                fecha_emision_obj.month,
                fecha_emision_obj.day
            )
        except ValueError:
            # Si el día no existe en el año de vencimiento (ej: 29 feb en año no bisiesto)
            fecha_vencimiento = date(
                fecha_emision_obj.year + self.vigencia_pasaporte_anos,
                fecha_emision_obj.month,
                fecha_emision_obj.day - 1
            )
        
        return self.formatear_fecha_pasaporte(fecha_vencimiento)
    
    def generar_codigo_verificacion(self, fecha_nacimiento):
        """Genera código de verificación basado en fecha de nacimiento"""
        if fecha_nacimiento is None or pd.isna(fecha_nacimiento):
            return "01-01-00"
        
        try:
            if isinstance(fecha_nacimiento, str):
                if not fecha_nacimiento.strip():
                    return "01-01-00"
                fecha = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            else:
                fecha = fecha_nacimiento
            
            return f"{fecha.day:02d}-{fecha.month:02d}-{str(fecha.year)[-2:]}"
        except Exception:
            return "01-01-00"
    
    def generar_mrz_linea1(self, nombre, apellido, numero_pasaporte):
        """
        Genera línea 1 del código MRZ (Machine Readable Zone)
        
        FORMATO MRZ LÍNEA 1 CORRECTO:
        P<VEN{APELLIDO}<<{NOMBRE}<<<<<<<<<<<<<<<
        
        Donde:
        - P = Tipo de documento (Pasaporte)
        - < = Separador
        - VEN = Código de país (Venezuela)
        - APELLIDO = Apellido completo (máximo 20 caracteres, relleno con <)
        - << = Separador doble
        - NOMBRE = Nombre completo (máximo 20 caracteres, relleno con <)
        - <<<<<<<<<<<<<<< = Relleno final (15 caracteres)
        
        TOTAL: 44 caracteres
        """
        # Limpiar y formatear apellido (sin espacios, solo letras)
        apellido_limpio = re.sub(r'[^A-Z]', '', apellido.upper())[:20]
        apellido_padded = apellido_limpio.ljust(20, '<')
        
        # Limpiar y formatear nombre (sin espacios, solo letras)
        nombre_limpio = re.sub(r'[^A-Z]', '', nombre.upper())[:20]
        nombre_padded = nombre_limpio.ljust(20, '<')
        
        # Construir línea MRZ completa (44 caracteres)
        mrz_linea = f"P<VEN{apellido_padded}<<{nombre_padded}"
        
        # Asegurar que tenga exactamente 44 caracteres
        if len(mrz_linea) < 44:
            mrz_linea = mrz_linea.ljust(44, '<')
        elif len(mrz_linea) > 44:
            mrz_linea = mrz_linea[:44]
        
        return mrz_linea
    
    def generar_mrz_linea2(self, numero_pasaporte, fecha_nacimiento, sexo):
        """
        Genera línea 2 del código MRZ (Machine Readable Zone)
        
        FORMATO MRZ LÍNEA 2 CORRECTO:
        {NUMERO_PASAPORTE}{CHECK_DIGIT}{PAIS}{FECHA_NAC}{SEXO}{FECHA_VENC}{CHECK_DIGIT}{RELLENO}{CHECK_DIGIT}
        
        Donde:
        - NUMERO_PASAPORTE = Número de pasaporte (9 dígitos)
        - CHECK_DIGIT = Dígito de verificación del número de pasaporte
        - PAIS = Código de país (VEN)
        - FECHA_NAC = Fecha de nacimiento (YYMMDD)
        - SEXO = F (Femenino) o M (Masculino)
        - FECHA_VENC = Fecha de vencimiento (YYMMDD)
        - CHECK_DIGIT = Dígito de verificación adicional
        - RELLENO = Relleno con < (15 caracteres)
        - CHECK_DIGIT = Dígito de verificación final
        
        TOTAL: 44 caracteres
        """
        # Formatear fecha de nacimiento para MRZ
        try:
            if fecha_nacimiento is None or pd.isna(fecha_nacimiento):
                # Usar fecha por defecto si no hay fecha válida
                fecha = datetime(1990, 1, 1)
            elif isinstance(fecha_nacimiento, str):
                if not fecha_nacimiento.strip():
                    fecha = datetime(1990, 1, 1)
                else:
                    fecha = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
            else:
                fecha = fecha_nacimiento
            
            fecha_mrz = f"{str(fecha.year)[-2:]}{fecha.month:02d}{fecha.day:02d}"
            
            # Fecha de vencimiento (10 años después)
            fecha_vencimiento = date(fecha.year + 10, 1, 1)
            fecha_venc_mrz = f"{str(fecha_vencimiento.year)[-2:]}{fecha_vencimiento.month:02d}{fecha_vencimiento.day:02d}"
        except Exception:
            # Usar fechas por defecto en caso de error
            fecha_mrz = "900101"
            fecha_venc_mrz = "000101"
        
        # Sexo para MRZ
        sexo_mrz = 'F' if sexo.upper() == 'F' else 'M'
        
        # Generar dígitos de verificación (simulados)
        check_digit_pasaporte = random.randint(0, 9)
        check_digit_adicional = random.randint(0, 9)
        check_digit_final = random.randint(0, 9)
        
        # Construir línea MRZ completa
        mrz_linea = f"{numero_pasaporte}{check_digit_pasaporte}VEN{fecha_mrz}{sexo_mrz}{fecha_venc_mrz}{check_digit_adicional}<<<<<<<<<<<<<<<{check_digit_final}"
        
        # Asegurar que tenga exactamente 44 caracteres
        if len(mrz_linea) < 44:
            mrz_linea = mrz_linea.ljust(44, '<')
        elif len(mrz_linea) > 44:
            mrz_linea = mrz_linea[:44]
        
        return mrz_linea
    
    def definir_rango_edad(self, edad):
        """Define rangos de edad apropiados para búsqueda de imágenes"""
        if edad <= 20:
            return (18, 20)
        elif edad <= 25:
            return (21, 25)
        elif edad <= 30:
            return (26, 30)
        elif edad <= 35:
            return (31, 35)
        elif edad <= 40:
            return (36, 40)
        elif edad <= 45:
            return (41, 45)
        elif edad <= 50:
            return (46, 50)
        else:
            return (51, 60)
    
    def buscar_imagen_por_edad(self, edad, genero='mujer'):
        """
        Busca una imagen que coincida exactamente con la edad, si no existe usa rangos
        
        Verifica:
        1. Coincidencia exacta de edad
        2. Rango de edad apropiado
        3. Selección aleatoria como último recurso
        """
        if genero.upper() != 'F':
            return None
        
        # Buscar imágenes de mujeres
        imagenes_disponibles = list(self.imagenes_mujeres_path.glob('*.png'))
        
        if not imagenes_disponibles:
            print(f"⚠️ No se encontraron imágenes en {self.imagenes_mujeres_path}")
            return None
        
        # 1. Buscar coincidencia exacta de edad
        imagenes_exactas = []
        for img_path in imagenes_disponibles:
            nombre_archivo = img_path.stem
            match = re.search(r'massive_venezuelan_mujer_(\d+)_', nombre_archivo)
            
            if match:
                edad_imagen = int(match.group(1))
                if edad_imagen == edad:
                    imagenes_exactas.append((img_path, edad_imagen))
        
        if imagenes_exactas:
            imagen_seleccionada, edad_imagen = random.choice(imagenes_exactas)
            return imagen_seleccionada
        
        # 2. Si no hay coincidencia exacta, usar rangos
        rango_min, rango_max = self.definir_rango_edad(edad)
        
        imagenes_rango = []
        for img_path in imagenes_disponibles:
            nombre_archivo = img_path.stem
            match = re.search(r'massive_venezuelan_mujer_(\d+)_', nombre_archivo)
            
            if match:
                edad_imagen = int(match.group(1))
                if rango_min <= edad_imagen <= rango_max:
                    imagenes_rango.append((img_path, edad_imagen))
        
        if imagenes_rango:
            imagen_seleccionada, edad_imagen = random.choice(imagenes_rango)
            return imagen_seleccionada
        
        # 3. Si no hay coincidencias en rango, usar selección aleatoria como fallback
        if imagenes_disponibles:
            return random.choice(imagenes_disponibles)
        
        return None
    
    def procesar_imagen_optimizada(self, ruta_imagen):
        """OPTIMIZACIÓN: Procesa imagen usando OpenCV en lugar de MediaPipe/rembg"""
        try:
            # Cargar imagen con OpenCV
            imagen = cv2.imread(str(ruta_imagen))
            if imagen is None:
                return None
            
            # Convertir a RGB
            imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
            
            # Detectar cara usando OpenCV (más rápido que MediaPipe)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                # Tomar la cara más grande
                face = max(faces, key=lambda x: x[2] * x[3])
                x, y, w, h = face
                
                # Recortar cara
                cara_recortada = imagen_rgb[y:y+h, x:x+w]
                
                # Remover fondo usando OpenCV (más rápido que rembg)
                hsv = cv2.cvtColor(cara_recortada, cv2.COLOR_RGB2HSV)
                lower_skin = np.array([0, 20, 70], dtype=np.uint8)
                upper_skin = np.array([20, 255, 255], dtype=np.uint8)
                mask = cv2.inRange(hsv, lower_skin, upper_skin)
                
                # Aplicar morfología para limpiar la máscara
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                # Aplicar la máscara
                resultado = cara_recortada.copy()
                resultado[mask == 0] = [0, 0, 0, 0]  # Transparente
                
                # Convertir a PIL
                imagen_pil = Image.fromarray(resultado)
                return imagen_pil
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error procesando imagen: {e}")
            return None
    
    def mover_imagen_usada(self, ruta_imagen):
        """Mueve la imagen usada a una subcarpeta para evitar reutilización"""
        try:
            # Crear subcarpeta para imágenes usadas
            carpeta_usadas = self.imagenes_mujeres_path / 'usadas'
            carpeta_usadas.mkdir(exist_ok=True)
            
            # Mover imagen y su archivo JSON correspondiente
            imagen_path = Path(ruta_imagen)
            json_path = imagen_path.with_suffix('.json')
            
            # Verificar que la imagen existe antes de moverla
            if not imagen_path.exists():
                print(f"⚠️ Imagen no encontrada: {imagen_path}")
                return False
            
            # Mover imagen
            destino_imagen = carpeta_usadas / imagen_path.name
            shutil.move(str(imagen_path), str(destino_imagen))
            print(f"📁 Imagen movida: {imagen_path.name} → usadas/")
            
            # Mover JSON si existe
            if json_path.exists():
                destino_json = carpeta_usadas / json_path.name
                shutil.move(str(json_path), str(destino_json))
                print(f"📁 JSON movido: {json_path.name} → usadas/")
            
            return True
            
        except Exception as e:
            print(f"❌ Error moviendo imagen: {e}")
            return False
    
    def generar_firma_personalizada(self, nombre, apellido):
        """
        Genera una firma personalizada realista basada en nombre y apellido
        
        COMBINA MÚLTIPLES MÉTODOS:
        - Método 1: Estilos (formal, elegante, tradicional, moderno, artístico)
        - Método 3: Combinaciones de nombres (1-2 nombres, 1-2 apellidos)
        - Método 5: Variaciones de puntuación (con/sin puntos, guiones, espacios)
        - Método 6: Elementos gráficos (subrayado, cursiva, símbolos)
        - Método 7: Garabatos (trazos continuos, curvas, bucles)
        
        EVITA firmas con solo iniciales (A. A.) - debe ser más elaborada
        """
        # Limpiar y formatear nombres
        nombre_limpio = nombre.strip().title()
        apellido_limpio = apellido.strip().title()
        
        # Obtener iniciales
        inicial_nombre = nombre_limpio[0]
        inicial_apellido = apellido_limpio[0]
        
        # MÉTODO 1: ESTILOS DE FIRMA
        estilos = {
            'formal': self._generar_firma_formal,
            'elegante': self._generar_firma_elegante,
            'tradicional': self._generar_firma_tradicional,
            'moderno': self._generar_firma_moderno,
            'artistico': self._generar_firma_artistico,
            'garabato': self._generar_firma_garabato
        }
        
        # Seleccionar estilo aleatorio
        estilo_seleccionado = random.choice(list(estilos.keys()))
        
        # Generar firma según el estilo seleccionado
        firma = estilos[estilo_seleccionado](nombre_limpio, apellido_limpio, inicial_nombre, inicial_apellido)
        
        # Asegurar que no sea muy larga (máximo 30 caracteres para garabatos)
        if len(firma) > 30:
            firma = firma[:30]
        
        # Asegurar que no sea muy corta (mínimo 4 caracteres para evitar solo iniciales)
        if len(firma) < 4:
            firma = f"{inicial_nombre}. {apellido_limpio}"
        
        # VERIFICACIÓN FINAL: Evitar firmas con solo iniciales
        if firma.strip() in [f"{inicial_nombre}. {inicial_apellido}.", f"{inicial_nombre} {inicial_apellido}"]:
            # Si solo tiene iniciales, usar patrón más elaborado
            firma = f"{inicial_nombre}. {apellido_limpio}"
        
        # NUEVO: Seleccionar fuente óptima según la longitud de la firma
        fuente_optima = self.seleccionar_fuente_por_longitud(firma)
        
        return firma, fuente_optima
    
    def _generar_firma_formal(self, nombre, apellido, inicial_nombre, inicial_apellido):
        """Estilo formal: Inicial + Apellido completo - MÁS DE 20 VARIACIONES"""
        patrones = [
            # Patrones formales básicos
            f"{inicial_nombre}. {apellido}",
            f"{inicial_nombre}. {apellido}",
            f"{inicial_nombre}. {apellido}",
            f"{inicial_nombre}. {apellido[:4]}",
            f"{inicial_nombre}. {apellido[:3]}",
            f"{inicial_nombre}. {apellido[:5]}",
            f"{inicial_nombre}. {apellido[:2]}",
            
            # Variaciones con espacios
            f"{inicial_nombre} {apellido}",
            f"{inicial_nombre} {apellido[:4]}",
            f"{inicial_nombre} {apellido[:3]}",
            
            # Variaciones con guiones
            f"{inicial_nombre}-{apellido}",
            f"{inicial_nombre}-{apellido[:4]}",
            f"{inicial_nombre}-{apellido[:3]}",
            
            # Variaciones con apellido primero
            f"{apellido} {inicial_nombre}.",
            f"{apellido[:4]} {inicial_nombre}.",
            f"{apellido[:3]} {inicial_nombre}.",
            
            # Variaciones mixtas
            f"{inicial_nombre}.{apellido[:2]}",
            f"{inicial_nombre}{apellido[:2]}",
            f"{inicial_nombre}.{apellido[:3]}",
            f"{inicial_nombre}{apellido[:3]}",
            
            # Variaciones con nombres cortos
            f"{nombre[:2]}. {apellido}",
            f"{nombre[:3]}. {apellido}",
            f"{nombre[:4]}. {apellido}"
        ]
        return random.choice(patrones)
    
    def _generar_firma_elegante(self, nombre, apellido, inicial_nombre, inicial_apellido):
        """Estilo elegante: Nombre completo + Inicial apellido - MÁS DE 25 VARIACIONES"""
        patrones = [
            # Patrones elegantes básicos
            f"{nombre} {inicial_apellido}.",
            f"{nombre} {inicial_apellido}.",
            f"{nombre} {inicial_apellido}.",
            f"{nombre[:4]} {inicial_apellido}.",
            f"{nombre[:3]} {inicial_apellido}.",
            f"{nombre[:5]} {inicial_apellido}.",
            f"{nombre[:2]} {inicial_apellido}.",
            
            # Variaciones con espacios
            f"{nombre} {inicial_apellido}",
            f"{nombre[:4]} {inicial_apellido}",
            f"{nombre[:3]} {inicial_apellido}",
            
            # Variaciones con guiones
            f"{nombre}-{inicial_apellido}.",
            f"{nombre[:4]}-{inicial_apellido}.",
            f"{nombre[:3]}-{inicial_apellido}.",
            
            # Variaciones con apellido primero
            f"{inicial_apellido}. {nombre}",
            f"{inicial_apellido}. {nombre[:4]}",
            f"{inicial_apellido}. {nombre[:3]}",
            
            # Variaciones mixtas
            f"{nombre}.{inicial_apellido}",
            f"{nombre}{inicial_apellido}",
            f"{nombre[:4]}.{inicial_apellido}",
            f"{nombre[:3]}.{inicial_apellido}",
            
            # Variaciones con nombres cortos
            f"{nombre[:2]} {inicial_apellido}.",
            f"{nombre[:3]} {inicial_apellido}.",
            f"{nombre[:4]} {inicial_apellido}.",
            
            # Variaciones creativas
            f"{nombre} {apellido[:2]}",
            f"{nombre[:4]} {apellido[:2]}",
            f"{nombre[:3]} {apellido[:2]}"
        ]
        return random.choice(patrones)
    
    def _generar_firma_tradicional(self, nombre, apellido, inicial_nombre, inicial_apellido):
        """Estilo tradicional: Apellido + Inicial nombre - MÁS DE 25 VARIACIONES"""
        patrones = [
            # Patrones tradicionales básicos
            f"{apellido} {inicial_nombre}.",
            f"{apellido} {inicial_nombre}.",
            f"{apellido} {inicial_nombre}.",
            f"{apellido[:4]} {inicial_nombre}.",
            f"{apellido[:3]} {inicial_nombre}.",
            f"{apellido[:5]} {inicial_nombre}.",
            f"{apellido[:2]} {inicial_nombre}.",
            
            # Variaciones con espacios
            f"{apellido} {inicial_nombre}",
            f"{apellido[:4]} {inicial_nombre}",
            f"{apellido[:3]} {inicial_nombre}",
            
            # Variaciones con guiones
            f"{apellido}-{inicial_nombre}.",
            f"{apellido[:4]}-{inicial_nombre}.",
            f"{apellido[:3]}-{inicial_nombre}.",
            
            # Variaciones con nombre primero
            f"{inicial_nombre}. {apellido}",
            f"{inicial_nombre}. {apellido[:4]}",
            f"{inicial_nombre}. {apellido[:3]}",
            
            # Variaciones mixtas
            f"{apellido}.{inicial_nombre}",
            f"{apellido}{inicial_nombre}",
            f"{apellido[:4]}.{inicial_nombre}",
            f"{apellido[:3]}.{inicial_nombre}",
            
            # Variaciones con apellidos cortos
            f"{apellido[:2]} {inicial_nombre}.",
            f"{apellido[:3]} {inicial_nombre}.",
            f"{apellido[:4]} {inicial_nombre}.",
            
            # Variaciones creativas
            f"{apellido} {nombre[:2]}",
            f"{apellido[:4]} {nombre[:2]}",
            f"{apellido[:3]} {nombre[:2]}"
        ]
        return random.choice(patrones)
    
    def _generar_firma_moderno(self, nombre, apellido, inicial_nombre, inicial_apellido):
        """Estilo moderno: Combinaciones abreviadas - MÁS DE 30 VARIACIONES"""
        patrones = [
            # Patrones modernos básicos
            f"{nombre} {apellido[:4]}",
            f"{nombre[:4]} {apellido}",
            f"{inicial_nombre}. {apellido[:3]}",
            f"{nombre[:3]} {apellido[:3]}",
            f"{inicial_nombre}{apellido[:2]}",
            f"{nombre[:2]}{apellido[:2]}",
            
            # Variaciones con diferentes longitudes
            f"{nombre} {apellido[:3]}",
            f"{nombre} {apellido[:5]}",
            f"{nombre[:3]} {apellido}",
            f"{nombre[:5]} {apellido}",
            f"{nombre[:2]} {apellido[:4]}",
            f"{nombre[:4]} {apellido[:2]}",
            
            # Variaciones con espacios
            f"{nombre} {apellido[:2]}",
            f"{nombre[:2]} {apellido}",
            f"{nombre[:3]} {apellido[:2]}",
            f"{nombre[:2]} {apellido[:3]}",
            
            # Variaciones con guiones
            f"{nombre}-{apellido[:3]}",
            f"{nombre[:3]}-{apellido}",
            f"{nombre[:2]}-{apellido[:2]}",
            f"{nombre[:4]}-{apellido[:2]}",
            
            # Variaciones con puntos
            f"{nombre}.{apellido[:3]}",
            f"{nombre[:3]}.{apellido}",
            f"{nombre[:2]}.{apellido[:2]}",
            f"{nombre[:4]}.{apellido[:2]}",
            
            # Variaciones sin separadores
            f"{nombre}{apellido[:3]}",
            f"{nombre[:3]}{apellido}",
            f"{nombre[:2]}{apellido[:2]}",
            f"{nombre[:4]}{apellido[:2]}",
            
            # Variaciones creativas
            f"{apellido[:2]} {nombre[:2]}",
            f"{apellido[:3]} {nombre[:3]}",
            f"{apellido[:4]} {nombre[:2]}",
            f"{apellido[:2]} {nombre[:4]}"
        ]
        return random.choice(patrones)
    
    def _generar_firma_artistico(self, nombre, apellido, inicial_nombre, inicial_apellido):
        """Estilo artístico: Con elementos gráficos naturales - MÁS DE 35 VARIACIONES"""
        patrones = [
            # Estilos artísticos naturales básicos
            f"{nombre} {apellido}",
            f"{inicial_nombre}. {apellido}",
            f"{nombre} {inicial_apellido}.",
            f"{inicial_nombre}. {apellido[:4]}",
            f"{nombre[:4]} {apellido}",
            f"{nombre} {apellido[:3]}",
            f"{inicial_nombre}. {apellido[:3]}",
            f"{nombre[:3]} {apellido[:3]}",
            f"{inicial_nombre}{apellido[:2]}",
            f"{nombre[:2]}{apellido[:2]}",
            f"{apellido} {inicial_nombre}.",
            f"{apellido[:4]} {inicial_nombre}.",
            
            # Variaciones con diferentes longitudes
            f"{nombre} {apellido[:2]}",
            f"{nombre[:2]} {apellido}",
            f"{nombre[:3]} {apellido[:2]}",
            f"{nombre[:2]} {apellido[:3]}",
            f"{nombre[:5]} {apellido}",
            f"{nombre} {apellido[:5]}",
            
            # Variaciones con espacios
            f"{nombre} {apellido[:4]}",
            f"{nombre[:4]} {apellido}",
            f"{nombre[:3]} {apellido[:4]}",
            f"{nombre[:4]} {apellido[:3]}",
            
            # Variaciones con guiones
            f"{nombre}-{apellido}",
            f"{nombre[:3]}-{apellido[:3]}",
            f"{nombre[:2]}-{apellido[:2]}",
            f"{nombre[:4]}-{apellido[:2]}",
            
            # Variaciones con puntos
            f"{nombre}.{apellido}",
            f"{nombre[:3]}.{apellido[:3]}",
            f"{nombre[:2]}.{apellido[:2]}",
            f"{nombre[:4]}.{apellido[:2]}",
            
            # Variaciones sin separadores
            f"{nombre}{apellido}",
            f"{nombre[:3]}{apellido[:3]}",
            f"{nombre[:2]}{apellido[:2]}",
            f"{nombre[:4]}{apellido[:2]}",
            
            # Variaciones creativas
            f"{apellido[:2]} {nombre[:2]}",
            f"{apellido[:3]} {nombre[:3]}",
            f"{apellido[:4]} {nombre[:2]}",
            f"{apellido[:2]} {nombre[:4]}",
            f"{apellido[:5]} {nombre[:2]}",
            f"{apellido[:2]} {nombre[:5]}"
        ]
        return random.choice(patrones)
    
    def _generar_firma_garabato(self, nombre, apellido, inicial_nombre, inicial_apellido):
        """Estilo garabato: Trazos continuos naturales, sin símbolos artificiales - MÁS DE 40 VARIACIONES"""
        patrones = [
            # Garabatos naturales sin símbolos artificiales
            f"{nombre} {apellido}",
            f"{inicial_nombre}. {apellido}",
            f"{nombre} {inicial_apellido}.",
            f"{inicial_nombre}. {apellido[:4]}",
            f"{nombre[:4]} {apellido}",
            f"{nombre} {apellido[:3]}",
            f"{inicial_nombre}. {apellido[:3]}",
            f"{nombre[:3]} {apellido[:3]}",
            f"{inicial_nombre}{apellido[:2]}",
            f"{nombre[:2]}{apellido[:2]}",
            f"{apellido} {inicial_nombre}.",
            f"{apellido[:4]} {inicial_nombre}.",
            
            # Variaciones con diferentes longitudes
            f"{nombre} {apellido[:2]}",
            f"{nombre[:2]} {apellido}",
            f"{nombre[:3]} {apellido[:2]}",
            f"{nombre[:2]} {apellido[:3]}",
            f"{nombre[:5]} {apellido}",
            f"{nombre} {apellido[:5]}",
            
            # Variaciones con espacios
            f"{nombre} {apellido[:4]}",
            f"{nombre[:4]} {apellido}",
            f"{nombre[:3]} {apellido[:4]}",
            f"{nombre[:4]} {apellido[:3]}",
            
            # Variaciones con guiones
            f"{nombre}-{apellido}",
            f"{nombre[:3]}-{apellido[:3]}",
            f"{nombre[:2]}-{apellido[:2]}",
            f"{nombre[:4]}-{apellido[:2]}",
            
            # Variaciones con puntos
            f"{nombre}.{apellido}",
            f"{nombre[:3]}.{apellido[:3]}",
            f"{nombre[:2]}.{apellido[:2]}",
            f"{nombre[:4]}.{apellido[:2]}",
            
            # Variaciones sin separadores
            f"{nombre}{apellido}",
            f"{nombre[:3]}{apellido[:3]}",
            f"{nombre[:2]}{apellido[:2]}",
            f"{nombre[:4]}{apellido[:2]}",
            
            # Variaciones creativas
            f"{apellido[:2]} {nombre[:2]}",
            f"{apellido[:3]} {nombre[:3]}",
            f"{apellido[:4]} {nombre[:2]}",
            f"{apellido[:2]} {nombre[:4]}",
            f"{apellido[:5]} {nombre[:2]}",
            f"{apellido[:2]} {nombre[:5]}",
            
            # Variaciones con nombres cortos
            f"{nombre[:2]} {apellido[:2]}",
            f"{nombre[:3]} {apellido[:2]}",
            f"{nombre[:2]} {apellido[:3]}",
            f"{nombre[:4]} {apellido[:2]}",
            f"{nombre[:2]} {apellido[:4]}"
        ]
        return random.choice(patrones)
    
    def seleccionar_fuente_por_longitud(self, texto_firma):
        """
        Selecciona la fuente óptima según la longitud del texto de la firma
        
        CATEGORÍAS:
        - Cortas (1-8 caracteres): Fuentes que se ven bien con pocos caracteres
        - Medianas (9-15 caracteres): Balance perfecto de legibilidad  
        - Largas (16+ caracteres): Fuentes que manejan textos extensos
        """
        longitud = len(texto_firma)
        disponibles = set(self.validador_fuentes.fuentes_disponibles)

        # Preferencias del usuario por longitud:
        # - White Sign (DemoVersion).otf y Lovtony Script.ttf → corto, medio y largo
        # - Amsterdam.ttf → corto y medio
        # - Todas las demás (del set disponible) → solo corto
        preferidas_corto = [
            "White Sign (DemoVersion).otf",
            "Lovtony Script.ttf",
            "Amsterdam.ttf",
            # Resto solo-corto (si están disponibles)
            "BrittanySignature.ttf",
            "Autography.otf",
            "Breathing Personal Use Only.ttf",
            "Thesignature.ttf",
            "Amalfi Coast.ttf",
            "South Brittany FREE.otf",
            "Royalty Free.ttf",
            "RetroSignature.otf"
        ]
        preferidas_medio = [
            "White Sign (DemoVersion).otf",
            "Lovtony Script.ttf",
            "Amsterdam.ttf"
        ]
        preferidas_largo = [
            "White Sign (DemoVersion).otf",
            "Lovtony Script.ttf"
        ]

        if longitud <= 8:
            # Firma corta seleccionada
            orden = preferidas_corto
        elif longitud <= 15:
            # Firma mediana seleccionada
            orden = preferidas_medio
        else:
            # Firma larga seleccionada
            orden = preferidas_largo

        # Elegir la primera preferida que esté disponible
        for fuente in orden:
            if fuente in disponibles:
                # Fuente seleccionada
                return fuente

        # Fallback: BrittanySignature si está disponible
        if "BrittanySignature.ttf" in disponibles:
            # Fallback a BrittanySignature
            return "BrittanySignature.ttf"

        # Último recurso: escoger cualquiera disponible (evita Arial para firmas)
        if disponibles:
            candidato = sorted(disponibles)[0]
            print(f"   ⚠️ Sin coincidencias en preferencias, usando {candidato}")
            return candidato

        # Si no hay ninguna disponible, retornar Brittany para que el otro módulo intente fallback
        print("   ❌ No hay fuentes disponibles detectadas, devolviendo BrittanySignature.ttf como marcador")
        return "BrittanySignature.ttf"
    
    def generar_cedula_venezolana(self):
        """Genera una cédula venezolana simulada más realista"""
        # Las cédulas venezolanas tienen 8 dígitos
        # Patrones más realistas basados en rangos de años
        año_actual = datetime.now().year
        
        # Generar cédula basada en rango de años (más realista)
        if año_actual >= 2020:
            # Cédulas más recientes (mayor número)
            cedula = random.randint(20000000, 99999999)
        elif año_actual >= 2010:
            # Cédulas de rango medio
            cedula = random.randint(15000000, 29999999)
        else:
            # Cédulas más antiguas
            cedula = random.randint(8000000, 19999999)
        
        return str(cedula)
    
    def generar_nombre_archivo_pasaporte(self, correo):
        """Genera nombre de archivo basado en correo electrónico completo"""
        if pd.isna(correo) or correo == '':
            return f"pasaporte_{random.randint(100000, 999999)}.png"
        
        # Limpiar correo y crear nombre de archivo
        correo_limpio = str(correo).lower().strip()
        
        # Usar el correo completo, no solo la parte antes del @
        # Limpiar caracteres no válidos para nombres de archivo
        nombre_archivo = re.sub(r'[^\w\-_.@]', '_', correo_limpio)
        
        # Limitar longitud (máximo 50 caracteres para el nombre completo)
        if len(nombre_archivo) > 50:
            nombre_archivo = nombre_archivo[:50]
        
        return f"{nombre_archivo}.png"
    
    def generar_pasaporte_visual_optimizado(self, datos_pasaporte):
        """OPTIMIZACIÓN: Genera pasaporte usando recursos reservados reutilizables"""
        if ScriptMaestroIntegrado is None:
            return None
        
        try:
            # OPTIMIZACIÓN: Cargar ScriptMaestroIntegrado solo cuando se necesite
            script_maestro = self._cargar_script_maestro_lazy()
            if script_maestro is None:
                return None
            
            # Extraer datos necesarios
            ruta_foto = datos_pasaporte.get('ruta_foto')
            numero_pasaporte = datos_pasaporte.get('numero_pasaporte')
            nombre_archivo = datos_pasaporte.get('nombre_archivo', 'pasaporte.png')
            
            if not ruta_foto or not numero_pasaporte:
                return None
            
            # Verificar que la imagen existe
            if not Path(ruta_foto).exists():
                return None
            
            # LIMPIAR datos previos y configurar los datos en el script maestro
            script_maestro.datos_pasaporte = {}  # Limpiar datos previos
            script_maestro.datos_pasaporte = datos_pasaporte
            
            # Generar el pasaporte usando recursos reservados reutilizables
            if self.silencioso:
                with open(os.devnull, 'w') as _null, contextlib.redirect_stdout(_null):
                    resultado = script_maestro.generar_gafete_integrado(
                        ruta_foto=ruta_foto,
                        numero_pasaporte=numero_pasaporte
                    )
            else:
                resultado = script_maestro.generar_gafete_integrado(
                    ruta_foto=ruta_foto,
                    numero_pasaporte=numero_pasaporte
                )
            
            if resultado:
                # Guardar con el nombre basado en correo completo
                ruta_destino = self.pasaportes_visuales_path / nombre_archivo
                resultado.save(ruta_destino)
                
                # Liberar solo la imagen resultante, mantener recursos reservados
                del resultado
                
                return str(ruta_destino)
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error en generación de pasaporte visual: {e}")
            return None

    def generar_pasaporte_visual(self, datos_pasaporte):
        """Método legacy - redirige al optimizado"""
        return self.generar_pasaporte_visual_optimizado(datos_pasaporte)
    
    def procesar_registro(self, registro):
        """Procesa un registro individual y genera los datos del pasaporte"""
        # Procesamiento silencioso
        
        # Verificar y liberar memoria si es necesario
        self.gestor_memoria.incrementar_contador()
        
        # Limpiar y procesar datos básicos
        primer_nombre = self.limpiar_texto(registro.get('PRIMER_NOMBRE', ''))
        segundo_nombre = self.limpiar_texto(registro.get('SEGUNDO_NOMBRE', ''))
        primer_apellido = self.limpiar_texto(registro.get('PRIMER_APELLIDO', ''))
        segundo_apellido = self.limpiar_texto(registro.get('SEGUNDO_APELLIDO', ''))
        genero = registro.get('GENERO', 'F')
        fecha_nacimiento = registro.get('FECHA_NACIMIENTO')
        
        # Calcular edad
        edad = self.calcular_edad(fecha_nacimiento)
        if edad is None:
            edad = 25  # Edad por defecto
        
        # Generar datos del pasaporte
        numero_pasaporte = str(self.generar_numero_pasaporte())
        
        # Construir nombre completo (manejar 1-2 nombres)
        nombre_completo = primer_nombre
        if segundo_nombre and segundo_nombre.strip():
            nombre_completo += f" {segundo_nombre}"
        
        # Construir apellido completo (manejar 1-2 apellidos)
        apellido_completo = primer_apellido
        if segundo_apellido and segundo_apellido.strip():
            apellido_completo += f" {segundo_apellido}"
        
        # Generar datos adicionales
        lugar_nacimiento = self.seleccionar_lugar_nacimiento()
        fecha_emision = self.generar_fecha_emision(fecha_nacimiento)
        fecha_vencimiento = self.generar_fecha_vencimiento(fecha_emision)
        codigo_verificacion = self.generar_codigo_verificacion(fecha_nacimiento)
        
        # Generar códigos MRZ
        mrz_linea1 = self.generar_mrz_linea1(nombre_completo, apellido_completo, numero_pasaporte)
        mrz_linea2 = self.generar_mrz_linea2(numero_pasaporte, fecha_nacimiento, genero)
        
        # Buscar imagen correspondiente
        ruta_imagen = self.buscar_imagen_por_edad(edad, genero)
        
        # Generar firma personalizada usando nombres completos
        firma_personalizada, fuente_optima = self.generar_firma_personalizada(nombre_completo, apellido_completo)
        
        # Generar nombre de archivo basado en correo
        nombre_archivo = self.generar_nombre_archivo_pasaporte(registro.get('CORREO', ''))
        
        # Construir datos completos del pasaporte
        # IMPORTANTE: El mismo número de pasaporte debe usarse en todos los campos
        datos_pasaporte = {
            'ruta_foto': str(ruta_imagen) if ruta_imagen else None,
            'numero_pasaporte_1': numero_pasaporte,  # Para N°PASAPORTE1 (vertical)
            'numero_pasaporte_2': numero_pasaporte,  # Para N°PASAPORTE2 (vertical)
            'numero_pasaporte': numero_pasaporte,     # Para campo horizontal estándar
            'tipo': 'P',
            'pais_emisor': 'VEN',
            'nombre_completo': nombre_completo,
            'apellido_completo': apellido_completo,
            'fecha_nacimiento': self.formatear_fecha_pasaporte(fecha_nacimiento),
            'cedula': self.generar_cedula_venezolana(),  # Cédula venezolana simulada
            'fecha_emision': fecha_emision,
            'fecha_vencimiento': fecha_vencimiento,
            'sexo': genero,
            'nacionalidad': 'VENEZOLANA',
            'lugar_nacimiento': lugar_nacimiento,
            'codigo_verificacion': codigo_verificacion,
            'firma': firma_personalizada,
            'fuente_firma': fuente_optima,
            'mrz_linea1': mrz_linea1,
            'mrz_linea2': mrz_linea2,
            'edad': edad,
            'correo_original': registro.get('CORREO', ''),
            'imagen_usada': str(ruta_imagen) if ruta_imagen else None,
            'nombre_archivo': nombre_archivo
        }

        # Si no hay imagen adecuada, omitir generación de PNG y registrar motivo
        if ruta_imagen is None:
            datos_pasaporte['estado'] = 'omitido'
            datos_pasaporte['motivo_no_generado'] = f"Sin imagen adecuada para edad {edad} (sin exacta ni en rango)"
            try:
                with open(self.archivo_errores, 'a') as f:
                    f.write(f"{datetime.now().isoformat()} - Registro omitido por falta de imagen adecuada (edad {edad})\n")
            except Exception:
                pass
            return datos_pasaporte
        
        # Generar pasaporte visual
        ruta_pasaporte_visual = self.generar_pasaporte_visual(datos_pasaporte)
        if ruta_pasaporte_visual:
            datos_pasaporte['pasaporte_visual'] = ruta_pasaporte_visual
        
        # OPTIMIZACIÓN: Liberación de memoria más frecuente para 20K+ registros
        memoria_actual = self.gestor_memoria.verificar_memoria()
        if memoria_actual > 80:  # Más frecuente para evitar colgadas
            self.gestor_memoria.liberar_memoria(forzar=True)
        
        return datos_pasaporte
    
    def generar_pasaportes_masivos(self, limite=None, archivo_csv=None):
        """Genera pasaportes masivos de forma simple y estable"""
        print("🎯 GENERADOR MASIVO DE PASAPORTES VENEZOLANOS")
        print("=" * 50)
        
        # Limpieza previa
        self._limpieza_previa()
        
        # Validar fuentes
        if not self.validador_fuentes.verificar_fuentes():
            print("❌ ERROR: Faltan fuentes requeridas")
            self.validador_fuentes.mostrar_estado_fuentes()
            return False
        
        # Cargar datos del CSV
        df = self.cargar_datos_csv(archivo_csv)
        if df is None:
            return False
        
        # Inicializar sistema de progreso simple
        self.progreso = ProgresoSimple()
        
        # Procesar registros
        registros_procesados = []
        total_registros = len(df) if limite is None else min(limite, len(df))
        
        print(f"📊 Procesando {total_registros} registros...")
        
        for idx, registro in df.iterrows():
            if limite and idx >= limite:
                break
            
            try:
                # Procesar registro de forma simple
                datos_pasaporte = self._procesar_registro_simple(idx, registro)
                if datos_pasaporte:
                    registros_procesados.append(datos_pasaporte)
                
                # Mostrar progreso cada 10 registros
                if (idx + 1) % 10 == 0:
                    generados = sum(1 for r in registros_procesados if r.get('estado') == 'generado')
                    omitidos = sum(1 for r in registros_procesados if r.get('estado') == 'omitido')
                    print(f"📊 Progreso: {idx + 1}/{total_registros} - Generados: {generados}, Omitidos: {omitidos}")
                
            except Exception as e:
                print(f"❌ Error en registro {idx + 1}: {e}")
                continue
        
        # Guardar resultados
        self.guardar_datos_procesados(registros_procesados)
        
        # Eliminar CSV procesado para evitar confusión
        self.eliminar_csv_procesado()
        
        # Resumen final
        generados = sum(1 for r in registros_procesados if r.get('estado') == 'generado')
        omitidos = sum(1 for r in registros_procesados if r.get('estado') == 'omitido')
        
        print(f"\n🎉 PROCESAMIENTO COMPLETADO")
        print(f"📊 Total procesados: {len(registros_procesados)}")
        print(f"✅ Pasaportes generados: {generados}")
        print(f"⚠️ Registros omitidos: {omitidos}")
        
        return True
    
    def guardar_datos_procesados(self, registros_procesados):
        """Guarda los datos procesados en archivos JSON y Excel"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar como JSON
        json_path = self.output_path / f'pasaportes_procesados_{timestamp}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(registros_procesados, f, ensure_ascii=False, indent=2, default=str)
        
        # Guardar como Excel
        excel_path = self.output_path / f'pasaportes_procesados_{timestamp}.xlsx'
        df_procesados = pd.DataFrame(registros_procesados)
        df_procesados.to_excel(excel_path, index=False)

        # Si hay CSV de entrada, anexar resultados por registro (estado, imagen usada, salida)
        try:
            if self.csv_path_used and Path(self.csv_path_used).exists():
                df_in = pd.read_csv(self.csv_path_used, dtype=str, keep_default_na=False)
                df_out = pd.DataFrame(registros_procesados)
                # Asegurar columnas de resultado
                if 'pasaporte_visual' not in df_out.columns:
                    df_out['pasaporte_visual'] = ''
                if 'estado' not in df_out.columns:
                    df_out['estado'] = df_out['pasaporte_visual'].apply(lambda x: 'generado' if str(x) else 'omitido')
                if 'motivo_no_generado' not in df_out.columns:
                    df_out['motivo_no_generado'] = ''
                # Selección de columnas útiles
                cols_result = [
                    'correo_original', 'numero_pasaporte', 'ruta_foto', 'imagen_usada',
                    'pasaporte_visual', 'estado', 'motivo_no_generado'
                ]
                for c in cols_result:
                    if c not in df_out.columns:
                        df_out[c] = ''
                # Concatenar lógicamente (mismo orden de procesamiento)
                df_in_result = pd.concat([df_in.reset_index(drop=True), df_out[cols_result].reset_index(drop=True)], axis=1)
                # Agregar fila meta al inicio con total de registros del CSV y timestamp
                # Asegurar columnas meta
                for meta_col in ['meta_total_registros', 'meta_timestamp']:
                    if meta_col not in df_in_result.columns:
                        df_in_result[meta_col] = ''
                # Construir fila meta vacía con columnas del resultado
                meta_row = {c: '' for c in df_in_result.columns}
                meta_row['meta_total_registros'] = str(len(df_in_result))
                meta_row['meta_timestamp'] = timestamp
                df_meta = pd.DataFrame([meta_row])
                final_df = pd.concat([df_meta, df_in_result], ignore_index=True)
                # Escribir un CSV resultado en carpeta separada para evitar confusión
                csv_result = self.output_path / f"{Path(self.csv_path_used).stem}_RESULT_{timestamp}.csv"
                final_df.to_csv(csv_result, index=False, encoding='utf-8')
                print(f"💾 Resultados por registro guardados en: {csv_result.name}")
        except Exception as e:
            print(f"⚠️ No se pudo anexar resultados al CSV: {e}")
        
        print(f"💾 Datos guardados:")
        print(f"   📄 JSON: {json_path}")
        print(f"   📊 Excel: {excel_path}")
    
    def eliminar_csv_procesado(self):
        """Elimina el archivo CSV después de procesarlo para evitar confusión"""
        if self.csv_path_used and Path(self.csv_path_used).exists():
            try:
                # Crear backup antes de eliminar
                backup_path = self.csv_path_used.with_suffix('.csv.backup')
                shutil.copy2(self.csv_path_used, backup_path)
                print(f"💾 Backup creado: {backup_path.name}")
                
                # Eliminar archivo CSV original
                Path(self.csv_path_used).unlink()
                print(f"🗑️ CSV eliminado: {Path(self.csv_path_used).name}")
                print("✅ Archivo CSV eliminado para evitar confusión")
                
                return True
            except Exception as e:
                print(f"⚠️ Error eliminando CSV: {e}")
                return False
        return True
    
    def mostrar_archivos_generados(self):
        """Muestra qué archivos se van a generar durante el proceso"""
        print("📋 ARCHIVOS QUE SE GENERARÁN:")
        print("=" * 50)
        
        # Archivos principales (pasaportes)
        print("🎯 ARCHIVOS PRINCIPALES (PASAPORTES):")
        print(f"   📁 Carpeta: {self.pasaportes_visuales_path}")
        print(f"   🖼️ Archivos: pasaporte_[correo].png (uno por registro)")
        print(f"   📝 Ejemplo: pasaporte_juan.perez@email.com.png")
        
        # Archivos de datos
        print(f"\n📊 ARCHIVOS DE DATOS:")
        print(f"   📁 Carpeta: [ruta_csv]/resultados_pasaportes/")
        print(f"   📄 JSON: pasaportes_procesados_[timestamp].json")
        print(f"   📊 Excel: pasaportes_procesados_[timestamp].xlsx")
        print(f"   📋 CSV Resultado: [nombre_csv]_RESULT_[timestamp].csv")
        
        # Archivos de logs (si están habilitados)
        if GUARDAR_LOGS_ERRORES:
            print(f"\n📝 ARCHIVOS DE LOGS:")
            print(f"   📁 Carpeta: {self.base_path / 'OUTPUT' / 'logs'}")
            print(f"   📄 Progreso: progreso_actual.json")
            print(f"   📄 Errores: errores.log")
            print(f"   📄 Ubicación CSV: ultima_ubicacion_csv.json")
        
        # Archivos temporales
        print(f"\n🗂️ ARCHIVOS TEMPORALES:")
        print(f"   📁 Carpeta: {self.base_path / 'OUTPUT' / 'temp'}")
        print(f"   🧹 Se limpian automáticamente")
        
        # Imágenes movidas
        print(f"\n📁 IMÁGENES PROCESADAS:")
        print(f"   📁 Carpeta: {self.imagenes_mujeres_path / 'usadas'}")
        print(f"   🖼️ Imágenes usadas se mueven aquí para evitar reutilización")
        
        print(f"\n✅ RESUMEN:")
        print(f"   🎯 Archivos importantes: Pasaportes PNG en {self.pasaportes_visuales_path}")
        print(f"   📊 Datos procesados: JSON, Excel, CSV en [ruta_csv]/resultados_pasaportes/")
        print(f"   🧹 Archivos temporales: Se limpian automáticamente")
        print(f"   📁 Carpeta CSV original: Se crea subcarpeta 'resultados_pasaportes' para archivos de salida")

    def verificar_preparacion_produccion(self):
        """Verifica que el sistema esté listo para producción"""
        print("🔍 VERIFICANDO PREPARACIÓN PARA PRODUCCIÓN")
        print("=" * 50)
        
        verificaciones = []
        
        # 1. Verificar configuración de límite de registros
        if LIMITE_REGISTROS is None:
            verificaciones.append(("✅ Límite de registros", "Configurado para procesar todos los registros"))
        else:
            verificaciones.append(("⚠️ Límite de registros", f"Limitado a {LIMITE_REGISTROS} registros (modo prueba)"))
        
        # 2. Verificar modo de producción
        if MODO_PRODUCCION:
            verificaciones.append(("✅ Modo de producción", "Activado"))
        else:
            verificaciones.append(("⚠️ Modo de producción", "Desactivado (modo desarrollo)"))
        
        # 3. Verificar configuración de memoria
        verificaciones.append(("✅ Configuración de memoria", f"Límite RAM: {MEMORIA_LIMITE_PORCENTAJE}%, VRAM: {VRAM_LIMITE_PORCENTAJE}%"))
        
        # 4. Verificar configuración de lotes
        verificaciones.append(("✅ Configuración de lotes", f"Tamaño: {TAMANO_LOTE_PRODUCCION}, Workers: {MAX_WORKERS_PARALELO}"))
        
        # 5. Verificar logging
        if LOGGING_DETALLADO:
            verificaciones.append(("⚠️ Logging", "Detallado activado (puede afectar rendimiento)"))
        else:
            verificaciones.append(("✅ Logging", "Mínimo (optimizado para rendimiento)"))
        
        # 6. Verificar fuentes
        if self.validador_fuentes.verificar_fuentes():
            verificaciones.append(("✅ Fuentes", "Todas las fuentes requeridas están disponibles"))
        else:
            verificaciones.append(("❌ Fuentes", "Faltan fuentes requeridas"))
        
        # 7. Verificar GPU
        if self.gpu_disponible:
            verificaciones.append(("✅ GPU", f"Detectada: {self.gpu_name}"))
        else:
            verificaciones.append(("⚠️ GPU", "No detectada, usando CPU"))
        
        # Mostrar resultados
        for estado, descripcion in verificaciones:
            print(f"   {estado}: {descripcion}")
        
        # Determinar si está listo para producción
        errores_criticos = sum(1 for estado, _ in verificaciones if estado.startswith("❌"))
        advertencias = sum(1 for estado, _ in verificaciones if estado.startswith("⚠️"))
        
        print(f"\n📊 RESUMEN:")
        print(f"   ✅ Verificaciones exitosas: {len(verificaciones) - errores_criticos - advertencias}")
        print(f"   ⚠️ Advertencias: {advertencias}")
        print(f"   ❌ Errores críticos: {errores_criticos}")
        
        if errores_criticos == 0:
            print(f"\n🎉 SISTEMA LISTO PARA PRODUCCIÓN")
            if advertencias > 0:
                print(f"⚠️ Se recomienda revisar las advertencias antes de proceder")
            return True
        else:
            print(f"\n❌ SISTEMA NO LISTO PARA PRODUCCIÓN")
            print(f"🔧 Corrija los errores críticos antes de continuar")
            return False
    
    def crear_lista_campos_requeridos(self):
        """Crea una lista detallada de todos los campos requeridos para el pasaporte"""
        print("\n📋 CAMPOS REQUERIDOS PARA EL PASAPORTE VENEZOLANO")
        print("=" * 60)
        
        campos_info = {
            'Datos del Excel': {
                'GENERO': 'Género (F/M)',
                'PRIMER_NOMBRE': 'Primer nombre',
                'SEGUNDO_NOMBRE': 'Segundo nombre (opcional)',
                'PRIMER_APELLIDO': 'Primer apellido', 
                'SEGUNDO_APELLIDO': 'Segundo apellido (opcional)',
                'FECHA_NACIMIENTO': 'Fecha de nacimiento (YYYY-MM-DD)',
                'CORREO': 'Correo electrónico'
            },
            'Datos Generados Automáticamente': {
                'numero_pasaporte': 'Número de pasaporte (aleatorio)',
                'lugar_nacimiento': 'Lugar de nacimiento (aleatorio de estados venezolanos)',
                'fecha_emision': 'Fecha de emisión (aleatoria últimos 5 años)',
                'fecha_vencimiento': 'Fecha de vencimiento (10 años después de emisión)',
                'cedula': 'Número de cédula (simulado)',
                'codigo_verificacion': 'Código de verificación (basado en fecha nacimiento)',
                'mrz_linea1': 'Código MRZ línea 1',
                'mrz_linea2': 'Código MRZ línea 2'
            },
            'Datos Fijos': {
                'tipo': 'Tipo de documento (P = Pasaporte)',
                'pais_emisor': 'País emisor (VEN)',
                'nacionalidad': 'Nacionalidad (VENEZOLANA)',
                'firma': 'Texto de firma (Firma Digital)'
            },
            'Datos de Imagen': {
                'ruta_foto': 'Ruta a la imagen de la persona (seleccionada por edad)',
                'edad_imagen': 'Edad extraída del nombre de la imagen'
            }
        }
        
        for categoria, campos in campos_info.items():
            print(f"\n📂 {categoria}:")
            for campo, descripcion in campos.items():
                print(f"   • {campo}: {descripcion}")
        
        return campos_info

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Generador Masivo de Pasaportes Venezolanos')
    parser.add_argument('--base-path', '-b', help='Ruta base del proyecto')
    parser.add_argument('--listar-campos', action='store_true', help='Listar campos requeridos')
    parser.add_argument('--verificar-produccion', action='store_true', help='Verificar preparación para producción')
    parser.add_argument('--mostrar-archivos', action='store_true', help='Mostrar qué archivos se generarán')
    parser.add_argument('--sin-gui', action='store_true', help='Ejecutar sin interfaz gráfica')
    
    args = parser.parse_args()
    
    # Inicializar generador
    generador = GeneradorPasaportesMasivo(args.base_path)
    
    if args.listar_campos:
        generador.crear_lista_campos_requeridos()
        return
    
    if args.verificar_produccion:
        generador.verificar_preparacion_produccion()
        return
    
    if args.mostrar_archivos:
        generador.mostrar_archivos_generados()
        return
    
    # Mostrar configuración actual
    print("⚙️ CONFIGURACIÓN ACTUAL:")
    print(f"   • Archivo CSV: {ARCHIVO_CSV if ARCHIVO_CSV else 'Selección automática'}")
    print(f"   • Límite registros: {LIMITE_REGISTROS if LIMITE_REGISTROS else 'Todos'}")
    print()
    
    # Mostrar mensaje de bienvenida mínimo
    print("🎯 GENERADOR MASIVO DE PASAPORTES VENEZOLANOS")
    
    # Generar pasaportes masivos usando configuración global
    exito = generador.generar_pasaportes_masivos(LIMITE_REGISTROS, ARCHIVO_CSV)
    
    if exito:
        print("\n🎉 ¡Generación masiva de pasaportes completada exitosamente!")
        print("📋 Revisa los archivos generados:")
        print("   📄 Datos procesados: OUTPUT/pasaportes_generados/")
        print("   🖼️ Pasaportes visuales: OUTPUT/pasaportes_visuales/")
        print("📁 Las imágenes usadas se movieron a Imagenes_Mujeres/usadas/")
    else:
        print("\n💥 Error en la generación masiva de pasaportes")
        sys.exit(1)

if __name__ == "__main__":
    main()
