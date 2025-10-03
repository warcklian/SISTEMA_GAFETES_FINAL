#!/usr/bin/env python3
"""
Script Maestro Completo - Sistema de Generación Masiva de Pasaportes
Integra todo el proceso: Excel → Datos → Pasaportes Visuales
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse
from datetime import datetime

class ScriptMaestroCompleto:
    def __init__(self, base_path=None):
        """Inicializa el script maestro completo"""
        self.base_path = Path(base_path) if base_path else Path('/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL')
        self.scripts_path = self.base_path
        self.output_path = self.base_path / 'OUTPUT'
        
        # Crear directorios necesarios
        self.output_path.mkdir(parents=True, exist_ok=True)
        
    def ejecutar_comando(self, comando, descripcion):
        """Ejecuta un comando y maneja errores"""
        print(f"\n🔄 {descripcion}")
        print("-" * 50)
        
        try:
            resultado = subprocess.run(
                comando, 
                shell=True, 
                cwd=self.base_path,
                capture_output=True, 
                text=True, 
                check=True
            )
            
            print(f"✅ {descripcion} - Completado")
            if resultado.stdout:
                print(f"📤 Salida: {resultado.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en {descripcion}: {e}")
            if e.stderr:
                print(f"📤 Error: {e.stderr}")
            return False
    
    def paso1_procesar_datos_excel(self, limite=None):
        """Paso 1: Procesar datos del Excel y generar datos estructurados"""
        print("\n" + "="*60)
        print("📊 PASO 1: PROCESAMIENTO DE DATOS DEL EXCEL")
        print("="*60)
        
        comando = f"python3 generador_pasaportes_masivo.py"
        if limite:
            comando += f" --limite {limite}"
        
        return self.ejecutar_comando(comando, "Procesando datos del Excel y generando datos estructurados")
    
    def paso2_generar_pasaportes_visuales(self, limite=None):
        """Paso 2: Generar pasaportes visuales usando el script maestro"""
        print("\n" + "="*60)
        print("🎨 PASO 2: GENERACIÓN DE PASAPORTES VISUALES")
        print("="*60)
        
        comando = f"python3 generador_pasaportes_visuales.py"
        if limite:
            comando += f" --limite {limite}"
        
        return self.ejecutar_comando(comando, "Generando pasaportes visuales con el script maestro")
    
    def paso3_crear_pasaporte_ejemplo(self):
        """Paso 3: Crear pasaporte de ejemplo para verificar funcionamiento"""
        print("\n" + "="*60)
        print("🔍 PASO 3: CREACIÓN DE PASAPORTE DE EJEMPLO")
        print("="*60)
        
        comando = "python3 generador_pasaportes_visuales.py --ejemplo"
        return self.ejecutar_comando(comando, "Creando pasaporte de ejemplo para verificar funcionamiento")
    
    def verificar_archivos_generados(self):
        """Verifica que se hayan generado los archivos esperados"""
        print("\n" + "="*60)
        print("🔍 VERIFICACIÓN DE ARCHIVOS GENERADOS")
        print("="*60)
        
        # Verificar archivos de datos procesados
        datos_path = self.output_path / 'pasaportes_generados'
        if datos_path.exists():
            archivos_datos = list(datos_path.glob('pasaportes_procesados_*.json'))
            if archivos_datos:
                print(f"✅ Archivos de datos encontrados: {len(archivos_datos)}")
                for archivo in archivos_datos:
                    print(f"   📄 {archivo.name}")
            else:
                print("⚠️ No se encontraron archivos de datos procesados")
        else:
            print("❌ Directorio de datos no encontrado")
        
        # Verificar pasaportes visuales
        visuales_path = self.output_path / 'pasaportes_visuales'
        if visuales_path.exists():
            archivos_visuales = list(visuales_path.glob('pasaporte_*.png'))
            if archivos_visuales:
                print(f"✅ Pasaportes visuales encontrados: {len(archivos_visuales)}")
                for archivo in archivos_visuales[:5]:  # Mostrar solo los primeros 5
                    print(f"   🖼️ {archivo.name}")
                if len(archivos_visuales) > 5:
                    print(f"   ... y {len(archivos_visuales) - 5} más")
            else:
                print("⚠️ No se encontraron pasaportes visuales")
        else:
            print("❌ Directorio de pasaportes visuales no encontrado")
        
        return True
    
    def generar_reporte_final(self):
        """Genera un reporte final del proceso"""
        print("\n" + "="*60)
        print("📋 GENERANDO REPORTE FINAL")
        print("="*60)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte_path = self.output_path / f'reporte_final_{timestamp}.txt'
        
        try:
            with open(reporte_path, 'w', encoding='utf-8') as f:
                f.write("REPORTE FINAL - GENERACIÓN MASIVA DE PASAPORTES\n")
                f.write("=" * 60 + "\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Directorio base: {self.base_path}\n\n")
                
                # Contar archivos generados
                datos_path = self.output_path / 'pasaportes_generados'
                visuales_path = self.output_path / 'pasaportes_visuales'
                
                if datos_path.exists():
                    archivos_datos = list(datos_path.glob('pasaportes_procesados_*.json'))
                    f.write(f"Archivos de datos procesados: {len(archivos_datos)}\n")
                
                if visuales_path.exists():
                    archivos_visuales = list(visuales_path.glob('pasaporte_*.png'))
                    f.write(f"Pasaportes visuales generados: {len(archivos_visuales)}\n")
                
                f.write("\nESTRUCTURA DE ARCHIVOS GENERADOS:\n")
                f.write("-" * 40 + "\n")
                
                # Listar estructura de directorios
                for root, dirs, files in os.walk(self.output_path):
                    level = root.replace(str(self.output_path), '').count(os.sep)
                    indent = ' ' * 2 * level
                    f.write(f"{indent}{os.path.basename(root)}/\n")
                    subindent = ' ' * 2 * (level + 1)
                    for file in files[:10]:  # Limitar a 10 archivos por directorio
                        f.write(f"{subindent}{file}\n")
                    if len(files) > 10:
                        f.write(f"{subindent}... y {len(files) - 10} archivos más\n")
            
            print(f"✅ Reporte final generado: {reporte_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generando reporte final: {e}")
            return False
    
    def ejecutar_proceso_completo(self, limite=None):
        """Ejecuta el proceso completo de generación masiva"""
        print("🚀 INICIANDO PROCESO COMPLETO DE GENERACIÓN MASIVA")
        print("=" * 80)
        print("Este proceso incluye:")
        print("1. 📊 Procesamiento de datos del Excel")
        print("2. 🎨 Generación de pasaportes visuales")
        print("3. 🔍 Verificación de archivos generados")
        print("4. 📋 Generación de reporte final")
        print("=" * 80)
        
        if limite:
            print(f"⚠️ Límite de registros: {limite}")
        
        # Paso 1: Procesar datos del Excel
        if not self.paso1_procesar_datos_excel(limite):
            print("❌ Error en el paso 1. Abortando proceso.")
            return False
        
        # Paso 2: Generar pasaportes visuales
        if not self.paso2_generar_pasaportes_visuales(limite):
            print("❌ Error en el paso 2. Abortando proceso.")
            return False
        
        # Paso 3: Crear pasaporte de ejemplo
        if not self.paso3_crear_pasaporte_ejemplo():
            print("⚠️ Error en el paso 3 (ejemplo), pero continuando...")
        
        # Verificar archivos generados
        self.verificar_archivos_generados()
        
        # Generar reporte final
        self.generar_reporte_final()
        
        print("\n" + "="*80)
        print("🎉 ¡PROCESO COMPLETO FINALIZADO EXITOSAMENTE!")
        print("="*80)
        print("📁 Archivos generados en:")
        print(f"   📊 Datos procesados: {self.output_path}/pasaportes_generados/")
        print(f"   🎨 Pasaportes visuales: {self.output_path}/pasaportes_visuales/")
        print(f"   📋 Reportes: {self.output_path}/")
        
        return True
    
    def ejecutar_solo_datos(self, limite=None):
        """Ejecuta solo el procesamiento de datos"""
        print("📊 EJECUTANDO SOLO PROCESAMIENTO DE DATOS")
        print("=" * 50)
        
        return self.paso1_procesar_datos_excel(limite)
    
    def ejecutar_solo_visuales(self, limite=None):
        """Ejecuta solo la generación de pasaportes visuales"""
        print("🎨 EJECUTANDO SOLO GENERACIÓN DE PASAPORTES VISUALES")
        print("=" * 50)
        
        return self.paso2_generar_pasaportes_visuales(limite)

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Script Maestro Completo - Generación Masiva de Pasaportes')
    parser.add_argument('--modo', '-m', choices=['completo', 'datos', 'visuales'], 
                       default='completo', help='Modo de ejecución')
    parser.add_argument('--limite', '-l', type=int, help='Límite de registros a procesar')
    parser.add_argument('--base-path', '-b', help='Ruta base del proyecto')
    
    args = parser.parse_args()
    
    # Inicializar script maestro
    maestro = ScriptMaestroCompleto(args.base_path)
    
    # Ejecutar según el modo seleccionado
    if args.modo == 'completo':
        exito = maestro.ejecutar_proceso_completo(args.limite)
    elif args.modo == 'datos':
        exito = maestro.ejecutar_solo_datos(args.limite)
    elif args.modo == 'visuales':
        exito = maestro.ejecutar_solo_visuales(args.limite)
    
    if exito:
        print("\n🎉 ¡Proceso completado exitosamente!")
    else:
        print("\n💥 Error en el proceso")
        sys.exit(1)

if __name__ == "__main__":
    main()
