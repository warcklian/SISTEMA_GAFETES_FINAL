#!/usr/bin/env python3
"""
Script de Instalación Automática del Sistema de Pasaportes
Instala dependencias y configura el sistema automáticamente
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def instalar_dependencias():
    """Instala las dependencias de Python"""
    print("🔧 Instalando dependencias de Python...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def instalar_fuentes():
    """Instala las fuentes en el sistema"""
    print("🔤 Instalando fuentes especializadas...")
    
    fuentes_dir = Path("TEMPLATE/Fuentes_Base")
    if not fuentes_dir.exists():
        print("❌ Directorio de fuentes no encontrado")
        return False
    
    sistema = platform.system()
    
    try:
        if sistema == "Windows":
            # Windows: copiar a C:\Windows\Fonts\
            import shutil
            fonts_dir = Path("C:/Windows/Fonts")
            for fuente in fuentes_dir.glob("*"):
                if fuente.is_file():
                    destino = fonts_dir / fuente.name
                    shutil.copy2(fuente, destino)
                    print(f"   ✅ {fuente.name} instalada")
            
        elif sistema == "Linux":
            # Linux: copiar a /usr/share/fonts/
            import shutil
            fonts_dir = Path("/usr/share/fonts/truetype")
            fonts_dir.mkdir(parents=True, exist_ok=True)
            
            for fuente in fuentes_dir.glob("*.ttf"):
                destino = fonts_dir / fuente.name
                shutil.copy2(fuente, destino)
                print(f"   ✅ {fuente.name} instalada")
            
            # Fuentes OpenType
            fonts_otf_dir = Path("/usr/share/fonts/opentype")
            fonts_otf_dir.mkdir(parents=True, exist_ok=True)
            
            for fuente in fuentes_dir.glob("*.otf"):
                destino = fonts_otf_dir / fuente.name
                shutil.copy2(fuente, destino)
                print(f"   ✅ {fuente.name} instalada")
            
            # Actualizar caché de fuentes
            subprocess.run(["fc-cache", "-fv"], check=True)
            
        elif sistema == "Darwin":  # macOS
            # macOS: copiar a ~/Library/Fonts/
            import shutil
            fonts_dir = Path.home() / "Library/Fonts"
            fonts_dir.mkdir(parents=True, exist_ok=True)
            
            for fuente in fuentes_dir.glob("*"):
                if fuente.is_file():
                    destino = fonts_dir / fuente.name
                    shutil.copy2(fuente, destino)
                    print(f"   ✅ {fuente.name} instalada")
        
        print("✅ Fuentes instaladas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error instalando fuentes: {e}")
        print("⚠️  Instalación manual requerida")
        return False

def crear_estructura_directorios():
    """Crea la estructura de directorios necesaria"""
    print("📁 Creando estructura de directorios...")
    
    directorios = [
        "DATA/Imagenes_OK",
        "OUTPUT/plantillas_integradas",
        "OUTPUT/plantillas_con_imagenes_originales"
    ]
    
    for directorio in directorios:
        Path(directorio).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directorio}")
    
    return True

def verificar_instalacion():
    """Verifica que la instalación sea correcta"""
    print("🔍 Verificando instalación...")
    
    # Verificar archivos principales
    archivos_requeridos = [
        "SCRIPTS/script_maestro_integrado.py",
        "CONFIG/config.json",
        "Plantillas_analisis/PASAPORTE-VENEZUELA-CLEAN.png",
        "requirements.txt"
    ]
    
    for archivo in archivos_requeridos:
        if not Path(archivo).exists():
            print(f"❌ Archivo faltante: {archivo}")
            return False
        print(f"   ✅ {archivo}")
    
    # Verificar fuentes
    fuentes_dir = Path("TEMPLATE/Fuentes_Base")
    fuentes_requeridas = [
        "Arial.ttf",
        "BrittanySignature.ttf",
        "OCR-B10PitchBT Regular.otf",
        "Pasaport Numbers Front-Regular.ttf"
    ]
    
    for fuente in fuentes_requeridas:
        if not (fuentes_dir / fuente).exists():
            print(f"❌ Fuente faltante: {fuente}")
            return False
        print(f"   ✅ {fuente}")
    
    print("✅ Verificación completada")
    return True

def main():
    """Función principal"""
    print("🚀 INSTALADOR DEL SISTEMA DE PASAPORTES")
    print("=" * 50)
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 1. Crear estructura de directorios
    if not crear_estructura_directorios():
        print("❌ Error creando directorios")
        return False
    
    # 2. Instalar dependencias
    if not instalar_dependencias():
        print("❌ Error instalando dependencias")
        return False
    
    # 3. Instalar fuentes
    if not instalar_fuentes():
        print("⚠️  Fuentes no instaladas automáticamente")
        print("📋 Instalación manual requerida:")
        print("   - Copiar archivos de TEMPLATE/Fuentes_Base/ al sistema")
        print("   - Verificar README.md para instrucciones específicas")
    
    # 4. Verificar instalación
    if not verificar_instalacion():
        print("❌ Error en verificación")
        return False
    
    print("\n🎉 ¡INSTALACIÓN COMPLETADA!")
    print("=" * 50)
    print("📋 Próximos pasos:")
    print("1. Colocar imágenes originales en DATA/Imagenes_OK/")
    print("2. Ejecutar: python3 SCRIPTS/script_maestro_integrado.py")
    print("3. Revisar resultados en OUTPUT/plantillas_integradas/")
    print("\n📖 Para más información, consultar README.md")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
