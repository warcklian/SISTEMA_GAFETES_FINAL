# 📅 Configuración de Fechas en Pasaportes - Guía Completa

## 🎯 Objetivo
Este documento explica cómo configurar correctamente las fechas en el sistema de pasaportes para mantener la armonía visual y evitar problemas comunes.

## 🚨 **PROBLEMA CRÍTICO IDENTIFICADO**

### **Síntomas del Problema**
- Las fechas se ven distorsionadas o estiradas
- Las fechas no empiezan en el mismo punto izquierdo
- Las fechas tienen tamaños diferentes entre pasaportes
- Se rompe la armonía visual del pasaporte

### **Causa Raíz**
El sistema de `stretch_to_fit` estaba estirando artificialmente el texto de las fechas, rompiendo la proporción natural y la armonía visual.

## ✅ **SOLUCIÓN IMPLEMENTADA**

### **1. Configuración JSON Corregida**

#### **Configuración Base para Todas las Fechas**
```json
{
  "font_size": 12,
  "render_size_pt": 12,
  "font_color": "#000000",
  "bold_thickness": 0,
  "letter_spacing": 0,
  "stretch_to_fit": false,
  "position": {
    "x": 336,
    "ancho": 185,
    "alto": 17,
    "offset_x": 0,
    "offset_y": -3,
    "alignment": "top_left"
  }
}
```

#### **Configuración Específica por Fecha**

**fecha_nacimiento:**
```json
"fecha_nacimiento": {
  "layer_name": "FECHA.NACI",
  "font_size": 12,
  "render_size_pt": 12,
  "font_color": "#000000",
  "bold_thickness": 0,
  "letter_spacing": 0,
  "stretch_to_fit": false,
  "position": {
    "x": 336,
    "y": 1013,
    "ancho": 185,
    "alto": 17,
    "offset_x": 0,
    "offset_y": -3,
    "alignment": "top_left"
  },
  "date_format": "DD / MMM / MMM / YYYY"
}
```

**fecha_emision:**
```json
"fecha_emision": {
  "layer_name": "FECHA.EMISION",
  "font_size": 12,
  "render_size_pt": 12,
  "font_color": "#000000",
  "bold_thickness": 0,
  "letter_spacing": 0,
  "stretch_to_fit": false,
  "position": {
    "x": 336,
    "y": 1059,
    "ancho": 185,
    "alto": 17,
    "offset_x": 0,
    "offset_y": -3,
    "alignment": "top_left"
  },
  "date_format": "DD / MMM / MMM / YYYY"
}
```

**fecha_vencimiento:**
```json
"fecha_vencimiento": {
  "layer_name": "FECHA.VENCIMIENTO",
  "font_size": 12,
  "render_size_pt": 12,
  "font_color": "#000000",
  "bold_thickness": 0,
  "letter_spacing": 0,
  "stretch_to_fit": false,
  "position": {
    "x": 336,
    "y": 1107,
    "ancho": 185,
    "alto": 17,
    "offset_x": 0,
    "offset_y": -4,
    "alignment": "top_left"
  },
  "date_format": "DD / MMM / MMM / YYYY"
}
```

### **2. Código Python Actualizado**

**Ubicación:** `SCRIPTS/script_maestro_integrado.py` - función `insertar_texto_alineado_izquierda`

```python
# Usar configuración del JSON para posicionamiento - SIEMPRE empezar en el mismo punto izquierdo
left_x = pos['x'] + pos.get('offset_x', 0)  # Posición fija desde JSON
top_y = pos['y'] + pos.get('offset_y', 0)   # Posición fija desde JSON
```

## 📋 **Parámetros Clave Explicados**

### **stretch_to_fit: false**
- **Propósito:** Desactiva el estiramiento automático del texto
- **Efecto:** Mantiene la proporción natural del texto
- **Importancia:** CRÍTICO para preservar la armonía visual

### **offset_x: 0**
- **Propósito:** Estandariza la posición horizontal de inicio
- **Efecto:** Todas las fechas empiezan en el mismo punto (x: 336)
- **Importancia:** CRÍTICO para alineación uniforme

### **font_size: 12 y render_size_pt: 12**
- **Propósito:** Tamaño consistente para todas las fechas
- **Efecto:** Uniformidad visual entre pasaportes
- **Importancia:** CRÍTICO para consistencia

### **bold_thickness: 0**
- **Propósito:** Sin negritas en las fechas
- **Efecto:** Texto limpio y legible
- **Importancia:** Estético y profesional

### **letter_spacing: 0**
- **Propósito:** Espaciado natural entre letras
- **Efecto:** Texto bien proporcionado
- **Importancia:** Legibilidad y armonía

## 🚨 **TROUBLESHOOTING: Problemas Comunes**

### **Problema 1: Las fechas se ven distorsionadas o estiradas**
**Síntomas:**
- El texto se ve alargado horizontalmente
- Las letras se ven deformadas
- Se rompe la armonía visual

**Causa:** `stretch_to_fit: true` está activado

**Solución:**
```json
"stretch_to_fit": false
```

### **Problema 2: Las fechas no empiezan en el mismo punto**
**Síntomas:**
- Las fechas están desalineadas horizontalmente
- Algunas empiezan más a la izquierda que otras
- Falta uniformidad visual

**Causa:** Diferentes valores de `offset_x`

**Solución:**
```json
"offset_x": 0  // Para todas las fechas
```

### **Problema 3: Las fechas tienen tamaños diferentes**
**Síntomas:**
- Algunas fechas se ven más grandes que otras
- Inconsistencia visual entre pasaportes
- Falta de uniformidad

**Causa:** Diferentes valores de `font_size` o `render_size_pt`

**Solución:**
```json
"font_size": 12,
"render_size_pt": 12
```

### **Problema 4: Las fechas se ven muy gruesas**
**Síntomas:**
- El texto se ve muy bold/grueso
- Falta de elegancia visual
- Texto pesado

**Causa:** `bold_thickness > 0`

**Solución:**
```json
"bold_thickness": 0
```

### **Problema 5: Las fechas tienen espaciado extraño**
**Síntomas:**
- Las letras están muy juntas o muy separadas
- Texto difícil de leer
- Falta de armonía

**Causa:** `letter_spacing` diferente de 0

**Solución:**
```json
"letter_spacing": 0
```

## ✅ **Verificación de Configuración Correcta**

### **Checklist de Verificación**
- [ ] `stretch_to_fit: false` en todas las fechas
- [ ] `offset_x: 0` en todas las fechas
- [ ] `font_size: 12` en todas las fechas
- [ ] `render_size_pt: 12` en todas las fechas
- [ ] `bold_thickness: 0` en todas las fechas
- [ ] `letter_spacing: 0` en todas las fechas
- [ ] `x: 336` en todas las fechas (posición base)
- [ ] `ancho: 185` en todas las fechas (contenedor uniforme)
- [ ] `alto: 17` en todas las fechas (altura uniforme)

### **Resultado Esperado**
- ✅ **Armonía visual preservada**: Las fechas mantienen su proporción natural
- ✅ **Alineación uniforme**: Todas las fechas empiezan en el mismo punto (x: 336)
- ✅ **Tamaño consistente**: 12pt para todas las fechas
- ✅ **Sin distorsión**: El texto no se estira artificialmente
- ✅ **Legibilidad perfecta**: Texto limpio y profesional
- ✅ **Consistencia entre pasaportes**: Mismo aspecto visual

## 🔧 **Mantenimiento y Actualizaciones**

### **Si se Modifica el Sistema**
1. **NUNCA** activar `stretch_to_fit: true` para fechas
2. **SIEMPRE** mantener `offset_x: 0` para alineación
3. **SIEMPRE** usar `font_size: 12` y `render_size_pt: 12`
4. **SIEMPRE** mantener `bold_thickness: 0`
5. **SIEMPRE** mantener `letter_spacing: 0`

### **Si se Agregan Nuevas Fechas**
- Copiar la configuración base de una fecha existente
- Cambiar solo `layer_name` y `y` (posición vertical)
- Mantener todos los demás parámetros iguales

### **Si se Cambia el Tamaño de Fuente**
- Cambiar tanto `font_size` como `render_size_pt`
- Mantener ambos valores iguales
- Aplicar el cambio a TODAS las fechas

## 📝 **Notas Importantes**

1. **Esta configuración ha sido probada exhaustivamente** y funciona correctamente
2. **NO modificar** los parámetros críticos sin justificación
3. **SIEMPRE probar** los cambios con el script de test
4. **Mantener consistencia** entre todas las fechas
5. **Documentar** cualquier cambio que se haga

---

**📅 Última actualización:** 2025-01-02  
**🔧 Versión:** 1.0  
**✅ Estado:** Probado y funcionando correctamente
