#!/usr/bin/env python3
"""
Script de Instalación Completa del Sistema de Pasaportes
Instala todas las dependencias y configura el sistema automáticamente
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando y muestra el resultado"""
    print(f"🔧 {descripcion}...")
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if resultado.returncode == 0:
            print(f"   ✅ {descripcion} completado")
            return True
        else:
            print(f"   ❌ Error en {descripcion}: {resultado.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error ejecutando {descripcion}: {e}")
        return False

def verificar_python():
    """Verifica que Python 3.8+ esté instalado"""
    print("🐍 Verificando Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requerido 3.8+)")
        return False

def instalar_dependencias_sistema():
    """Instala dependencias del sistema operativo"""
    print("🖥️ Instalando dependencias del sistema...")
    
    sistema = platform.system().lower()
    
    if sistema == "linux":
        comandos = [
            "sudo apt update",
            "sudo apt install -y python3-pip python3-venv python3-dev",
            "sudo apt install -y build-essential cmake",
            "sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1"
        ]
    elif sistema == "darwin":  # macOS
        comandos = [
            "brew install python3",
            "brew install cmake"
        ]
    elif sistema == "windows":
        print("   ⚠️ En Windows, instala manualmente:")
        print("   - Python 3.8+ desde python.org")
        print("   - Visual Studio Build Tools")
        return True
    else:
        print(f"   ⚠️ Sistema operativo no reconocido: {sistema}")
        return True
    
    for comando in comandos:
        if not ejecutar_comando(comando, f"Ejecutando: {comando}"):
            print(f"   ⚠️ Error en comando: {comando}")
    
    return True

def instalar_python_deps():
    """Instala dependencias de Python"""
    print("📦 Instalando dependencias de Python...")
    
    # Actualizar pip
    ejecutar_comando("python3 -m pip install --upgrade pip", "Actualizando pip")
    
    # Instalar dependencias desde requirements.txt
    if Path("requirements.txt").exists():
        ejecutar_comando("python3 -m pip install -r requirements.txt", "Instalando dependencias")
    else:
        print("   ❌ No se encontró requirements.txt")
        return False
    
    return True

def verificar_gpu():
    """Verifica si hay GPU disponible"""
    print("🎮 Verificando GPU...")
    
    try:
        import torch
        if torch.cuda.is_available():
            num_gpus = torch.cuda.device_count()
            print(f"   ✅ {num_gpus} GPU(s) NVIDIA detectada(s)")
            for i in range(num_gpus):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                print(f"      GPU {i}: {gpu_name} ({gpu_memory:.1f} GB)")
            return True
        else:
            print("   ⚠️ No se detectó GPU NVIDIA (usará CPU)")
            return True
    except ImportError:
        print("   ⚠️ PyTorch no instalado aún")
        return True
    except Exception as e:
        print(f"   ⚠️ Error verificando GPU: {e}")
        return True

def crear_estructura_directorios():
    """Crea la estructura de directorios necesaria"""
    print("📁 Creando estructura de directorios...")
    
    directorios = [
        "DATA",
        "DATA/Imagenes_Mujeres",
        "DATA/Imagenes_Hombres", 
        "DATA/Imagenes_Mujeres/usadas",
        "DATA/Imagenes_Hombres/usadas",
        "OUTPUT",
        "OUTPUT/pasaportes_visuales",
        "OUTPUT/pasaportes_generados",
        "OUTPUT/logs",
        "OUTPUT/temp",
        "CONFIG",
        "TEMPLATE/Fuentes_Base"
    ]
    
    for directorio in directorios:
        try:
            Path(directorio).mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {directorio}")
        except Exception as e:
            print(f"   ❌ Error creando {directorio}: {e}")
    
    return True

def instalar_fuentes():
    """Instala las fuentes del sistema"""
    print("🔤 Instalando fuentes...")
    
    fuentes_path = Path("TEMPLATE/Fuentes_Base")
    if not fuentes_path.exists():
        print("   ⚠️ No se encontró carpeta de fuentes")
        return True
    
    sistema = platform.system().lower()
    
    if sistema == "linux":
        # Copiar fuentes al sistema
        for fuente in fuentes_path.glob("*.ttf"):
            ejecutar_comando(f"sudo cp '{fuente}' /usr/share/fonts/truetype/", f"Instalando {fuente.name}")
        for fuente in fuentes_path.glob("*.otf"):
            ejecutar_comando(f"sudo cp '{fuente}' /usr/share/fonts/opentype/", f"Instalando {fuente.name}")
        
        # Actualizar cache de fuentes
        ejecutar_comando("sudo fc-cache -fv", "Actualizando cache de fuentes")
        
    elif sistema == "darwin":  # macOS
        print("   ℹ️ En macOS, instala las fuentes manualmente:")
        print("   - Abre cada archivo .ttf y .otf")
        print("   - Haz clic en 'Instalar'")
        
    elif sistema == "windows":
        print("   ℹ️ En Windows, copia las fuentes a C:\\Windows\\Fonts\\")
        print("   - Copia todos los archivos .ttf y .otf")
        print("   - Pega en C:\\Windows\\Fonts\\")
    
    return True

def crear_archivo_config():
    """Crea archivo de configuración por defecto"""
    print("⚙️ Creando configuración por defecto...")
    
    config_path = Path("CONFIG/config.json")
    if config_path.exists():
        print("   ✅ Archivo de configuración ya existe")
        return True
    
    config_default = {
        "fecha_nacimiento": {
            "font_size": 12,
            "render_size_pt": 12,
            "bold_thickness": 0,
            "letter_spacing": 0,
            "stretch_to_fit": False,
            "position": {
                "x": 336,
                "offset_x": 0,
                "alignment": "top_left"
            }
        },
        "fecha_emision": {
            "font_size": 12,
            "render_size_pt": 12,
            "bold_thickness": 0,
            "letter_spacing": 0,
            "stretch_to_fit": False,
            "position": {
                "x": 336,
                "offset_x": 0,
                "alignment": "top_left"
            }
        },
        "fecha_vencimiento": {
            "font_size": 12,
            "render_size_pt": 12,
            "bold_thickness": 0,
            "letter_spacing": 0,
            "stretch_to_fit": False,
            "position": {
                "x": 336,
                "offset_x": 0,
                "alignment": "top_left"
            }
        }
    }
    
    try:
        import json
        with open(config_path, 'w') as f:
            json.dump(config_default, f, indent=2)
        print("   ✅ Archivo de configuración creado")
        return True
    except Exception as e:
        print(f"   ❌ Error creando configuración: {e}")
        return False

def verificar_instalacion():
    """Verifica que la instalación sea correcta"""
    print("🔍 Verificando instalación...")
    
    verificaciones = []
    
    # Verificar Python
    verificaciones.append(("Python", verificar_python()))
    
    # Verificar dependencias
    try:
        import torch, cv2, numpy, pandas, PIL, psutil, mediapipe
        verificaciones.append(("Dependencias Python", True))
    except ImportError as e:
        print(f"   ❌ Dependencia faltante: {e}")
        verificaciones.append(("Dependencias Python", False))
    
    # Verificar GPU
    verificaciones.append(("GPU", verificar_gpu()))
    
    # Verificar estructura
    directorios_requeridos = ["DATA", "OUTPUT", "CONFIG", "TEMPLATE"]
    estructura_ok = all(Path(d).exists() for d in directorios_requeridos)
    verificaciones.append(("Estructura", estructura_ok))
    
    # Verificar archivos principales
    archivos_requeridos = ["generador_pasaportes_masivo.py", "procesador_xlsx.py"]
    archivos_ok = all(Path(f).exists() for f in archivos_requeridos)
    verificaciones.append(("Archivos principales", archivos_ok))
    
    # Mostrar resultados
    print("\n📊 RESUMEN DE VERIFICACIÓN:")
    for nombre, estado in verificaciones:
        estado_texto = "✅" if estado else "❌"
        print(f"   {estado_texto} {nombre}")
    
    return all(estado for _, estado in verificaciones)

def main():
    """Función principal de instalación"""
    print("🚀 INSTALADOR COMPLETO DEL SISTEMA DE PASAPORTES")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("generador_pasaportes_masivo.py").exists():
        print("❌ Error: Ejecuta este script desde el directorio del proyecto")
        print("   cd SISTEMA_GAFETES_FINAL")
        print("   python3 instalar_completo.py")
        return False
    
    pasos = [
        ("Verificando Python", verificar_python),
        ("Instalando dependencias del sistema", instalar_dependencias_sistema),
        ("Instalando dependencias de Python", instalar_python_deps),
        ("Creando estructura de directorios", crear_estructura_directorios),
        ("Instalando fuentes", instalar_fuentes),
        ("Creando configuración", crear_archivo_config),
        ("Verificando instalación", verificar_instalacion)
    ]
    
    for nombre, funcion in pasos:
        print(f"\n📋 {nombre}")
        print("-" * 40)
        
        if not funcion():
            print(f"\n❌ Error en: {nombre}")
            print("🔧 Revisa los errores arriba y ejecuta nuevamente")
            return False
    
    print("\n🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 60)
    print("📋 PRÓXIMOS PASOS:")
    print("1. Coloca tu archivo Excel en DATA/")
    print("2. Coloca imágenes en DATA/Imagenes_Mujeres/ y DATA/Imagenes_Hombres/")
    print("3. Ejecuta: python3 generador_pasaportes_masivo.py")
    print("\n📚 Para más información, lee README.md")
    
    return True

if __name__ == "__main__":
    try:
        exito = main()
        sys.exit(0 if exito else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Instalación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
