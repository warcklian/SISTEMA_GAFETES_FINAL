import os
import shutil
import sys
from typing import Optional, Tuple

import pandas as pd

try:
    from unidecode import unidecode
except Exception:  # pragma: no cover
    unidecode = None  # Se manejará en tiempo de ejecución

try:
    import gender_guesser.detector as gender
except Exception:  # pragma: no cover
    gender = None

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:  # pragma: no cover
    tk = None
    filedialog = None
    messagebox = None


NOMBRES_ES_DICT = {
    # Overrides rápidos y comunes en español (ampliable)
    "maria": "Femenino",
    "maría": "Femenino",
    "jose": "Masculino",
    "josé": "Masculino",
    "juan": "Masculino",
    "carlos": "Masculino",
    "luis": "Masculino",
    "ana": "Femenino",
    "luisa": "Femenino",
    "sofia": "Femenino",
    "sofía": "Femenino",
    "andres": "Masculino",
    "andrés": "Masculino",
    "marta": "Femenino",
    "laura": "Femenino",
    "paula": "Femenino",
    "pablo": "Masculino",
    "pedro": "Masculino",
    "diego": "Masculino",
    "camila": "Femenino",
    "valentina": "Femenino",
}


def normalizar_nombre_bruto(nombre_bruto: str) -> str:
    if not isinstance(nombre_bruto, str):
        return ""
    texto = nombre_bruto.strip()
    if unidecode is not None:
        try:
            texto = unidecode(texto)
        except Exception:
            pass
    return texto.lower()


def extraer_primer_nombre(texto_nombre: str) -> str:
    if not texto_nombre:
        return ""
    partes = texto_nombre.split()
    return partes[0] if partes else ""


def inferir_genero_por_nombre(primer_nombre: str, detector: Optional[object]) -> Tuple[str, str]:
    nombre_norm = normalizar_nombre_bruto(primer_nombre)

    # 1) Diccionario español (override)
    if nombre_norm in NOMBRES_ES_DICT:
        return NOMBRES_ES_DICT[nombre_norm], "diccionario_es"

    # 2) Heurística: terminación típica en español
    if nombre_norm.endswith("a") and len(nombre_norm) > 2:
        return "Femenino", "heuristica_terminacion_a"
    if nombre_norm.endswith("o") and len(nombre_norm) > 2:
        return "Masculino", "heuristica_terminacion_o"

    # 3) gender-guesser (si disponible)
    if detector is not None and nombre_norm:
        try:
            resultado = detector.get_gender(nombre_norm)
            if resultado in ("female", "mostly_female"):
                return "Femenino", "gender_guesser"
            if resultado in ("male", "mostly_male"):
                return "Masculino", "gender_guesser"
        except Exception:
            pass

    return "Desconocido", "sin_coincidencia"


def detectar_columnas(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    # Se asume: primera columna es género a completar si su nombre sugiere género
    posibles_genero = {"genero", "género", "sexo", "gender"}
    posibles_nombre = {"nombre", "nombres", "nombre completo", "full name", "persona", "titular"}

    col_genero = None
    col_nombre = None

    columnas_norm = {c: normalizar_nombre_bruto(c) for c in df.columns}

    # Detectar nombre
    for c, cn in columnas_norm.items():
        if cn in posibles_nombre or any(p in cn for p in ("nombre", "name")):
            col_nombre = c
            break

    # Detectar género (prioriza primera columna si coincide)
    primera = list(df.columns)[0]
    if normalizar_nombre_bruto(primera) in posibles_genero:
        col_genero = primera
    else:
        for c, cn in columnas_norm.items():
            if cn in posibles_genero:
                col_genero = c
                break

    return col_nombre, col_genero


def crear_backup(ruta_xlsx: str) -> Optional[str]:
    try:
        base, ext = os.path.splitext(ruta_xlsx)
        backup = f"{base}.backup{ext}"
        shutil.copy2(ruta_xlsx, backup)
        return backup
    except Exception:
        return None


def procesar_xlsx_en_sitio(ruta_xlsx: str) -> Tuple[int, int]:
    # Cargar DataFrame (primera hoja por defecto)
    df = pd.read_excel(ruta_xlsx)

    col_nombre, col_genero = detectar_columnas(df)
    if not col_nombre:
        raise ValueError("No se pudo detectar la columna de nombres. Renombra la columna (ej.: 'Nombre').")
    if not col_genero:
        # Si no existe, crear la primera columna 'Género'
        df.insert(0, "Género", None)
        col_genero = "Género"

    # Inicializar detector si está disponible
    detector = None
    if gender is not None:
        try:
            detector = gender.Detector(case_sensitive=False)
        except Exception:
            detector = None

    completados = 0
    total_faltantes = 0

    # Completar únicamente faltantes o vacíos
    for idx, fila in df.iterrows():
        val_genero = fila.get(col_genero)
        if pd.isna(val_genero) or (isinstance(val_genero, str) and not val_genero.strip()):
            total_faltantes += 1
            nombre_bruto = str(fila.get(col_nombre, ""))
            primer_nombre = extraer_primer_nombre(nombre_bruto)
            genero_inferido, _fuente = inferir_genero_por_nombre(primer_nombre, detector)
            if genero_inferido != "Desconocido":
                df.at[idx, col_genero] = genero_inferido
                completados += 1

    # Guardar de vuelta en el mismo archivo, reemplazando la primera hoja
    # Usamos engine openpyxl para mayor compatibilidad
    with pd.ExcelWriter(ruta_xlsx, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        # Si no sabemos el nombre de la hoja original, por defecto 'Sheet1'
        # Para mantener nombre, leemos los nombres de hojas primero
        try:
            xls = pd.ExcelFile(ruta_xlsx)
            sheet_name = xls.sheet_names[0] if xls.sheet_names else "Sheet1"
        except Exception:
            sheet_name = "Sheet1"
        df.to_excel(writer, index=False, sheet_name=sheet_name)

    return completados, total_faltantes


def seleccionar_archivo_ui() -> Optional[str]:
    if tk is None or filedialog is None:
        print("tkinter no está disponible en este entorno.")
        return None
    root = tk.Tk()
    root.withdraw()
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx")],
    )
    return ruta


def main():
    if len(sys.argv) > 1:
        ruta = sys.argv[1]
    else:
        ruta = seleccionar_archivo_ui()

    if not ruta:
        print("No se seleccionó archivo.")
        return

    if not os.path.isfile(ruta):
        print(f"Ruta inválida: {ruta}")
        return

    backup = crear_backup(ruta)
    if backup:
        print(f"Backup creado: {backup}")
    else:
        print("No se pudo crear backup (continuando con precaución)...")

    try:
        completados, faltantes = procesar_xlsx_en_sitio(ruta)
        msg = (
            f"Completados {completados} de {faltantes} géneros faltantes. "
            f"Archivo actualizado: {ruta}"
        )
        print(msg)
        if messagebox is not None:
            try:
                messagebox.showinfo("Proceso finalizado", msg)
            except Exception:
                pass
    except Exception as e:
        print(f"Error procesando archivo: {e}")
        if messagebox is not None:
            try:
                messagebox.showerror("Error", str(e))
            except Exception:
                pass


if __name__ == "__main__":
    main()


