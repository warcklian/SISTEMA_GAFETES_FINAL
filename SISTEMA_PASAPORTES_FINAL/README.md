# Sistema de Automatización de Pasaportes - Versión Final

## 📋 Descripción
Sistema completo para generar pasaportes venezolanos automáticamente desde imágenes originales. Incluye procesamiento de IA, escala de grises optimizada, y todos los elementos del pasaporte.

## 🚀 Características Principales
- **Procesamiento completo de imágenes originales**
- **IA elimina fondo automáticamente** (rembg)
- **Detección facial y escalado inteligente** (MediaPipe)
- **Escala de grises tono 217** (extraído de plantilla real)
- **Todos los campos del pasaporte** (números, textos, firmas, códigos MRZ)
- **Fuentes especializadas** incluidas

## 📁 Estructura del Sistema
```
SISTEMA_PASAPORTES_FINAL/
├── SCRIPTS/
│   └── script_maestro_integrado.py    # Script principal
├── CONFIG/
│   └── config_desde_ejemplo_ISABELALVAREZRAMIREZ5@hotmail.com_Página_1_Imagen_0001.json
├── TEMPLATE/
│   └── Fuentes Extras/                # Fuentes especializadas
│       ├── Arial.ttf
│       ├── BrittanySignature.ttf
│       ├── OCR-B10PitchBT Regular.otf
│       └── Pasaport Numbers Front-Regular.ttf
├── Plantillas_analisis/
│   └── PASAPORTE-VENEZUELA-CLEAN.png  # Plantilla base
├── DATA/
│   └── Imagenes_OK/                   # Colocar imágenes originales aquí
├── OUTPUT/                            # Pasaportes generados
├── requirements.txt                   # Dependencias Python
└── README.md                          # Esta documentación
```

## 🛠️ Instalación

### 1. Requisitos del Sistema
- Python 3.8 o superior
- Sistema operativo: Windows, Linux, macOS

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Instalar Fuentes (Opcional)
Las fuentes están incluidas en `TEMPLATE/Fuentes Extras/`. Para instalarlas:

**Windows:**
- Copiar archivos .ttf y .otf a `C:\Windows\Fonts\`

**Linux:**
```bash
sudo cp TEMPLATE/Fuentes\ Extras/*.ttf /usr/share/fonts/truetype/
sudo cp TEMPLATE/Fuentes\ Extras/*.otf /usr/share/fonts/opentype/
sudo fc-cache -fv
```

**macOS:**
- Doble clic en cada archivo de fuente y hacer clic en "Instalar"

## 🎯 Uso del Sistema

### 1. Preparar Imágenes
Colocar las imágenes originales en:
```
DATA/Imagenes_OK/
```

**Formatos soportados:** PNG, JPG, JPEG

### 2. Ejecutar el Sistema
```bash
python3 SCRIPTS/script_maestro_integrado.py
```

### 3. Resultados
Los pasaportes generados se guardan en:
```
OUTPUT/plantillas_integradas/
├── gafete_integrado_imagen_original.png
└── gafete_integrado_imagen_original_con_rectangulos.png
```

## 🔧 Configuración Avanzada

### Modificar Configuración
Editar el archivo `CONFIG/config_desde_ejemplo_ISABELALVAREZRAMIREZ5@hotmail.com_Página_1_Imagen_0001.json` para:
- Cambiar posiciones de campos
- Modificar tamaños de fuente
- Ajustar colores
- Configurar dimensiones de foto

### Usar Imagen Específica
```bash
python3 SCRIPTS/script_maestro_integrado.py --foto ruta/a/imagen.png
```

### Usar Número de Pasaporte Específico
```bash
python3 SCRIPTS/script_maestro_integrado.py --numero 123456789
```

## 🎨 Procesamiento de Imágenes

### Flujo Completo:
1. **Carga imagen original**
2. **IA elimina fondo** (rembg)
3. **Suaviza bordes** (erosión + feather)
4. **Detecta cara** (MediaPipe Face Mesh)
5. **Escala inteligentemente**
6. **Aplica escala de grises tono 217**
7. **Inserta en plantilla**
8. **Agrega todos los textos y elementos**

### Características Técnicas:
- **Resolución de salida:** 300 DPI
- **Dimensiones:** 1060x1414 píxeles
- **Formato:** PNG de alta calidad
- **Escala de grises:** Tono 217 (extraído de plantilla real)

## 📊 Elementos del Pasaporte

### Campos de Texto:
- Número de pasaporte (N°PASAPORTE1 y N°PASAPORTE2)
- Nombre y apellido
- Fecha de nacimiento
- Número de documento
- Fechas de emisión y vencimiento
- Sexo, nacionalidad, lugar de nacimiento

### Elementos Especiales:
- **Firma digital** (BrittanySignature.ttf)
- **Códigos MRZ** (OCR-B10PitchBT Regular.otf)
- **Números de pasaporte** (Pasaport Numbers Front-Regular.ttf)

## 🐛 Solución de Problemas

### Error: "No se encontró la fuente"
- Instalar fuentes desde `TEMPLATE/Fuentes Extras/`
- Verificar que las fuentes estén en el sistema

### Error: "No se encontraron imágenes"
- Verificar que las imágenes estén en `DATA/Imagenes_OK/`
- Verificar formatos soportados (PNG, JPG, JPEG)

### Error de dependencias
```bash
pip install --upgrade -r requirements.txt
```

### Error de MediaPipe
```bash
pip install --upgrade mediapipe
```

## 📈 Rendimiento
- **Tiempo promedio por pasaporte:** ~8-10 segundos
- **Calidad:** Alta resolución (300 DPI)
- **Precisión:** Escala de grises exacta (tono 217)

## 🔒 Seguridad
- No se almacenan datos personales
- Procesamiento local (sin envío a servidores externos)
- Imágenes se procesan temporalmente

## 📞 Soporte
Para problemas técnicos, verificar:
1. Versión de Python (3.8+)
2. Dependencias instaladas
3. Fuentes instaladas
4. Estructura de directorios

## 📝 Changelog
- **v1.0** - Sistema completo con procesamiento de IA y escala de grises optimizada
- Integración de todas las funcionalidades en un solo script
- Procesamiento completo desde imágenes originales
- Escala de grises tono 217 extraída de plantilla real
