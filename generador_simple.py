#!/usr/bin/env python3
"""
Generador Simple de Pasaportes - VERSIÓN ESTABLE
Elimina paralelismo y complejidad para evitar cuelgues
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
import gc
import psutil
from pathlib import Path
from PIL import Image
import argparse
import contextlib
import tkinter as tk
from tkinter import filedialog, messagebox

# Configuración GPU mínima
os.environ.setdefault('CUDA_VISIBLE_DEVICES', '0')
os.environ.setdefault('MEDIAPIPE_GPU', '0')  # Deshabilitar MediaPipe para estabilidad

# Importar el script maestro
sys.path.append(str(Path(__file__).parent / 'SCRIPTS'))
try:
    from script_maestro_integrado import ScriptMaestroIntegrado
except ImportError:
    print("️ No se pudo importar script_maestro_integrado.py")
    ScriptMaestroIntegrado = None

class GeneradorSimple:
    def __init__(self, base_path=None):
        """Inicializa el generador simple"""
        self.base_path = Path(base_path) if base_path else Path('/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL')
        self.data_path = self.base_path / 'DATA'
        self.output_path = self.base_path / 'OUTPUT' / 'pasaportes_generados'
        self.pasaportes_visuales_path = self.base_path / 'OUTPUT' / 'pasaportes_visuales'
        self.imagenes_mujeres_path = self.data_path / 'Imagenes_Mujeres'
        
        # Crear directorios
        self._crear_directorios()
        
        # Estados y capitales venezolanos
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
        
        # Rango de números de pasaporte
        self.rango_pasaporte_min = 100000000
        self.rango_pasaporte_max = 199999999
        
        # Vigencia del pasaporte (10 años)
        self.vigencia_pasaporte_anos = 10
        
        # Script maestro cache
        self.script_maestro_cache = None

    def _crear_directorios(self):
        """Crea directorios necesarios"""
        directorios = [
            self.output_path,
            self.pasaportes_visuales_path,
            self.imagenes_mujeres_path,
            self.imagenes_mujeres_path / 'usadas',
            self.base_path / 'OUTPUT' / 'logs'
        ]
        
        for directorio in directorios:
            directorio.mkdir(parents=True, exist_ok=True)

    def seleccionar_archivo_csv(self):
        """Selecciona archivo CSV"""
        root = tk.Tk()
        root.withdraw()
        
        archivo_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
            initialdir=str(self.output_path)
        )
        
        root.destroy()
        return archivo_path

    def cargar_datos_csv(self, archivo_path=None):
        """Carga datos desde CSV"""
        if archivo_path is None:
            archivo_path = self.seleccionar_archivo_csv()
            if not archivo_path:
                return None
        
        try:
            df = pd.read_csv(archivo_path, dtype=str, keep_default_na=False)
            print(f" Datos cargados: {len(df)} registros")
            return df
        except Exception as e:
            print(f" Error cargando CSV: {e}")
            return None

    def calcular_edad(self, fecha_nacimiento):
        """Calcula la edad"""
        if pd.isna(fecha_nacimiento):
            return None
        
        if isinstance(fecha_nacimiento, str):
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        elif isinstance(fecha_nacimiento, datetime):
            fecha_nacimiento = fecha_nacimiento.date()
        
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year
        
        if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
            edad -= 1
            
        return edad

    def limpiar_texto(self, texto):
        """Limpia y normaliza texto"""
        if pd.isna(texto) or texto == '':
            return ''
        
        texto = str(texto).strip()
        texto = texto.replace('á', 'A').replace('é', 'E').replace('í', 'I').replace('ó', 'O').replace('ú', 'U')
        texto = texto.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        texto = texto.replace('ñ', 'N').replace('Ñ', 'N')
        texto = texto.upper()
        texto = ' '.join(texto.split())
        
        return texto

    def generar_numero_pasaporte(self):
        """Genera número de pasaporte"""
        return random.randint(self.rango_pasaporte_min, self.rango_pasaporte_max)

    def seleccionar_lugar_nacimiento(self):
        """Selecciona lugar de nacimiento"""
        estado = random.choice(list(self.estados_venezuela.keys()))
        capital = self.estados_venezuela[estado]
        capital_norm = self.limpiar_texto(capital)
        return f"{capital_norm} VEN"

    def formatear_fecha_pasaporte(self, fecha):
        """Formatea fecha para pasaporte"""
        if pd.isna(fecha):
            return "01/ENE/ENE/2000"
        
        try:
            if isinstance(fecha, str):
                fecha = datetime.strptime(fecha, '%Y-%m-%d')
            elif isinstance(fecha, datetime):
                pass
            elif isinstance(fecha, date):
                fecha = datetime.combine(fecha, datetime.min.time())
        except Exception:
            return "01/ENE/ENE/2000"
        
        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }
        
        mes = meses[fecha.month]
        return f"{fecha.day:02d}/{mes}/{mes}/{fecha.year}"

    def generar_fecha_emision(self, fecha_nacimiento):
        """Genera fecha de emisión"""
        hoy = date.today()
        
        if isinstance(fecha_nacimiento, str):
            fecha_nac = datetime.strptime(fecha_nacimiento, '%Y-%m-%d').date()
        else:
            fecha_nac = fecha_nacimiento.date() if hasattr(fecha_nacimiento, 'date') else fecha_nacimiento
        
        fecha_18_anos = date(fecha_nac.year + 18, fecha_nac.month, fecha_nac.day)
        fecha_inicio_emision = max(fecha_18_anos, date(hoy.year - 5, 1, 1))
        
        if hoy.month > 3:
            fecha_limite = date(hoy.year, hoy.month - 3, hoy.day)
        else:
            fecha_limite = date(hoy.year - 1, hoy.month + 9, hoy.day)
        fecha_fin_emision = min(fecha_limite, hoy)
        
        if fecha_inicio_emision >= fecha_fin_emision:
            fecha_emision = date(hoy.year - 2, 1, 1)
        else:
            dias_diferencia = (fecha_fin_emision - fecha_inicio_emision).days
            dias_aleatorios = random.randint(0, dias_diferencia)
            fecha_emision = fecha_inicio_emision + pd.Timedelta(days=dias_aleatorios)
        
        return self.formatear_fecha_pasaporte(fecha_emision)

    def generar_fecha_vencimiento(self, fecha_emision):
        """Genera fecha de vencimiento"""
        if isinstance(fecha_emision, str):
            partes = fecha_emision.split('/')
            dia = int(partes[0])
            año = int(partes[3])
            
            meses = {
                'ENE': 1, 'FEB': 2, 'MAR': 3, 'ABR': 4, 'MAY': 5, 'JUN': 6,
                'JUL': 7, 'AGO': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DIC': 12
            }
            mes = meses.get(partes[1], 1)
            
            fecha_emision_obj = date(año, mes, dia)
        else:
            fecha_emision_obj = fecha_emision
        
        try:
            fecha_vencimiento = date(
                fecha_emision_obj.year + self.vigencia_pasaporte_anos,
                fecha_emision_obj.month,
                fecha_emision_obj.day
            )
        except ValueError:
            fecha_vencimiento = date(
                fecha_emision_obj.year + self.vigencia_pasaporte_anos,
                fecha_emision_obj.month,
                fecha_emision_obj.day - 1
            )
        
        return self.formatear_fecha_pasaporte(fecha_vencimiento)

    def buscar_imagen_por_edad(self, edad, genero='mujer'):
        """Busca imagen por edad"""
        if genero.upper() != 'F':
            return None
        
        imagenes_disponibles = list(self.imagenes_mujeres_path.glob('*.png'))
        
        if not imagenes_disponibles:
            return None
        
        # Buscar coincidencia exacta
        for img_path in imagenes_disponibles:
            nombre_archivo = img_path.stem
            match = re.search(r'massive_venezuelan_mujer_(\d+)_', nombre_archivo)
            
            if match:
                edad_imagen = int(match.group(1))
                if edad_imagen == edad:
                    return img_path
        
        # Buscar en rango
        rango_min = max(18, edad - 2)
        rango_max = min(60, edad + 2)
        
        for img_path in imagenes_disponibles:
            nombre_archivo = img_path.stem
            match = re.search(r'massive_venezuelan_mujer_(\d+)_', nombre_archivo)
            
            if match:
                edad_imagen = int(match.group(1))
                if rango_min <= edad_imagen <= rango_max:
                    return img_path
        
        # Selección aleatoria como último recurso
        return random.choice(imagenes_disponibles) if imagenes_disponibles else None

    def mover_imagen_usada(self, ruta_imagen):
        """Mueve imagen usada"""
        try:
            carpeta_usadas = self.imagenes_mujeres_path / 'usadas'
            carpeta_usadas.mkdir(exist_ok=True)
            
            imagen_path = Path(ruta_imagen)
            json_path = imagen_path.with_suffix('.json')
            
            # Verificar que la imagen existe antes de moverla
            if not imagen_path.exists():
                print(f"️ Imagen no encontrada: {imagen_path}")
                return False
            
            destino_imagen = carpeta_usadas / imagen_path.name
            shutil.move(str(imagen_path), str(destino_imagen))
            print(f" Imagen movida: {imagen_path.name} → usadas/")
            
            if json_path.exists():
                destino_json = carpeta_usadas / json_path.name
                shutil.move(str(json_path), str(destino_json))
                print(f" JSON movido: {json_path.name} → usadas/")
            
            return True
        except Exception as e:
            print(f" Error moviendo imagen: {e}")
            return False

    def generar_pasaporte_visual(self, datos_pasaporte):
        """Genera pasaporte visual"""
        if ScriptMaestroIntegrado is None:
            return None
        
        try:
            if self.script_maestro_cache is None:
                self.script_maestro_cache = ScriptMaestroIntegrado()
            
            ruta_foto = datos_pasaporte.get('ruta_foto')
            numero_pasaporte = datos_pasaporte.get('numero_pasaporte')
            nombre_archivo = datos_pasaporte.get('nombre_archivo', 'pasaporte.png')
            
            if not ruta_foto or not numero_pasaporte:
                return None
            
            self.script_maestro_cache.datos_pasaporte = datos_pasaporte
            
            resultado = self.script_maestro_cache.generar_gafete_integrado(
                ruta_foto=ruta_foto,
                numero_pasaporte=numero_pasaporte
            )
            
            if resultado:
                ruta_destino = self.pasaportes_visuales_path / nombre_archivo
                resultado.save(ruta_destino)
                del resultado
                gc.collect()
                return str(ruta_destino)
            
            return None
        except Exception as e:
            print(f" Error generando pasaporte: {e}")
            return None

    def procesar_registro(self, registro, idx, total):
        """Procesa un registro individual"""
        print(f" Procesando {idx + 1}/{total}")
        
        # Datos básicos
        primer_nombre = self.limpiar_texto(registro.get('PRIMER_NOMBRE', ''))
        segundo_nombre = self.limpiar_texto(registro.get('SEGUNDO_NOMBRE', ''))
        primer_apellido = self.limpiar_texto(registro.get('PRIMER_APELLIDO', ''))
        segundo_apellido = self.limpiar_texto(registro.get('SEGUNDO_APELLIDO', ''))
        genero = registro.get('GENERO', 'F')
        fecha_nacimiento = registro.get('FECHA_NACIMIENTO')
        
        # Calcular edad
        edad = self.calcular_edad(fecha_nacimiento)
        if edad is None:
            edad = 25
        
        # Generar datos
        numero_pasaporte = str(self.generar_numero_pasaporte())
        
        nombre_completo = primer_nombre
        if segundo_nombre and segundo_nombre.strip():
            nombre_completo += f" {segundo_nombre}"
        
        apellido_completo = primer_apellido
        if segundo_apellido and segundo_apellido.strip():
            apellido_completo += f" {segundo_apellido}"
        
        # Buscar imagen
        ruta_imagen = self.buscar_imagen_por_edad(edad, genero)
        
        if not ruta_imagen:
            return {
                'estado': 'omitido',
                'motivo_no_generado': f'Sin imagen para edad {edad}',
                'correo_original': registro.get('CORREO', ''),
                'edad': edad
            }
        
        # Generar datos del pasaporte
        datos_pasaporte = {
            'ruta_foto': str(ruta_imagen),
            'numero_pasaporte_1': numero_pasaporte,
            'numero_pasaporte_2': numero_pasaporte,
            'tipo': 'P',
            'pais_emisor': 'VEN',
            'nombre_completo': nombre_completo,
            'apellido_completo': apellido_completo,
            'fecha_nacimiento': self.formatear_fecha_pasaporte(fecha_nacimiento),
            'cedula': str(random.randint(10000000, 99999999)),
            'fecha_emision': self.generar_fecha_emision(fecha_nacimiento),
            'fecha_vencimiento': self.generar_fecha_vencimiento(self.generar_fecha_emision(fecha_nacimiento)),
            'sexo': genero,
            'nacionalidad': 'VENEZOLANA',
            'lugar_nacimiento': self.seleccionar_lugar_nacimiento(),
            'numero_pasaporte': numero_pasaporte,
            'codigo_verificacion': f"{random.randint(10, 99)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
            'firma': f"{primer_nombre} {primer_apellido}",
            'fuente_firma': 'BrittanySignature.ttf',
            'mrz_linea1': f"P<VEN{apellido_completo[:20]:<20}<<{nombre_completo[:20]:<20}",
            'mrz_linea2': f"{numero_pasaporte}0VEN{str(edad).zfill(2)}01{genero}2501010<<<<<<<<<<<<<<<0",
            'edad': edad,
            'correo_original': registro.get('CORREO', ''),
            'imagen_usada': str(ruta_imagen),
            'nombre_archivo': f"{registro.get('CORREO', 'pasaporte')}.png"
        }
        
        # Generar pasaporte visual
        ruta_pasaporte_visual = self.generar_pasaporte_visual(datos_pasaporte)
        if ruta_pasaporte_visual:
            datos_pasaporte['pasaporte_visual'] = ruta_pasaporte_visual
            datos_pasaporte['estado'] = 'generado'
            # Mover imagen usada
            self.mover_imagen_usada(str(ruta_imagen))
        else:
            datos_pasaporte['estado'] = 'omitido'
            datos_pasaporte['motivo_no_generado'] = 'Error generando pasaporte visual'
        
        # Liberar memoria cada 10 registros
        if (idx + 1) % 10 == 0:
            gc.collect()
        
        return datos_pasaporte

    def generar_pasaportes_masivos(self, limite=None):
        """Genera pasaportes masivos de forma simple"""
        print(" GENERADOR SIMPLE DE PASAPORTES")
        print("=" * 50)
        
        # Cargar datos
        df = self.cargar_datos_csv()
        if df is None:
            return False
        
        # Procesar registros
        registros_procesados = []
        total_registros = len(df) if limite is None else min(limite, len(df))
        
        print(f" Procesando {total_registros} registros...")
        
        for idx, registro in df.iterrows():
            if limite and idx >= limite:
                break
            
            try:
                datos_pasaporte = self.procesar_registro(registro, idx, total_registros)
                registros_procesados.append(datos_pasaporte)
                
                # Mostrar progreso cada 10 registros
                if (idx + 1) % 10 == 0:
                    generados = sum(1 for r in registros_procesados if r.get('estado') == 'generado')
                    omitidos = sum(1 for r in registros_procesados if r.get('estado') == 'omitido')
                    print(f" Progreso: {idx + 1}/{total_registros} - Generados: {generados}, Omitidos: {omitidos}")
                
            except Exception as e:
                print(f" Error en registro {idx + 1}: {e}")
                continue
        
        # Guardar resultados
        self.guardar_resultados(registros_procesados)
        
        # Resumen final
        generados = sum(1 for r in registros_procesados if r.get('estado') == 'generado')
        omitidos = sum(1 for r in registros_procesados if r.get('estado') == 'omitido')
        
        print(f"\n ¡PROCESO COMPLETADO!")
        print(f" Pasaportes generados: {generados}")
        print(f"️ Pasaportes omitidos: {omitidos}")
        print(f" Resultados en: {self.output_path}")
        
        return True

    def guardar_resultados(self, registros_procesados):
        """Guarda los resultados sin eliminar pasaportes existentes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # OPTIMIZACIÓN: Verificar si hay archivos existentes para continuar
        archivos_existentes = list(self.output_path.glob('pasaportes_procesados_*.xlsx'))
        
        if archivos_existentes:
            # Continuar con el archivo más reciente
            archivo_mas_reciente = max(archivos_existentes, key=lambda x: x.stat().st_mtime)
            print(f" Continuando con archivo existente: {archivo_mas_reciente.name}")
            
            # Cargar datos existentes
            try:
                df_existente = pd.read_excel(archivo_mas_reciente)
                registros_existentes = df_existente.to_dict('records')
                
                # Combinar con nuevos registros
                todos_los_registros = registros_existentes + registros_procesados
                
                # Guardar archivo actualizado
                df_combinado = pd.DataFrame(todos_los_registros)
                df_combinado.to_excel(archivo_mas_reciente, index=False)
                
                print(f" Resultados actualizados: {archivo_mas_reciente.name}")
                print(f" Total registros: {len(todos_los_registros)} (existentes: {len(registros_existentes)}, nuevos: {len(registros_procesados)})")
                
            except Exception as e:
                print(f"️ Error cargando archivo existente: {e}")
                # Fallback: crear nuevo archivo
                excel_path = self.output_path / f'pasaportes_procesados_{timestamp}.xlsx'
                df_procesados = pd.DataFrame(registros_procesados)
                df_procesados.to_excel(excel_path, index=False)
                print(f" Nuevo archivo creado: {excel_path}")
        else:
            # No hay archivos existentes, crear nuevo
            excel_path = self.output_path / f'pasaportes_procesados_{timestamp}.xlsx'
            df_procesados = pd.DataFrame(registros_procesados)
            df_procesados.to_excel(excel_path, index=False)
            print(f" Nuevo archivo creado: {excel_path}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Generador Simple de Pasaportes')
    parser.add_argument('--limite', '-l', type=int, help='Límite de registros a procesar')
    parser.add_argument('--base-path', '-b', help='Ruta base del proyecto')
    
    args = parser.parse_args()
    
    generador = GeneradorSimple(args.base_path)
    exito = generador.generar_pasaportes_masivos(args.limite)
    
    if not exito:
        sys.exit(1)

if __name__ == "__main__":
    main()
