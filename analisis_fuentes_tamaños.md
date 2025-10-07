#  ANÁLISIS DE FUENTES Y TAMAÑOS - DISCREPANCIAS Y CÓDIGO HARDCODEADO

##  RESUMEN EJECUTIVO

**PROBLEMA IDENTIFICADO**: Existen **DISCREPANCIAS CRÍTICAS** entre la configuración JSON y el código Python, además de **valores hardcodeados** que sobrescriben la configuración.

##  TABLA COMPARATIVA: JSON vs PYTHON

| Campo | JSON `font_size` | JSON `render_size_pt` | JSON `font_name` | Python Hardcodeado | Python Usado | / |
|-------|------------------|----------------------|------------------|-------------------|---------------|-------|
| **NOMBRES** | 63.32 | 16.5 | Arial | 63.32 (default) | 16.5 (JSON) |  |
| **APELLIDOS** | 63.32 | 16.5 | Arial | 63.32 (default) | 16.5 (JSON) |  |
| **FECHA.NACI** | 63.32 | 15 | Arial | 63.32 (default) | 15 (JSON) |  |
| **CEDULA** | 63.32 | 14.5 | Arial | 63.32 (default) | 14.5 (JSON) |  |
| **FECHA.EMISION** | 63.32 | 15 | Arial | 63.32 (default) | 15 (JSON) |  |
| **FECHA.VENCIMIENTO** | 63.32 | 15 | Arial | 63.32 (default) | 15 (JSON) |  |
| **SEXO** | 63.32 | 16.5 | Arial | 63.32 (default) | 16.5 (JSON) |  |
| **NACIONALIDAD** | 63.32 | 16.5 | Arial | 63.32 (default) | 16.5 (JSON) |  |
| **LUGAR.NACI** | 63.32 | 16.5 | Arial | 63.32 (default) | 16.5 (JSON) |  |
| **N°PASAPORTE** | 63.32 | 14.5 | Arial | 63.32 (default) | 14.5 (JSON) |  |
| **PAÍS** | 17 | 17 | Arial | 17 (default) | 17 (JSON) |  |
| **TIPO** | 17 | 15 | Arial | 17 (default) | 15 (JSON) |  |
| **N°PASAPORTE1** | 273.45 | 95 | Pasaport Numbers | 95 (fallback) | 95 (JSON) |  |
| **N°PASAPORTE2** | 104.75 | 23 | Arial | 23 (fallback) | 23 (JSON) |  |
| **LETRA.FINAL1** | 106.8 | 26.5 | OCR-B10PitchBT | 106.8 (default) | 26.5 (JSON) |  |
| **LETRA.FINAL2** | 106.8 | 26.5 | OCR-B10PitchBT | 106.8 (default) | 26.5 (JSON) |  |
| **CODE** | 16 | 20 | Arial | 16 (default) | 20 (JSON) |  |
| **LETRA.FIRMA** | 17 | 20 | BrittanySignature | 17 (default) | 20 (JSON) |  |

##  CÓDIGO HARDCODEADO IDENTIFICADO

### 1. **VALORES HARDCODEADOS EN `generar_gafete_integrado`**

```python
# LÍNEA 1393: Valor hardcodeado que NO se usa
text_size = 16.5  # pyright: ignore[reportUnusedVariable]

# LÍNEAS 1420-1428: Valores hardcodeados que SOBRESCRIBEN JSON
img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_nacimiento", fecha_nacimiento, 15)  #  HARDCODEADO
img_base = self.insertar_texto_estandar(img_base, "numero_documento", cedula, 14.5)  #  HARDCODEADO
img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_emision", fecha_emision, 15)  #  HARDCODEADO
img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_vencimiento", fecha_vencimiento, 15)  #  HARDCODEADO
img_base = self.insertar_texto_estandar(img_base, "numero_pasaporte", numero_pasaporte, 14.5)  #  HARDCODEADO
img_base = self.insertar_code_negritas(img_base, codigo_verificacion, 20)  #  HARDCODEADO

# LÍNEAS 1433-1439: Valores hardcodeados que SOBRESCRIBEN JSON
img_base = self.insertar_firma_texto(img_base, firma, 28, fuente_firma)  #  HARDCODEADO (28 vs JSON 20)
img_base = self.insertar_letra_final1(img_base, mrz_linea1, 26.5)  #  HARDCODEADO
img_base = self.insertar_letra_final2(img_base, mrz_linea2, 26.5)  #  HARDCODEADO
```

### 2. **PARÁMETROS DEFAULT HARDCODEADOS EN MÉTODOS**

```python
# MÉTODOS CON VALORES DEFAULT HARDCODEADOS:
def insertar_tipo_documento(self, img_base, tipo_documento="P", font_size_pt=17):  #  HARDCODEADO
def insertar_pais_emisor(self, img_base, pais="VEN", font_size_pt=17):  #  HARDCODEADO
def insertar_texto_estandar(self, img_base, campo, texto, font_size_pt=63.32):  #  HARDCODEADO
def insertar_nombre_alineado_izquierda(self, img_base, texto, font_size_pt=63.32):  #  HARDCODEADO
def insertar_texto_alineado_izquierda(self, img_base, campo, texto, font_size_pt=63.32):  #  HARDCODEADO
def insertar_code_negritas(self, img_base, texto, font_size_pt=16):  #  HARDCODEADO
def insertar_firma_texto(self, img_base, texto_firma="Firma Digital", font_size_pt=17, fuente_personalizada=None):  #  HARDCODEADO
def insertar_letra_final1(self, img_base, texto_letra_final1="...", font_size_pt=106.8):  #  HARDCODEADO
def insertar_letra_final2(self, img_base, texto_letra_final2="...", font_size_pt=106.8):  #  HARDCODEADO
```

## ️ PROBLEMAS CRÍTICOS IDENTIFICADOS

### 1. **SOBRESCRITURA DE CONFIGURACIÓN JSON**
- Los valores hardcodeados en `generar_gafete_integrado` **SOBRESCRIBEN** la configuración JSON
- Esto hace que el JSON sea **INEFECTIVO** para esos campos

### 2. **INCONSISTENCIA EN FIRMA**
- JSON especifica: `render_size_pt: 20`
- Python hardcodeado: `28`
- **DIFERENCIA**: 40% más grande que lo configurado

### 3. **VALORES DEFAULT OBSOLETOS**
- Los parámetros default en los métodos no se usan porque el código lee del JSON
- Crean confusión y pueden causar errores si el JSON falla

##  RECOMENDACIONES DE CORRECCIÓN

### 1. **ELIMINAR VALORES HARDCODEADOS**
```python
#  ANTES (hardcodeado):
img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_nacimiento", fecha_nacimiento, 15)

#  DESPUÉS (usar JSON):
img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_nacimiento", fecha_nacimiento)
```

### 2. **ELIMINAR PARÁMETROS DEFAULT OBSOLETOS**
```python
#  ANTES:
def insertar_tipo_documento(self, img_base, tipo_documento="P", font_size_pt=17):

#  DESPUÉS:
def insertar_tipo_documento(self, img_base, tipo_documento="P"):
```

### 3. **USAR CONFIGURACIÓN JSON EXCLUSIVAMENTE**
- Todos los métodos deben leer `render_size_pt` del JSON
- Eliminar todos los valores hardcodeados
- Mantener solo fallbacks para casos de error

##  ESTADO ACTUAL

| Aspecto | Estado | Impacto |
|---------|--------|---------|
| **Configuración JSON** |  Completa | Configuración base correcta |
| **Lectura JSON en métodos** |  Funcional | Los métodos leen correctamente del JSON |
| **Valores hardcodeados** |  **CRÍTICO** | Sobrescriben configuración JSON |
| **Consistencia** |  **PROBLEMA** | JSON vs Python no coinciden |
| **Mantenibilidad** |  **BAJA** | Cambios requieren modificar código |

##  CONCLUSIÓN

**El sistema está usando la configuración JSON correctamente en los métodos individuales, PERO los valores hardcodeados en `generar_gafete_integrado` están sobrescribiendo la configuración, haciendo que el JSON sea inefectivo para la generación real de pasaportes.**

**PRIORIDAD**: Eliminar todos los valores hardcodeados y usar exclusivamente la configuración JSON.
