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
import cv2
import os
import mediapipe as mp
from pathlib import Path
try:
    import onnxruntime as ort  # Aceleración GPU para RetinaFace ONNX
except Exception:
    ort = None

class ScriptMaestroIntegrado:
    def __init__(self, config_path=None):
        """Inicializa el script maestro con configuración"""
        self.config_path = config_path or '/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL/CONFIG/config.json'
        self.config = self.cargar_configuracion()
        self.base_path = Path('/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL')
        self.fuentes_dir = self.base_path / 'TEMPLATE' / 'Fuentes_Base'
        self.plantilla_clean_path = self.base_path / 'TEMPLATE' / 'PASAPORTE-VENEZUELA-CLEAN.png'
        
        # Configuración de fuentes - soportar ambos directorios
        self.fuentes_extras_dir = self.base_path / 'TEMPLATE' / 'Fuentes Extras'
        self.font_paths = {
            "OCR-B10PitchBT Regular.otf": str(self.fuentes_dir / "OCR-B10PitchBT Regular.otf"),
            "BrittanySignature.ttf": str(self.fuentes_dir / "BrittanySignature.ttf"),
            "Pasaport Numbers Front-Regular.ttf": str(self.fuentes_dir / "Pasaport Numbers Front-Regular.ttf"),
            "Arial": str(self.fuentes_dir / "Arial.ttf") 
        }
        
        # OPTIMIZACIÓN: Cache de fuentes cargadas para evitar recargar
        self.font_cache = {}
        self._precargar_fuentes_comunes()
        
        # Control de contenedores individuales
        self.mostrar_contenedores_individuales = False
        
        # Lista blanca de fuentes para firmas (simulan trazos manuscritos naturales)
        self.fuentes_firma_whitelist = [
            "BrittanySignature.ttf",
            "Amsterdam.ttf",
            "Autography.otf",
            "Breathing Personal Use Only.ttf",
            "Thesignature.ttf",
            "Amalfi Coast.ttf",
            "South Brittany FREE.otf",
            "White Sign (DemoVersion).otf",
            "Lovtony Script.ttf",
            "Royalty Free.ttf",
            "RetroSignature.otf"
        ]
        
        # Activar OpenCL en OpenCV si está disponible (mejor uso GPU/driver)
        try:
            cv2.ocl.setUseOpenCL(True)
            print(f"   ⚙️ OpenCL habilitado en OpenCV: {cv2.ocl.useOpenCL()}")
        except Exception as e:
            print(f"   ⚠️ No se pudo habilitar OpenCL en OpenCV: {e}")

        # Inicializar MediaPipe Face Mesh con preferencia GPU (controlado por env MEDIAPIPE_GPU)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

        # OPTIMIZACIÓN: ONNX Runtime eliminado (reemplazado por OpenCV)
        self.ort_session = None
        self.ort_input_name = None
        self.ort_input_size = (640, 640)
        print(f"   ⚠️ ONNX Runtime deshabilitado (usando OpenCV)")

        # Inicializar sesión persistente de rembg con preferencia CUDA
        self.rembg_session = None
        try:
            from rembg import new_session
            rembg_providers = []
            if ort is not None and hasattr(ort, 'get_available_providers') and 'CUDAExecutionProvider' in ort.get_available_providers():
                rembg_providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            else:
                rembg_providers = ['CPUExecutionProvider']
            # Modelos posibles: 'u2net', 'u2net_human_seg', 'isnet-anime', etc. Usar el estándar u2net_human_seg
            self.rembg_session = new_session('u2net_human_seg', providers=rembg_providers)
            print(f"   🧠 rembg sesión inicializada ({rembg_providers})")
        except Exception as e:
            self.rembg_session = None
            print(f"   ⚠️ No se pudo inicializar sesión rembg: {e}")
        
    def _precargar_fuentes_comunes(self):
        """OPTIMIZACIÓN: Precarga las fuentes más comunes para evitar recargar"""
        print("🔄 Precargando fuentes comunes...")
        
        # Tamaños comunes que se usan frecuentemente
        tamanos_comunes = [12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 36, 40, 48, 60, 72, 90]
        
        # Fuentes más usadas
        fuentes_comunes = [
            "Arial",
            "BrittanySignature.ttf", 
            "Pasaport Numbers Front-Regular.ttf",
            "OCR-B10PitchBT Regular.otf"
        ]
        
        for fuente in fuentes_comunes:
            for tamano in tamanos_comunes:
                cache_key = f"{fuente}_{tamano}"
                try:
                    font = self._cargar_fuente_optimizada(fuente, tamano)
                    if font:
                        self.font_cache[cache_key] = font
                except Exception:
                    pass  # Si falla, se carga bajo demanda
        
        print(f"✅ {len(self.font_cache)} fuentes precargadas")

    def _cargar_fuente_optimizada(self, font_name, font_size_pt, dpi=96):
        """OPTIMIZACIÓN: Carga fuente con cache para evitar recargar"""
        # Convertir puntos a píxeles
        font_size_px = self.puntos_a_pixeles(font_size_pt, dpi)
        cache_key = f"{font_name}_{font_size_px}"
        
        # Verificar cache primero
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Si no está en cache, cargar y guardar
        font = self._cargar_fuente_original(font_name, font_size_pt, dpi)
        if font:
            self.font_cache[cache_key] = font
        return font

    def _cargar_fuente_original(self, font_name, font_size_pt, dpi=96):
        """Carga fuente original (método anterior) - soporta ambos directorios"""
        # Convertir puntos a píxeles
        font_size_px = self.puntos_a_pixeles(font_size_pt, dpi)
        
        # Resolución estricta de fuentes según proyecto (no cambiar tipografías)
        if font_name == "Arial":
            # Intentar rutas comunes del sistema para Arial sin sustituir por otras fuentes
            candidate_paths = [
                self.font_paths.get("Arial", "arial.ttf"),
                str(self.fuentes_dir / "Arial.ttf"),
                str(self.fuentes_extras_dir / "Arial.ttf"),
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
                    return font
                except IOError:
                    continue
            # Si no se encontró, fallar claramente para no cambiar tipografía
            raise IOError("No se encontró la fuente Arial en el sistema")
        else:
            # Primero intentar desde las rutas configuradas (ambos directorios)
            candidate_paths = [
                self.font_paths.get(font_name),
                str(self.fuentes_dir / font_name),
                str(self.fuentes_extras_dir / font_name)
            ]
            
            for font_path in candidate_paths:
                if font_path:
                    try:
                        font = ImageFont.truetype(font_path, font_size_px)
                        return font
                    except IOError:
                        pass
            
            # Si no se encuentra en rutas configuradas, intentar cargar desde el sistema
            # Intentar diferentes variaciones del nombre de la fuente
            font_variations = [
                font_name,  # Nombre original
                font_name.replace(" ", ""),  # Sin espacios
                font_name.replace(" ", "-"),  # Espacios por guiones
                font_name.replace(" ", "_"),  # Espacios por guiones bajos
            ]
            
            for variation in font_variations:
                try:
                    font = ImageFont.truetype(variation, font_size_px)
                    return font
                except IOError:
                    continue
            
            # Último recurso: intentar desde ~/.fonts/
            try:
                home_fonts = os.path.expanduser("~/.fonts")
                font_path = os.path.join(home_fonts, font_name)
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size_px)
                    return font
            except IOError:
                pass
            
            # Si no se encuentra, devolver None
            return None

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
        """OPTIMIZACIÓN: Carga la plantilla limpia usando cache reutilizable"""
        try:
            # Si ya tenemos la plantilla en cache, reutilizarla
            if hasattr(self, 'plantilla_cache') and self.plantilla_cache is not None:
                return self.plantilla_cache
            
            # Si no existe, cargarla una sola vez
            if self.plantilla_clean_path.exists():
                img = Image.open(self.plantilla_clean_path)
                # Guardar en cache para reutilización (SIN COPY para mantener la misma instancia)
                self.plantilla_cache = img
                print(f"✅ Plantilla limpia cargada y cacheada: {self.plantilla_clean_path}")
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
        """OPTIMIZACIÓN: Obtiene fuente usando cache para evitar recargar"""
        # Usar método optimizado con cache
        font = self._cargar_fuente_optimizada(font_name, font_size_pt, dpi)
        
        if font:
            # Solo mostrar mensaje si no está en cache (primera carga)
            cache_key = f"{font_name}_{self.puntos_a_pixeles(font_size_pt, dpi)}"
            if cache_key not in self.font_cache:
                print(f"   ✅ Fuente {font_name} cargada: {font_size_pt} pt (DPI {dpi})")
        else:
            print(f"   ❌ No se pudo cargar fuente {font_name}")
        
        return font
    
    def calcular_posicion_desde_json(self, pos):
        """Calcula la posición final usando solo configuración del JSON - INDEPENDIENTE DEL CONTENEDOR"""
        x = pos['x']
        y = pos['y']
        offset_x = pos.get('offset_x', 0)
        offset_y = pos.get('offset_y', 0)
        alignment = pos.get('alignment', 'top_left')
        
        if alignment == 'top_left':
            # Solo usar posición base + offset (independiente del contenedor)
            return x + offset_x, y + offset_y
        elif alignment == 'bottom_center':
            # Solo usar posición base + offset (independiente del contenedor)
            return x + offset_x, y + offset_y
        elif alignment == 'center':
            # Solo usar posición base + offset (independiente del contenedor)
            return x + offset_x, y + offset_y
        else:
            # Solo usar posición base + offset (independiente del contenedor)
            return x + offset_x, y + offset_y
    
    def dibujar_texto_con_espaciado(self, draw, x, y, text, font, fill, thickness, letter_spacing, blur_radius=0, blur_padding=None):
        """Dibuja texto con espaciado personalizado entre letras y difuminado opcional"""
        current_x = x
        
        # Configuración de padding por defecto
        if blur_padding is None:
            blur_padding = {'normal': 5, 'hyphen': 8}
        
        for i, char in enumerate(text):
            # Calcular el ancho de la letra actual
            bbox = font.getbbox(char)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            
            if blur_radius > 0 and char != '-':
                # Crear una imagen temporal para la letra con blur (solo letras y números)
                # Usar padding configurado desde JSON
                padding = blur_padding.get('normal', 5)
                temp_img = Image.new('RGBA', (char_width + padding*2, char_height + padding*2), (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                
                # Dibujar la letra en la imagen temporal
                self.simular_negritas(temp_draw, padding, padding, char, font, fill, thickness)
                
                # Aplicar blur
                temp_img = temp_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                
                # Pegar la letra difuminada en la imagen principal
                draw._image.paste(temp_img, (int(current_x - padding), int(y - padding)), temp_img)
            else:
                # Dibujar cada letra individualmente (guiones sin blur, letras con o sin blur)
                self.simular_negritas(draw, current_x, y, char, font, fill, thickness)
            
            # Mover a la siguiente posición con espaciado
            current_x += int(char_width) + int(letter_spacing)
    
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
            if self.rembg_session is not None:
                output_data = remove(input_data, session=self.rembg_session)
            else:
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
        """Detecta la cara y escala; prioriza ONNX (CUDA) y cae a MediaPipe o simple."""
        # 1) Intentar ONNX RetinaFace si está disponible
        if self.ort_session is not None:
            try:
                # Preprocesar a 640x640 RGB
                img_rgb = img.convert('RGB')
                import numpy as np  # local import para mantener dependencias
                arr = np.array(img_rgb)
                h0, w0 = arr.shape[:2]
                arr_res = cv2.resize(arr, self.ort_input_size, interpolation=cv2.INTER_LINEAR)
                # Normalización básica [0,1] y CHW
                inp = arr_res.astype('float32') / 255.0
                inp = np.transpose(inp, (2, 0, 1))[None, ...]
                # Inferencia
                outputs = self.ort_session.run(None, {self.ort_input_name: inp})
                # Nota: Diferentes exportes entregan (loc, conf, landms) o un set de cajas ya decodificadas.
                # Para mantener compatibilidad sin romper flujo, aplicamos heurística:
                # - Si algún output tiene forma (N, 5) lo tratamos como [x1,y1,x2,y2,score]
                bbox = None
                for out in outputs:
                    if isinstance(out, np.ndarray) and out.ndim == 2 and out.shape[1] >= 5:
                        # Tomar la caja con mayor score
                        idx = int(np.argmax(out[:, 4]))
                        x1, y1, x2, y2, sc = out[idx, :5]
                        if sc > 0.3:
                            # Reescalar a tamaño original
                            x1 = max(0, min(w0 - 1, int(x1 / self.ort_input_size[0] * w0)))
                            x2 = max(0, min(w0 - 1, int(x2 / self.ort_input_size[0] * w0)))
                            y1 = max(0, min(h0 - 1, int(y1 / self.ort_input_size[1] * h0)))
                            y2 = max(0, min(h0 - 1, int(y2 / self.ort_input_size[1] * h0)))
                            bbox = (x1, y1, x2, y2)
                            break
                if bbox is not None:
                    x1, y1, x2, y2 = bbox
                    # Expandir ligeramente la caja y recortar
                    pad_x = int((x2 - x1) * 0.15)
                    pad_y = int((y2 - y1) * 0.20)
                    x1 = max(0, x1 - pad_x)
                    y1 = max(0, y1 - pad_y)
                    x2 = min(w0, x2 + pad_x)
                    y2 = min(h0, y2 + pad_y)
                    face = img.crop((x1, y1, x2, y2))
                    return face
            except Exception as e:
                # ONNX falló, continuar con MediaPipe
                print(f"   ⚠️ Fallback a MediaPipe (ONNX no decodificado): {e}")

        # 2) MediaPipe Face Mesh
        try:
            import numpy as np
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2RGB)
            results = self.face_mesh.process(img_cv)
            if not results.multi_face_landmarks:
                return self._escalar_simple(img)
            landmarks = results.multi_face_landmarks[0]
            h, w = img_cv.shape[:2]
            left_eye = [landmarks.landmark[33].x * w, landmarks.landmark[33].y * h]
            right_eye = [landmarks.landmark[362].x * w, landmarks.landmark[362].y * h]
            eye_center = [(left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2]
            face_width = abs(right_eye[0] - left_eye[0]) * 2.5
            target_face_width = 200
            scale_factor = target_face_width / max(face_width, 1e-6)
            new_w = max(1, int(w * scale_factor))
            new_h = max(1, int(h * scale_factor))
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
            
            # Inicializar Face Mesh con GPU
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
            target_face_width = target_width * 0.65  # Zoom reducido (más torso visible)
            scale_factor = target_face_width / face_width
            
            # Redimensionar
            new_w = int(w * scale_factor)
            new_h = int(h * scale_factor)
            img_scaled = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Calcular posición del centro del rostro en imagen escalada
            eye_center_x = eye_center[0] * scale_factor
            eye_center_y = eye_center[1] * scale_factor
            
            # Posición objetivo en contenedor (ojos al 45% de altura)
            target_x = target_width // 2 - 15  # CENTRO horizontal del contenedor (ajustado para centrado visual)
            target_y = int(target_height * 0.45)  # Ojos al 45% de altura (imagen más abajo)
            
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
    
    def crear_marco_semitransparente(self, img, target_width, target_height):
        """Crea un marco semi-transparente DENTRO de las dimensiones existentes"""
        print("   🖼️ Creando marco semi-transparente dentro del contenedor...")
        
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
        
        print("   ✅ Marco semi-transparente creado dentro del contenedor")
        return img_con_marco
    
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
        
        # Crear marco semi-transparente alrededor de la imagen
        img_con_marco = self.crear_marco_semitransparente(img_recortada, target_width, target_height)
        
        # Pegar imagen en la plantilla
        img_base.paste(img_con_marco, (pos_x, pos_y), img_con_marco)
        
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
        font_color = field_config.get('font_color', '#000000')
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', 95))
        pasaport_font = self.obtener_fuente("Pasaport Numbers Front-Regular.ttf", font_size_pt)
        
        # Obtener configuración de escalado, espaciado y negritas
        scale_x = field_config.get('scale_x', 1.0)
        scale_y = field_config.get('scale_y', 1.0)
        letter_spacing = field_config.get('letter_spacing', 0)
        thickness = field_config.get('bold_thickness', 2)
        stretch_to_fit = field_config.get('stretch_to_fit', False)
        
        # Usar configuración del JSON para posicionamiento
        offset_x = pos.get('offset_x', 0)
        offset_y = pos.get('offset_y', 0)
        alignment = pos.get('alignment', 'bottom_center')
        
        # Obtener el bounding box del texto
        bbox_horizontal = pasaport_font.getbbox(numero_pasaporte)
        text_w_horiz = bbox_horizontal[2] - bbox_horizontal[0]
        text_h_horiz = bbox_horizontal[3] - bbox_horizontal[1]
        
        # Crear una imagen temporal para el texto horizontal
        temp_text_layer = Image.new('RGBA', (text_w_horiz + 5, text_h_horiz + 5), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_text_layer)
        self.simular_negritas(temp_draw, 0, 0, numero_pasaporte, pasaport_font, font_color, thickness)
        
        # Aplicar stretch_to_fit si está habilitado
        if stretch_to_fit:
            # Para texto vertical, necesitamos ajustar la altura al contenedor
            # Después de rotar 90°, la altura del texto se convierte en el ancho
            target_height = rect_height  # Altura del contenedor vertical
            current_height = temp_text_layer.height
            
            if current_height > 0 and current_height > target_height:
                # Solo escalar si el texto es más alto que el contenedor
                scale_factor = target_height / current_height
                # Limitar el factor de escalado para evitar escalado excesivo
                scale_factor = min(scale_factor, 0.8)  # Máximo 80% del tamaño original
                
                new_width = int(temp_text_layer.width * scale_factor)
                new_height = int(temp_text_layer.height * scale_factor)
                
                # Redimensionar la imagen
                temp_text_layer = temp_text_layer.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"   🔧 Stretch to fit aplicado: {current_height}px -> {new_height}px (factor: {scale_factor:.3f})")
            else:
                print(f"   ✅ Texto ya cabe en el contenedor: {current_height}px <= {target_height}px")
        
        # Aplicar escalado si es necesario
        if scale_x != 1.0 or scale_y != 1.0:
            # Calcular nuevas dimensiones
            new_width = int(temp_text_layer.width * scale_x)
            new_height = int(temp_text_layer.height * scale_y)
            
            # Redimensionar la imagen
            temp_text_layer = temp_text_layer.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"   🔧 Escalado aplicado: {scale_x}x{scale_y} -> {new_width}x{new_height}")
        
        # Rotar la imagen del texto 90 grados anti-horario
        rotated_text_layer = temp_text_layer.rotate(rotation, expand=1, resample=Image.Resampling.BICUBIC)
        
        # Aplicar espaciado entre letras si es necesario
        if letter_spacing != 0:
            # Método simple: dibujar cada letra individualmente con espaciado
            draw = ImageDraw.Draw(img_base)
            current_x = rect_x + offset_x
            current_y = rect_y + offset_y
            
            for char in numero_pasaporte:
                # Crear una imagen temporal para cada letra
                char_bbox = pasaport_font.getbbox(char)
                char_width = int((char_bbox[2] - char_bbox[0]) * scale_x)
                char_height = int((char_bbox[3] - char_bbox[1]) * scale_y)
                
                # Crear imagen temporal para la letra
                temp_char_img = Image.new('RGBA', (char_width + 10, char_height + 10), (0, 0, 0, 0))
                temp_char_draw = ImageDraw.Draw(temp_char_img)
                self.simular_negritas(temp_char_draw, 5, 5, char, pasaport_font, font_color, thickness)
                
                # Rotar la letra individual 90 grados
                rotated_char = temp_char_img.rotate(rotation, expand=1, resample=Image.Resampling.BICUBIC)
                
                # Pegar la letra rotada en la imagen principal
                img_base.paste(rotated_char, (int(current_x), int(current_y)), rotated_char)
                
                # Mover a la siguiente posición con espaciado (verticalmente hacia abajo)
                current_y += rotated_char.height + int(letter_spacing)
            
            print(f"   🔧 Espaciado aplicado: {letter_spacing}px entre letras")
            return img_base
        
        # Posicionar según alineación - INDEPENDIENTE DEL CONTENEDOR
        if alignment == 'bottom_center':
            # Centrado horizontal, alineado a la parte inferior (sin limitaciones del contenedor)
            paste_x = rect_x + offset_x  # Solo usar posición base + offset
            paste_y = rect_y + offset_y  # Solo usar posición base + offset
        elif alignment == 'top_left':
            # Esquina superior izquierda
            paste_x = rect_x + offset_x
            paste_y = rect_y + offset_y
        else:
            # Por defecto, usar posición base + offset
            paste_x = rect_x + offset_x
            paste_y = rect_y + offset_y
        
        # Pegar el texto rotado en la plantilla
        img_base.paste(rotated_text_layer, (paste_x, paste_y), rotated_text_layer)
        
        print(f"   ✅ N°PASAPORTE1 insertado en posición ({paste_x}, {paste_y}) con rotación {rotation}°")
        print(f"   📏 Escalado: {scale_x}x{scale_y}, Espaciado: {letter_spacing}px, Grosor: {thickness}")
        
        print(f"   📏 Tamaño: {font_size_pt} pt, grosor: {thickness}, independiente del contenedor")
        
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
        rotation = field_config.get('rotation', 90)
        layer_name = field_config['layer_name']
        font_color = field_config.get('font_color', '#000000')
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', 15))
        # Obtener fuente desde font_mapping
        font_name = self.config['fonts']['font_mapping'].get(layer_name, "Arial")
        ocr_font = self.obtener_fuente(font_name, font_size_pt)
        
        # Obtener configuración de escalado, espaciado y negritas
        scale_x = field_config.get('scale_x', 1.0)
        scale_y = field_config.get('scale_y', 1.0)
        letter_spacing = field_config.get('letter_spacing', 0)
        thickness = field_config.get('bold_thickness', 2.0)
        
        # Usar configuración del JSON para posicionamiento
        offset_x = pos.get('offset_x', 0)
        offset_y = pos.get('offset_y', 0)
        alignment = pos.get('alignment', 'bottom_center')
        
        # Obtener el bounding box del texto
        bbox_horizontal = ocr_font.getbbox(numero_pasaporte)
        text_w_horiz = bbox_horizontal[2] - bbox_horizontal[0]
        text_h_horiz = bbox_horizontal[3] - bbox_horizontal[1]
        
        # Crear una imagen temporal para el texto horizontal
        temp_text_layer = Image.new('RGBA', (text_w_horiz + 5, text_h_horiz + 5), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_text_layer)
        self.simular_negritas(temp_draw, 0, 0, numero_pasaporte, ocr_font, font_color, thickness)
        
        # Aplicar escalado si es necesario
        if scale_x != 1.0 or scale_y != 1.0:
            # Calcular nuevas dimensiones
            new_width = int(temp_text_layer.width * scale_x)
            new_height = int(temp_text_layer.height * scale_y)
            
            # Redimensionar la imagen
            temp_text_layer = temp_text_layer.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"   🔧 Escalado aplicado: {scale_x}x{scale_y} -> {new_width}x{new_height}")
        
        # Rotar la imagen del texto 90 grados anti-horario
        rotated_text_layer = temp_text_layer.rotate(rotation, expand=1, resample=Image.Resampling.BICUBIC)
        
        # COMENTADO - Método de espaciado letra por letra (causaba problemas)
        # if letter_spacing != 0:
        #     # Método simple: dibujar cada letra individualmente con espaciado
        #     draw = ImageDraw.Draw(img_base)
        #     current_x = rect_x + offset_x
        #     current_y = rect_y + offset_y
        #     
        #     for char in numero_pasaporte:
        #         # Crear una imagen temporal para cada letra
        #         char_bbox = ocr_font.getbbox(char)
        #         char_width = int((char_bbox[2] - char_bbox[0]) * scale_x)
        #         char_height = int((char_bbox[3] - char_bbox[1]) * scale_y)
        #         
        #         # Crear imagen temporal para la letra
        #         temp_char_img = Image.new('RGBA', (char_width + 10, char_height + 10), (0, 0, 0, 0))
        #         temp_char_draw = ImageDraw.Draw(temp_char_img)
        #         self.simular_negritas(temp_char_draw, 5, 5, char, ocr_font, font_color, thickness)
        #         
        #         # Rotar la letra individual 90 grados
        #         rotated_char = temp_char_img.rotate(rotation, expand=1, resample=Image.Resampling.BICUBIC)
        #         
        #         # Pegar la letra rotada en la imagen principal
        #         img_base.paste(rotated_char, (int(current_x), int(current_y)), rotated_char)
        #         
        #         # Mover a la siguiente posición con espaciado (verticalmente hacia abajo)
        #         current_y += rotated_char.height + int(letter_spacing)
        #     
        #     print(f"   🔧 Espaciado aplicado: {letter_spacing}px entre letras")
        #     return img_base
        
        # Posicionar según alineación - INDEPENDIENTE DEL CONTENEDOR
        if alignment == 'bottom_center':
            # Centrado horizontal, alineado a la parte inferior (sin limitaciones del contenedor)
            paste_x = rect_x + offset_x  # Solo usar posición base + offset
            paste_y = rect_y + offset_y  # Solo usar posición base + offset
        elif alignment == 'top_left':
            # Esquina superior izquierda
            paste_x = rect_x + offset_x
            paste_y = rect_y + offset_y
        else:
            # Por defecto, usar posición base + offset
            paste_x = rect_x + offset_x
            paste_y = rect_y + offset_y
        
        # Pegar el texto rotado en la plantilla
        img_base.paste(rotated_text_layer, (paste_x, paste_y), rotated_text_layer)
        
        print(f"   ✅ N°PASAPORTE2 insertado en posición ({paste_x}, {paste_y}) con rotación {rotation}°")
        print(f"   📏 Escalado: {scale_x}x{scale_y}, Grosor: {thickness}")
        print(f"   📏 Tamaño: {font_size_pt} pt, grosor: {thickness}, independiente del contenedor")
        
        return img_base
    
    def insertar_tipo_documento(self, img_base, tipo_documento="P"):
        """Inserta el tipo de documento TIPO usando configuración JSON"""
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
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', 17))
        layer_name = field_config['layer_name']
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt_conf = field_config.get('render_size_pt', field_config.get('font_size', font_size_pt))
        # Obtener fuente desde font_mapping
        font_name = self.config['fonts']['font_mapping'].get(layer_name, "Arial")
        font = self.obtener_fuente(font_name, font_size_pt_conf)
        
        # Crear objeto de dibujo
        draw = ImageDraw.Draw(img_base)
        
        # Obtener el bounding box del texto
        bbox = font.getbbox(tipo_documento)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Usar configuración del JSON para posicionamiento
        offset_x = pos.get('offset_x', 0)
        offset_y = pos.get('offset_y', 0)
        alignment = pos.get('alignment', 'top_left')
        
        if alignment == 'top_left':
            left_x = x + offset_x
            top_y = y + offset_y
        else:
            # Por defecto, usar posición base + offset
            left_x = x + offset_x
            top_y = y + offset_y
        
        # Dibujar el texto en negritas
        thickness = field_config.get('bold_thickness', 0.7)
        self.simular_negritas(draw, left_x, top_y, tipo_documento, font, font_color, thickness=thickness)
        
        print(f"   ✅ TIPO insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt_conf} pt, fuente: Arial, alineado a la izquierda (top-left)")
        
        return img_base
    
    def insertar_pais_emisor(self, img_base, pais="VEN"):
        """Inserta el país emisor PAÍS usando configuración JSON"""
        print(f"   🌍 Insertando PAÍS: {pais}")
        
        # Obtener configuración del campo PAÍS
        field_config = self.config['field_mapping'].get('pais_emisor')
        if not field_config:
            print("   ❌ Error: Configuración para 'pais_emisor' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho = pos['ancho']
        alto = pos['alto']
        font_color = field_config.get('font_color', '#000000')
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', 17))
        layer_name = field_config['layer_name']
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt_conf = field_config.get('render_size_pt', field_config.get('font_size', font_size_pt))
        # Obtener fuente desde font_mapping
        font_name = self.config['fonts']['font_mapping'].get(layer_name, "Arial")
        font = self.obtener_fuente(font_name, font_size_pt_conf)
        
        # Crear objeto de dibujo
        draw = ImageDraw.Draw(img_base)
        
        # Obtener el bounding box del texto
        bbox = font.getbbox(pais)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Usar configuración del JSON para posicionamiento
        left_x, top_y = self.calcular_posicion_desde_json(pos)
        
        # Dibujar el texto (negritas según config)
        thickness = field_config.get('bold_thickness', 0)
        self.simular_negritas(draw, left_x, top_y, pais, font, font_color, thickness=thickness)
        
        print(f"   ✅ PAÍS insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt_conf} pt, fuente: Arial, alineado a la izquierda (top-left)")
        
        return img_base
    
    def insertar_texto_estandar(self, img_base, campo, texto, font_size_pt=63.32):
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
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt_conf = field_config.get('render_size_pt', field_config.get('font_size', font_size_pt))
        # Obtener fuente desde font_mapping
        font_name = self.config['fonts']['font_mapping'].get(layer_name, "Arial")
        font = self.obtener_fuente(font_name, font_size_pt_conf)
        
        # Crear objeto de dibujo
        draw = ImageDraw.Draw(img_base)
        
        # Obtener el bounding box del texto
        bbox = font.getbbox(texto)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Usar configuración del JSON para posicionamiento
        left_x, top_y = self.calcular_posicion_desde_json(pos)
        
        # Dibujar el texto en negritas (grosor desde JSON)
        thickness = field_config.get('bold_thickness', 0.7)
        letter_spacing = field_config.get('letter_spacing', 0)
        blur_radius = field_config.get('blur_radius', 0)
        
        if letter_spacing != 0 or blur_radius > 0:
            # Aplicar espaciado entre letras y/o difuminado
            blur_padding = field_config.get('blur_padding', {'normal': 5, 'hyphen': 8})
            self.dibujar_texto_con_espaciado(draw, left_x, top_y, texto, font, font_color, thickness, letter_spacing, blur_radius, blur_padding)
        else:
            # Dibujo normal sin espaciado ni difuminado
            self.simular_negritas(draw, left_x, top_y, texto, font, font_color, thickness=thickness)
        
        print(f"   ✅ {campo} insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: Arial (top-left)")
        
        return img_base
    
    def insertar_nombre_alineado_izquierda(self, img_base, texto, font_size_pt=63.32):
        """Inserta el nombre alineado a la izquierda como los otros textos"""
        field_config = self.config['field_mapping'].get('nombre')
        if not field_config:
            print("   ❌ Error: Configuración para 'nombre' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho, alto = pos['ancho'], pos['alto']
        font_color = field_config.get('font_color', '#000000')
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', font_size_pt))
        # Obtener fuente según mapeo del JSON
        layer_name = field_config.get('layer_name', 'NOMBRES')
        font_name = self.config['fonts']['font_mapping'].get(layer_name, "Arial")
        font = self.obtener_fuente(font_name, font_size_pt)
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📝 Insertando nombre: {texto}")
        print(f"   ✅ Fuente {font_name} cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Usar configuración del JSON para posicionamiento
        left_x, top_y = self.calcular_posicion_desde_json(pos)
        
        # Dibujar el texto en negritas
        draw = ImageDraw.Draw(img_base)
        thickness = field_config.get('bold_thickness', 0.7)
        self.simular_negritas(draw, left_x, top_y, texto, font, font_color, thickness=thickness)
        
        print(f"   ✅ nombre insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: {font_name}, top-left")
        
        return img_base
    
    def insertar_texto_alineado_izquierda(self, img_base, campo, texto, font_size_pt=63.32):
        """Inserta texto alineado a la izquierda del marco interno del contenedor"""
        field_config = self.config['field_mapping'].get(campo)
        if not field_config:
            print(f"   ❌ Error: Configuración para '{campo}' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho, alto = pos['ancho'], pos['alto']
        font_color = field_config.get('font_color', '#000000')
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', font_size_pt))
        # Obtener fuente según mapeo del JSON
        layer_name = field_config.get('layer_name', campo.upper())
        font_name = self.config['fonts']['font_mapping'].get(layer_name, "Arial")
        font = self.obtener_fuente(font_name, font_size_pt)
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📝 Insertando {campo}: {texto}")
        print(f"   ✅ Fuente {font_name} cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Verificar si tiene estiramiento para ajustar al contenedor
        stretch_to_fit = field_config.get('stretch_to_fit', False)
        fit_width = field_config.get('fit_width', ancho)
        
        # SISTEMA DE CONTENEDORES INDIVIDUALES PARA FECHAS
        # Si es una fecha, dividir en elementos individuales con contenedores fijos
        if campo in ['fecha_nacimiento', 'fecha_emision', 'fecha_vencimiento']:
            # Dividir la fecha en elementos individuales
            # Formato esperado: "14/May/May/1985"
            partes = texto.split('/')
            if len(partes) == 4:
                dia, mes_es, mes_en, año = partes
                
                # CONTENEDORES FIJOS PARA CADA ELEMENTO
                contenedores = {
                    'dia': {'ancho': 25, 'texto': dia},
                    'mes_es': {'ancho': 35, 'texto': mes_es},
                    'mes_en': {'ancho': 35, 'texto': mes_en},
                    'año': {'ancho': 40, 'texto': año}
                }
                
                # Separadores fijos
                separadores = {'ancho': 8, 'texto': '/'}
                
                # Calcular ancho total del contenedor compuesto
                ancho_total = sum(c['ancho'] for c in contenedores.values()) + (len(contenedores) - 1) * separadores['ancho']
                
                # Ajustar el ancho del contenedor principal
                ancho = ancho_total
                
                print(f"   🔧 Contenedores individuales:")
                print(f"      Día: {dia} ({contenedores['dia']['ancho']}px)")
                print(f"      Mes ES: {mes_es} ({contenedores['mes_es']['ancho']}px)")
                print(f"      Mes EN: {mes_en} ({contenedores['mes_en']['ancho']}px)")
                print(f"      Año: {año} ({contenedores['año']['ancho']}px)")
                print(f"      Ancho total: {ancho_total}px")
                
                # Aplicar espaciado mínimo para centrar cada elemento en su contenedor
                field_config['letter_spacing'] = 0.5
            else:
                # Si no se puede dividir, usar ancho estándar
                ancho_estandar = 200
                ancho = ancho_estandar
                print(f"   🔧 Formato no reconocido, usando ancho estándar: {ancho_estandar}px")
        
        # RENDERIZAR FECHAS CON CONTENEDORES INDIVIDUALES
        if campo in ['fecha_nacimiento', 'fecha_emision', 'fecha_vencimiento'] and len(texto.split('/')) == 4:
            return self.insertar_fecha_con_contenedores_individuales(img_base, campo, texto, x, y, field_config, mostrar_contenedores=self.mostrar_contenedores_individuales)
        
        if stretch_to_fit:
            # Calcular el factor de escalado SOLO horizontal para ajustar al ancho del contenedor
            scale_factor = fit_width / text_width if text_width > 0 else 1.0
            print(f"   🔧 Estirando SOLO horizontalmente: {text_width}px -> {fit_width}px (factor: {scale_factor:.3f})")
            
            # Crear una capa temporal con el ancho estirado pero altura original
            padding = field_config.get('stretch_padding', 10)  # Padding desde JSON
            temp_width = fit_width + padding
            temp_height = text_height + padding  # Mantener altura original
            temp_layer = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_layer)
            
            # Obtener thickness desde field_config
            thickness = field_config.get('bold_thickness', 0.7)
            
            # Dibujar el texto en la capa temporal con offset para centrar
            offset_x = padding // 2
            offset_y = padding // 2
            self.simular_negritas(temp_draw, offset_x, offset_y, texto, font, font_color, thickness=thickness)
            
            # Redimensionar SOLO horizontalmente al ancho exacto del contenedor
            final_width = fit_width
            final_height = text_height  # Mantener altura original
            scaled_layer = temp_layer.resize((final_width, final_height), Image.Resampling.LANCZOS)
            
            # Usar configuración del JSON para posicionamiento - SIEMPRE empezar en el mismo punto izquierdo
            left_x = pos['x'] + pos.get('offset_x', 0)  # Posición fija desde JSON
            top_y = pos['y'] + pos.get('offset_y', 0)   # Posición fija desde JSON
            
            # Pegar la capa escalada en la imagen base
            img_base.paste(scaled_layer, (left_x, top_y), scaled_layer)
            
            print(f"   ✅ Texto estirado SOLO horizontalmente: {final_width}x{final_height} (altura original mantenida)")
        else:
            # Verificar si tiene escalado manual (como N°PASAPORTE1 y N°PASAPORTE2)
            scale_x = field_config.get('scale_x', 1.0)
            scale_y = field_config.get('scale_y', 1.0)
            
            if scale_x != 1.0 or scale_y != 1.0:
                # Crear una capa temporal para el texto escalado
                temp_width = int(text_width * scale_x)
                temp_height = int(text_height * scale_y)
                temp_layer = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
                temp_draw = ImageDraw.Draw(temp_layer)
                
                # Obtener thickness desde field_config
                thickness = field_config.get('bold_thickness', 0.7)
                
                # Dibujar el texto en la capa temporal
                self.simular_negritas(temp_draw, 0, 0, texto, font, font_color, thickness=thickness)
                
                # Redimensionar la capa temporal
                scaled_layer = temp_layer.resize((temp_width, temp_height), Image.Resampling.LANCZOS)
                
                # Usar configuración del JSON para posicionamiento
                left_x, top_y = self.calcular_posicion_desde_json(pos)
                
                # Pegar la capa escalada en la imagen base
                img_base.paste(scaled_layer, (left_x, top_y), scaled_layer)
                
                print(f"   🔧 Escalado manual aplicado: {scale_x}x{scale_y} -> {temp_width}x{temp_height}")
            else:
                # Usar configuración del JSON para posicionamiento
                left_x, top_y = self.calcular_posicion_desde_json(pos)
                
                # Dibujar el texto en negritas (grosor desde JSON)
                draw = ImageDraw.Draw(img_base)
                thickness = field_config.get('bold_thickness', 0.7)
                letter_spacing = field_config.get('letter_spacing', 0)
                blur_radius = field_config.get('blur_radius', 0)
                
                if letter_spacing != 0 or blur_radius > 0:
                    # Aplicar espaciado entre letras y/o difuminado
                    blur_padding = field_config.get('blur_padding', {'normal': 5, 'hyphen': 8})
                    self.dibujar_texto_con_espaciado(draw, left_x, top_y, texto, font, font_color, thickness, letter_spacing, blur_radius, blur_padding)
                else:
                    # Dibujo normal sin espaciado ni difuminado
                    self.simular_negritas(draw, left_x, top_y, texto, font, font_color, thickness=thickness)
        
        print(f"   ✅ {campo} insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: {font_name}, top-left")
        
        return img_base
    
    def insertar_fecha_con_contenedores_individuales(self, img_base, campo, texto, x, y, field_config, mostrar_contenedores=False):
        """Inserta una fecha con contenedores individuales para cada elemento"""
        try:
            # Dividir la fecha en elementos
            partes = texto.split('/')
            if len(partes) != 4:
                print(f"   ❌ Formato de fecha inválido: {texto}")
                return img_base
            
            dia, mes_es, mes_en, año = partes
            
            # CONTENEDORES CONFIGURABLES DESDE JSON CON POSICIONES INDIVIDUALES
            contenedores_config = field_config.get('contenedores_individuales', {})
            
            # Valores por defecto si no están en el JSON
            contenedores = {
                'dia': {
                    'ancho': contenedores_config.get('dia', {}).get('ancho', 25),
                    'alto': contenedores_config.get('dia', {}).get('alto', 17),
                    'x': contenedores_config.get('dia', {}).get('x', 0),
                    'y': contenedores_config.get('dia', {}).get('y', 0),
                    'texto': dia,
                    'color_borde': contenedores_config.get('dia', {}).get('color_borde', '#FF0000'),
                    'grosor_borde': contenedores_config.get('dia', {}).get('grosor_borde', 2)
                },
                'mes_es': {
                    'ancho': contenedores_config.get('mes_es', {}).get('ancho', 35),
                    'alto': contenedores_config.get('mes_es', {}).get('alto', 17),
                    'x': contenedores_config.get('mes_es', {}).get('x', 33),
                    'y': contenedores_config.get('mes_es', {}).get('y', 0),
                    'texto': mes_es,
                    'color_borde': contenedores_config.get('mes_es', {}).get('color_borde', '#FF0000'),
                    'grosor_borde': contenedores_config.get('mes_es', {}).get('grosor_borde', 2)
                },
                'mes_en': {
                    'ancho': contenedores_config.get('mes_en', {}).get('ancho', 35),
                    'alto': contenedores_config.get('mes_en', {}).get('alto', 17),
                    'x': contenedores_config.get('mes_en', {}).get('x', 76),
                    'y': contenedores_config.get('mes_en', {}).get('y', 0),
                    'texto': mes_en,
                    'color_borde': contenedores_config.get('mes_en', {}).get('color_borde', '#FF0000'),
                    'grosor_borde': contenedores_config.get('mes_en', {}).get('grosor_borde', 2)
                },
                'año': {
                    'ancho': contenedores_config.get('año', {}).get('ancho', 40),
                    'alto': contenedores_config.get('año', {}).get('alto', 17),
                    'x': contenedores_config.get('año', {}).get('x', 119),
                    'y': contenedores_config.get('año', {}).get('y', 0),
                    'texto': año,
                    'color_borde': contenedores_config.get('año', {}).get('color_borde', '#FF0000'),
                    'grosor_borde': contenedores_config.get('año', {}).get('grosor_borde', 2)
                }
            }
            
            # Separadores configurable con posiciones individuales
            separadores_config = {
                'separador1': contenedores_config.get('separador1', {}),
                'separador2': contenedores_config.get('separador2', {}),
                'separador3': contenedores_config.get('separador3', {})
            }
            
            # Obtener configuración de fuente
            font_name = field_config.get('font_name', 'Arial')
            font_size_pt = field_config.get('font_size_pt', 12)
            font_color = field_config.get('font_color', '#000000')
            thickness = field_config.get('bold_thickness', 0)
            
            # Cargar fuente usando el método existente
            font = self.obtener_fuente(font_name, font_size_pt)
            
            # Renderizar cada elemento en su posición individual
            elementos = ['dia', 'mes_es', 'mes_en', 'año']
            
            for i, elemento in enumerate(elementos):
                contenedor = contenedores[elemento]
                texto_elemento = contenedor['texto']
                ancho_contenedor = contenedor['ancho']
                alto_contenedor = contenedor['alto']
                pos_x = contenedor['x']
                pos_y = contenedor['y']
                
                # TEXTO INDEPENDIENTE DEL CONTENEDOR - Solo referencia visual
                # Obtener propiedades de fuente del contenedor individual (usar render_size_pt si existe)
                font_size_pt = contenedores_config.get(elemento, {}).get('render_size_pt', contenedores_config.get(elemento, {}).get('font_size', 12))
                font_color = contenedores_config.get(elemento, {}).get('font_color', '#000000')
                bold_thickness = contenedores_config.get(elemento, {}).get('bold_thickness', 0)
                letter_spacing = contenedores_config.get(elemento, {}).get('letter_spacing', 0)
                
                # Cargar fuente usando el método existente
                font = self.obtener_fuente(font_name, font_size_pt)
                
                # Obtener dimensiones del texto
                bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), texto_elemento, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # POSICIONAMIENTO ABSOLUTO INDEPENDIENTE DEL CONTENEDOR
                # Usar text_x y text_y como coordenadas absolutas desde la posición base
                text_x_absoluto = x + pos_x + contenedores_config.get(elemento, {}).get('text_x', 0)
                text_y_absoluto = y + pos_y + contenedores_config.get(elemento, {}).get('text_y', 0)
                
                # Dibujar el texto directamente en la imagen base (independiente del contenedor)
                draw = ImageDraw.Draw(img_base)
                draw.text((text_x_absoluto, text_y_absoluto), texto_elemento, font=font, fill=font_color)
                
                # Dibujar contenedor de referencia visual solo si se solicita
                if mostrar_contenedores:
                    color_borde = contenedor.get('color_borde', '#FF0000')
                    grosor_borde = contenedor.get('grosor_borde', 2)
                    final_x = x + pos_x
                    final_y = y + pos_y
                    draw.rectangle([final_x, final_y, final_x + ancho_contenedor-1, final_y + alto_contenedor-1], 
                                 outline=color_borde, width=grosor_borde)
                
                print(f"   📝 {elemento.capitalize()}: '{texto_elemento}' en posición ({text_x_absoluto}, {text_y_absoluto}) - contenedor {ancho_contenedor}x{alto_contenedor}px")
                
                # Agregar separador si no es el último elemento
                if i < len(elementos) - 1:
                    separador_key = f'separador{i+1}'
                    separador_config = separadores_config.get(separador_key, {})
                    
                    separador_ancho = separador_config.get('ancho', 8)
                    separador_alto = separador_config.get('alto', 17)
                    separador_x = separador_config.get('x', 0)
                    separador_y = separador_config.get('y', 0)
                    separador_color = separador_config.get('color_borde', '#0000FF')
                    separador_grosor = separador_config.get('grosor_borde', 2)
                    
                    # SEPARADOR INDEPENDIENTE DEL CONTENEDOR - Solo referencia visual
                    # Obtener propiedades de fuente del separador individual (usar render_size_pt si existe)
                    sep_font_size_pt = separador_config.get('render_size_pt', separador_config.get('font_size', 12))
                    sep_font_color = separador_config.get('font_color', '#000000')
                    sep_bold_thickness = separador_config.get('bold_thickness', 0)
                    sep_letter_spacing = separador_config.get('letter_spacing', 0)
                    
                    sep_font = self.obtener_fuente(font_name, sep_font_size_pt)
                    
                    # Obtener dimensiones del separador
                    sep_bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), '/', font=sep_font)
                    sep_width = sep_bbox[2] - sep_bbox[0]
                    sep_height = sep_bbox[3] - sep_bbox[1]
                    
                    # POSICIONAMIENTO ABSOLUTO INDEPENDIENTE DEL CONTENEDOR
                    # Usar text_x y text_y como coordenadas absolutas desde la posición base
                    sep_text_x_absoluto = x + separador_x + separador_config.get('text_x', 0)
                    sep_text_y_absoluto = y + separador_y + separador_config.get('text_y', 0)
                    
                    # Dibujar el separador directamente en la imagen base (independiente del contenedor)
                    draw = ImageDraw.Draw(img_base)
                    draw.text((sep_text_x_absoluto, sep_text_y_absoluto), '/', font=sep_font, fill=sep_font_color)
                    
                    # Dibujar contenedor de referencia visual solo si se solicita
                    if mostrar_contenedores:
                        separador_final_x = x + separador_x
                        separador_final_y = y + separador_y
                        draw.rectangle([separador_final_x, separador_final_y, separador_final_x + separador_ancho-1, separador_final_y + separador_alto-1], 
                                     outline=separador_color, width=separador_grosor)
                    
                    print(f"   📝 {separador_key.capitalize()}: '/' en posición ({sep_text_x_absoluto}, {sep_text_y_absoluto}) - contenedor {separador_ancho}x{separador_alto}px")
            
            print(f"   ✅ Fecha con contenedores individuales insertada en posición ({x}, {y})")
            return img_base
            
        except Exception as e:
            print(f"   ❌ Error insertando fecha con contenedores individuales: {e}")
            return img_base
    
    def insertar_code_negritas(self, img_base, texto, font_size_pt=16):
        """Inserta el campo code en negritas"""
        field_config = self.config['field_mapping'].get('code')
        if not field_config:
            print("   ❌ Error: Configuración para 'code' no encontrada")
            return img_base
        
        pos = field_config['position']
        x, y = pos['x'], pos['y']
        ancho, alto = pos['ancho'], pos['alto']
        font_color = field_config.get('font_color', '#000000')
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', font_size_pt))
        # Obtener fuente según mapeo del JSON
        layer_name = field_config.get('layer_name', 'CODE')
        font_name = self.config['fonts']['font_mapping'].get(layer_name, "Arial")
        font = self.obtener_fuente(font_name, font_size_pt)
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📝 Insertando code: {texto}")
        print(f"   ✅ Fuente {font_name} cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Crear una imagen temporal para el texto con negritas más compacto y alto
        temp_text_layer = Image.new('RGBA', (text_width + 12, text_height + 20), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_text_layer)
        # Usar color gris opaco fijo (requerimiento)
        gray_color = "#666666"
        thickness = field_config.get('bold_thickness', 1)
        self.simular_negritas(temp_draw, 6, 10, texto, font, gray_color, thickness=thickness)
        
        # Usar configuración del JSON para posicionamiento
        left_x, top_y = self.calcular_posicion_desde_json(pos)
        
        # Pegar el texto con negritas en la plantilla
        img_base.paste(temp_text_layer, (left_x, top_y), temp_text_layer)
        
        print(f"   ✅ code insertado en posición ({left_x}, {top_y})")
        print(f"   📏 Tamaño: {font_size_pt} pt, fuente: {font_name}, negritas, color gris opaco, formato compacto y alto, top-left")
        
        return img_base
    
    def insertar_firma_texto(self, img_base, texto_firma="Firma Digital", fuente_personalizada=None):
        """Inserta el texto de firma usando configuración JSON - más grande, negritas y centrada"""
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
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', 25))
        layer_name = field_config['layer_name']
        
        # Elegir fuente solo de la lista blanca; si la propuesta no está, buscar la primera disponible de la whitelist
        candidatos = []
        if fuente_personalizada and fuente_personalizada in self.fuentes_firma_whitelist:
            candidatos.append(fuente_personalizada)
        for f in self.fuentes_firma_whitelist:
            if f not in candidatos:
                candidatos.append(f)
        
        font = None
        fuente_a_usar = None
        for candidato in candidatos:
            try:
                font = self.obtener_fuente(candidato, font_size_pt)
                fuente_a_usar = candidato
                print(f"   ✅ Fuente de firma aprobada (whitelist): {candidato}")
                break
            except Exception as e:
                print(f"   ⚠️ Fuente no disponible o no válida para firma: {candidato} ({e})")
                continue
        
        # Fallback final a BrittanySignature si nada cargó
        if font is None:
            try:
                fuente_a_usar = "BrittanySignature.ttf"
                font = self.obtener_fuente(fuente_a_usar, font_size_pt)
                print(f"   ✅ Fallback a {fuente_a_usar}")
            except Exception as e:
                print(f"   ❌ No se pudo cargar ninguna fuente manuscrita ni BrittanySignature: {e}")
                # No usar Arial para firmas; abortar inserción de firma para evitar aspecto artificial
                return img_base
        
        # Obtener dimensiones del texto
        bbox = font.getbbox(texto_firma)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        print(f"   📏 Dimensiones del texto: {text_width}x{text_height}")
        print(f"   📏 Dimensiones del rectángulo: {ancho}x{alto}")
        
        # Crear una imagen temporal para el texto con negritas suaves
        # Usar padding mínimo para maximizar área útil
        padding = 8
        temp_text_layer = Image.new('RGBA', (text_width + 2*padding, text_height + 2*padding), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_text_layer)
        
        # Usar color específico solicitado
        color_suave = "#444549"  # Color específico #444549
        
        # Aplicar negritas con grosor desde JSON
        thickness = field_config.get('bold_thickness', 1)
        self.simular_negritas(temp_draw, padding, padding, texto_firma, font, color_suave, thickness=thickness)
        
        # Escalado dinámico para encajar al contenedor sin desbordarse
        scale_w = ancho / max(1, temp_text_layer.width)
        scale_h = alto / max(1, temp_text_layer.height)
        scale = min(scale_w, scale_h)
        # Permitir crecer hasta llenar el 96% del contenedor y reducir si es necesario
        target_scale = min(scale, 0.96)
        if abs(target_scale - 1.0) > 0.02:
            new_w = max(1, int(temp_text_layer.width * target_scale))
            new_h = max(1, int(temp_text_layer.height * target_scale))
            temp_text_layer = temp_text_layer.resize((new_w, new_h), Image.Resampling.LANCZOS)
            print(f"   🔧 Firma escalada para encajar: {new_w}x{new_h} (cont: {ancho}x{alto})")
        
        # Calcular posición centrada en el rectángulo
        center_x = x + (ancho - temp_text_layer.width) // 2
        center_y = y + (alto - temp_text_layer.height) // 2
        
        # Ajuste fino para mejor centrado visual
        center_x = max(x, center_x)  # No salir del rectángulo por la izquierda
        center_y = max(y, center_y)  # No salir del rectángulo por arriba
        
        # Ajuste fino vertical
        center_y = center_y - 4
        
        # Pegar el texto con negritas suaves en la plantilla
        img_base.paste(temp_text_layer, (center_x, center_y), temp_text_layer)
        
        print(f"   ✅ firma_texto insertado en posición centrada ({center_x}, {center_y})")
        print(f"   📏 Tamaño base: {font_size_pt} pt, fuente: {fuente_a_usar}, color: {color_suave}")
        
        return img_base
    
    def generar_mrz_linea1(self, nombre, apellido, numero_pasaporte):
        """
        Genera línea 1 del código MRZ (Machine Readable Zone)
        
        FORMATO MRZ LÍNEA 1 CORRECTO:
        P<VEN{APELLIDO}<<{NOMBRE}<<<<<<<<<<<<<<<
        
        Donde:
        - P = Tipo de documento (Pasaporte)
        - < = Separador
        - VEN = Código de país (Venezuela)
        - APELLIDO = Apellido completo (máximo 20 caracteres, relleno con <)
        - << = Separador doble
        - NOMBRE = Nombre completo (máximo 20 caracteres, relleno con <)
        - <<<<<<<<<<<<<<< = Relleno final (15 caracteres)
        
        TOTAL: 44 caracteres
        """
        import re
        
        # Limpiar y formatear apellido (sin espacios, solo letras)
        apellido_limpio = re.sub(r'[^A-Z]', '', apellido.upper())[:20]
        apellido_padded = apellido_limpio.ljust(20, '<')
        
        # Limpiar y formatear nombre (sin espacios, solo letras)
        nombre_limpio = re.sub(r'[^A-Z]', '', nombre.upper())[:20]
        nombre_padded = nombre_limpio.ljust(20, '<')
        
        # Construir línea MRZ completa (44 caracteres)
        mrz_linea = f"P<VEN{apellido_padded}<<{nombre_padded}"
        
        # Asegurar que tenga exactamente 44 caracteres
        if len(mrz_linea) < 44:
            mrz_linea = mrz_linea.ljust(44, '<')
        elif len(mrz_linea) > 44:
            mrz_linea = mrz_linea[:44]
        
        return mrz_linea
    
    def generar_mrz_linea2(self, numero_pasaporte, fecha_nacimiento, sexo):
        """
        Genera línea 2 del código MRZ (Machine Readable Zone)
        
        FORMATO MRZ LÍNEA 2 CORRECTO:
        {NUMERO_PASAPORTE}{CHECK_DIGIT}{PAIS}{FECHA_NAC}{SEXO}{FECHA_VENC}{CHECK_DIGIT}{RELLENO}{CHECK_DIGIT}
        
        Donde:
        - NUMERO_PASAPORTE = Número de pasaporte (9 dígitos)
        - CHECK_DIGIT = Dígito de verificación del número de pasaporte
        - PAIS = Código de país (VEN)
        - FECHA_NAC = Fecha de nacimiento (YYMMDD)
        - SEXO = F (Femenino) o M (Masculino)
        - FECHA_VENC = Fecha de vencimiento (YYMMDD)
        - CHECK_DIGIT = Dígito de verificación adicional
        - RELLENO = Relleno con < (15 caracteres)
        - CHECK_DIGIT = Dígito de verificación final
        
        TOTAL: 44 caracteres
        """
        import random
        from datetime import datetime, date
        
        # Formatear fecha de nacimiento para MRZ
        if isinstance(fecha_nacimiento, str):
            fecha = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
        else:
            fecha = fecha_nacimiento
        
        fecha_mrz = f"{str(fecha.year)[-2:]}{fecha.month:02d}{fecha.day:02d}"
        
        # Fecha de vencimiento (10 años después)
        fecha_vencimiento = date(fecha.year + 10, 1, 1)
        fecha_venc_mrz = f"{str(fecha_vencimiento.year)[-2:]}{fecha_vencimiento.month:02d}{fecha_vencimiento.day:02d}"
        
        # Sexo para MRZ
        sexo_mrz = 'F' if sexo.upper() == 'F' else 'M'
        
        # Generar dígitos de verificación (simulados)
        check_digit_pasaporte = random.randint(0, 9)
        check_digit_adicional = random.randint(0, 9)
        check_digit_final = random.randint(0, 9)
        
        # Construir línea MRZ completa
        mrz_linea = f"{numero_pasaporte}{check_digit_pasaporte}VEN{fecha_mrz}{sexo_mrz}{fecha_venc_mrz}{check_digit_adicional}<<<<<<<<<<<<<<<{check_digit_final}"
        
        # Asegurar que tenga exactamente 44 caracteres
        if len(mrz_linea) < 44:
            mrz_linea = mrz_linea.ljust(44, '<')
        elif len(mrz_linea) > 44:
            mrz_linea = mrz_linea[:44]
        
        return mrz_linea

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
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', font_size_pt))
        # Obtener fuente desde font_mapping
        font_name = self.config['fonts']['font_mapping'].get(layer_name, "OCR-B10PitchBT Regular.otf")
        try:
            font = self.obtener_fuente(font_name, font_size_pt)
            print(f"   ✅ Fuente {font_name} cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        except Exception as e:
            print(f"   ⚠️ Error al cargar {font_name}: {e}")
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
    
    def insertar_letra_final2(self, img_base, texto_letra_final2="1086413983VEN9708141M2503011<<<<<<<<<<<<<<<6", font_size_pt=106.8):
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
        
        # Usar el tamaño según configuración JSON (render_size_pt si existe, sino font_size)
        font_size_pt = field_config.get('render_size_pt', field_config.get('font_size', font_size_pt))
        # Obtener fuente desde font_mapping
        font_name = self.config['fonts']['font_mapping'].get(layer_name, "OCR-B10PitchBT Regular.otf")
        try:
            font = self.obtener_fuente(font_name, font_size_pt)
            print(f"   ✅ Fuente {font_name} cargada: {font_size_pt} pt = {self.puntos_a_pixeles(font_size_pt)} px (DPI 96)")
        except Exception as e:
            print(f"   ⚠️ Error al cargar {font_name}: {e}")
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
        
        # Obtener datos del pasaporte si están disponibles
        datos = getattr(self, 'datos_pasaporte', {})
        
        # USAR UNA SOLA VARIABLE PARA EL NÚMERO DE PASAPORTE
        # Todos los campos tomarán el valor de esta variable
        # PRIORIZAR el número de pasaporte de los datos sobre el parámetro
        
        # 2. Insertar número de pasaporte N°PASAPORTE1
        img_base = self.insertar_numero_pasaporte1(img_base, numero_pasaporte)
        
        # 3. Insertar número de pasaporte N°PASAPORTE2
        img_base = self.insertar_numero_pasaporte2(img_base, numero_pasaporte)
        
        # 4. Insertar tipo de documento TIPO
        img_base = self.insertar_tipo_documento(img_base, "P")
        
        # 5. Insertar país emisor PAÍS
        img_base = self.insertar_pais_emisor(img_base, "VEN")
        # 6. Insertar campos de texto estándar (tamaños ajustados)
        # Usar datos dinámicos si están disponibles, sino usar datos por defecto
        datos = getattr(self, 'datos_pasaporte', {})
        
        nombre = datos.get('nombre_completo', 'LA MASCARA')
        apellido = datos.get('apellido_completo', 'PLANTILLAS VIRTUALES')
        fecha_nacimiento = datos.get('fecha_nacimiento', '14 / Ago / Ago / 1997')
        cedula = datos.get('cedula', '12345678')
        fecha_emision = datos.get('fecha_emision', '12 / Mar / Mar / 2020')
        fecha_vencimiento = datos.get('fecha_vencimiento', '01 / Mar / Mar / 2025')
        sexo = datos.get('sexo', 'F')
        nacionalidad = datos.get('nacionalidad', 'VENEZOLANA')
        lugar_nacimiento = datos.get('lugar_nacimiento', 'MARACAIBO VEN')
        codigo_verificacion = datos.get('codigo_verificacion', '14-04-97')
        firma = datos.get('firma', 'Firma Digital')
        mrz_linea1 = datos.get('mrz_linea1', 'P<VENVARGARCIAGONZALEZ<<MARCOS<<<<<<<<<<<<<<<')
        # CORREGIR MRZ LÍNEA 2: Debe usar el número de pasaporte consistente
        mrz_linea2_original = datos.get('mrz_linea2', '1086413983VEN9708141M2503011<<<<<<<<<<<<<<<6')
        mrz_linea2 = self.corregir_mrz_linea2(mrz_linea2_original, numero_pasaporte)
        
        
        img_base = self.insertar_nombre_alineado_izquierda(img_base, nombre)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "apellido", apellido)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_nacimiento", fecha_nacimiento)
        img_base = self.insertar_texto_estandar(img_base, "numero_documento", cedula)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_emision", fecha_emision)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "fecha_vencimiento", fecha_vencimiento)
        img_base = self.insertar_texto_estandar(img_base, "sexo", sexo)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "nacionalidad", nacionalidad)
        img_base = self.insertar_texto_alineado_izquierda(img_base, "lugar_nacimiento", lugar_nacimiento)
        # Usar el número de pasaporte consistente (ya validado arriba)
        img_base = self.insertar_texto_estandar(img_base, "numero_pasaporte", numero_pasaporte)
        img_base = self.insertar_texto_estandar(img_base, "codigo_barras", codigo_verificacion)
        
        # 7. Insertar firma (más grande, negritas y centrada) con fuente personalizada
        fuente_firma = getattr(self, 'datos_pasaporte', {}).get('fuente_firma')
        # Aumentar el tamaño de la firma para que llene mejor el contenedor
        img_base = self.insertar_firma_texto(img_base, firma, fuente_personalizada=fuente_firma)
        
        # 8. Insertar letra final1
        img_base = self.insertar_letra_final1(img_base, mrz_linea1)
        
        # 9. Insertar letra final2
        img_base = self.insertar_letra_final2(img_base, mrz_linea2)
        
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

    def corregir_mrz_linea2(self, mrz_original, numero_pasaporte_correcto):
        """
        Corrige la línea 2 del MRZ para usar el número de pasaporte correcto
        
        FORMATO MRZ LÍNEA 2:
        {NUMERO_PASAPORTE}{CHECK_DIGIT}{PAIS}{FECHA_NAC}{SEXO}{FECHA_VENC}{CHECK_DIGIT}{RELLENO}{CHECK_DIGIT}
        """
        
        try:
            # Si el MRZ original ya tiene el número correcto, devolverlo
            if mrz_original.startswith(numero_pasaporte_correcto):
                return mrz_original
            
            # Extraer componentes del MRZ original
            if len(mrz_original) >= 44:
                # Extraer partes del MRZ original
                check_digit_pasaporte = mrz_original[9] if len(mrz_original) > 9 else '0'
                pais = mrz_original[10:13] if len(mrz_original) > 13 else 'VEN'
                fecha_nac = mrz_original[13:19] if len(mrz_original) > 19 else '900101'
                sexo = mrz_original[19] if len(mrz_original) > 19 else 'M'
                fecha_venc = mrz_original[20:26] if len(mrz_original) > 26 else '000101'
                check_digit_adicional = mrz_original[26] if len(mrz_original) > 26 else '0'
                relleno = mrz_original[27:42] if len(mrz_original) > 42 else '<<<<<<<<<<<<<<<'
                check_digit_final = mrz_original[42] if len(mrz_original) > 42 else '0'
                
                # Construir nuevo MRZ con el número de pasaporte correcto
                nuevo_mrz = f"{numero_pasaporte_correcto}{check_digit_pasaporte}{pais}{fecha_nac}{sexo}{fecha_venc}{check_digit_adicional}{relleno}{check_digit_final}"
                
                # Asegurar que tenga exactamente 44 caracteres
                if len(nuevo_mrz) < 44:
                    nuevo_mrz = nuevo_mrz.ljust(44, '<')
                elif len(nuevo_mrz) > 44:
                    nuevo_mrz = nuevo_mrz[:44]
                
                return nuevo_mrz
            else:
                # Si el MRZ es muy corto, generar uno básico
                return f"{numero_pasaporte_correcto}0VEN900101M0001010<<<<<<<<<<<<<<<0"
                
        except Exception as e:
            print(f"   ⚠️ Error corrigiendo MRZ: {e}")
            # Devolver MRZ básico con el número correcto
            return f"{numero_pasaporte_correcto}0VEN900101M0001010<<<<<<<<<<<<<<<0"

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
