#!/usr/bin/env python3
import os
import time
import statistics
from pathlib import Path

import psutil

from PIL import Image

from script_maestro_integrado import ScriptMaestroIntegrado


def medir(func, *args, repeticiones=1, **kwargs):
    tiempos = []
    resultado = None
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        resultado = func(*args, **kwargs)
        t1 = time.perf_counter()
        tiempos.append(t1 - t0)
    return resultado, tiempos


def bytes_a_mb(x):
    return x / (1024 * 1024)


def info_gpu():
    info = {"disponible": False, "backend": "cpu", "detalle": ""}
    # onnxruntime
    try:
        import onnxruntime as ort
        providers = getattr(ort, "get_available_providers", lambda: [])()
        info["ort_providers"] = providers
        if "CUDAExecutionProvider" in providers:
            info["disponible"] = True
            info["backend"] = "onnx-cuda"
            info["detalle"] = "ORT CUDAExecutionProvider"
    except Exception as e:
        info["ort_error"] = str(e)

    # torch
    try:
        import torch
        if torch.cuda.is_available():
            info["disponible"] = True
            info["backend"] = "torch-cuda"
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["vram_total_mb"] = int(torch.cuda.get_device_properties(0).total_memory / (1024*1024))
    except Exception as e:
        info["torch_error"] = str(e)

    return info


def main():
    base_path = Path("/media/warcklian/DATA_500GB/CODE/Plantillas_PSD_Automatizar")
    imagenes_ok_dir = base_path / "DATA" / "Imagenes_OK"
    # Buscar una imagen de prueba
    candidatos = list(imagenes_ok_dir.rglob("*.png")) + list(imagenes_ok_dir.rglob("*.jpg")) + list(imagenes_ok_dir.rglob("*.jpeg"))
    if not candidatos:
        print(f" No se encontraron imágenes en {imagenes_ok_dir}")
        return 1
    ruta_foto = str(candidatos[0])

    print(" Benchmark de rendimiento (por pasaporte)")
    print("Imagen de prueba:", Path(ruta_foto).name)

    maestro = ScriptMaestroIntegrado()

    ginfo = info_gpu()
    print("GPU:", ginfo)

    # Medir etapas
    resultado, t_rembg = medir(maestro.remover_fondo_rembg, ruta_foto, repeticiones=3)
    if resultado is None:
        print(" rembg falló, abortando benchmark")
        return 1

    img_sin_fondo = resultado
    resultado, t_refinar = medir(maestro.refinar_contorno, img_sin_fondo, repeticiones=3)
    img_refinada = resultado

    resultado, t_det = medir(maestro.detectar_cara_y_escalar, img_refinada, repeticiones=3)
    img_proc = resultado

    # Recortar al contenedor configurado
    foto_config = maestro.config['field_mapping'].get('ruta_foto', {})
    target_w = foto_config.get('size', {}).get('width', 350)
    target_h = foto_config.get('size', {}).get('height', 450)
    resultado, t_rec = medir(maestro.recortar_imagen_por_contenedor, img_proc, target_w, target_h, repeticiones=3)
    img_rec = resultado

    resultado, t_fx = medir(maestro.aplicar_efectos_imagen, img_rec, repeticiones=3)

    def resumen(nombre, tiempos):
        return f"{nombre:28s} -> {statistics.mean(tiempos):6.3f}s (min {min(tiempos):.3f}s, max {max(tiempos):.3f}s)"

    print("\n⏱️ Tiempos por etapa (promedio de 3):")
    print(resumen("remover_fondo_rembg", t_rembg))
    print(resumen("refinar_contorno", t_refinar))
    print(resumen("detectar_cara_y_escalar", t_det))
    print(resumen("recortar_imagen", t_rec))
    print(resumen("aplicar_efectos", t_fx))

    # Medir end-to-end generación de un pasaporte
    resultado, t_full = medir(maestro.generar_gafete_integrado, ruta_foto, repeticiones=3)
    print(resumen("E2E generar_gafete", t_full))

    # Memoria
    proceso = psutil.Process()
    rss_mb = bytes_a_mb(proceso.memory_info().rss)
    print(f"\n Memoria RSS proceso: {rss_mb:.1f} MB")

    # Salida válida
    ok = resultado is not None and isinstance(resultado, Image.Image)
    print("\n️ Salida válida:", ok)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())


