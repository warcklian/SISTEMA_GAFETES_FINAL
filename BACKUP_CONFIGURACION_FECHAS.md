# 📋 BACKUP: CONFIGURACIÓN DE FECHAS - ANTES Y DESPUÉS

## 🕐 Fecha de Backup: 2025-10-02 23:25:00

---

## 🔴 CONFIGURACIÓN ANTERIOR (CON REDUNDANCIA)

### **fecha_nacimiento (ANTES):**
```json
"fecha_nacimiento": {
  "layer_name": "FECHA.NACI",
  "font_size": 12,                    // ← REDUNDANTE
  "render_size_pt": 12,              // ← REDUNDANTE
  "font_color": "#000000",           // ← REDUNDANTE
  "bold_thickness": 0,               // ← REDUNDANTE
  "letter_spacing": 3.5,             // ← REDUNDANTE
  "stretch_to_fit": false,           // ← REDUNDANTE
  "position": {                      // ← REDUNDANTE
    "x": 336,                        // ← REDUNDANTE
    "y": 1013,                       // ← REDUNDANTE
    "ancho": 185,                    // ← REDUNDANTE
    "alto": 17,                      // ← REDUNDANTE
    "alignment": "top_left"          // ← REDUNDANTE
  },
  "date_format": "DD / MMM / MMM / YYYY",
  "contenedores_individuales": {
    "dia": {
      "x": 0,
      "y": 0,
      "ancho": 25,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#FF0000",
      "grosor_borde": 2
    },
    "mes_es": {
      "x": 33,
      "y": 0,
      "ancho": 35,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#FF0000",
      "grosor_borde": 2
    },
    "mes_en": {
      "x": 76,
      "y": 0,
      "ancho": 35,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#FF0000",
      "grosor_borde": 2
    },
    "año": {
      "x": 119,
      "y": 0,
      "ancho": 40,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#FF0000",
      "grosor_borde": 2
    },
    "separador1": {
      "x": 25,
      "y": 0,
      "ancho": 8,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#0000FF",
      "grosor_borde": 2
    },
    "separador2": {
      "x": 68,
      "y": 0,
      "ancho": 8,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#0000FF",
      "grosor_borde": 2
    },
    "separador3": {
      "x": 111,
      "y": 0,
      "ancho": 8,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#0000FF",
      "grosor_borde": 2
    }
  }
}
```

---

## 🟢 CONFIGURACIÓN NUEVA (SIN REDUNDANCIA)

### **fecha_nacimiento (DESPUÉS):**
```json
"fecha_nacimiento": {
  "layer_name": "FECHA.NACI",        // ← MANTENER (necesario)
  "date_format": "DD / MMM / MMM / YYYY",  // ← MANTENER (necesario)
  "contenedores_individuales": {
    "dia": {
      "x": 0,
      "y": 0,
      "ancho": 25,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#FF0000",
      "grosor_borde": 2
    },
    "mes_es": {
      "x": 33,
      "y": 0,
      "ancho": 35,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#FF0000",
      "grosor_borde": 2
    },
    "mes_en": {
      "x": 76,
      "y": 0,
      "ancho": 35,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#FF0000",
      "grosor_borde": 2
    },
    "año": {
      "x": 119,
      "y": 0,
      "ancho": 40,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#FF0000",
      "grosor_borde": 2
    },
    "separador1": {
      "x": 25,
      "y": 0,
      "ancho": 8,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#0000FF",
      "grosor_borde": 2
    },
    "separador2": {
      "x": 68,
      "y": 0,
      "ancho": 8,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#0000FF",
      "grosor_borde": 2
    },
    "separador3": {
      "x": 111,
      "y": 0,
      "ancho": 8,
      "alto": 17,
      "font_size": 12,               // ← CONTROL INDIVIDUAL
      "font_color": "#000000",       // ← CONTROL INDIVIDUAL
      "bold_thickness": 0,           // ← CONTROL INDIVIDUAL
      "letter_spacing": 0,           // ← CONTROL INDIVIDUAL
      "color_borde": "#0000FF",
      "grosor_borde": 2
    }
  }
}
```

---

## 📊 RESUMEN DE CAMBIOS

### **❌ ELIMINADOS (Redundantes):**
- `font_size` (nivel global)
- `render_size_pt` (nivel global)
- `font_color` (nivel global)
- `bold_thickness` (nivel global)
- `letter_spacing` (nivel global)
- `stretch_to_fit` (nivel global)
- `position` completo (nivel global)

### **✅ MANTENIDOS (Necesarios):**
- `layer_name` - Para identificar el campo
- `date_format` - Para el formato de fecha
- `contenedores_individuales` - **Controles individuales completos**

### **🎯 BENEFICIOS:**
- ✅ **Sin redundancia** - Cada control tiene un solo lugar
- ✅ **Control granular** - Cada elemento es independiente
- ✅ **Configuración limpia** - Solo lo necesario
- ✅ **Fácil mantenimiento** - Sin duplicación de configuraciones

---

## 🔄 CAMPOS AFECTADOS:
- `fecha_nacimiento`
- `fecha_emision` 
- `fecha_vencimiento`

## 📁 ARCHIVO ORIGINAL:
`/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL/CONFIG/config.json`

## 🛡️ BACKUP COMPLETO:
Este archivo contiene la configuración completa antes y después del cambio para poder restaurar si es necesario.
