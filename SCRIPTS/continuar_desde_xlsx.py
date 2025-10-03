#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime


def encontrar_ultimo_xlsx(generados_dir: Path) -> Path | None:
    candidatos = sorted(generados_dir.glob("pasaportes_procesados_*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidatos[0] if candidatos else None


def normalizar_str(x):
    return "" if pd.isna(x) else str(x)


def main():
    parser = argparse.ArgumentParser(description="Continuar generación desde el último XLSX en OUTPUT/pasaportes_generados (automático)")
    parser.add_argument("--xlsx", help="Ruta a un XLSX específico (opcional)")
    parser.add_argument("--base-path", help="Ruta base del proyecto (opcional)")
    args = parser.parse_args()

    base = Path(args.base_path) if args.base_path else Path(__file__).resolve().parents[1]
    generados_dir = base / "OUTPUT" / "pasaportes_generados"
    if not generados_dir.exists():
        raise SystemExit(f"No existe carpeta: {generados_dir}")

    # Selección de XLSX: argumento → diálogo GUI → cancelar detiene
    if args.xlsx:
        xlsx_path = Path(args.xlsx)
    else:
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk(); root.withdraw()
            seleccionado = filedialog.askopenfilename(
                title="Seleccionar XLSX de pasaportes a continuar",
                filetypes=[("Archivos Excel", "*.xlsx"), ("Todos", "*.*")],
                initialdir=str(generados_dir)
            )
            root.destroy()
            if not seleccionado:
                print("Operación cancelada por el usuario. No se seleccionó archivo.")
                return
            xlsx_path = Path(seleccionado)
        except Exception as e:
            raise SystemExit(f"No fue posible abrir el diálogo de selección: {e}")

    if not xlsx_path.exists():
        raise SystemExit("El XLSX seleccionado no existe.")

    # Importar generador principal y utilidades
    sys.path.append(str(base))
    from generador_pasaportes_masivo import GeneradorPasaportesMasivo

    generador = GeneradorPasaportesMasivo(str(base))

    # Cargar el XLSX existente
    df = pd.read_excel(xlsx_path, dtype=str)
    df = df.fillna("")

    # Backup de seguridad antes de modificar en sitio
    ts_backup = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = xlsx_path.with_name(xlsx_path.stem + f"_BACK_{ts_backup}.xlsx")
    try:
        df.to_excel(backup_path, index=False)
        print(f"🛡️ Backup creado: {backup_path.name}")
    except Exception as e:
        print(f"⚠️ No se pudo crear backup previo: {e}")

    # Determinar pendientes: sin pasaporte_visual
    col_pv = "pasaporte_visual" if "pasaporte_visual" in df.columns else None
    pendientes_idx = []
    if col_pv:
        pendientes_idx = [i for i, v in enumerate(df[col_pv].tolist()) if not str(v)]
    else:
        # Si no existe la columna, nada que completar
        print("No hay columna 'pasaporte_visual' en el XLSX. Nada que continuar.")
        return

    if not pendientes_idx:
        print(f"✅ El archivo está completo. No hay registros pendientes: {xlsx_path.name}")
        return

    print(f"📌 Registros pendientes: {len(pendientes_idx)}")

    generados = 0
    omitidos = 0
    for i in pendientes_idx:
        row = df.iloc[i].to_dict()

        # Recuperar datos mínimos para generar
        numero_pasaporte = normalizar_str(row.get("numero_pasaporte")) or normalizar_str(row.get("numero_pasaporte_1"))
        nombre_archivo = normalizar_str(row.get("nombre_archivo")) or (normalizar_str(row.get("correo_original")) + ".png")
        genero = normalizar_str(row.get("sexo", "F"))
        edad_str = normalizar_str(row.get("edad"))
        try:
            edad = int(edad_str) if edad_str else None
        except Exception:
            edad = None

        ruta_foto = normalizar_str(row.get("ruta_foto"))
        if not ruta_foto:
            # Buscar una imagen adecuada ahora que hay nuevas
            if edad is not None:
                img = generador.buscar_imagen_por_edad(edad, genero)
                if img:
                    ruta_foto = str(img)
            # Si sigue sin imagen, omitir
            if not ruta_foto:
                df.loc[i, "estado"] = "omitido"
                df.loc[i, "motivo_no_generado"] = f"Sin imagen adecuada (edad {edad if edad is not None else 'N/A'})"
                omitidos += 1
                continue

        # Construir estructura de datos esperada por el generador visual
        datos_pasaporte = {
            'ruta_foto': ruta_foto,
            'numero_pasaporte': numero_pasaporte or normalizar_str(row.get("numero_pasaporte_2")),
            'nombre_archivo': nombre_archivo,
            'tipo': row.get('tipo', 'P'),
            'pais_emisor': row.get('pais_emisor', 'VEN'),
            'nombre_completo': row.get('nombre_completo', ''),
            'apellido_completo': row.get('apellido_completo', ''),
            'fecha_nacimiento': row.get('fecha_nacimiento', ''),
            'cedula': row.get('cedula', ''),
            'fecha_emision': row.get('fecha_emision', ''),
            'fecha_vencimiento': row.get('fecha_vencimiento', ''),
            'sexo': row.get('sexo', 'F'),
            'nacionalidad': row.get('nacionalidad', 'VENEZOLANA'),
            'lugar_nacimiento': row.get('lugar_nacimiento', ''),
            'codigo_verificacion': row.get('codigo_verificacion', ''),
            'firma': row.get('firma', 'Firma Digital'),
            'mrz_linea1': row.get('mrz_linea1', ''),
            'mrz_linea2': row.get('mrz_linea2', '')
        }

        # Generar PNG
        png_path = generador.generar_pasaporte_visual(datos_pasaporte)
        if png_path:
            df.loc[i, "pasaporte_visual"] = png_path
            df.loc[i, "ruta_foto"] = ruta_foto
            df.loc[i, "imagen_usada"] = ruta_foto
            df.loc[i, "estado"] = "generado"
            df.loc[i, "motivo_no_generado"] = ""
            generados += 1
            # Marcar imagen como usada
            try:
                generador.mover_imagen_usada(ruta_foto)
            except Exception:
                pass
            # Guardar progreso en el mismo XLSX
            try:
                df.to_excel(xlsx_path, index=False)
            except Exception as e:
                print(f"⚠️ No se pudo guardar progreso en XLSX: {e}")
        else:
            df.loc[i, "estado"] = "omitido"
            df.loc[i, "motivo_no_generado"] = "Error generando pasaporte visual"
            omitidos += 1
            # Guardar progreso en el mismo XLSX
            try:
                df.to_excel(xlsx_path, index=False)
            except Exception as e:
                print(f"⚠️ No se pudo guardar progreso en XLSX: {e}")

    # Guardar al final sobre el mismo archivo
    try:
        df.to_excel(xlsx_path, index=False)
    except Exception as e:
        print(f"⚠️ No se pudo escribir XLSX final: {e}")

    print(f"✅ Continuación completada. Generados: {generados}, Omitidos: {omitidos}")
    print(f"📄 XLSX actualizado en sitio: {xlsx_path.name}")


if __name__ == "__main__":
    main()


