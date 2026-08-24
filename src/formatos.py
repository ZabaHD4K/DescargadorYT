# -*- coding: utf-8 -*-
"""Lógica pura de procesamiento de formatos de yt-dlp.

Extraída de descargador.py a un módulo propio para poder testearla sin
arrancar la GUI ni tocar la red. Es el punto históricamente más frágil
del programa (throttling y duplicados HLS de YouTube), así que es el que
más se beneficia de tests de regresión (ver tests/test_formatos.py).

descargador.py la importa; PyInstaller la empaqueta automáticamente al
seguir el import, sin cambios en el .spec.
"""


def familia_codec(vcodec_raw):
    """Normaliza el vcodec a una familia legible: vp9, av01, avc1, etc."""
    if not vcodec_raw or vcodec_raw == 'none':
        return 'unknown'
    base = vcodec_raw.split('.')[0].lower()
    if base.startswith('avc'):
        return 'avc1'
    if base.startswith('av01') or base == 'av1':
        return 'av01'
    if base.startswith('vp9') or base == 'vp09':
        return 'vp9'
    if base.startswith('vp8'):
        return 'vp8'
    if base.startswith('hev') or base == 'h265':
        return 'hevc'
    return base[:5]


def procesar_formatos_video(formats):
    """Devuelve la lista de formatos de vídeo ordenada y lista para la UI.

    - Deduplica por (altura, familia de códec, fps, rango dinámico) quedándose
      con el de mayor tbr en cada choque.
    - DESCARTA los formatos HLS (m3u8): yt-dlp los expone como duplicados
      "Untested" de los DASH, con tbr estimado inflado (así ganaban el
      desempate) y producen mp4 con timestamps sin definir que rompen el
      merge a MKV ("Can't write packet with unknown timestamp"). Los DASH
      (protocol=https) cubren todas las resoluciones y mergean correctamente.
    - Ordena por altura, fps, SDR<HDR y tbr, de mayor a menor.

    No incluye la entrada de "Audio Only" (eso lo añade la UI).
    """
    formatos_video = {}

    for f in formats or []:
        tiene_video = f.get('vcodec') not in ['none', None]
        height = f.get('height')

        protocolo = f.get('protocol') or ''
        if 'm3u8' in protocolo:
            continue

        if tiene_video and height:
            vcodec = familia_codec(f.get('vcodec'))
            fps = int(f.get('fps') or 30)
            format_id = f.get('format_id')
            if not format_id:
                continue

            # HDR / dynamic range para no colapsar SDR y HDR en la misma key
            dynamic_range = (f.get('dynamic_range') or 'SDR').upper()
            key = f"{height}_{vcodec}_{fps}_{dynamic_range}"

            # Preferir el formato con mayor tbr (bitrate) si hay choque
            tbr = f.get('tbr') or 0
            existente = formatos_video.get(key)
            if existente and existente.get('_tbr', 0) >= tbr:
                continue

            etiqueta = f"{height}p ({vcodec}, {fps}fps"
            if dynamic_range and dynamic_range != 'SDR':
                etiqueta += f", {dynamic_range}"
            etiqueta += ")"

            formatos_video[key] = {
                'height': height,
                'format_id': format_id,
                'fps': fps,
                'vcodec': vcodec,
                'dynamic_range': dynamic_range,
                '_tbr': tbr,
                'label': etiqueta,
            }

    return sorted(
        formatos_video.values(),
        key=lambda x: (x['height'], x['fps'], 0 if x['dynamic_range'] == 'SDR' else 1, x.get('_tbr', 0)),
        reverse=True
    )
