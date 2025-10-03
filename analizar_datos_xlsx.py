#!/usr/bin/env python3
"""
Script para analizar el archivo Excel y entender su estructura
"""

import pandas as pd
import os
from pathlib import Path

def analizar_excel():
    """Analiza el archivo Excel para entender su estructura"""
    excel_path = "/media/warcklian/DATA_500GB/CODE/SISTEMA_PASAPORTES_FINAL/DATA/Datos_Crear_Pasaportes.xlsx"
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(excel_path)
        
        print("📊 ANÁLISIS DEL ARCHIVO EXCEL")
        print("=" * 50)
        print(f"📁 Archivo: {excel_path}")
        print(f"📏 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"📋 Columnas disponibles: {list(df.columns)}")
        print("\n📝 Primeras 5 filas:")
        print(df.head())
        
        print("\n📊 Información de tipos de datos:")
        print(df.dtypes)
        
        print("\n📈 Estadísticas descriptivas:")
        print(df.describe(include='all'))
        
        print("\n🔍 Valores únicos por columna:")
        for col in df.columns:
            unique_count = df[col].nunique()
            print(f"   {col}: {unique_count} valores únicos")
            if unique_count <= 10:  # Mostrar valores si son pocos
                print(f"      Valores: {df[col].unique()}")
        
        # Verificar si hay valores nulos
        print("\n❓ Valores nulos por columna:")
        null_counts = df.isnull().sum()
        for col, count in null_counts.items():
            if count > 0:
                print(f"   {col}: {count} valores nulos")
        
        return df
        
    except Exception as e:
        print(f"❌ Error al leer el archivo Excel: {e}")
        return None

if __name__ == "__main__":
    df = analizar_excel()
