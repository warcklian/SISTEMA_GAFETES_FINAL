# 🚀 Instalación Rápida del Sistema de Pasaportes

## ⚡ Instalación en 3 Pasos

### 1️⃣ Instalar Dependencias
```bash
python3 instalar.py
```

### 2️⃣ Colocar Imágenes
Colocar imágenes originales en:
```
DATA/Imagenes_OK/
```

### 3️⃣ Ejecutar Sistema
```bash
python3 SCRIPTS/script_maestro_integrado.py
```

## 📁 Resultados
Los pasaportes se generan en:
```
OUTPUT/plantillas_integradas/
```

---

## 🔧 Instalación Manual (Si la automática falla)

### 1. Instalar Python 3.8+
- **Windows:** Descargar de python.org
- **Linux:** `sudo apt install python3 python3-pip`
- **macOS:** `brew install python3`

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Instalar Fuentes
**Windows:**
- Copiar archivos de `TEMPLATE/Fuentes Extras/` a `C:\Windows\Fonts\`

**Linux:**
```bash
sudo cp TEMPLATE/Fuentes\ Extras/*.ttf /usr/share/fonts/truetype/
sudo cp TEMPLATE/Fuentes\ Extras/*.otf /usr/share/fonts/opentype/
sudo fc-cache -fv
```

**macOS:**
- Doble clic en cada archivo de fuente y hacer clic en "Instalar"

### 4. Verificar Instalación
```bash
python3 probar_sistema.py
```

---

## 🎯 Uso Rápido

### Generar Pasaportes
```bash
# Usar todas las imágenes en DATA/Imagenes_OK/
python3 SCRIPTS/script_maestro_integrado.py

# Usar imagen específica
python3 SCRIPTS/script_maestro_integrado.py --foto ruta/imagen.png

# Usar número específico
python3 SCRIPTS/script_maestro_integrado.py --numero 123456789
```

### Ver Ejemplos
```bash
python3 ejemplo_uso.py
```

---

## 🐛 Solución de Problemas

### Error: "No se encontró la fuente"
- Instalar fuentes manualmente
- Verificar que estén en el sistema

### Error: "No se encontraron imágenes"
- Colocar imágenes en `DATA/Imagenes_OK/`
- Verificar formatos (PNG, JPG, JPEG)

### Error de dependencias
```bash
pip install --upgrade -r requirements.txt
```

### Error de MediaPipe
```bash
pip install --upgrade mediapipe
```

---

## 📋 Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Fuentes instaladas en el sistema
- [ ] Estructura de directorios creada
- [ ] Imágenes colocadas en `DATA/Imagenes_OK/`
- [ ] Sistema probado (`python3 probar_sistema.py`)

---

## 📞 Soporte

Si tienes problemas:
1. Ejecutar `python3 probar_sistema.py`
2. Revisar mensajes de error
3. Verificar que todos los archivos estén presentes
4. Consultar `README.md` para información detallada
