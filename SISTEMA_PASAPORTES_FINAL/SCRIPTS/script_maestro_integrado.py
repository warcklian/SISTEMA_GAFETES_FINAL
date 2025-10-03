#!/usr/bin/env python3
"""
Script Maestro Integrado - Sistema de Automatización de Gafetes
Integra todas las implementaciones que ya funcionan correctamente:
1. Imagen con efectos (escala de grises, integración con fondo)
2. Número de pasaporte (N°PASAPORTE1) con tamaño 90, negritas, sin padding
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import argparse
import cv2
import mediapipe as mp

class ScriptMaestroIntegrado:
    def __init__(self, config_path=None):
        """Inicializa el script maestro con configuración"""
        self.config_path = config_path or '/media/warcklian/DATA_500GB/CODE/Plantillas_PSD_Automatizar/CONFIG/config_desde_ejemplo_ISABELALVAREZRAMIREZ5@hotmail.com_Página_1_Imagen_0001.json'
        self.config = self.cargar_configuracion()
        self.base_path = Path('/media/warcklian/DATA_500GB/CODE/Plantillas_PSD_Automatizar')
        self.fuentes_dir = self.base_path / 'TEMPLATE' / 'Fuentes Extras'
        self.plantilla_clean_path = self.base_path / 'Plantillas_analisis' / 'PASAPORTE-VENEZUELA-CLEAN.png'
        
        # Configuración de fuentes
        self.font_paths = {
            "OCR-B10PitchBT Regular.otf": str(self.fuentes_dir / "OCR-B10PitchBT Regular.otf"),
            "BrittanySignature.ttf": str(self.fuentes_dir / "BrittanySignature.ttf"),
            "Pasaport Numbers Front-Regular.ttf": str(self.fuentes_dir / "Pasaport Numbers Front-Regular.ttf"),
            "Arial": str(self.fuentes_dir / "Arial.ttf") 
        }
        
        # Inicializar MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
    def cargar_configuracion(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo de configuración: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error en el archivo de configuración: {e}")
            sys.exit(1)
    
    def cargar_plantilla_clean(self):
        """Carga la plantilla limpia"""
        try:
            if self.plantilla_clean_path.exists():
                img = Image.open(self.plantilla_clean_path)
                print(f"✅ Plantilla limpia cargada: {self.plantilla_clean_path}")
                print(f"📐 Dimensiones: {img.width}x{img.height}")
                return img
            else:
                print(f"❌ No se encontró la plantilla limpia: {self.plantilla_clean_path}")
                return None
        except Exception as e:
            print(f"❌ Error al cargar plantilla limpia: {e}")
            return None
    
    def puntos_a_pixeles(self, puntos, dpi=96):
        """Convierte puntos (pt) a píxeles basado en el DPI"""
        # 1 pulgada = 72 puntos
        # píxeles = (puntos / 72) * dpi
        return int((puntos / 72) * dpi)
    
    def obtener_fuente(self, font_name, font_size_pt, dpi=96):
        """Obtiene una fuente específica convirtiendo puntos a píxeles"""
        # Convertir puntos a píxeles
        font_size_px = self.puntos_a_pixeles(font_size_pt, dpi)
        
        # Resolución estricta de fuentes según proyecto (no cambiar tipografías)
        if font_name == "Arial":
            # Intentar rutas comunes del sistema para Arial sin sustituir por otras fuentes
            candidate_paths = [
                self.font_paths.get("Arial", "arial.ttf"),
                "Arial.ttf",
                "arial.ttf",
                "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
                "/usr/share/fonts/truetype/msttcorefonts/arial.ttf",
                "/usr/share/fonts/TTF/Arial.ttf",
                "/usr/share/fonts/TTF/arial.ttf",
            ]
            for p in candidate_paths:
                try:
                    font = ImageFont.truetype(p, font_size_px)
                    print(f"   ✅ Fuente Arial cargada: {font_size_pt} pt = {font_size_px} px (DPI {dpi}) desde {p}")
                    return font
                except IOError:
                    continue
            # Si no se encontró, fallar claramente para no cambiar tipografía
            raise IOError("No se encontró la fuente Arial en el sistema")
        else:
            font_path = self.font_paths.get(font_name)
            try:
                font = ImageFont.truetype(font_path, font_size_px)
                print(f"   ✅ Fuente {font_name} cargada: {font_size_pt} pt = {font_size_px} px (DPI {dpi})")
                return font
            except IOError as e:
                # Fallar explícitamente para respetar tipografías del proyecto
                raise e
    
    def simular_negritas(self, draw, x, y, text, font, fill, thickness=2):
        """Simula negritas dibujando el texto varias veces con pequeños offsets"""
        # Convertir thickness a entero para range()
        thickness_int = int(thickness)
        if thickness_int == 0:
            # Si thickness es 0, solo dibujar una vez
            draw.text((x, y), text, font=font, fill=fill)
        else:
            for i in range(-thickness_int // 2, thickness_int // 2 + 1):
                for j in range(-thickness_int // 2, thickness_int // 2 + 1):
                    draw.text((x + i, y + j), text, font=font, fill=fill)
    
    def remover_fondo_rembg(self, ruta_imagen):
        """Remover fondo usando rembg (método que ya funcionaba)"""
        try:
            from rembg import remove
            
            # Cargar imagen
            with open(ruta_imagen, 'rb') as f:
                input_data = f.read()
            
            # Eliminar fondo con IA
            output_data = remove(input_data)
            
            # Convertir a PIL
            from io import BytesIO
            img_pil = Image.open(BytesIO(output_data))
            
            return img_pil
        except Exception as e:
            print(f"   ❌ Error rembg: {e}")
            return None
    
    def refinar_contorno(self, img):
        """Refinar contorno con erosión y feather (método que ya funcionaba)"""
        try:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            alpha = img.split()[-1]
            alpha_array = np.array(alpha)
            
            # Erosión ligera
            kernel = np.ones((3,3), np.uint8)
            alpha_eroded = cv2.erode(alpha_array, kernel, iterations=1)
            
            # Feather
            alpha_feathered = cv2.GaussianBlur(alpha_eroded, (5, 5), 2)
            
            # Reconstruir
            img_array = np.array(img)
            img_array[:, :, 3] = alpha_feathered
            img_refinada = Image.fromarray(img_array, 'RGBA')
            
            return img_refinada
        except Exception as e:
            print(f"   ❌ Error refinando: {e}")
            return img
    
    def calcular_distancia_al_borde(self, mask, x, y):
        """Calcula la distancia al borde más cercano de la máscara"""
        height, width = mask.shape
        min_distance = float('inf')
        
        radius = min(15, min(width, height) // 6)
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if mask[ny, nx] == 0:  # Si encontramos un pixel de fondo
                        distance = np.sqrt(dx*dx + dy*dy)
                        min_distance = min(min_distance, distance)
        
        return min_distance if min_distance != float('inf') else radius
    
    def procesar_imagen_desde_cero(self, ruta_imagen):
        """Procesa una imagen desde cero: eliminar fondo, refinar, detectar cara, escalar, recortar"""
        # Paso 1: Remover fondo con rembg (método que ya funcionaba)
        img_sin_fondo = self.remover_fondo_rembg(ruta_imagen)
        if img_sin_fondo is None:
            return None
        
        # Paso 2: Refinar contorno
        img_refinada = self.refinar_contorno(img_sin_fondo)
        
        # Paso 3: Detectar cara y escalar
        img_final = self.detectar_cara_y_escalar(img_refinada)
        
        return img_final
    
    def detectar_cara_y_escalar(self, img):
        """Detecta la cara y escala la imagen homogéneamente"""
        try:
            # Convertir a OpenCV
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2RGB)
            results = self.face_mesh.process(img_cv)
            
            if not results.multi_face_landmarks:
                return self._escalar_simple(img)
            
            landmarks = results.multi_face_landmarks[0]
            h, w = img_cv.shape[:2]
            
            # Puntos clave del rostro
            left_eye = [landmarks.landmark[33].x * w, landmarks.landmark[33].y * h]
            right_eye = [landmarks.landmark[362].x * w, landmarks.landmark[362].y * h]
            eye_center = [(left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2]
            face_width = abs(right_eye[0] - left_eye[0]) * 2.5
            
            # Escalar basado en ancho del rostro
            target_face_width = 200  # Ancho objetivo del rostro
            scale_factor = target_face_width / face_width
            
            # Redimensionar
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            img_scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            return img_scaled
            
        except Exception as e:
            print(f"   ❌ Error detectando cara: {e}")
            return self._escalar_simple(img)
    
    def _escalar_simple(self, img):
        """Método simple de escalado como fallback"""
        try:
            current_width, current_height = img.size
            target_size = 400  # Tamaño objetivo
            scale = target_size / max(current_width, current_height)
            
            new_width = int(current_width * scale)
            new_height = int(current_height * scale)
            
            img_scaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return img_scaled
        except Exception as e:
            print(f"   ❌ Error en escalado simple: {e}")
            return img
    
    def aplicar_efectos_imagen(self, img):
        """Aplica efectos de integración con el fondo a la imagen con escala de grises tono 217"""
        print("   🎨 Aplicando efectos de integración con fondo y escala de grises tono 217...")
        
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
        
        print("   ✅ Efectos aplicados: escala de grises tono 217, transparencia gradual, blur sutil")
        return img_final
    
    def integrar_solo_contorno_persona(self, img):
        """Integra solo el contorno de la persona, eliminando fondo y marco"""
        print("   🎯 Procesando imagen para mostrar solo contorno de la persona...")
        
        # Asegurar que la imagen esté en RGBA
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Convertir a numpy array para procesamiento
        data = np.array(img)
        result = data.copy()
        
        # Obtener dimensiones
        height, width = data.shape[:2]
        
        # Método simplificado: detectar áreas con contenido vs transparencia
        # Si la imagen ya tiene canal alfa, usar eso como base
        alpha_channel = data[:, :, 3]
        
        # Crear máscara de la persona basada en el canal alfa
        # Si el canal alfa es 0, es transparente (fondo)
        # Si el canal alfa es > 0, es la persona
        person_mask = alpha_channel > 0
        
        # Si no hay canal alfa útil, usar detección de contenido
        if np.all(alpha_channel == 255):  # Si todo es opaco
            # Convertir a escala de grises para detectar contenido
            gray = np.mean(data[:, :, :3], axis=2)
            
            # Detectar áreas con contenido (no blancas/transparentes)
            # Usar umbral adaptativo
            threshold = np.percentile(gray, 20)  # Percentil 20 para detectar contenido
            person_mask = gray > threshold
        
        # Aplicar transparencia total al fondo
        background_mask = ~person_mask
        result[background_mask, 3] = 0  # Alpha = 0 para fondo
        
        # Para la persona, mantener opacidad pero con transparencia gradual en bordes
        # Crear transparencia gradual en los bordes
        for y in range(height):
            for x in range(width):
                if person_mask[y, x]:
                    # Calcular distancia al borde más cercano
                    distance_to_edge = self.calcular_distancia_al_borde_simple(person_mask, x, y)
                    max_distance = min(width, height) // 15  # Ajustar según necesidad
                    
                    if distance_to_edge < max_distance:
                        # Transparencia gradual hacia el borde
                        alpha_factor = min(1.0, distance_to_edge / max_distance)
                        result[y, x, 3] = int(255 * alpha_factor)
                    else:
                        # Área central de la persona: opaca
                        result[y, x, 3] = 255
        
        # Convertir de vuelta a imagen
        img_final = Image.fromarray(result, 'RGBA')
        
        print("   ✅ Contorno de persona procesado: fondo eliminado, solo contorno visible")
        return img_final
    
    def calcular_distancia_al_borde_simple(self, mask, x, y):
        """Calcula la distancia al borde más cercano de la máscara (versión optimizada)"""
        height, width = mask.shape
        min_distance = float('inf')
        
        # Buscar en un radio pequeño para eficiencia
        radius = min(15, min(width, height) // 6)
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    if not mask[ny, nx]:  # Si encontramos un pixel de fondo
                        distance = np.sqrt(dx*dx + dy*dy)
                        min_distance = min(min_distance, distance)
        
        return min_distance if min_distance != float('inf') else radius
    
    def recortar_imagen_por_contenedor(self, img, target_width, target_height):
        """Recorta la imagen para que no se salga del contenedor usando Face Mesh"""
        try:
            # Importar MediaPipe
            import mediapipe as mp
            import cv2
            import numpy as np
            
            # Inicializar Face Mesh
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )
            
            # Detectar rostro
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2RGB)
            results = face_mesh.process(img_cv)
            
            if not results.multi_face_landmarks:
                # Si no se detecta rostro, usar método simple
                return self._recortar_simple(img, target_width, target_height)
            
            landmarks = results.multi_face_landmarks[0]
            h, w = img_cv.shape[:2]
            
            # Puntos clave
            left_eye = [landmarks.landmark[33].x * w, landmarks.landmark[33].y * h]
            right_eye = [landmarks.landmark[362].x * w, landmarks.landmark[362].y * h]
            eye_center = [(left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2]
            face_width = abs(right_eye[0] - left_eye[0]) * 2.5
            
            # Escalar basado en ancho del rostro
            target_face_width = target_width * 0.6
            scale_factor = target_face_width / face_width
            
            # Redimensionar
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            img_scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Calcular posición del centro del rostro en imagen escalada
            eye_center_x = eye_center[0] * scale_factor
            eye_center_y = eye_center[1] * scale_factor
            
            # Posición objetivo en contenedor (ojos al 40% de altura)
            target_x = target_width // 2
            target_y = int(target_height * 0.4)
            
            # Calcular offset para centrar
            offset_x = target_x - eye_center_x
            offset_y = target_y - eye_center_y
            
            # Crear lienzo del tamaño del contenedor
            canvas = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
            
            # Pegar imagen en posición calculada
            paste_x = int(offset_x)
            paste_y = int(offset_y)
            
            # Asegurar que no se salga del lienzo
            if paste_x < 0:
                crop_left = -paste_x
                paste_x = 0
            else:
                crop_left = 0
            
            if paste_y < 0:
                crop_top = -paste_y
                paste_y = 0
            else:
                crop_top = 0
            
            # Recortar imagen si es necesario
            if crop_left > 0 or crop_top > 0:
                img_cropped = img_scaled.crop((crop_left, crop_top, 
                                              min(img_scaled.width, crop_left + target_width),
                                              min(img_scaled.height, crop_top + target_height)))
            else:
                img_cropped = img_scaled
            
            # Pegar en lienzo
            canvas.paste(img_cropped, (paste_x, paste_y), img_cropped)
            
            print(f"   ✂️ Imagen recortada con Face Mesh: {img.size} → {target_width}x{target_height}")
            return canvas
            
        except Exception as e:
            print(f"   ❌ Error recortando con Face Mesh: {e}")
            return self._recortar_simple(img, target_width, target_height)
    
    def _recortar_simple(self, img, target_width, target_height):
        """Método simple de recorte como fallback"""
        try:
            current_width, current_height = img.size
            scale_x = target_width / current_width
            scale_y = target_height / current_height
            scale = min(scale_x, scale_y)
            
            new_width = int(current_width * scale)
            new_height = int(current_height * scale)
            
            img_scaled = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            canvas = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
            
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2
            
            canvas.paste(img_scaled, (paste_x, paste_y), img_scaled)
            
            print(f"   ✂️ Imagen recortada (método simple): {current_width}x{current_height} → {target_width}x{target_height}")
            return canvas
        except Exception as e:
            print(f"   ❌ Error en recorte simple: {e}")
            return img
    
    def insertar_imagen_con_efectos(self, img_base, ruta_foto):
        """Inserta la imagen con procesamiento completo desde imagen original"""
        print(f"   📸 Procesando imagen original: {ruta_foto}")
        
        # Procesar imagen desde cero (eliminar fondo, refinar, detectar cara, escalar)
        img_procesada = self.procesar_imagen_desde_cero(ruta_foto)
        if img_procesada is None:
            print("❌ Error procesando imagen original")
            return img_base
        
        # Obtener configuración de la foto
        foto_config = self.config['field_mapping'].get('ruta_foto')
        if not foto_config:
            print("   ❌ Error: Configuración de foto no encontrada")
            return img_base
        
        # Obtener dimensiones y posición
        target_width = foto_config['size']['width']
        target_height = foto_config['size']['height']
        pos_x = foto_config['position']['x']
        pos_y = foto_config['position']['y']
        
        # Recortar imagen ANTES de redimensionar para que no se salga del marco
        img_recortada = self.recortar_imagen_por_contenedor(img_procesada, target_width, target_height)
        
        # Redimensionar imagen manteniendo proporciones
        img_recortada = img_recortada.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Aplicar efectos de integración con escala de grises tono 217
        img_recortada = self.aplicar_efectos_imagen(img_recortada)
        
        # Pegar imagen en la plantilla
        img_base.paste(img_recortada, (pos_x, pos_y), img_recortada)
        
        print(f"   ✅ Imagen procesada e insertada en posición ({pos_x}, {pos_y}) con dimensiones {target_width}x{target_height}")
        print(f"   🎯 Procesamiento completo: IA elimina fondo → suaviza bordes → escalado → escala de grises tono 217")
        return img_base
    
    def insertar_numero_pasaporte1(self, img_base, numero_pasaporte="108641398"):
        """Inserta el número de pasaporte N°PASAPORTE1 con configuración final"""
        print(f"   🔢 Insertando N°PASAPORTE1: {numero_pasaporte}")
        
        # Obtener configuración del campo N°PASAPORTE1
        field_config = self.config['field_mapping'].get('numero_pasaporte_vertical1')
        if not field_config:
            print("   ❌ Error: Configuración para 'numero_pasaporte_vertical1' no encontrada")
            return img_base
        
        pos = field_config['position']
        rect_x, rect_y = pos['x'], pos['y']
        rect_width = pos['ancho']
        rect_height = pos['alto']
        rotation = field_config.get('rotation', 0)
        layer_name = field_config['layer_name']
        font_color = '#6E5342'  # Color marrón oscuro personalizado
        
        # Usar el tamaño calibrado que ya funcionaba: 95 pt
        pasaport_font = self.obtener_fuente("Pasaport Numbers Front-Regular.ttf", 95)
        
        # Obtener el bounding box del texto
        bbox_horizontal = pasaport_font.getbbox(numero_pasaporte)
        text_w_horiz = bbox_horizontal[2] - bbox_horizontal[0]
        text_h_horiz = bbox_horizontal[3] - bbox_horizontal[1]
        
        # Crear una imagen temporal para el texto horizontal con menos padding
        temp_text_layer = Image.new('RGBA', (text_w_horiz + 5, text_h_horiz + 5), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_text_layer)
        self.simular_negritas(temp_draw, 0, 0, numero_pasaporte, pasaport_font, font_color, thickness=2)
        
        # Rotar la imagen del texto 90 grados anti-horario
        rotated_text_layer = temp_text_layer.rotate(rotation, expand=1, resample=Image.Resampling.BICUBIC)
        
        # Calcular la posición X para centrar el texto rotado horizontalmente
        # Ajustar más hacia la derecha para que esté mejor centrado en el rectángulo
        paste_x = rect_x + (rect_width - rotated_text_layer.width) // 2 + 16
        
        # Calcular la posición Y para que el texto toque mejor el borde superior interno
        # Ajustar más hacia arriba para que toque el borde superior
        paste_y = rect_y - 4
        
        # Escalar el texto para que toque exactamente los bordes internos superior e inferior
        # Usar más altura para que toque mejor el borde superior
        scale_factor = (rect_height + 8) / rotated_text_layer.height  # +8 píxeles para tocar mejor los bordes
        new_width = int(rotated_text_layer.width * scale_factor)
        new_height = int(rotated_text_layer.height * scale_factor)
        rotated_text_layer = rotated_text_layer.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"   ⚠️  Texto escalado para tocar los bordes internos: {new_width}x{new_height}")
        
        # Pegar el texto rotado en la plantilla
        img_base.paste(rotated_text_layer, (paste_x, paste_y), rotated_text_layer)
        
        print(f"   ✅ N°PASAPORTE1 insertado en posición ({paste_x}, {paste_y}) con rotación {rotation}°")
        print(f"   📏 Tamaño: 95 (negritas), escalado para tocar los bordes internos superior e inferior")
        
        return img_base
    
    def insertar_numero_pasaporte2(self, img_base, numero_pasaporte="108641398"):
        """Inserta el número de pasaporte N°PASAPORTE2 con configuración final"""
        print(f"   🔢 Insertando N°PASAPORTE2: {numero_pasaporte}")
        
        # Obtener configuración del campo N°PASAPORTE2
        field_config = self.config['field_mapping'].get('numero_pasaporte_vertical2')
        if not field_config:
            print("   ❌ Error: Configuración para 'numero_pasaporte_vertical2' no encontrada")
            return img_base
        
        pos = field_config['position']
        rect_x, rect_y = pos['x'], pos['y']
        rect_width = pos['ancho']
        rect_height = pos['alto']
        rotation = 90  # Forzar rotación 90° como N°PASAPORTE1
        layer_name = field_config['layer_name']
        font_color = field_config.get('font_color', '#000000')
        
        # Cargar la fuente Arial con tamaño reducido
        ocr_font = self.obtener_fuente("Arial", 23)  # Aumentar para mejor nitidez
        print(f"   ✅ Fuente Arial cargada con tamaño 23 pt")
        
        # Obtener el bounding box del texto
        bbox_horizontal = ocr_font.getbbox(numero_pasaporte)
        text_w_horiz = bbox_horizontal[2] - bbox_horizontal[0]
        text_h_horiz = bbox_horizontal[3] - bbox_horizontal[1]
        
        # Crear una imagen temporal para el texto horizontal con padding generoso para evitar recorte
        temp_text_layer = Image.new('RGBA', (text_w_horiz + 20, text_h_horiz + 20), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_text_layer)
        temp_draw.text((10, 10), numero_pasaporte, fill=font_color, font=ocr_font)
        
        # Rotar la imagen del texto 90 grados anti-horario
        rotated_text_layer = temp_text_layer.rotate(rotation, expand=1, resample=Image.Resampling.BICUBIC)
        
        # Escalar para que toque exactamente los bordes superior e inferior
        # Ajustar el factor de escala para que llene completamente la altura
        scale_factor_y = rect_height / rotated_text_layer.height
        new_width = int(rotated_text_layer.width * scale_factor_y)
        new_height = int(rotated_text_layer.height * scale_factor_y)
        rotated_text_layer = rotated_text_layer.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calcular la posición X para alinear a la izquierda del rectángulo, compensando el padding
        paste_x = rect_x - 17
        
        # Calcular la posición Y para que toque exactamente el borde superior
        paste_y = rect_y + 11
        
        # Pegar el texto rotado en la plantilla
        img_base.paste(rotated_text_layer, (paste_x, paste_y), rotated_text_layer)
        
        print(f"   ✅ N°PASAPORTE2 insertado en posición ({paste_x}, {paste_y}) con rotación {rotation}°")
        print(f"   📏 Tamaño: 23 pt, escalado para ajustarse al contenedor")
        
        return img_base
    
    def insertar_tipo_documento(self, img_base, tipo_documento="P", font_size_pt=15):
        """Inserta el tipo de documento TIPO con configuración final"""
        print(f"   📝 Insertando TIPO: {tipo_documento}")
        
        # Obtener configuración del campo TIPO
        field_config = self.config['field_mapping'].get('tipo_documento')
        if not field_config:
            print("   ❌ Error: Configuración para 'tipo_documento' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho = pos['ancho']
        alto = pos['alto']
        font_color = field_config.get('font_color', '#000000')
        layer_name = field_config['layer_name']
        
        # Usar la fuente Arial con tamaño variable
        font = self.obtener_fuente("Arial", font_size_pt)
        
        # Crear objeto de dibujo
        draw = ImageDraw.Draw(img_base)
        
        # Obtener el bounding box del texto
        bbox = font.getbbox(tipo_documento)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Colocar en esquina superior izquierda del rectángulo (alineado a la izquierda)
        left_x = x
        top_y = y - 4
        
        # Dibujar el texto en negritas
        self.simular_negritas(draw, left_x, top_y, tipo_documento, font, font_color, thickness=0.7)
        
        print(f"   ✅ TIPO insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: Arial, alineado a la izquierda (top-left)")
        
        return img_base
    
    def insertar_pais_emisor(self, img_base, pais="VEN"):
        """Inserta el país emisor PAÍS usando configuración JSON"""
        print(f"   🌍 Insertando PAÍS: {pais}")
        
        # Obtener configuración del campo PAÍS
        field_config = self.config['field_mapping'].get('pais')
        if not field_config:
            print("   ❌ Error: Configuración para 'pais' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho = pos['ancho']
        alto = pos['alto']
        font_color = field_config.get('font_color', '#000000')
        layer_name = field_config['layer_name']
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt_conf = field_config.get('render_size_pt', field_config.get('font_size', 12))
        # Obtener fuente desde font_mapping si existe esa lógica; si no, Arial
        font = self.obtener_fuente("Arial", font_size_pt_conf)
        
        # Crear objeto de dibujo
        draw = ImageDraw.Draw(img_base)
        
        # Obtener el bounding box del texto
        bbox = font.getbbox(pais)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Posición respetando alignment/offset del JSON
        left_x, top_y = self.calcular_posicion_desde_json(pos)
        
        # Dibujar el texto (sin negritas por defecto)
        self.simular_negritas(draw, left_x, top_y, pais, font, font_color, thickness=field_config.get('bold_thickness', 0))
        
        print(f"   ✅ PAÍS insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt_conf} pt, fuente: Arial, alineado a la izquierda (top-left)")
        
        return img_base
    
    def insertar_texto_estandar(self, img_base, campo, texto, font_size_pt=15):
        """Inserta texto con configuración estándar (Arial, tamaño en puntos)"""
        print(f"   📝 Insertando {campo}: {texto}")
        
        # Obtener configuración del campo
        field_config = self.config['field_mapping'].get(campo)
        if not field_config:
            print(f"   ❌ Error: Configuración para '{campo}' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho = pos['ancho']
        alto = pos['alto']
        font_color = field_config.get('font_color', '#000000')
        layer_name = field_config['layer_name']
        
        # Usar la fuente Arial con tamaño en puntos
        font = self.obtener_fuente("Arial", font_size_pt)
        
        # Crear objeto de dibujo
        draw = ImageDraw.Draw(img_base)
        
        # Obtener el bounding box del texto
        bbox = font.getbbox(texto)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Colocar en esquina superior izquierda del rectángulo
        left_x = x
        # Ajuste especial para sexo y numero_documento: subir 1 px más
        # TIPO, PAÍS y numero_pasaporte deben estar a la misma altura
        if campo == "numero_documento":
            top_y = y - 4
        elif campo == "sexo":
            top_y = y - 5  # Subir sexo un píxel más
        elif campo == "numero_pasaporte":
            top_y = y - 4  # Misma altura que TIPO y PAÍS
        else:
            top_y = y - 3
        
        # Dibujar el texto en negritas
        self.simular_negritas(draw, left_x, top_y, texto, font, font_color, thickness=0.7)
        
        print(f"   ✅ {campo} insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: Arial (top-left)")
        
        return img_base
    
    def insertar_nombre_alineado_izquierda(self, img_base, texto, font_size_pt=20):
        """Inserta el nombre alineado a la izquierda como los otros textos"""
        field_config = self.config['field_mapping'].get('nombre')
        if not field_config:
            print("   ❌ Error: Configuración para 'nombre' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho, alto = pos['ancho'], pos['alto']
        font_color = field_config.get('font_color', '#000000')
        
        # Obtener fuente
        font = self.obtener_fuente("Arial", font_size_pt)
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📝 Insertando nombre: {texto}")
        print(f"   ✅ Fuente Arial cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Colocar en esquina superior izquierda del rectángulo
        left_x = x
        top_y = y - 5
        
        # Dibujar el texto en negritas
        draw = ImageDraw.Draw(img_base)
        self.simular_negritas(draw, left_x, top_y, texto, font, font_color, thickness=0.7)
        
        print(f"   ✅ nombre insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: Arial, top-left")
        
        return img_base
    
    def insertar_texto_alineado_izquierda(self, img_base, campo, texto, font_size_pt=20):
        """Inserta texto alineado a la izquierda del marco interno del contenedor"""
        field_config = self.config['field_mapping'].get(campo)
        if not field_config:
            print(f"   ❌ Error: Configuración para '{campo}' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho, alto = pos['ancho'], pos['alto']
        font_color = field_config.get('font_color', '#000000')
        
        # Obtener fuente
        font = self.obtener_fuente("Arial", font_size_pt)
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📝 Insertando {campo}: {texto}")
        print(f"   ✅ Fuente Arial cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Colocar en esquina superior izquierda del rectángulo
        # Ajuste especial para fecha_nacimiento y fecha_emision: mover 1px más a la izquierda
        if campo in ["fecha_nacimiento", "fecha_emision"]:
            left_x = x - 1
        else:
            left_x = x
        # Ajuste especial para fecha_nacimiento: bajar 1 px
        # nacionalidad debe estar a la misma altura que numero_documento
        # fecha_emision debe estar a la misma altura que fecha_nacimiento
        # fecha_vencimiento debe estar a la misma altura que fecha_nacimiento y fecha_emision
        if campo == "fecha_nacimiento":
            top_y = y - 4
        elif campo == "nacionalidad":
            top_y = y - 5  # Subir nacionalidad un píxel más
        elif campo == "fecha_emision":
            top_y = y - 4  # Misma altura que fecha_nacimiento
        elif campo == "fecha_vencimiento":
            top_y = y - 4  # Misma altura que fecha_nacimiento y fecha_emision
        else:
            top_y = y - 5
        
        # Dibujar el texto en negritas
        draw = ImageDraw.Draw(img_base)
        self.simular_negritas(draw, left_x, top_y, texto, font, font_color, thickness=0.7)
        
        print(f"   ✅ {campo} insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: Arial, top-left")
        
        return img_base
    
    def insertar_code_negritas(self, img_base, texto, font_size_pt=20):
        """Inserta el campo code en negritas"""
        field_config = self.config['field_mapping'].get('code')
        if not field_config:
            print("   ❌ Error: Configuración para 'code' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho, alto = pos['ancho'], pos['alto']
        font_color = field_config.get('font_color', '#000000')
        
        # Obtener fuente Arial para el code
        font = self.obtener_fuente("Arial", font_size_pt)
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📝 Insertando code: {texto}")
        print(f"   ✅ Fuente Arial cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Crear una imagen temporal para el texto con negritas más compacto y alto
        temp_text_layer = Image.new('RGBA', (text_width + 12, text_height + 20), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_text_layer)
        # Usar color gris opaco en lugar de negro
        gray_color = "#666666"  # Gris opaco
        self.simular_negritas(temp_draw, 6, 10, texto, font, gray_color, thickness=1)
        
        # Colocar en esquina superior izquierda del rectángulo
        left_x = x - 6  # Mover texto 2 píxeles más a la izquierda
        top_y = y - 15  # Subir texto 1 píxel más
        
        # Pegar el texto con negritas en la plantilla
        img_base.paste(temp_text_layer, (left_x, top_y), temp_text_layer)
        
        print(f"   ✅ code insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: Arial, negritas, color gris opaco, formato compacto y alto, top-left")
        
        return img_base
    
    def insertar_firma_texto(self, img_base, texto_firma="Firma Digital", font_size_pt=25):
        """Inserta el texto de firma usando la fuente BrittanySignature.ttf - más grande, negritas y centrada"""
        print(f"   ✍️ Insertando firma: {texto_firma}")
        
        # Obtener configuración del campo firma_texto
        field_config = self.config['field_mapping'].get('firma_texto')
        if not field_config:
            print("   ❌ Error: Configuración para 'firma_texto' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho, alto = pos['ancho'], pos['alto']
        font_color = field_config.get('font_color', '#000000')
        layer_name = field_config['layer_name']
        
        # Usar la fuente BrittanySignature.ttf para la firma con tamaño más grande
        try:
            font = self.obtener_fuente("BrittanySignature.ttf", font_size_pt)
            print(f"   ✅ Fuente BrittanySignature.ttf cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        except Exception as e:
            print(f"   ⚠️ Error al cargar BrittanySignature.ttf: {e}")
            print("   🔄 Usando fuente Arial como respaldo")
            font = self.obtener_fuente("Arial", font_size_pt)
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto_firma)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Crear una imagen temporal para el texto con negritas suaves
        temp_text_layer = Image.new('RGBA', (text_width + 20, text_height + 20), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_text_layer)
        
        # Usar color específico solicitado
        color_suave = "#444549"  # Color específico #444549
        
        # Aplicar negritas con grosor reducido (thickness=1 en lugar de 2)
        self.simular_negritas(temp_draw, 10, 10, texto_firma, font, color_suave, thickness=1)
        
        # Calcular posición centrada en el rectángulo
        center_x = x + (ancho - temp_text_layer.width) // 2
        center_y = y + (alto - temp_text_layer.height) // 2
        
        # Ajuste fino para mejor centrado visual
        center_x = max(x, center_x)  # No salir del rectángulo por la izquierda
        center_y = max(y, center_y)  # No salir del rectángulo por arriba
        
        # Subir la firma un poco más
        center_y = center_y - 8  # Subir 8 píxeles
        
        # Pegar el texto con negritas suaves en la plantilla
        img_base.paste(temp_text_layer, (center_x, center_y), temp_text_layer)
        
        print(f"   ✅ firma_texto insertado en posición centrada ({center_x}, {center_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: BrittanySignature.ttf, negritas suaves, centrada, color: {color_suave}")
        
        return img_base
    
    def insertar_letra_final1(self, img_base, texto_letra_final1="P<VENVARGARCIAGONZALEZ<<MARCOS<<<<<<<<<<<<<<<", font_size_pt=106.8):
        """Inserta el texto de letra final1 usando la fuente OCR-B10PitchBT Regular.otf"""
        print(f"   🔤 Insertando LETRA.FINAL1: {texto_letra_final1}")
        
        # Obtener configuración del campo codigo_mrz_linea1
        field_config = self.config['field_mapping'].get('codigo_mrz_linea1')
        if not field_config:
            print("   ❌ Error: Configuración para 'codigo_mrz_linea1' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho, alto = pos['ancho'], pos['alto']
        font_color = field_config.get('font_color', '#000000')
        layer_name = field_config['layer_name']
        
        # Usar la fuente OCR-B10PitchBT Regular.otf
        try:
            font = self.obtener_fuente("OCR-B10PitchBT Regular.otf", font_size_pt)
            print(f"   ✅ Fuente OCR-B10PitchBT Regular.otf cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        except Exception as e:
            print(f"   ⚠️ Error al cargar OCR-B10PitchBT Regular.otf: {e}")
            print("   🔄 Usando fuente Arial como respaldo")
            font = self.obtener_fuente("Arial", font_size_pt)
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto_letra_final1)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Crear objeto de dibujo
        draw = ImageDraw.Draw(img_base)
        
        # Colocar en esquina superior izquierda del rectángulo
        left_x = x
        top_y = y
        
        # Dibujar el texto
        draw.text((left_x, top_y), texto_letra_final1, font=font, fill=font_color)
        
        print(f"   ✅ LETRA.FINAL1 insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: OCR-B10PitchBT Regular.otf, color: {font_color}")
        
        return img_base
    
    def insertar_letra_final2(self, img_base, texto_letra_final2="1086413983VEN9708141M2503011<<<<<<<<<<<<<<<6", font_size_pt=26.5):
        """Inserta el texto de letra final2 usando la fuente OCR-B10PitchBT Regular.otf"""
        print(f"   🔤 Insertando LETRA.FINAL2: {texto_letra_final2}")
        
        # Obtener configuración del campo codigo_mrz_linea2
        field_config = self.config['field_mapping'].get('codigo_mrz_linea2')
        if not field_config:
            print("   ❌ Error: Configuración para 'codigo_mrz_linea2' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho, alto = pos['ancho'], pos['alto']
        font_color = field_config.get('font_color', '#000000')
        layer_name = field_config['layer_name']
        
        # Usar la fuente OCR-B10PitchBT Regular.otf
        try:
            font = self.obtener_fuente("OCR-B10PitchBT Regular.otf", font_size_pt)
            print(f"   ✅ Fuente OCR-B10PitchBT Regular.otf cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        except Exception as e:
            print(f"   ⚠️ Error al cargar OCR-B10PitchBT Regular.otf: {e}")
            print("   🔄 Usando fuente Arial como respaldo")
            font = self.obtener_fuente("Arial", font_size_pt)
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto_letra_final2)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Crear objeto de dibujo
        draw = ImageDraw.Draw(img_base)
        
        # Colocar en esquina superior izquierda del rectángulo
        left_x = x
        top_y = y
        
        # Dibujar el texto
        draw.text((left_x, top_y), texto_letra_final2, font=font, fill=font_color)
        
        print(f"   ✅ LETRA.FINAL2 insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: OCR-B10PitchBT Regular.otf, color: {font_color}")
        
        return img_base
    
    def generar_gafete_integrado(self, ruta_foto, numero_pasaporte="108641398"):
        """Genera un gafete con las implementaciones integradas incluyendo firma"""
        print("🚀 GENERANDO GAFETE CON IMPLEMENTACIONES INTEGRADAS + FIRMA")
        print("=" * 70)
        
        # Cargar plantilla limpia
        img_base = self.cargar_plantilla_clean()
        if img_base is None:
            return None
        
        # Convertir a RGBA para poder pegar imágenes con transparencia
        img_base = img_base.convert('RGBA')
        
        # 1. Insertar imagen con efectos
        img_base = self.insertar_imagen_con_efectos(img_base, ruta_foto)
        
        # 2. Insertar número de pasaporte N°PASAPORTE1
        img_base = self.insertar_numero_pasaporte1(img_base, numero_pasaporte)
        
        # 3. Insertar número de pasaporte N°PASAPORTE2
        img_base = self.insertar_numero_pasaporte2(img_base, numero_pasaporte)
        
        # Definir tamaño de texto para todos los campos
        text_size = 16.5  # pyright: ignore[reportUnusedVariable]
        
        # 4. Insertar tipo de documento TIPO
        img_base = self.insertar_tipo_documento(img_base, "P", text_size)
        
        # 5. Insertar país emisor PAÍS
        img_base = self.insertar_pais_emisor(img_base, "VEN", text_size)
        # 6. Insertar campos de texto estándar (tamaños ajustados)
        img_base = self.insertar_nombre_alineado_izquierda(img_base, "LA MASCARA", text_size)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "apellido", "PLANTILLAS VIRTUALES", text_size)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_nacimiento", "14 / Ago / Ago / 1997", 15)
        img_base = self.insertar_texto_estandar(img_base, "numero_documento", "12345678", 14.5)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_emision", "12 / Mar / Mar / 2020", 15)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_vencimiento", "01 / Mar / Mar / 2025", 15)
        img_base = self.insertar_texto_estandar(img_base, "sexo", "F", text_size)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "nacionalidad", "VENEZOLANA", text_size)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "lugar_nacimiento", "MARACAIBO VEN", text_size)
        img_base = self.insertar_texto_estandar(img_base, "numero_pasaporte", numero_pasaporte, 14.5)
        img_base = self.insertar_code_negritas(img_base, "14-04-97", 20)
        
        # 7. Insertar firma (más grande, negritas y centrada)
        img_base = self.insertar_firma_texto(img_base, "Firma Digital", 20)
        
        # 8. Insertar letra final1
        img_base = self.insertar_letra_final1(img_base, "P<VENVARGARCIAGONZALEZ<<MARCOS<<<<<<<<<<<<<<<", 26.5)
        
        # 9. Insertar letra final2
        img_base = self.insertar_letra_final2(img_base, "1086413983VEN9708141M2503011<<<<<<<<<<<<<<<6", 26.5)
        
        # Convertir de vuelta a RGB para guardar
        img_final = Image.new('RGB', img_base.size, (255, 255, 255))
        img_final.paste(img_base, mask=img_base.split()[-1])
        
        return img_final
    
    def crear_plantillas_integradas(self):
        """Crea plantillas con las implementaciones integradas"""
        print("🚀 CREANDO PLANTILLAS CON IMPLEMENTACIONES INTEGRADAS")
        print("=" * 80)
        
        # Crear directorio de salida
        output_dir = self.base_path / 'OUTPUT' / 'plantillas_integradas'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Usar imágenes originales de Imagenes_OK
        imagenes_ok_dir = self.base_path / 'DATA' / 'Imagenes_OK'
        if not imagenes_ok_dir.exists():
            print(f"❌ Error: Directorio de imágenes no encontrado: {imagenes_ok_dir}")
            return False
        
        # Buscar imágenes en todas las subcarpetas
        imagenes = []
        for subdir in imagenes_ok_dir.iterdir():
            if subdir.is_dir():
                for img_file in list(subdir.glob('*.png')) + list(subdir.glob('*.jpg')) + list(subdir.glob('*.jpeg')):
                    imagenes.append(img_file)
        
        if not imagenes:
            print(f"❌ Error: No se encontraron imágenes en: {imagenes_ok_dir}")
            return False
        
        # Usar la primera imagen como ejemplo
        foto_ejemplo = imagenes[0]
        print(f"📸 Usando imagen original: {foto_ejemplo.name}")
        
        # Generar gafete integrado
        gafete_integrado = self.generar_gafete_integrado(str(foto_ejemplo))
        
        if gafete_integrado:
            # Guardar gafete integrado con imagen original
            output_path = output_dir / 'gafete_integrado_imagen_original.png'
            gafete_integrado.save(output_path, 'PNG', dpi=(300, 300))
            
            print(f"\n✅ Gafete integrado con imagen original guardado: {output_path}")
            print(f"📐 Dimensiones: {gafete_integrado.width}x{gafete_integrado.height}")
            
            # Crear también una versión con rectángulos marcados para referencia
            img_con_rectangulos = gafete_integrado.copy()
            draw = ImageDraw.Draw(img_con_rectangulos)
            
            # Marcar rectángulo de la foto
            foto_config = self.config['field_mapping'].get('ruta_foto')
            if foto_config:
                pos = foto_config['position']
                size = foto_config['size']
                draw.rectangle([pos['x'], pos['y'], pos['x'] + size['width'], pos['y'] + size['height']], 
                             outline='blue', width=3)
            
            # Marcar rectángulo del número de pasaporte N°PASAPORTE1
            pasaporte1_config = self.config['field_mapping'].get('numero_pasaporte_vertical1')
            if pasaporte1_config:
                pos = pasaporte1_config['position']
                draw.rectangle([pos['x'], pos['y'], pos['x'] + pos['ancho'], pos['y'] + pos['alto']], 
                             outline='green', width=3)
            
            # Marcar rectángulo del número de pasaporte N°PASAPORTE2
            pasaporte2_config = self.config['field_mapping'].get('numero_pasaporte_vertical2')
            if pasaporte2_config:
                pos = pasaporte2_config['position']
                draw.rectangle([pos['x'], pos['y'], pos['x'] + pos['ancho'], pos['y'] + pos['alto']], 
                             outline='orange', width=3)
            
            # Marcar rectángulo del tipo de documento TIPO
            tipo_config = self.config['field_mapping'].get('tipo_documento')
            if tipo_config:
                pos = tipo_config['position']
                draw.rectangle([pos['x'], pos['y'], pos['x'] + pos['ancho'], pos['y'] + pos['alto']], 
                             outline='purple', width=3)
            
            # Marcar rectángulo del país emisor PAÍS
            pais_config = self.config['field_mapping'].get('pais')
            if pais_config:
                pos = pais_config['position']
                draw.rectangle([pos['x'], pos['y'], pos['x'] + pos['ancho'], pos['y'] + pos['alto']], 
                             outline='cyan', width=3)
            
            # Marcar rectángulos de todos los campos de texto estándar
            campos_estandar = [
                ('nombre', 'red'),
                ('apellido', 'darkred'),
                ('fecha_nacimiento', 'blue'),
                ('numero_documento', 'darkblue'),
                ('fecha_emision', 'green'),
                ('fecha_vencimiento', 'darkgreen'),
                ('sexo', 'yellow'),
                ('nacionalidad', 'orange'),
                ('lugar_nacimiento', 'pink'),
                ('numero_pasaporte', 'brown'),
                ('code', 'purple'),
                ('firma_texto', 'magenta'),
                ('codigo_mrz_linea1', 'darkgreen'),
                ('codigo_mrz_linea2', 'darkblue')
            ]
            
            for campo, color in campos_estandar:
                campo_config = self.config['field_mapping'].get(campo)
                if campo_config:
                    pos = campo_config['position']
                    draw.rectangle([pos['x'], pos['y'], pos['x'] + pos['ancho'], pos['y'] + pos['alto']], 
                                 outline=color, width=2)
            
            # Guardar versión con rectángulos
            output_path_rectangulos = output_dir / 'gafete_integrado_imagen_original_con_rectangulos.png'
            img_con_rectangulos.save(output_path_rectangulos, 'PNG', dpi=(300, 300))
            
            print(f"✅ Gafete con rectángulos guardado: {output_path_rectangulos}")
            
            print(f"\n🎉 ¡Plantillas integradas con imágenes originales creadas exitosamente!")
            print("📋 Archivos generados en OUTPUT/plantillas_integradas/:")
            print("   📄 gafete_integrado_imagen_original.png - Gafete con procesamiento completo de imagen original")
            print("   📄 gafete_integrado_imagen_original_con_rectangulos.png - Gafete con rectángulos de referencia")
            
            return True
        else:
            print("❌ Error al generar gafete integrado")
            return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Script Maestro Integrado - Gafetes con Implementaciones')
    parser.add_argument('--config', '-c',
                       help='Archivo de configuración JSON')
    parser.add_argument('--foto', '-f',
                       help='Ruta a la foto específica')
    parser.add_argument('--numero', '-n',
                       help='Número de pasaporte específico')
    
    args = parser.parse_args()
    
    # Inicializar script maestro
    maestro = ScriptMaestroIntegrado(args.config)
    
    # Crear plantillas integradas
    exito = maestro.crear_plantillas_integradas()
    
    if exito:
        print("\n🎉 ¡Script maestro integrado ejecutado exitosamente!")
        print("📋 Revisa los archivos en OUTPUT/plantillas_integradas/")
        print("🎯 Estas plantillas muestran el procesamiento completo: imágenes originales → IA → escala de grises → contenedores → textos → firmas")
    else:
        print("\n💥 Error al ejecutar script maestro integrado")
        sys.exit(1)

if __name__ == "__main__":
    main()
