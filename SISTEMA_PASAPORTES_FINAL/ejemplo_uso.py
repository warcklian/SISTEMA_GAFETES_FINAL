#!/usr/bin/env python3
"""
Ejemplo de Uso del Sistema de Pasaportes
Muestra cómo usar el sistema paso a paso
"""

import os
import sys
from pathlib import Path

# Agregar el directorio SCRIPTS al path
sys.path.append(str(Path(__file__).parent / "SCRIPTS"))

def ejemplo_basico():
    """Ejemplo básico de uso del sistema"""
    print("🚀 EJEMPLO DE USO DEL SISTEMA DE PASAPORTES")
    print("=" * 60)
    
    try:
        # Importar el script maestro
        from script_maestro_integrado import ScriptMaestroIntegrado
        
        # Inicializar el sistema
        print("1️⃣ Inicializando sistema...")
        maestro = ScriptMaestroIntegrado()
        
        # Verificar que hay imágenes disponibles
        imagenes_dir = Path("DATA/Imagenes_OK")
        if not imagenes_dir.exists():
            print("❌ Error: Directorio DATA/Imagenes_OK no encontrado")
            print("📋 Solución: Crear el directorio y colocar imágenes originales")
            return False
        
        # Buscar imágenes
        imagenes = []
        for subdir in imagenes_dir.iterdir():
            if subdir.is_dir():
                for img_file in list(subdir.glob('*.png')) + list(subdir.glob('*.jpg')) + list(subdir.glob('*.jpeg')):
                    imagenes.append(img_file)
        
        if not imagenes:
            print("❌ Error: No se encontraron imágenes en DATA/Imagenes_OK/")
            print("📋 Solución: Colocar imágenes originales en el directorio")
            return False
        
        print(f"✅ Encontradas {len(imagenes)} imágenes")
        
        # Ejecutar el sistema
        print("2️⃣ Ejecutando sistema de generación de pasaportes...")
        exito = maestro.crear_plantillas_integradas()
        
        if exito:
            print("✅ ¡Sistema ejecutado exitosamente!")
            print("📁 Revisar resultados en OUTPUT/plantillas_integradas/")
            return True
        else:
            print("❌ Error ejecutando el sistema")
            return False
            
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("📋 Solución: Ejecutar 'python3 instalar.py' primero")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def ejemplo_con_imagen_especifica():
    """Ejemplo usando una imagen específica"""
    print("\n🎯 EJEMPLO CON IMAGEN ESPECÍFICA")
    print("=" * 40)
    
    try:
        from script_maestro_integrado import ScriptMaestroIntegrado
        
        # Inicializar sistema
        maestro = ScriptMaestroIntegrado()
        
        # Buscar primera imagen disponible
        imagenes_dir = Path("DATA/Imagenes_OK")
        imagen_ejemplo = None
        
        for subdir in imagenes_dir.iterdir():
            if subdir.is_dir():
                for img_file in list(subdir.glob('*.png')) + list(subdir.glob('*.jpg')):
                    imagen_ejemplo = img_file
                    break
            if imagen_ejemplo:
                break
        
        if not imagen_ejemplo:
            print("❌ No se encontró imagen de ejemplo")
            return False
        
        print(f"📸 Usando imagen: {imagen_ejemplo.name}")
        
        # Generar pasaporte específico
        gafete = maestro.generar_gafete_integrado(str(imagen_ejemplo), "123456789")
        
        if gafete:
            # Guardar resultado
            output_dir = Path("OUTPUT/plantillas_integradas")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = output_dir / "ejemplo_pasaporte_especifico.png"
            gafete.save(output_path, 'PNG', dpi=(300, 300))
            
            print(f"✅ Pasaporte generado: {output_path}")
            return True
        else:
            print("❌ Error generando pasaporte")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def verificar_estructura():
    """Verifica que la estructura del sistema esté completa"""
    print("🔍 VERIFICANDO ESTRUCTURA DEL SISTEMA")
    print("=" * 45)
    
    archivos_requeridos = [
        "SCRIPTS/script_maestro_integrado.py",
        "CONFIG/config_desde_ejemplo_ISABELALVAREZRAMIREZ5@hotmail.com_Página_1_Imagen_0001.json",
        "Plantillas_analisis/PASAPORTE-VENEZUELA-CLEAN.png",
        "TEMPLATE/Fuentes Extras/Arial.ttf",
        "TEMPLATE/Fuentes Extras/BrittanySignature.ttf",
        "TEMPLATE/Fuentes Extras/OCR-B10PitchBT Regular.otf",
        "TEMPLATE/Fuentes Extras/Pasaport Numbers Front-Regular.ttf"
    ]
    
    todos_ok = True
    
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTANTE")
            todos_ok = False
    
    if todos_ok:
        print("✅ Estructura completa")
    else:
        print("❌ Estructura incompleta")
    
    return todos_ok

def main():
    """Función principal"""
    print("📚 EJEMPLOS DE USO DEL SISTEMA DE PASAPORTES")
    print("=" * 60)
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 1. Verificar estructura
    if not verificar_estructura():
        print("\n❌ Sistema incompleto. Ejecutar 'python3 instalar.py' primero")
        return False
    
    # 2. Ejemplo básico
    if not ejemplo_basico():
        print("\n❌ Error en ejemplo básico")
        return False
    
    # 3. Ejemplo con imagen específica
    if not ejemplo_con_imagen_especifica():
        print("\n❌ Error en ejemplo específico")
        return False
    
    print("\n🎉 ¡TODOS LOS EJEMPLOS EJECUTADOS EXITOSAMENTE!")
    print("📁 Revisar resultados en OUTPUT/plantillas_integradas/")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Ejecución cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
