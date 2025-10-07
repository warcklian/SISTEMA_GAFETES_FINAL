#  Resumen de Ajustes para Producción - Sistema de Pasaportes

##  Objetivo
Este documento contiene todos los ajustes realizados en el sistema de pasaportes para replicar exactamente la configuración que funciona correctamente.

##  Archivos Modificados

### 1. `script_maestro_integrado.py`

####  **Ajustes de Zoom y Posicionamiento de Imagen**

**Ubicación:** Línea 444
```python
# ANTES:
target_face_width = target_width * 0.7  # Imagen más grande (70% vs 60%)

# DESPUÉS:
target_face_width = target_width * 0.65  # Zoom reducido (más torso visible)
```

**Ubicación:** Línea 459
```python
# ANTES:
target_y = int(target_height * 0.4)  # Ojos al 40% de altura

# DESPUÉS:
target_y = int(target_height * 0.45)  # Ojos al 45% de altura (imagen más abajo)
```

**Ubicación:** Línea 458
```python
# ANTES:
target_x = target_width // 2  # CENTRO horizontal del contenedor

# DESPUÉS:
target_x = target_width // 2 - 15  # CENTRO horizontal del contenedor (ajustado para centrado visual)
```

#### ️ **Marco Semi-transparente**

**Ubicación:** Líneas 306-328 (método `crear_marco_semitransparente`)
```python
def crear_marco_semitransparente(self, img, target_width, target_height):
    """Crea un marco semi-transparente DENTRO de las dimensiones existentes"""
    print("   ️ Creando marco semi-transparente dentro del contenedor...")
    
    # Crear una copia de la imagen para trabajar
    img_con_marco = img.copy()
    
    # Crear marco semi-transparente DENTRO de las dimensiones existentes
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img_con_marco)
    
    # Marco exterior (borde más visible) - dentro del contenedor
    marco_color_exterior = (240, 240, 240, 100)  # Gris claro con más opacidad
    draw.rectangle([0, 0, target_width-1, target_height-1], 
                  outline=marco_color_exterior, width=2)
    
    # Marco interior (borde más sutil) - dentro del contenedor
    marco_color_interior = (250, 250, 250, 60)  # Gris más claro con más opacidad
    draw.rectangle([2, 2, target_width-3, target_height-3], 
                  outline=marco_color_interior, width=1)
    
    print("    Marco semi-transparente creado dentro del contenedor")
    return img_con_marco
```

**Integración en el flujo:** Línea 564
```python
# Crear marco semi-transparente alrededor de la imagen
img_con_marco = self.crear_marco_semitransparente(img_recortada, target_width, target_height)
```

####  **Escala de Grises Tono 217**

**Ubicación:** Líneas 257-304 (método `aplicar_efectos_imagen`)
```python
def aplicar_efectos_imagen(self, img):
    """Aplica efectos de integración con el fondo a la imagen con escala de grises tono 217"""
    print("    Aplicando efectos de integración con fondo y escala de grises tono 217...")
    
    # Asegurar que la imagen esté en RGBA para preservar transparencia
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Convertir a numpy array para procesamiento
    data = np.array(img)
    
    # Crear una copia para trabajar
    result = data.copy()
    
    # Aplicar escala de grises con tono 217 (extraído de plantilla real)
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            if data[y, x, 3] > 0:  # Solo procesar píxeles no transparentes
                # Convertir a escala de grises
                gray = int(0.299 * data[y, x, 0] + 0.587 * data[y, x, 1] + 0.114 * data[y, x, 2])
                
                # Aplicar ajuste para lograr tono 217 (extraído de plantilla real)
                factor_ajuste = 217.0 / 255.0  # Factor fijo basado en el tono objetivo
                gray = int(gray * factor_ajuste)
                gray = max(0, min(255, gray))  # Asegurar rango válido
                
                # Aplicar el valor de gris a todos los canales RGB
                result[y, x, 0] = gray
                result[y, x, 1] = gray
                result[y, x, 2] = gray
                
                # Aplicar transparencia gradual (reducir alpha)
                center_x, center_y = data.shape[1] // 2, data.shape[0] // 2
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                max_distance = np.sqrt(center_x**2 + center_y**2)
                
                # Reducir transparencia gradualmente
                alpha_reduction = int(255 * (distance / max_distance * 0.3))
                result[y, x, 3] = max(0, data[y, x, 3] - alpha_reduction)
    
    # Convertir de vuelta a imagen
    img_final = Image.fromarray(result, 'RGBA')
    
    # Aplicar blur sutil
    img_final = img_final.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    print("    Efectos aplicados: escala de grises tono 217, transparencia gradual, blur sutil")
    return img_final
```

### 2. `config.json`

####  **Configuración del Contenedor de Imagen**

**Ubicación:** Líneas 222-233
```json
"ruta_foto": {
  "layer_name": "FOTO",
  "size": {
    "width": 300,
    "height": 350
  },
  "position": {
    "x": 25,
    "y": 866
  },
  "crop_mode": "center"
}
```

##  **Pasos para Implementar en Producción**

### 1. **Modificar `script_maestro_integrado.py`**

#### A. Ajustar Zoom de Imagen (Línea 444)
```python
# Cambiar de:
target_face_width = target_width * 0.7

# A:
target_face_width = target_width * 0.65  # Zoom reducido (más torso visible)
```

#### B. Ajustar Posición Vertical (Línea 459)
```python
# Cambiar de:
target_y = int(target_height * 0.4)

# A:
target_y = int(target_height * 0.45)  # Ojos al 45% de altura (imagen más abajo)
```

#### C. Ajustar Posición Horizontal (Línea 458)
```python
# Cambiar de:
target_x = target_width // 2

# A:
target_x = target_width // 2 - 15  # CENTRO horizontal del contenedor (ajustado para centrado visual)
```

#### D. Agregar Marco Semi-transparente
- Agregar el método `crear_marco_semitransparente` (líneas 306-328)
- Modificar el método `insertar_imagen_con_efectos` para incluir la llamada al marco (línea 564)

#### E. Implementar Escala de Grises Tono 217
- Reemplazar el método `aplicar_efectos_imagen` con la versión que incluye el tono 217 (líneas 257-304)

### 2. **Modificar Archivo de Configuración JSON**

#### A. Ajustar Contenedor de Imagen
```json
"ruta_foto": {
  "layer_name": "FOTO",
  "size": {
    "width": 300,
    "height": 350
  },
  "position": {
    "x": 25,
    "y": 866
  },
  "crop_mode": "center"
}
```

##  **Resumen de Cambios**

| Parámetro | Valor Anterior | Valor Nuevo | Efecto |
|-----------|----------------|--------------|---------|
| `target_face_width` | `0.7` | `0.65` | Zoom reducido, más torso visible |
| `target_y` | `0.4` | `0.45` | Imagen más abajo en el contenedor |
| `target_x` | `target_width // 2` | `target_width // 2 - 15` | Centrado visual mejorado |
| `marco_color_exterior` | - | `(240, 240, 240, 100)` | Marco semi-transparente visible |
| `marco_color_interior` | - | `(250, 250, 250, 60)` | Marco interior sutil |
| `factor_ajuste` | - | `217.0 / 255.0` | Escala de grises tono 217 |

##  **PROBLEMA CRÍTICO RESUELTO: Configuración de Fechas**

### **Problema Identificado**
El sistema de `stretch_to_fit` para las fechas estaba rompiendo la armonía visual del pasaporte al estirar artificialmente el texto.

### **Solución Implementada**
**Desactivar estiramiento automático** y mantener configuración natural:

#### **Configuración JSON Corregida (fechas)**
```json
"fecha_nacimiento": {
  "layer_name": "FECHA.NACI",
  "font_size": 12,
  "render_size_pt": 12,
  "font_color": "#000000",
  "bold_thickness": 0,
  "letter_spacing": 0,
  "stretch_to_fit": false,  // ← DESACTIVADO
  "position": {
    "x": 336,
    "y": 1013,
    "ancho": 185,
    "alto": 17,
    "offset_x": 0,  // ← ESTANDARIZADO
    "offset_y": -3,
    "alignment": "top_left"
  }
}
```

#### **Cambios Aplicados a las 3 Fechas**
-  `stretch_to_fit: false` (desactivado)
-  `offset_x: 0` (estandarizado para alineación uniforme)
-  `font_size: 12` y `render_size_pt: 12` (tamaño consistente)
-  `bold_thickness: 0` (sin negritas)
-  `letter_spacing: 0` (espaciado natural)

### **Código Python Actualizado**
**Ubicación:** `SCRIPTS/script_maestro_integrado.py` - función `insertar_texto_alineado_izquierda`

```python
# Usar configuración del JSON para posicionamiento - SIEMPRE empezar en el mismo punto izquierdo
left_x = pos['x'] + pos.get('offset_x', 0)  # Posición fija desde JSON
top_y = pos['y'] + pos.get('offset_y', 0)   # Posición fija desde JSON
```

### **Resultado**
-  **Armonía visual preservada**: Las fechas mantienen su proporción natural
-  **Alineación uniforme**: Todas las fechas empiezan en el mismo punto (x: 336)
-  **Tamaño consistente**: 12pt para todas las fechas
-  **Sin distorsión**: El texto no se estira artificialmente

##  **Verificación Final**

Después de implementar estos cambios, verificar que:

1. **Zoom:** La imagen muestra más torso (menos zoom)
2. **Posición:** La imagen está centrada horizontalmente y ligeramente más abajo
3. **Marco:** Se ve un borde semi-transparente alrededor de la foto
4. **Escala de grises:** La foto tiene el tono 217 (gris claro y suave)
5. **Fechas:** Mantienen armonía visual sin estiramiento artificial
6. **Alineación:** Todas las fechas empiezan en el mismo punto izquierdo

##  **Resultado Esperado**

-  Imagen con zoom reducido (más torso visible)
-  Centrado visual perfecto
-  Marco semi-transparente como pasaporte real
-  Escala de grises tono 217 (gris claro y suave)
-  Integración perfecta con el fondo del documento
-  **Fechas con armonía visual preservada**
-  **Alineación uniforme de fechas**

##  **TROUBLESHOOTING: Problemas Comunes**

### **Problema: Las fechas se ven distorsionadas o estiradas**
**Causa:** `stretch_to_fit: true` está activado
**Solución:** Cambiar a `stretch_to_fit: false` en el JSON

### **Problema: Las fechas no empiezan en el mismo punto**
**Causa:** Diferentes valores de `offset_x`
**Solución:** Estandarizar todos los `offset_x: 0`

### **Problema: Las fechas tienen tamaños diferentes**
**Causa:** Diferentes valores de `font_size` o `render_size_pt`
**Solución:** Estandarizar a `font_size: 12` y `render_size_pt: 12`

### **Problema: Las fechas se ven muy gruesas**
**Causa:** `bold_thickness > 0`
**Solución:** Cambiar a `bold_thickness: 0`

---

** Nota:** Estos ajustes han sido probados y funcionan correctamente. Implementar exactamente como se especifica para obtener el resultado deseado.
