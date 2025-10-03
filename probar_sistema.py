#!/usr/bin/env python3
"""
Script de Prueba del Sistema de Pasaportes
Verifica que todos los componentes funcionen correctamente
"""

import os
import sys
import subprocess
from pathlib import Path

def verificar_python():
    """Verifica la versión de Python"""
    print("🐍 Verificando Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Se requiere Python 3.8+")
        return False

def verificar_dependencias():
    """Verifica que las dependencias estén instaladas"""
    print("📦 Verificando dependencias...")
    
    dependencias = [
        "PIL",
        "cv2", 
        "numpy",
        "pandas",
        "mediapipe",
        "rembg"
    ]
    
    todas_ok = True
    
    for dep in dependencias:
        try:
            if dep == "PIL":
                import PIL
                print(f"   ✅ {dep} - {PIL.__version__}")
            elif dep == "cv2":
                import cv2
                print(f"   ✅ {dep} - {cv2.__version__}")
            elif dep == "numpy":
                import numpy
                print(f"   ✅ {dep} - {numpy.__version__}")
            elif dep == "pandas":
                import pandas
                print(f"   ✅ {dep} - {pandas.__version__}")
            elif dep == "mediapipe":
                import mediapipe
                print(f"   ✅ {dep} - {mediapipe.__version__}")
            elif dep == "rembg":
                import rembg
                print(f"   ✅ {dep} - {rembg.__version__}")
        except ImportError:
            print(f"   ❌ {dep} - NO INSTALADO")
            todas_ok = False
    
    return todas_ok

def verificar_archivos():
    """Verifica que todos los archivos necesarios estén presentes"""
    print("📁 Verificando archivos del sistema...")
    
    archivos_requeridos = [
        "SCRIPTS/script_maestro_integrado.py",
        "CONFIG/config.json",
        "Plantillas_analisis/PASAPORTE-VENEZUELA-CLEAN.png",
        "TEMPLATE/Fuentes_Base/Arial.ttf",
        "TEMPLATE/Fuentes_Base/BrittanySignature.ttf",
        "TEMPLATE/Fuentes_Base/OCR-B10PitchBT Regular.otf",
        "TEMPLATE/Fuentes_Base/Pasaport Numbers Front-Regular.ttf",
        "requirements.txt",
        "README.md"
    ]
    
    todas_ok = True
    
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTANTE")
            todas_ok = False
    
    return todas_ok

def verificar_directorios():
    """Verifica que los directorios necesarios existan"""
    print("📂 Verificando directorios...")
    
    directorios_requeridos = [
        "SCRIPTS",
        "CONFIG", 
        "TEMPLATE/Fuentes_Base",
        "Plantillas_analisis",
        "DATA",
        "OUTPUT"
    ]
    
    todas_ok = True
    
    for directorio in directorios_requeridos:
        if Path(directorio).exists():
            print(f"   ✅ {directorio}/")
        else:
            print(f"   ❌ {directorio}/ - FALTANTE")
            todas_ok = False
    
    return todas_ok

def probar_importacion():
    """Prueba la importación del script maestro"""
    print("🔧 Probando importación del script maestro...")
    
    try:
        # Agregar SCRIPTS al path
        sys.path.append(str(Path("SCRIPTS")))
        
        # Intentar importar
        from script_maestro_integrado import ScriptMaestroIntegrado
        print("   ✅ Script maestro importado correctamente")
        
        # Intentar inicializar
        maestro = ScriptMaestroIntegrado()
        print("   ✅ Script maestro inicializado correctamente")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Error importando: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error inicializando: {e}")
        return False

def probar_configuracion():
    """Prueba la carga de configuración"""
    print("⚙️ Probando configuración...")
    
    try:
        import json
        
        config_path = "CONFIG/config.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("   ✅ Configuración cargada correctamente")
        
        # Verificar campos importantes
        campos_requeridos = [
            "field_mapping.ruta_foto",
            "field_mapping.numero_pasaporte_vertical1",
            "field_mapping.nombre",
            "field_mapping.apellido"
        ]
        
        for campo in campos_requeridos:
            partes = campo.split('.')
            valor = config
            for parte in partes:
                if parte in valor:
                    valor = valor[parte]
                else:
                    print(f"   ❌ Campo faltante: {campo}")
                    return False
        
        print("   ✅ Campos de configuración verificados")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en configuración: {e}")
        return False

def probar_plantilla():
    """Prueba la carga de la plantilla"""
    print("🖼️ Probando plantilla base...")
    
    try:
        from PIL import Image
        
        plantilla_path = "Plantillas_analisis/PASAPORTE-VENEZUELA-CLEAN.png"
        
        if not Path(plantilla_path).exists():
            print(f"   ❌ Plantilla no encontrada: {plantilla_path}")
            return False
        
        img = Image.open(plantilla_path)
        print(f"   ✅ Plantilla cargada: {img.width}x{img.height}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error cargando plantilla: {e}")
        return False

def probar_fuentes():
    """Prueba la carga de fuentes"""
    print("🔤 Probando fuentes...")
    
    try:
        from PIL import ImageFont
        
        fuentes_dir = Path("TEMPLATE/Fuentes_Base")
        fuentes_requeridas = [
            "Arial.ttf",
            "BrittanySignature.ttf", 
            "OCR-B10PitchBT Regular.otf",
            "Pasaport Numbers Front-Regular.ttf"
        ]
        
        todas_ok = True
        
        for fuente in fuentes_requeridas:
            fuente_path = fuentes_dir / fuente
            if fuente_path.exists():
                try:
                    font = ImageFont.truetype(str(fuente_path), 20)
                    print(f"   ✅ {fuente}")
                except Exception as e:
                    print(f"   ❌ {fuente} - Error cargando: {e}")
                    todas_ok = False
            else:
                print(f"   ❌ {fuente} - Archivo no encontrado")
                todas_ok = False
        
        return todas_ok
        
    except Exception as e:
        print(f"   ❌ Error probando fuentes: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA COMPLETA DEL SISTEMA DE PASAPORTES")
    print("=" * 60)
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    pruebas = [
        ("Python", verificar_python),
        ("Dependencias", verificar_dependencias),
        ("Archivos", verificar_archivos),
        ("Directorios", verificar_directorios),
        ("Importación", probar_importacion),
        ("Configuración", probar_configuracion),
        ("Plantilla", probar_plantilla),
        ("Fuentes", probar_fuentes)
    ]
    
    resultados = []
    
    for nombre, funcion in pruebas:
        print(f"\n🔍 {nombre}:")
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n📊 RESUMEN DE PRUEBAS:")
    print("=" * 30)
    
    exitosos = 0
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"   {estado} - {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Resultado: {exitosos}/{total} pruebas exitosas")
    
    if exitosos == total:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("📋 Puedes ejecutar: python3 SCRIPTS/script_maestro_integrado.py")
        return True
    else:
        print("❌ Sistema con problemas")
        print("📋 Ejecutar: python3 instalar.py para corregir")
        return False

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Prueba cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
