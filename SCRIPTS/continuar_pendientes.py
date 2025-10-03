#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
import pandas as pd


def encontrar_ultimo_result_csv(data_dir: Path) -> Path | None:
    candidatos = sorted(data_dir.glob("*_RESULT_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidatos[0] if candidatos else None


def crear_csv_pendientes(result_csv: Path) -> Path:
    df = pd.read_csv(result_csv, dtype=str, keep_default_na=False)
    # Columnas de estado añadidas por el generador
    if "estado" in df.columns:
        pendientes = df[df["estado"].astype(str).str.lower() == "omitido"].copy()
    else:
        # Fallback: si no hay 'estado', usar pasaporte_visual vacío
        col = "pasaporte_visual" if "pasaporte_visual" in df.columns else None
        if col is None:
            raise RuntimeError("El RESULT CSV no contiene columnas de estado ni pasaporte_visual")
        pendientes = df[df[col].astype(str).str.len() == 0].copy()

    if pendientes.empty:
        raise RuntimeError("No hay registros pendientes (omitidos) en el RESULT CSV")

    # Guardar CSV de pendientes junto al RESULT
    out = result_csv.with_name(result_csv.stem.replace("_RESULT", "_PENDIENTES") + ".csv")
    pendientes.to_csv(out, index=False, encoding="utf-8")
    return out


def ejecutar_generador(csv_pendientes: Path, base_path: Path | None = None) -> None:
    # Importar clase principal
    proyecto_root = base_path or Path(__file__).resolve().parents[1]
    sys.path.append(str(proyecto_root))
    from generador_pasaportes_masivo import GeneradorPasaportesMasivo

    generador = GeneradorPasaportesMasivo(str(proyecto_root))
    # Ejecutar directamente sin GUI usando el CSV de pendientes
    generador.generar_pasaportes_masivos(limite=None, archivo_excel=str(csv_pendientes))


def main():
    parser = argparse.ArgumentParser(description="Reprocesar pendientes desde RESULT CSV y continuar generación")
    parser.add_argument("--result-csv", dest="result_csv", help="Ruta al RESULT CSV (si se omite, se busca el más reciente en DATA/")
    parser.add_argument("--base-path", dest="base_path", help="Ruta base del proyecto (opcional)")
    parser.add_argument("--solo-csv", action="store_true", help="Solo crear CSV de pendientes, sin ejecutar generación")
    args = parser.parse_args()

    base = Path(args.base_path) if args.base_path else Path(__file__).resolve().parents[1]
    data_dir = base / "DATA"

    result_csv = Path(args.result_csv) if args.result_csv else encontrar_ultimo_result_csv(data_dir)
    if not result_csv or not result_csv.exists():
        raise SystemExit("No se encontró RESULT CSV. Genera primero un RESULT ejecutando el generador principal.")

    pend_csv = crear_csv_pendientes(result_csv)
    print(f"📄 CSV de pendientes creado: {pend_csv}")

    if not args.solo_csv:
        ejecutar_generador(pend_csv, base)


if __name__ == "__main__":
    main()


