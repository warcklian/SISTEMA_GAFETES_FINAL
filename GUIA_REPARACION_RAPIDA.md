# 🚨 GUÍA DE REPARACIÓN RÁPIDA

## 🔧 Comandos de Emergencia

### **1. Verificar Estado del Sistema**
```bash
# Diagnóstico completo
python3 -c "
import torch, psutil, os
print(f'Python: {torch.__version__}')
print(f'CUDA: {torch.cuda.is_available()}')
print(f'GPUs: {torch.cuda.device_count()}')
print(f'RAM: {psutil.virtual_memory().percent}%')
print(f'CUDA_VISIBLE_DEVICES: {os.environ.get(\"CUDA_VISIBLE_DEVICES\", \"No definido\")}')
"
```

### **2. Reiniciar Completamente**
```bash
# Limpiar archivos de progreso
rm -rf OUTPUT/logs/progreso_actual.json
rm -rf OUTPUT/temp/*

# Verificar integridad
python3 -c "from generador_pasaportes_masivo import GeneradorPasaportesMasivo; g = GeneradorPasaportesMasivo(); print('Sistema OK')"
```

### **3. Verificar GPU**
```bash
# Verificar GPU NVIDIA
nvidia-smi

# Verificar CUDA
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPUs: {torch.cuda.device_count()}')"
```

## 🚨 Problemas Comunes y Soluciones

### **Error: "CUDA no disponible"**
```bash
# Reinstalar PyTorch con CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verificar
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

### **Error: "GPU no detectada"**
```bash
# Verificar drivers
nvidia-smi

# Instalar drivers (Ubuntu)
sudo apt update
sudo apt install nvidia-driver-525
sudo reboot
```

### **Error: "Memoria insuficiente"**
```bash
# Verificar memoria
free -h
nvidia-smi

# Reducir tamaño de lote (editar generador_pasaportes_masivo.py línea 308)
# Cambiar: self.tamano_lote = 50
# Por: self.tamano_lote = 10
```

### **Error: "Sistema se cuelga"**
```bash
# Verificar configuración de memoria
python3 -c "
from generador_pasaportes_masivo import GeneradorPasaportesMasivo
g = GeneradorPasaportesMasivo()
print(f'Liberar cada: {g.gestor_memoria.liberar_cada}')
print(f'Umbral memoria: {g.gestor_memoria.umbral_memoria}%')
print(f'Tamaño lote: {g.tamano_lote}')
"

# Ajustar si es necesario (editar generador_pasaportes_masivo.py):
# Línea 250: liberar_cada=50 -> liberar_cada=25
# Línea 308: tamano_lote=50 -> tamano_lote=25
```

### **Error: "No se puede continuar"**
```bash
# Verificar archivo de progreso
ls -la OUTPUT/logs/progreso_actual.json

# Eliminar para reiniciar
rm OUTPUT/logs/progreso_actual.json

# O continuar manualmente
python3 SCRIPTS/continuar_desde_xlsx.py
```

### **Error: "Archivo Excel no encontrado"**
```bash
# Verificar archivos Excel
ls -la DATA/*.xlsx DATA/*.xls

# Verificar permisos
chmod 644 DATA/*.xlsx
```

### **Error: "No se encontraron imágenes"**
```bash
# Verificar estructura
ls -la DATA/Imagenes_Mujeres/
ls -la DATA/Imagenes_Hombres/

# Crear directorios si no existen
mkdir -p DATA/Imagenes_Mujeres DATA/Imagenes_Hombres
```

### **Error: "Permisos denegados"**
```bash
# Dar permisos de escritura
chmod -R 755 OUTPUT/
chmod -R 755 DATA/

# Cambiar propietario si es necesario
sudo chown -R $USER:$USER OUTPUT/ DATA/
```

### **Error: "Espacio en disco insuficiente"**
```bash
# Verificar espacio
df -h

# Limpiar temporales
rm -rf OUTPUT/temp/*
rm -rf /tmp/*
```

## 🔍 Diagnóstico Avanzado

### **Script de Diagnóstico Completo**
```bash
# Crear y ejecutar diagnóstico
cat > diagnostico.py << 'EOF'
#!/usr/bin/env python3
import sys, os, torch, psutil

print("🔍 DIAGNÓSTICO DEL SISTEMA")
print("=" * 50)

# Python
print(f"Python: {sys.version}")

# GPU
if torch.cuda.is_available():
    print(f"CUDA: ✅ {torch.cuda.device_count()} GPU(s)")
    for i in range(torch.cuda.device_count()):
        print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"  VRAM: {torch.cuda.get_device_properties(i).total_memory / (1024**3):.1f} GB")
else:
    print("CUDA: ❌ No disponible")

# Memoria
mem = psutil.virtual_memory()
print(f"RAM: {mem.total / (1024**3):.1f} GB total, {mem.available / (1024**3):.1f} GB disponible")

# Variables de entorno
print(f"CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES', 'No definido')}")
print(f"MEDIAPIPE_GPU: {os.environ.get('MEDIAPIPE_GPU', 'No definido')}")

# Dependencias
try:
    import mediapipe
    print("MediaPipe: ✅")
except ImportError:
    print("MediaPipe: ❌")

try:
    import rembg
    print("rembg: ✅")
except ImportError:
    print("rembg: ❌")

try:
    import onnxruntime
    print("onnxruntime: ✅")
except ImportError:
    print("onnxruntime: ❌")
EOF

python3 diagnostico.py
rm diagnostico.py
```

## 🚀 Comandos de Recuperación

### **Reinstalar Dependencias**
```bash
# Reinstalar todo
pip install --upgrade -r requirements.txt

# Verificar instalación
python3 -c "import torch, mediapipe, rembg, onnxruntime; print('Todas las dependencias OK')"
```

### **Limpiar y Reiniciar**
```bash
# Limpiar completamente
rm -rf OUTPUT/logs/progreso_actual.json
rm -rf OUTPUT/temp/*
rm -rf /tmp/*

# Reiniciar sistema
python3 generador_pasaportes_masivo.py
```

### **Verificar Integridad**
```bash
# Verificar que el sistema funciona
python3 -c "from generador_pasaportes_masivo import GeneradorPasaportesMasivo; g = GeneradorPasaportesMasivo(); print('Sistema OK')"
```

## 📞 Soporte de Emergencia

### **Si nada funciona:**
1. **Ejecutar diagnóstico completo** (script arriba)
2. **Verificar logs**: `OUTPUT/logs/errores.log`
3. **Comprobar espacio**: `df -h`
4. **Verificar memoria**: `free -h`
5. **Revisar GPU**: `nvidia-smi`

### **Comandos de emergencia:**
```bash
# Reiniciar completamente
rm -rf OUTPUT/logs/progreso_actual.json
rm -rf OUTPUT/temp/*
python3 generador_pasaportes_masivo.py

# Verificar integridad
python3 -c "from generador_pasaportes_masivo import GeneradorPasaportesMasivo; g = GeneradorPasaportesMasivo(); print('Sistema OK')"
```

---

**📋 Esta guía cubre los problemas más comunes y sus soluciones rápidas.**
**Para problemas específicos, consultar la documentación completa en `README.md`.**
