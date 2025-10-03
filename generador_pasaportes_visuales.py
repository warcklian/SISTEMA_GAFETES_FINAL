#!/usr/bin/env python3
"""
Generador de Pasaportes Visuales
Integra los datos procesados con el script maestro para generar pasaportes visuales
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse

# Agregar el directorio SCRIPTS al path para importar el script maestro
sys.path.append('/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL/SCRIPTS')

try:
    from script_maestro_integrado import ScriptMaestroIntegrado
except ImportError as e:
    print(f"❌ Error importando script maestro: {e}")
    print("⚠️ Asegúrate de que el script maestro esté en la ruta correcta")
    sys.exit(1)

class GeneradorPasaportesVisuales:
    def __init__(self, base_path=None):
        """Inicializa el generador de pasaportes visuales"""
        self.base_path = Path(base_path) if base_path else Path('/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL')
        self.output_path = self.base_path / 'OUTPUT' / 'pasaportes_visuales'
        self.datos_path = self.base_path / 'OUTPUT' / 'pasaportes_generados'
        
        # Crear directorio de salida
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar script maestro
        self.script_maestro = ScriptMaestroIntegrado()
        
    def cargar_datos_procesados(self, archivo_datos=None):
        """Carga los datos procesados desde JSON o Excel"""
        if archivo_datos:
            archivo_path = Path(archivo_datos)
        else:
            # Buscar el archivo más reciente
            archivos_json = list(self.datos_path.glob('pasaportes_procesados_*.json'))
            if not archivos_json:
                print(f"❌ No se encontraron archivos de datos procesados en {self.datos_path}")
                return None
            
            archivo_path = max(archivos_json, key=lambda x: x.stat().st_mtime)
        
        print(f"📊 Cargando datos desde: {archivo_path}")
        
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            print(f"✅ Datos cargados: {len(datos)} registros")
            return datos
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return None
    
    def generar_pasaporte_individual(self, datos_pasaporte, indice):
        """Genera un pasaporte individual usando el script maestro"""
        print(f"\n🔄 Generando pasaporte {indice + 1}: {datos_pasaporte.get('nombre_completo', 'N/A')} {datos_pasaporte.get('apellido_completo', 'N/A')}")
        
        try:
            # Verificar que existe la imagen
            ruta_imagen = datos_pasaporte.get('ruta_foto')
            if not ruta_imagen or not Path(ruta_imagen).exists():
                print(f"⚠️ Imagen no encontrada: {ruta_imagen}")
                return None
            
            # Generar gafete usando el script maestro
            gafete = self.script_maestro.generar_gafete_integrado(
                ruta_foto=ruta_imagen,
                numero_pasaporte=datos_pasaporte.get('numero_pasaporte', '000000000')
            )
            
            if gafete is None:
                print(f"❌ Error generando gafete para registro {indice + 1}")
                return None
            
            # Guardar pasaporte generado
            nombre_archivo = f"pasaporte_{datos_pasaporte.get('numero_pasaporte', f'reg_{indice}')}_{indice + 1:03d}.png"
            ruta_salida = self.output_path / nombre_archivo
            
            gafete.save(ruta_salida, 'PNG', dpi=(300, 300))
            
            print(f"✅ Pasaporte guardado: {nombre_archivo}")
            print(f"📐 Dimensiones: {gafete.width}x{gafete.height}")
            
            return ruta_salida
            
        except Exception as e:
            print(f"❌ Error generando pasaporte {indice + 1}: {e}")
            return None
    
    def generar_pasaportes_visuales(self, archivo_datos=None, limite=None):
        """Genera pasaportes visuales masivos"""
        print("🎨 INICIANDO GENERACIÓN DE PASAPORTES VISUALES")
        print("=" * 60)
        
        # Cargar datos procesados
        datos = self.cargar_datos_procesados(archivo_datos)
        if not datos:
            return False
        
        # Procesar registros
        pasaportes_generados = []
        total_registros = len(datos) if limite is None else min(limite, len(datos))
        
        print(f"🎨 Generando {total_registros} pasaportes visuales...")
        
        for idx, datos_pasaporte in enumerate(datos):
            if limite and idx >= limite:
                break
            
            ruta_pasaporte = self.generar_pasaporte_individual(datos_pasaporte, idx)
            
            if ruta_pasaporte:
                pasaportes_generados.append({
                    'indice': idx + 1,
                    'numero_pasaporte': datos_pasaporte.get('numero_pasaporte'),
                    'nombre': datos_pasaporte.get('nombre_completo'),
                    'apellido': datos_pasaporte.get('apellido_completo'),
                    'archivo': str(ruta_pasaporte)
                })
        
        # Guardar resumen
        self.guardar_resumen_generacion(pasaportes_generados)
        
        print(f"\n🎉 ¡Generación de pasaportes visuales completada!")
        print(f"📊 Total de pasaportes generados: {len(pasaportes_generados)}")
        print(f"📁 Pasaportes guardados en: {self.output_path}")
        
        return True
    
    def guardar_resumen_generacion(self, pasaportes_generados):
        """Guarda un resumen de la generación"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar resumen como JSON
        resumen_path = self.output_path / f'resumen_generacion_{timestamp}.json'
        with open(resumen_path, 'w', encoding='utf-8') as f:
            json.dump(pasaportes_generados, f, ensure_ascii=False, indent=2)
        
        # Guardar resumen como Excel
        excel_path = self.output_path / f'resumen_generacion_{timestamp}.xlsx'
        df_resumen = pd.DataFrame(pasaportes_generados)
        df_resumen.to_excel(excel_path, index=False)
        
        print(f"📋 Resumen guardado:")
        print(f"   📄 JSON: {resumen_path}")
        print(f"   📊 Excel: {excel_path}")
    
    def crear_pasaporte_ejemplo(self):
        """Crea un pasaporte de ejemplo para verificar que todo funciona"""
        print("🔍 CREANDO PASAPORTE DE EJEMPLO")
        print("=" * 40)
        
        # Datos de ejemplo
        datos_ejemplo = {
            'ruta_foto': '/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL/DATA/Imagenes_Mujeres/massive_venezuelan_mujer_25_530_20250929_164337.png',
            'numero_pasaporte': '123456789',
            'nombre_completo': 'MARIA',
            'apellido_completo': 'GONZALEZ',
            'fecha_nacimiento': '15 / MAR / MAR / 1990',
            'sexo': 'F',
            'nacionalidad': 'VENEZOLANA',
            'lugar_nacimiento': 'CARACAS VEN',
            'fecha_emision': '01 / ENE / ENE / 2020',
            'fecha_vencimiento': '01 / ENE / ENE / 2030',
            'cedula': '12345678',
            'codigo_verificacion': '15-03-90',
            'firma': 'Firma Digital',
            'mrz_linea1': 'P<VENGONZALEZ<<MARIA<<<<<<<<<<<<<<<',
            'mrz_linea2': '1234567893VEN900315F3001011<<<<<<<<<<<<<<<5'
        }
        
        # Verificar que existe la imagen de ejemplo
        if not Path(datos_ejemplo['ruta_foto']).exists():
            print(f"⚠️ Imagen de ejemplo no encontrada: {datos_ejemplo['ruta_foto']}")
            return False
        
        # Generar pasaporte de ejemplo
        ruta_pasaporte = self.generar_pasaporte_individual(datos_ejemplo, 0)
        
        if ruta_pasaporte:
            print(f"✅ Pasaporte de ejemplo creado: {ruta_pasaporte}")
            return True
        else:
            print("❌ Error creando pasaporte de ejemplo")
            return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Generador de Pasaportes Visuales')
    parser.add_argument('--archivo-datos', '-a', help='Archivo de datos procesados (JSON)')
    parser.add_argument('--limite', '-l', type=int, help='Límite de pasaportes a generar')
    parser.add_argument('--ejemplo', action='store_true', help='Crear pasaporte de ejemplo')
    parser.add_argument('--base-path', '-b', help='Ruta base del proyecto')
    
    args = parser.parse_args()
    
    # Inicializar generador
    generador = GeneradorPasaportesVisuales(args.base_path)
    
    if args.ejemplo:
        # Crear pasaporte de ejemplo
        exito = generador.crear_pasaporte_ejemplo()
    else:
        # Generar pasaportes visuales
        exito = generador.generar_pasaportes_visuales(args.archivo_datos, args.limite)
    
    if exito:
        print("\n🎉 ¡Generación de pasaportes visuales completada exitosamente!")
        print("📋 Revisa los archivos generados en OUTPUT/pasaportes_visuales/")
    else:
        print("\n💥 Error en la generación de pasaportes visuales")
        sys.exit(1)

if __name__ == "__main__":
    main()
