#  ESTRUCTURA DEL PROYECTO - SISTEMA DE PASAPORTES

##  **PROPÓSITO**
Este documento describe la estructura completa del proyecto, la función de cada archivo y sus dependencias. Esencial para nuevos desarrolladores o instancias de chat que necesiten entender rápidamente el proyecto.

---

##  **ESTRUCTURA PRINCIPAL**

### **️ ARCHIVOS PRINCIPALES DE PRODUCCIÓN**

#### **`generador_pasaportes_masivo.py`**
- **Función**: Sistema principal de producción para generación masiva de pasaportes
- **Dependencias**: `SCRIPTS/script_maestro_integrado.py`, `CONFIG/config.json`
- **Características**:
  - Procesamiento masivo de datos CSV/Excel
  - Gestión de memoria optimizada (REGLA 15)
  - Sistema de recuperación automática
  - Procesamiento paralelo con GPU
  - Generación de firmas personalizadas
  - Asociación automática de imágenes por edad/género
- **Salidas**: Pasaportes visuales (PNG) + datos procesados (JSON/Excel)

#### **`SCRIPTS/script_maestro_integrado.py`**
- **Función**: Motor de renderizado de pasaportes visuales
- **Dependencias**: `CONFIG/config.json`, fuentes en `TEMPLATE/`
- **Características**:
  - Procesamiento de imágenes con IA (rembg, MediaPipe)
  - Renderizado de todos los elementos del pasaporte
  - Sistema de fuentes especializadas
  - Escala de grises tono 217
  - Códigos MRZ automáticos
- **Usado por**: `generador_pasaportes_masivo.py`, `test_pasaportes_config.py`

#### **`CONFIG/config.json`** (443 líneas)
- **Función**: Configuración centralizada de todos los elementos visuales
- **Dependencias**: Ninguna (archivo de configuración)
- **Contiene**:
  - Posicionamiento de todos los campos
  - Tamaños de fuentes y colores
  - Configuración de imágenes
  - Mapeo de fuentes especializadas
- **Usado por**: `script_maestro_integrado.py`, `test_pasaportes_config.py`
### **Rutas relativas actualizadas (2025-10-06)**
- El motor visual calcula `base_path` como el directorio del proyecto actual y consume:
  - `CONFIG/config.json`
  - `TEMPLATE/Fuentes_Base/`
  - `TEMPLATE/PASAPORTE-VENEZUELA-CLEAN.png`
- Reemplaza rutas absolutas antiguas, mejorando la portabilidad.

### **Fuentes locales (2025-10-06)**
- El validador de fuentes prioriza `TEMPLATE/Fuentes_Base` y realiza búsqueda case-insensitive.
---

### ** ARCHIVOS DE PRUEBA Y DESARROLLO**

#### **`test_pasaportes_config.py`** (435 líneas)
- **Función**: Sistema de pruebas para ajustes visuales
- **Dependencias**: `script_maestro_integrado.py`, `CONFIG/config.json`
- **Características**:
  - Genera solo 3 muestras para pruebas rápidas
  - Versiones con y sin contenedores para ajustes visuales
  - Validación de configuración JSON
  - Pruebas de fuentes y posicionamiento
- **Relación**: Ligado directamente con producción, usa misma configuración

#### **`procesador_xlsx.py`** (370 líneas)
- **Función**: Procesador de archivos Excel a CSV optimizado
- **Dependencias**: `pandas`, `openpyxl`
- **Características**:
  - Conversión Excel → CSV optimizado
  - Normalización de fechas
  - Validación de datos
- **Usado por**: `generador_pasaportes_masivo.py`

---

### ** ARCHIVOS DE DATOS**

#### **`DATA/`**
- **`Datos_Crear.xlsx`**: Archivo fuente principal con datos de personas
- **`Imagenes_Mujeres/`**: 664 imágenes de mujeres (332 PNG + 332 JSON)
- **`Imagenes_Hombres/`**: Imágenes de hombres
- **`resultados_pasaportes/`**: Archivos de salida procesados

#### **`TEMPLATE/`**
- **`PASAPORTE-VENEZUELA-CLEAN.png`**: Plantilla base del pasaporte
- **`Fuentes_Base/`**: Fuentes especializadas del sistema
  - `Arial.ttf`: Fuente estándar
  - `BrittanySignature.ttf`: Fuente de firmas
  - `OCR-B10PitchBT Regular.otf`: Fuente para códigos MRZ
  - `Pasaport Numbers Front-Regular.ttf`: Fuente para números de pasaporte

---

### ** ARCHIVOS DE CONFIGURACIÓN**

#### **`config_ejemplo_personalizado.json`**
- **Función**: Plantilla de configuración personalizada
- **Dependencias**: Ninguna
- **Uso**: Base para crear configuraciones específicas

#### **`requirements.txt`**
- **Función**: Dependencias Python del proyecto
- **Dependencias**: Ninguna
- **Contiene**: Lista completa de librerías necesarias

---

### **️ ARCHIVOS DE UTILIDADES**

#### **`instalar.py`**
- **Función**: Instalador automático del sistema
- **Dependencias**: `requirements.txt`
- **Características**:
  - Instalación automática de dependencias
  - Verificación de fuentes
  - Configuración inicial del sistema

#### **`probar_sistema.py`**
- **Función**: Verificador de funcionamiento del sistema
- **Dependencias**: `script_maestro_integrado.py`
- **Características**:
  - Verificación de dependencias
  - Pruebas de funcionalidad básica
  - Diagnóstico de problemas

#### **`ejemplo_uso.py`**
- **Función**: Ejemplos de uso del sistema
- **Dependencias**: `script_maestro_integrado.py`
- **Características**:
  - Ejemplos de código
  - Casos de uso comunes
  - Documentación práctica

---

### ** ARCHIVOS DE DOCUMENTACIÓN**

#### **`README.md`**
- **Función**: Documentación principal del proyecto
- **Contiene**: Instrucciones de instalación y uso

#### **`DOCUMENTACION_SISTEMA.md`**
- **Función**: Documentación técnica detallada
- **Contiene**: Arquitectura, flujos de procesamiento, estructura

#### **`INSTALACION_RAPIDA.md`**
- **Función**: Guía de instalación rápida
- **Contiene**: Pasos esenciales para configurar el sistema

#### **`GUIA_REPARACION_RAPIDA.md`**
- **Función**: Solución de problemas comunes
- **Contiene**: Diagnóstico y reparación de errores

#### **`CONFIGURACION_FECHAS_PASAPORTES.md`**
- **Función**: Documentación específica de configuración de fechas
- **Contiene**: Ajustes y optimizaciones de fechas

---

### ** ARCHIVOS DE ANÁLISIS Y REPORTES**

#### **`analisis_fuentes_tamaños.md`**
- **Función**: Análisis de fuentes y tamaños
- **Contiene**: Optimizaciones de tipografía

#### **`resumen_ajustes_produccion.md`**
- **Función**: Resumen de ajustes para producción
- **Contiene**: Configuraciones finales optimizadas

#### **`RESUMEN_IMPLEMENTACION.md`**
- **Función**: Resumen de implementaciones realizadas
- **Contiene**: Historial de cambios y mejoras

#### **`RESUMEN_MEJORAS_IMPLEMENTADAS.md`**
- **Función**: Documentación de mejoras específicas
- **Contiene**: Detalles de optimizaciones implementadas

---

### **️ ARCHIVOS DE SALIDA**

#### **`OUTPUT/`**
- **`pasaportes_generados/`**: Datos procesados (JSON/Excel)
- **`pasaportes_visuales/`**: Pasaportes visuales generados (PNG)
- **`plantillas_integradas/`**: Plantillas de prueba
- **`logs/`**: Archivos de registro del sistema
- **`temp/`**: Archivos temporales

---

##  **DEPENDENCIAS PRINCIPALES**

### **Flujo de Producción**:
```
generador_pasaportes_masivo.py
    ↓
procesador_xlsx.py (si es Excel)
    ↓
SCRIPTS/script_maestro_integrado.py
    ↓
CONFIG/config.json
    ↓
TEMPLATE/ (fuentes y plantilla)
    ↓
OUTPUT/ (resultados)
```

### **Flujo de Pruebas**:
```
test_pasaportes_config.py
    ↓
SCRIPTS/script_maestro_integrado.py
    ↓
CONFIG/config.json
    ↓
TEMPLATE/ (fuentes y plantilla)
    ↓
OUTPUT/plantillas_integradas/ (pruebas)
```

---

## ️ **ARCHIVOS CRÍTICOS**

### **NO ELIMINAR**:
- `CONFIG/config.json` - Configuración central
- `SCRIPTS/script_maestro_integrado.py` - Motor de renderizado
- `TEMPLATE/` - Fuentes y plantilla base
- `generador_pasaportes_masivo.py` - Sistema principal

### **PUEDEN REGENERARSE**:
- `OUTPUT/` - Archivos de salida
- `DATA/resultados_pasaportes/` - Resultados procesados
- Archivos temporales en `OUTPUT/temp/`

---

##  **CASOS DE USO COMUNES**

### **Para Ajustes Visuales**:
1. Usar `test_pasaportes_config.py`
2. Modificar `CONFIG/config.json`
3. Revisar resultados en `OUTPUT/plantillas_integradas/`

### **Para Producción Masiva**:
1. Preparar datos en `DATA/`
2. Ejecutar `generador_pasaportes_masivo.py`
3. Revisar resultados en `OUTPUT/pasaportes_visuales/`

### **Para Diagnóstico**:
1. Ejecutar `probar_sistema.py`
2. Revisar `GUIA_REPARACION_RAPIDA.md`
3. Verificar logs en `OUTPUT/logs/`

---

##  **NOTAS IMPORTANTES**

- **Configuración centralizada**: Todo está en `CONFIG/config.json`
- **Sin parámetros hardcodeados**: Todo configurable desde JSON
- **Sistema de recuperación**: Continúa desde donde se quedó
- **Optimización de memoria**: Gestión inteligente de recursos
- **Pruebas integradas**: Sistema de pruebas ligado a producción

---

*Este documento debe mantenerse actualizado cuando se agreguen nuevos archivos o se modifique la estructura del proyecto.*
