#!/usr/bin/env python3
"""
Procesador de Archivos Excel a CSV
Extrae y convierte datos de Excel a CSV optimizado para generación de pasaportes
"""

import os
import sys
import pandas as pd
import gc
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import argparse
import re
import json

# =============================================================================
# CONFIGURACIÓN GLOBAL - MODIFICAR AQUÍ LOS VALORES DESEADOS
# =============================================================================

# Número de registros por archivo CSV (cambiar este valor según necesites)
# Valores recomendados: 25, 50, 100, 200
REGISTROS_POR_ARCHIVO = 50

# Activar modo división automáticamente (True/False)
# True = Divide en múltiples archivos, False = Un solo archivo
MODO_DIVISION = True

# =============================================================================
# EJEMPLOS DE CONFIGURACIÓN:
# =============================================================================
# Para archivos pequeños (25 registros): REGISTROS_POR_ARCHIVO = 25
# Para archivos medianos (50 registros): REGISTROS_POR_ARCHIVO = 50  
# Para archivos grandes (100 registros): REGISTROS_POR_ARCHIVO = 100
# Para archivos muy grandes (200 registros): REGISTROS_POR_ARCHIVO = 200
# =============================================================================

class ProcesadorXLSX:
    def __init__(self, base_path=None):
        """Inicializa el procesador de archivos Excel"""
        # Usar ruta base del proyecto (directorio del script) si no se especifica
        self.base_path = Path(base_path) if base_path else Path(__file__).resolve().parent
        self.data_path = self.base_path / 'DATA'
        self.output_path = self.base_path / 'OUTPUT' / 'pasaportes_generados'
        self.logs_path = self.base_path / 'OUTPUT' / 'logs'
        self.ultima_ubicacion_file = self.logs_path / 'ultima_ubicacion_excel.json'
        
        # Crear directorios necesarios
        self._crear_directorios()
    
    def _crear_directorios(self):
        """Crea directorios necesarios"""
        try:
            self.output_path.mkdir(parents=True, exist_ok=True)
            self.data_path.mkdir(parents=True, exist_ok=True)
            self.logs_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"❌ Error creando directorios: {e}")
            raise
    
    def seleccionar_archivo_excel(self):
        """Abre una ventana para seleccionar el archivo Excel"""
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal
        
        # Cargar última ubicación usada si existe
        initial_dir = str(self.data_path)
        try:
            if self.ultima_ubicacion_file.exists():
                with open(self.ultima_ubicacion_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    last_dir = data.get('last_dir')
                    if last_dir and Path(last_dir).exists():
                        initial_dir = last_dir
        except Exception:
            pass

        archivo_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel con datos de pasaportes",
            filetypes=[
                ("Archivos Excel", ("*.xlsx", "*.xls", "*.XLSX", "*.XLS")),
                ("Todos los archivos", "*.*"),
            ],
            initialdir=initial_dir
        )
        
        # Guardar última ubicación usada
        try:
            if archivo_path:
                seleccion_dir = str(Path(archivo_path).parent)
                with open(self.ultima_ubicacion_file, 'w', encoding='utf-8') as f:
                    json.dump({"last_dir": seleccion_dir}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        root.destroy()
        return archivo_path
    
    def _normalizar_fechas_en_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Elimina HH:MM:SS dejando YYYY-MM-DD en columnas de fecha"""
        try:
            # Columnas candidatas: contienen 'FECHA' en el nombre
            cols_fecha = [c for c in df.columns if 'FECHA' in c.upper()]
            for c in cols_fecha:
                if c in df:
                    # Convertir a string, limpiar espacios y normalizar a YYYY-MM-DD
                    df[c] = (
                        df[c]
                        .astype(str)
                        .apply(self._parse_fecha_a_yyyy_mm_dd)
                    )
            return df
        except Exception:
            return df

    def _parse_fecha_a_yyyy_mm_dd(self, valor: str) -> str:
        """Normaliza una fecha a formato YYYY-MM-DD si detecta patrones comunes.

        Soporta:
        - "YYYY-MM-DD" (con o sin hora al final)
        - "MM/DD/YYYY" (con posibles signos de puntuación como coma o punto)
        - Cadenas con texto adicional; se extrae el primer patrón de fecha válido
        """
        if valor is None:
            return ""
        s = str(valor).strip()
        if not s or s == "nan":
            return ""

        # Eliminar caracteres de puntuación comunes adyacentes a la fecha
        # y reducir espacios múltiples
        s = re.sub(r"[\t\r\n]+", " ", s)
        s = s.replace("\u200b", "").strip()  # zero-width space si aparece

        # Si incluye hora, separar por espacio y analizar la parte inicial primero
        primera_parte = s.split(" ")[0]

        # 1) Buscar patrón YYYY-MM-DD en toda la cadena
        m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
        if m:
            y, mo, d = m.groups()
            return f"{y}-{int(mo):02d}-{int(d):02d}"

        # 2) Buscar patrón MM/DD/YYYY (puede venir con coma o punto después)
        m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
        if m:
            mo, d, y = m.groups()
            return f"{y}-{int(mo):02d}-{int(d):02d}"

        # 3) Intentar con la primera parte limpia (por si viene como 'YYYY-MM-DD,' o '03/29/1981.')
        parte_limpia = primera_parte.rstrip(",.;:")
        m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", parte_limpia)
        if m:
            y, mo, d = m.groups()
            return f"{y}-{int(mo):02d}-{int(d):02d}"
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", parte_limpia)
        if m:
            mo, d, y = m.groups()
            return f"{y}-{int(mo):02d}-{int(d):02d}"

        # Si no se reconoce, devolver valor original sin cambiar
        return s
    
    def _validar_columnas_requeridas(self, df: pd.DataFrame) -> bool:
        """Valida que el DataFrame tenga las columnas requeridas"""
        columnas_requeridas = [
            'GENERO', 'PRIMER_NOMBRE', 'PRIMER_APELLIDO', 
            'FECHA_NACIMIENTO', 'CORREO'
        ]
        
        columnas_faltantes = []
        for col in columnas_requeridas:
            if col not in df.columns:
                columnas_faltantes.append(col)
        
        if columnas_faltantes:
            print(f"❌ ERROR: Faltan columnas requeridas:")
            for col in columnas_faltantes:
                print(f"   • {col}")
            return False
        
        return True
    
    def _limpiar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y normaliza los datos del DataFrame"""
        try:
            # Rellenar valores nulos con strings vacíos
            df = df.fillna('')
            
            # Convertir todas las columnas a string para evitar problemas de tipo
            for col in df.columns:
                df[col] = df[col].astype(str)
            
            # Normalizar fechas
            df = self._normalizar_fechas_en_df(df)
            
            return df
        except Exception as e:
            print(f"⚠️ Error limpiando datos: {e}")
            return df
    
    def procesar_xlsx_a_csv_dividido(self, archivo_xlsx=None, registros_por_archivo=None):
        """Procesa archivo Excel y lo divide en múltiples CSV"""
        # Usar valor global si no se especifica
        if registros_por_archivo is None:
            registros_por_archivo = REGISTROS_POR_ARCHIVO
            
        print("🔄 PROCESADOR DE ARCHIVOS EXCEL A CSV DIVIDIDO")
        print("=" * 60)
        print(f"📊 Dividiendo en archivos de {registros_por_archivo} registros cada uno")
        
        # Seleccionar archivo Excel si no se proporciona
        if archivo_xlsx is None:
            archivo_xlsx = self.seleccionar_archivo_excel()
            if not archivo_xlsx:
                print("❌ No se seleccionó archivo Excel")
                return None
        
        archivo_path = Path(archivo_xlsx)
        if not archivo_path.exists():
            print(f"❌ Archivo no encontrado: {archivo_path}")
            return None
        
        try:
            print(f"📊 Cargando archivo Excel: {archivo_path.name}")
            
            # Cargar Excel con dtype=str para evitar cambios de formato
            df = pd.read_excel(archivo_path, dtype=str, keep_default_na=False)
            print(f"✅ Datos cargados: {len(df)} registros")
            
            # Validar columnas requeridas
            if not self._validar_columnas_requeridas(df):
                print("\n💡 SOLUCIÓN:")
                print("   1. Verificar que el archivo Excel tenga las columnas requeridas")
                print("   2. Usar nombres de columnas exactos: GENERO, PRIMER_NOMBRE, etc.")
                return None
            
            # Limpiar datos
            print("🧹 Limpiando y normalizando datos...")
            df = self._limpiar_datos(df)
            
            # Calcular número de archivos necesarios
            total_registros = len(df)
            num_archivos = (total_registros + registros_por_archivo - 1) // registros_por_archivo
            
            print(f"📊 División calculada:")
            print(f"   • Total registros: {total_registros}")
            print(f"   • Registros por archivo: {registros_por_archivo}")
            print(f"   • Número de archivos: {num_archivos}")
            
            # Generar timestamp para todos los archivos
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivos_generados = []
            
            # Dividir y guardar archivos
            for i in range(num_archivos):
                inicio = i * registros_por_archivo
                fin = min(inicio + registros_por_archivo, total_registros)
                
                # Extraer lote de datos
                df_lote = df.iloc[inicio:fin].copy()
                
                # Generar nombre de archivo con numeración
                numero_archivo = f"{i+1:03d}"  # 001, 002, 003, etc.
                csv_filename = f"{archivo_path.stem}_{timestamp}_{numero_archivo}.csv"
                csv_path = archivo_path.parent / csv_filename
                
                # Guardar CSV del lote
                print(f"💾 Guardando lote {i+1}/{num_archivos}: {csv_filename}")
                df_lote.to_csv(csv_path, index=False, encoding='utf-8')
                
                # Verificar archivo generado
                if csv_path.exists():
                    file_size = csv_path.stat().st_size / 1024  # KB
                    print(f"   ✅ Lote {i+1}: {len(df_lote)} registros, {file_size:.1f} KB")
                    archivos_generados.append(str(csv_path))
                else:
                    print(f"   ❌ Error creando lote {i+1}")
                
                # Liberar memoria del lote
                del df_lote
                gc.collect()
            
            # Liberar memoria del DataFrame principal
            del df
            gc.collect()
            
            # Resumen final
            print(f"\n🎉 DIVISIÓN COMPLETADA:")
            print(f"   📄 Archivos generados: {len(archivos_generados)}")
            print(f"   📊 Total registros procesados: {total_registros}")
            print(f"   📍 Ubicación: {archivo_path.parent}")
            
            # Mostrar lista de archivos generados
            print(f"\n📋 ARCHIVOS GENERADOS:")
            for i, archivo in enumerate(archivos_generados, 1):
                archivo_path_obj = Path(archivo)
                file_size = archivo_path_obj.stat().st_size / 1024  # KB
                print(f"   {i:2d}. {archivo_path_obj.name} ({file_size:.1f} KB)")
            
            return archivos_generados
                
        except Exception as e:
            print(f"❌ Error procesando archivo Excel: {e}")
            return None
    
    def procesar_xlsx_a_csv(self, archivo_xlsx=None):
        """Procesa archivo Excel y lo convierte a CSV optimizado (método original)"""
        print("🔄 PROCESADOR DE ARCHIVOS EXCEL A CSV")
        print("=" * 50)
        
        # Seleccionar archivo Excel si no se proporciona
        if archivo_xlsx is None:
            archivo_xlsx = self.seleccionar_archivo_excel()
            if not archivo_xlsx:
                print("❌ No se seleccionó archivo Excel")
                return None
        
        archivo_path = Path(archivo_xlsx)
        if not archivo_path.exists():
            print(f"❌ Archivo no encontrado: {archivo_path}")
            return None
        
        try:
            print(f"📊 Cargando archivo Excel: {archivo_path.name}")
            
            # Cargar Excel con dtype=str para evitar cambios de formato
            df = pd.read_excel(archivo_path, dtype=str, keep_default_na=False)
            print(f"✅ Datos cargados: {len(df)} registros")
            
            # Validar columnas requeridas
            if not self._validar_columnas_requeridas(df):
                print("\n💡 SOLUCIÓN:")
                print("   1. Verificar que el archivo Excel tenga las columnas requeridas")
                print("   2. Usar nombres de columnas exactos: GENERO, PRIMER_NOMBRE, etc.")
                return None
            
            # Limpiar datos
            print("🧹 Limpiando y normalizando datos...")
            df = self._limpiar_datos(df)
            
            # Generar nombre de archivo CSV con timestamp en la misma carpeta del XLSX
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_filename = f"{archivo_path.stem}_{timestamp}.csv"
            csv_path = archivo_path.parent / csv_filename
            
            # Guardar CSV optimizado
            print(f"💾 Guardando CSV optimizado: {csv_filename}")
            df.to_csv(csv_path, index=False, encoding='utf-8')
            
            # Verificar archivo generado
            if csv_path.exists():
                file_size = csv_path.stat().st_size / 1024  # KB
                print(f"✅ CSV generado exitosamente:")
                print(f"   📄 Archivo: {csv_filename}")
                print(f"   📊 Registros: {len(df)}")
                print(f"   💾 Tamaño: {file_size:.1f} KB")
                print(f"   📍 Ubicación: {csv_path}")
                
                # Liberar memoria
                del df
                gc.collect()
                
                return str(csv_path)
            else:
                print("❌ Error: No se pudo crear el archivo CSV")
                return None
                
        except Exception as e:
            print(f"❌ Error procesando archivo Excel: {e}")
            return None
    
    def mostrar_ayuda(self):
        """Muestra información de ayuda sobre el procesador"""
        print("\n🔄 PROCESADOR DE ARCHIVOS EXCEL A CSV")
        print("=" * 50)
        print("📋 COLUMNAS REQUERIDAS:")
        print("   • GENERO: Género (F/M)")
        print("   • PRIMER_NOMBRE: Primer nombre")
        print("   • SEGUNDO_NOMBRE: Segundo nombre (opcional)")
        print("   • PRIMER_APELLIDO: Primer apellido")
        print("   • SEGUNDO_APELLIDO: Segundo apellido (opcional)")
        print("   • FECHA_NACIMIENTO: Fecha de nacimiento (YYYY-MM-DD)")
        print("   • CORREO: Correo electrónico")
        print("\n💡 USO:")
        print("   python3 procesador_xlsx.py                    # Seleccionar archivo")
        print("   python3 procesador_xlsx.py --archivo ruta.xlsx # Archivo específico")
        print("\n⚙️ CONFIGURACIÓN:")
        print("   • Modificar variables globales en el código:")
        print("     - REGISTROS_POR_ARCHIVO = 50  # Número de registros por archivo")
        print("     - MODO_DIVISION = True        # Activar/desactivar división")
        print("\n✅ RESULTADO:")
        print("   • Modo división: Genera múltiples CSV con terminación 001, 002, 003...")
        print("   • CSV listo para usar con generador_pasaportes_masivo.py")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Procesador de Archivos Excel a CSV')
    parser.add_argument('--archivo', '-a', help='Ruta al archivo Excel específico')
    parser.add_argument('--ayuda', action='store_true', help='Mostrar información de ayuda')
    parser.add_argument('--base-path', '-b', help='Ruta base del proyecto')
    
    args = parser.parse_args()
    
    if args.ayuda:
        procesador = ProcesadorXLSX(args.base_path)
        procesador.mostrar_ayuda()
        return
    
    # Crear procesador
    procesador = ProcesadorXLSX(args.base_path)
    
    # Mostrar configuración actual
    print(f"⚙️ CONFIGURACIÓN ACTUAL:")
    print(f"   • Registros por archivo: {REGISTROS_POR_ARCHIVO}")
    print(f"   • Modo división: {'Activado' if MODO_DIVISION else 'Desactivado'}")
    print()
    
    # Procesar archivo según configuración global
    if MODO_DIVISION:
        # Modo división automático
        archivos_generados = procesador.procesar_xlsx_a_csv_dividido(args.archivo)
        
        if archivos_generados:
            print(f"\n🎉 ¡DIVISIÓN COMPLETADA!")
            print(f"📄 Archivos generados: {len(archivos_generados)}")
            print(f"🚀 Ahora puedes procesar cada archivo por separado:")
            for i, archivo in enumerate(archivos_generados, 1):
                print(f"   python3 generador_pasaportes_masivo.py --archivo-csv {archivo}")
        else:
            print("\n💥 Error en la división del archivo Excel")
            sys.exit(1)
    else:
        # Modo normal (un solo archivo)
        csv_path = procesador.procesar_xlsx_a_csv(args.archivo)
        
        if csv_path:
            print(f"\n🎉 ¡PROCESAMIENTO COMPLETADO!")
            print(f"📄 CSV generado: {Path(csv_path).name}")
            print(f"🚀 Ahora puedes ejecutar:")
            print(f"   python3 generador_pasaportes_masivo.py --archivo-csv {csv_path}")
        else:
            print("\n💥 Error en el procesamiento del archivo Excel")
            sys.exit(1)

if __name__ == "__main__":
    main()
