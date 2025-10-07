#  Instalación Rápida - Sistema de Pasaportes

##  Instalación en 3 Pasos

### 1. Descargar el Proyecto
```bash
git clone https://github.com/tu-usuario/SISTEMA_GAFETES_FINAL.git
cd SISTEMA_GAFETES_FINAL
```

### 2. Instalación Automática
```bash
python3 instalar_completo.py
```

### 3. Usar el Sistema
```bash
python3 generador_pasaportes_masivo.py
```

##  ¡Listo! El sistema está funcionando

---

##  Requisitos Mínimos

- **Python 3.8+** (recomendado 3.9+)
- **RAM**: 8GB mínimo, 16GB recomendado
- **GPU**: Opcional pero recomendada (RTX 2060+)
- **Sistema**: Linux (recomendado), Windows, macOS

##  Instalación Manual (si la automática falla)

### Linux/Ubuntu
```bash
# Dependencias del sistema
sudo apt update
sudo apt install python3-pip python3-venv python3-dev build-essential

# Dependencias de Python
pip install -r requirements.txt

# Fuentes (opcional)
sudo cp TEMPLATE/Fuentes_Base/*.ttf /usr/share/fonts/truetype/
sudo cp TEMPLATE/Fuentes_Base/*.otf /usr/share/fonts/opentype/
sudo fc-cache -fv
```

### Windows
1. Instalar Python 3.8+ desde python.org
2. Abrir PowerShell como administrador
3. Ejecutar:
```powershell
pip install -r requirements.txt
```

### macOS
```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Dependencias
brew install python3
pip install -r requirements.txt
```

##  Configuración GPU (Opcional)

### NVIDIA (Recomendado)
```bash
# Verificar GPU
nvidia-smi

# Si no aparece, instalar drivers
sudo apt install nvidia-driver-525
sudo reboot
```

### Verificar GPU en Python
```python
import torch
print(f"CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

##  Estructura de Archivos

Después de la instalación, tu proyecto debe verse así:

```
SISTEMA_GAFETES_FINAL/
├── instalar_completo.py          # ← Script de instalación
├── generador_pasaportes_masivo.py # ← Generador principal
├── procesador_xlsx.py            # ← Procesador Excel
├── requirements.txt              # ← Dependencias
├── README.md                     # ← Documentación completa
├── DATA/                         # ← Coloca aquí tus archivos
│   ├── tu_archivo.xlsx          # ← Tu base de datos
│   ├── Imagenes_Mujeres/         # ← Imágenes para mujeres
│   └── Imagenes_Hombres/         # ← Imágenes para hombres
├── OUTPUT/                       # ← Resultados generados
└── TEMPLATE/                     # ← Fuentes y plantillas
```

##  Uso Básico

### 1. Preparar Datos
- Coloca tu archivo Excel en `DATA/`
- Coloca imágenes en `DATA/Imagenes_Mujeres/` y `DATA/Imagenes_Hombres/`

### 2. Ejecutar
```bash
python3 generador_pasaportes_masivo.py
```

### 3. Resultados
- Pasaportes PNG en `OUTPUT/pasaportes_visuales/`
- Datos procesados en `OUTPUT/pasaportes_generados/`

##  Solución de Problemas

### Error: "Python no encontrado"
```bash
# Verificar Python
python3 --version

# Si no está instalado (Ubuntu)
sudo apt install python3 python3-pip
```

### Error: "Módulo no encontrado"
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### Error: "GPU no detectada"
```bash
# Verificar drivers NVIDIA
nvidia-smi

# Si no aparece, instalar drivers
sudo apt install nvidia-driver-525
sudo reboot
```

### Error: "Fuentes no encontradas"
```bash
# Instalar fuentes manualmente
sudo cp TEMPLATE/Fuentes_Base/*.ttf /usr/share/fonts/truetype/
sudo cp TEMPLATE/Fuentes_Base/*.otf /usr/share/fonts/opentype/
sudo fc-cache -fv
```

##  Soporte

Si tienes problemas:

1. **Ejecuta el diagnóstico:**
```bash
python3 -c "
import sys, torch, cv2
print(f'Python: {sys.version}')
print(f'CUDA: {torch.cuda.is_available()}')
print(f'OpenCV: {cv2.__version__}')
"
```

2. **Revisa los logs:**
```bash
cat OUTPUT/logs/errores.log
```

3. **Reinstala completamente:**
```bash
rm -rf OUTPUT/logs/*
python3 instalar_completo.py
```

##  Documentación Completa

Para más detalles, lee `README.md` que incluye:
- Configuración avanzada
- Optimización de rendimiento
- Solución de problemas detallada
- Ejemplos de uso

---

** ¡El sistema está listo para usar!**