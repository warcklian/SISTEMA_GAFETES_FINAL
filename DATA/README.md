# 📁 Carpeta DATA - Archivos de Entrada

Esta carpeta contiene todos los archivos de entrada necesarios para el sistema de pasaportes.

## 📋 Estructura Requerida

```
DATA/
├── README.md                    # Este archivo
├── Datos_Crear_PLANTILLA.xlsx   # Plantilla de estructura de datos
├── Imagenes_Mujeres/            # Imágenes para mujeres
│   ├── .gitkeep                 # Mantiene la carpeta en Git
│   └── [imágenes con patrón: massive_venezuelan_mujer_EDAD_*.png]
├── Imagenes_Hombres/            # Imágenes para hombres  
│   ├── .gitkeep                 # Mantiene la carpeta en Git
│   └── [imágenes con patrón: massive_venezuelan_hombre_EDAD_*.png]
└── [tu_archivo.xlsx]            # Base de datos Excel
```

## 🖼️ Imágenes Requeridas

### Para Mujeres (`Imagenes_Mujeres/`)
- **Patrón de nombre**: `massive_venezuelan_mujer_EDAD_*.png`
- **Ejemplo**: `massive_venezuelan_mujer_25_1234.png`
- **Edades**: 18-60 años
- **Formato**: PNG, JPG, JPEG

### Para Hombres (`Imagenes_Hombres/`)
- **Patrón de nombre**: `massive_venezuelan_hombre_EDAD_*.png`
- **Ejemplo**: `massive_venezuelan_hombre_30_5678.png`
- **Edades**: 18-60 años
- **Formato**: PNG, JPG, JPEG

## 📊 Base de Datos Excel

### 📋 Plantilla Incluida
- **`Datos_Crear_PLANTILLA.xlsx`** - Plantilla con la estructura correcta
- **Usar como referencia** para crear tu base de datos
- **Formato correcto** de columnas y datos

### Columnas Requeridas:
- `GENERO` - F (Femenino) o M (Masculino)
- `PRIMER_NOMBRE` - Primer nombre
- `SEGUNDO_NOMBRE` - Segundo nombre (opcional)
- `PRIMER_APELLIDO` - Primer apellido
- `SEGUNDO_APELLIDO` - Segundo apellido (opcional)
- `FECHA_NACIMIENTO` - Fecha en formato YYYY-MM-DD
- `CORREO` - Correo electrónico

### Ejemplo de Datos:
```
GENERO | PRIMER_NOMBRE | SEGUNDO_NOMBRE | PRIMER_APELLIDO | SEGUNDO_APELLIDO | FECHA_NACIMIENTO | CORREO
F      | MARIA         | JOSEFINA       | GONZALEZ        | RODRIGUEZ        | 1995-03-15       | maria@email.com
M      | CARLOS        |                | MARTINEZ        | LOPEZ            | 1988-07-22       | carlos@email.com
```

## 🎯 Cómo Usar

1. **Abre la plantilla**: `Datos_Crear_PLANTILLA.xlsx` para ver el formato correcto
2. **Crea tu base de datos** siguiendo la estructura de la plantilla
3. **Coloca tu archivo Excel** en esta carpeta
4. **Agrega imágenes** en las carpetas correspondientes
5. **Ejecuta el sistema**: `python3 generador_pasaportes_masivo.py`

## ⚠️ Notas Importantes

- **Patrón de imágenes**: El nombre debe contener la edad para que el sistema pueda hacer la correspondencia
- **Edades**: El sistema busca coincidencia exacta o por rango de edad
- **Género**: Las imágenes deben estar en la carpeta correcta según el género
- **Formato de fechas**: Debe ser YYYY-MM-DD para que el sistema calcule la edad correctamente

## 🔧 Solución de Problemas

### Error: "No se encontraron imágenes"
- Verifica que las imágenes estén en la carpeta correcta
- Verifica que el patrón de nombre sea correcto
- Verifica que la edad en el nombre coincida con la edad calculada

### Error: "Edad no encontrada"
- Verifica que la fecha de nacimiento esté en formato YYYY-MM-DD
- Verifica que la edad calculada tenga una imagen correspondiente
- El sistema busca coincidencia exacta o por rango (18-20, 21-25, 26-30, etc.)
