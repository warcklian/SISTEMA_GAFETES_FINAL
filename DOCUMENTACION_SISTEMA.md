## Actualización 2025-10-06: Rutas relativas, Fuentes locales y Fechas

### Rutas relativas
- El motor visual `SCRIPTS/script_maestro_integrado.py` calcula `base_path` en tiempo de ejecución desde el directorio del proyecto actual.
- Recursos consumidos desde el proyecto:
  - `CONFIG/config.json`
  - `TEMPLATE/Fuentes_Base/`
  - `TEMPLATE/PASAPORTE-VENEZUELA-CLEAN.png`
- Beneficio: portabilidad inmediata al clonar el repositorio en otro equipo.

### Fuentes locales (sin instalación del sistema)
- El validador de fuentes prioriza archivos en `TEMPLATE/Fuentes_Base`.
- Búsqueda case-insensitive por nombre (ej.: `White Sign (DemoVersion).otf`).
- Se limpia el estado interno antes de verificar para evitar falsos negativos.

### Normalización de fechas en `procesador_xlsx.py`
- Soportados y normalizados a `YYYY-MM-DD`:
  - `YYYY-MM-DD[ HH:MM:SS]` (ej.: `1998-09-04 00:00:00` → `1998-09-04`)
  - `MM/DD/YYYY` con comas/puntos o texto adicional (ej.: `03/29/1981.` → `1981-03-29`)
- El selector de archivos Excel muestra `*.xlsx` y `*.xls` y recuerda la última carpeta usada en `OUTPUT/logs/ultima_ubicacion_excel.json`.
# Sistema de Generación Masiva de Pasaportes Venezolanos

## 📋 Resumen del Sistema

Este sistema permite generar pasaportes venezolanos de forma masiva y dinámica, integrando datos del Excel con imágenes y utilizando el script maestro existente para crear pasaportes visuales completos.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **📊 Procesador de Datos Excel** (`generador_pasaportes_masivo.py`)
   - Lee datos del archivo Excel
   - Calcula edades automáticamente
   - Limpia y normaliza textos
   - Genera datos faltantes (lugar de nacimiento, fechas, etc.)
   - Asocia imágenes por edad y género

2. **🎨 Generador de Pasaportes Visuales** (`generador_pasaportes_visuales.py`)
   - Integra con el script maestro existente
   - Genera pasaportes visuales completos
   - Maneja errores y validaciones

3. **🚀 Script Maestro Completo** (`script_maestro_completo.py`)
   - Orquesta todo el proceso
   - Maneja la ejecución paso a paso
   - Genera reportes finales

## 📁 Estructura de Archivos

```
SISTEMA_PASAPORTES_FINAL/
├── DATA/
│   ├── Datos_Crear_Pasaportes.xlsx          # Datos fuente
│   ├── Imagenes_Mujeres/                    # Imágenes de mujeres
│   └── Imagenes_Hombres/                     # Imágenes de hombres
├── SCRIPTS/
│   └── script_maestro_integrado.py          # Script maestro original (con stretch_to_fit implementado)
├── CONFIG/
│   └── config.json                          # Configuración centralizada
├── TEMPLATE/
│   ├── PASAPORTE-VENEZUELA-CLEAN.png        # Plantilla base
│   └── Fuentes_Base/                        # Fuentes especializadas
├── OUTPUT/
│   ├── pasaportes_generados/                 # Datos procesados
│   └── pasaportes_visuales/                 # Pasaportes visuales
├── generador_pasaportes_masivo.py            # Procesador de datos
├── test_pasaportes_config.py                 # Sistema de pruebas
├── procesador_xlsx.py                        # Procesador Excel→CSV
├── PROJECT_STRUCTURE.md                      # Documentación de estructura
├── REGLAS_MEMORIA.md                         # Reglas de desarrollo
└── DOCUMENTACION_SISTEMA.md                 # Esta documentación
```

### **📋 Documentación de Estructura**
- **`PROJECT_STRUCTURE.md`**: Documentación completa de la estructura del proyecto, función de cada archivo y sus dependencias
- **`REGLAS_MEMORIA.md`**: Reglas de desarrollo implementadas (REGLA 16 y 17)

## 🎯 **MEJORAS IMPLEMENTADAS**

### **✅ Configuración Centralizada**
- **Todas las configuraciones** en `CONFIG/config.json`
- **Sin parámetros hardcodeados** en el código
- **Firma más grande**: `font_size: 25` (antes 17)
- **Contenedor más grande**: `ancho: 200, alto: 60` (antes 155x50)
- **Color mejorado**: `#444549` para mejor visibilidad

### **✅ Sistema de Ajuste Automático de Texto Vertical**
- **`stretch_to_fit: true`** para números de pasaporte verticales
- **Ajuste automático** del texto al contenedor sin salirse
- **Posición optimizada**: Y: 135 para evitar conflictos con el número "3"
- **Escalado inteligente**: Solo cuando es necesario, máximo 80% del tamaño original
- **Detección automática**: "✅ Texto ya cabe en el contenedor" cuando no necesita escalado
- **Alineación perfecta**: `bottom_center` mantenida en todas las posiciones

### **✅ Sistema de Pruebas Integrado**
- **`test_pasaportes_config.py`**: Sistema de pruebas ligado a producción
- **3 muestras** para pruebas rápidas
- **Versiones con y sin contenedores** para ajustes visuales
- **Misma configuración** que el sistema de producción
- **Números de pasaporte variados** (9 dígitos) para probar diferentes longitudes

### **✅ Documentación Completa**
- **`PROJECT_STRUCTURE.md`**: Estructura completa del proyecto
- **Función de cada archivo** y sus dependencias
- **Flujos de trabajo** claramente documentados
- **Casos de uso** comunes especificados

### **✅ Reglas de Desarrollo**
- **REGLA 16**: Documentación de estructura de proyecto
- **REGLA 17**: Configuraciones modulares
- **Eliminación de duplicación** de archivos de prueba
- **Organización** por buenas prácticas

## 🔄 Flujo de Procesamiento

### Paso 1: Análisis de Datos Excel
- **Entrada**: `Datos_Crear_Pasaportes.xlsx`
- **Campos disponibles**:
  - `GENERO`: Género (F/M)
  - `PRIMER_NOMBRE`: Primer nombre
  - `SEGUNDO_NOMBRE`: Segundo nombre (opcional)
  - `PRIMER_APELLIDO`: Primer apellido
  - `SEGUNDO_APELLIDO`: Segundo apellido (opcional)
  - `FECHA_NACIMIENTO`: Fecha de nacimiento (YYYY-MM-DD)
  - `CORREO`: Correo electrónico

### Paso 2: Procesamiento de Datos
- **Limpieza de textos**: Mayúsculas, sin acentos, sin espacios excesivos
- **Cálculo de edad**: Automático basado en fecha de nacimiento
- **Generación de datos faltantes**:
  - Número de pasaporte (aleatorio)
  - Lugar de nacimiento (aleatorio de estados venezolanos)
  - Fechas de emisión y vencimiento
  - Códigos MRZ
  - Código de verificación

### Paso 3: Asociación de Imágenes
- **Criterio**: Edad y género
- **Nomenclatura**: `massive_venezuelan_mujer_{edad}_{numero}_{timestamp}.png`
- **Tolerancia**: ±3 años para coincidencia de edad

### Paso 4: Generación Visual
- **Integración**: Con script maestro existente
- **Salida**: Pasaportes visuales completos en PNG
- **Resolución**: 300 DPI

## 🎯 Campos del Pasaporte Venezolano

### Datos del Excel (Fuente)
| Campo | Descripción | Procesamiento |
|-------|-------------|---------------|
| `GENERO` | Género (F/M) | Directo |
| `PRIMER_NOMBRE` | Primer nombre | Limpieza + mayúsculas |
| `SEGUNDO_NOMBRE` | Segundo nombre | Limpieza + mayúsculas |
| `PRIMER_APELLIDO` | Primer apellido | Limpieza + mayúsculas |
| `SEGUNDO_APELLIDO` | Segundo apellido | Limpieza + mayúsculas |
| `FECHA_NACIMIENTO` | Fecha nacimiento | Cálculo de edad |
| `CORREO` | Correo electrónico | Referencia |

### Datos Generados Automáticamente
| Campo | Descripción | Método |
|-------|-------------|--------|
| `numero_pasaporte` | Número de pasaporte | Aleatorio (100M-999M) |
| `lugar_nacimiento` | Lugar de nacimiento | Aleatorio (24 estados) |
| `fecha_emision` | Fecha de emisión | Aleatoria (últimos 5 años) |
| `fecha_vencimiento` | Fecha de vencimiento | 10 años después |
| `cedula` | Número de cédula | Simulado |
| `codigo_verificacion` | Código verificación | Basado en fecha nacimiento |
| `mrz_linea1` | Código MRZ línea 1 | Formato estándar |
| `mrz_linea2` | Código MRZ línea 2 | Formato estándar |

### Datos Fijos
| Campo | Valor | Descripción |
|-------|-------|-------------|
| `tipo` | P | Tipo de documento |
| `pais_emisor` | VEN | País emisor |
| `nacionalidad` | VENEZOLANA | Nacionalidad |
| `firma` | Firma Digital | Texto de firma |

## 🚀 Uso del Sistema

### Ejecución Completa
```bash
python3 script_maestro_completo.py --modo completo --limite 10
```

### Solo Procesamiento de Datos
```bash
python3 script_maestro_completo.py --modo datos --limite 5
```

### Solo Generación Visual
```bash
python3 script_maestro_completo.py --modo visuales --limite 5
```

### Crear Pasaporte de Ejemplo
```bash
python3 generador_pasaportes_visuales.py --ejemplo
```

### Listar Campos Requeridos
```bash
python3 generador_pasaportes_masivo.py --listar-campos
```

## 📊 Estados y Capitales de Venezuela

El sistema incluye los 24 estados de Venezuela para asignación aleatoria de lugar de nacimiento:

| Estado | Capital |
|--------|---------|
| Amazonas | Puerto Ayacucho |
| Anzoátegui | Barcelona |
| Apure | San Fernando de Apure |
| Aragua | Maracay |
| Barinas | Barinas |
| Bolívar | Ciudad Bolívar |
| Carabobo | Valencia |
| Cojedes | San Carlos |
| Delta Amacuro | Tucupita |
| Distrito Capital | Caracas |
| Falcón | Coro |
| Guárico | San Juan de los Morros |
| Lara | Barquisimeto |
| Mérida | Mérida |
| Miranda | Los Teques |
| Monagas | Maturín |
| Nueva Esparta | La Asunción |
| Portuguesa | Guanare |
| Sucre | Cumaná |
| Táchira | San Cristóbal |
| Trujillo | Trujillo |
| Vargas | La Guaira |
| Yaracuy | San Felipe |
| Zulia | Maracaibo |

## 🔧 Configuración y Personalización

### Sistema de Ajuste Automático de Texto Vertical
```json
"numero_pasaporte_vertical1": {
  "stretch_to_fit": true,
  "position": {
    "x": 53,
    "y": 135,
    "ancho": 72,
    "alto": 439,
    "alignment": "bottom_center"
  }
}
```

### Rango de Números de Pasaporte
```python
self.rango_pasaporte_min = 100000000
self.rango_pasaporte_max = 999999999
```

### Tolerancia de Edad para Imágenes
```python
if abs(edad_imagen - edad) <= 3:  # ±3 años
```

### Formato de Fechas
- **Entrada**: YYYY-MM-DD
- **Salida**: DD / MMM / MMM / YYYY

### Características del Sistema de Ajuste Automático
- **Detección inteligente**: Solo escala cuando el texto excede el contenedor
- **Límite de escalado**: Máximo 80% del tamaño original para evitar distorsión
- **Posicionamiento optimizado**: Y: 135 para evitar conflictos con elementos superiores
- **Alineación consistente**: `bottom_center` mantenida en todas las posiciones
- **Mensajes informativos**: "✅ Texto ya cabe en el contenedor" cuando no necesita ajuste

## 📈 Estadísticas del Sistema

### Datos de Entrada
- **Total registros**: 180
- **Género**: 100% Femenino
- **Nombres únicos**: 163
- **Apellidos únicos**: 159
- **Fechas únicas**: 177

### Procesamiento
- **Limpieza de textos**: Automática
- **Cálculo de edad**: Automático
- **Asociación de imágenes**: Por edad y género
- **Generación de datos**: Aleatoria controlada

## 🎯 Casos de Uso

### 1. Generación Masiva Completa
```bash
# Procesar todos los registros
python3 script_maestro_completo.py --modo completo
```

### 2. Prueba con Límite
```bash
# Procesar solo 5 registros para prueba
python3 script_maestro_completo.py --modo completo --limite 5
```

### 3. Solo Datos
```bash
# Solo procesar datos sin generar visuales
python3 script_maestro_completo.py --modo datos --limite 10
```

### 4. Solo Visuales
```bash
# Solo generar pasaportes visuales
python3 script_maestro_completo.py --modo visuales --limite 10
```

## 🔍 Verificación y Validación

### Archivos Generados
- **Datos procesados**: JSON + Excel
- **Pasaportes visuales**: PNG (300 DPI)
- **Reportes**: TXT con estadísticas
- **Resúmenes**: JSON + Excel

### Validaciones Automáticas
- ✅ Existencia de imágenes
- ✅ Formato de fechas
- ✅ Rango de números de pasaporte
- ✅ Coincidencia de edad con imágenes
- ✅ Integridad de datos

## 🚨 Manejo de Errores

### Errores Comunes
1. **Imagen no encontrada**: Se selecciona imagen aleatoria
2. **Fecha inválida**: Se usa fecha por defecto
3. **Datos faltantes**: Se generan automáticamente
4. **Error de script maestro**: Se reporta y continúa

### Logs y Reportes
- **Progreso en tiempo real**: Console output
- **Errores detallados**: Con stack trace
- **Estadísticas finales**: Archivos de reporte
- **Resúmenes**: JSON y Excel

## 📋 Checklist de Verificación

### Antes de Ejecutar
- [ ] Archivo Excel existe y es válido
- [ ] Imágenes disponibles en carpetas correctas
- [ ] Script maestro funcional
- [ ] Permisos de escritura en OUTPUT/

### Después de Ejecutar
- [ ] Archivos de datos generados
- [ ] Pasaportes visuales creados
- [ ] Reportes generados
- [ ] Sin errores críticos

## 🎉 Resultados Esperados

### Archivos de Salida
```
OUTPUT/
├── pasaportes_generados/
│   ├── pasaportes_procesados_YYYYMMDD_HHMMSS.json
│   └── pasaportes_procesados_YYYYMMDD_HHMMSS.xlsx
├── pasaportes_visuales/
│   ├── pasaporte_123456789_001.png
│   ├── pasaporte_123456790_002.png
│   └── ...
└── reporte_final_YYYYMMDD_HHMMSS.txt
```

### Estadísticas Típicas
- **Tiempo de procesamiento**: ~2-3 segundos por pasaporte
- **Tamaño de archivos**: ~500KB por pasaporte PNG
- **Resolución**: 300 DPI
- **Formato**: PNG con transparencia

## 🔧 Mantenimiento y Actualizaciones

### Actualizar Lista de Estados
Modificar `self.estados_venezuela` en `generador_pasaportes_masivo.py`

### Cambiar Rango de Pasaportes
Modificar `self.rango_pasaporte_min` y `self.rango_pasaporte_max`

### Ajustar Tolerancia de Edad
Modificar la condición `abs(edad_imagen - edad) <= 3`

### Personalizar Formato de Fechas
Modificar función `formatear_fecha_pasaporte()`

## 📞 Soporte y Troubleshooting

### Problemas Comunes
1. **Error de importación**: Verificar rutas de scripts
2. **Imagen no encontrada**: Verificar nomenclatura
3. **Error de permisos**: Verificar permisos de escritura
4. **Script maestro falla**: Verificar configuración JSON

### Logs de Debug
Todos los scripts incluyen logging detallado para facilitar el troubleshooting.

---

**Desarrollado por**: Sistema de Automatización de Pasaportes  
**Versión**: 1.0  
**Fecha**: 2025-09-29  
**Compatibilidad**: Python 3.6+, Linux
