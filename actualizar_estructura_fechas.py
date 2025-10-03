#!/usr/bin/env python3
"""
Script para actualizar la estructura de todos los contenedores de fecha_nacimiento
"""

import json
import os

def actualizar_estructura_fechas():
    """Actualiza la estructura de todos los contenedores de fecha_nacimiento"""
    
    config_path = "/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL/CONFIG/config.json"
    
    # Cargar configuración
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Estructura objetivo
    estructura_objetivo = {
        "y": -2,
        "ancho": 25,
        "alto": 23,
        "text_x": 0,
        "text_y": -1,
        "font_size": 12,
        "font_color": "#000000",
        "bold_thickness": 0,
        "letter_spacing": 0,
        "color_borde": "#FF0000",
        "grosor_borde": 2
    }
    
    # Campos de fecha que tienen contenedores individuales
    campos_fecha = ['fecha_nacimiento', 'fecha_emision', 'fecha_vencimiento']
    
    for campo in campos_fecha:
        if campo in config['field_mapping']:
            contenedores = config['field_mapping'][campo].get('contenedores_individuales', {})
            
            # Actualizar cada elemento
            elementos = ['dia', 'mes_es', 'mes_en', 'año', 'separador1', 'separador2', 'separador3']
            
            for elemento in elementos:
                if elemento in contenedores:
                    # Mantener x individual, actualizar resto
                    x_original = contenedores[elemento].get('x', 0)
                    
                    # Aplicar estructura objetivo
                    contenedores[elemento].update(estructura_objetivo)
                    
                    # Restaurar x original
                    contenedores[elemento]['x'] = x_original
                    
                    # Mantener color_borde para separadores
                    if elemento.startswith('separador'):
                        contenedores[elemento]['color_borde'] = '#0000FF'
    
    # Guardar configuración actualizada
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Estructura actualizada para todos los contenedores de fechas")
    print("📋 Campos actualizados:")
    for campo in campos_fecha:
        print(f"   • {campo}")
        contenedores = config['field_mapping'][campo].get('contenedores_individuales', {})
        for elemento in ['dia', 'mes_es', 'mes_en', 'año', 'separador1', 'separador2', 'separador3']:
            if elemento in contenedores:
                y = contenedores[elemento].get('y', 'N/A')
                ancho = contenedores[elemento].get('ancho', 'N/A')
                alto = contenedores[elemento].get('alto', 'N/A')
                text_x = contenedores[elemento].get('text_x', 'N/A')
                text_y = contenedores[elemento].get('text_y', 'N/A')
                print(f"     - {elemento}: y={y}, ancho={ancho}, alto={alto}, text_x={text_x}, text_y={text_y}")

if __name__ == "__main__":
    actualizar_estructura_fechas()
