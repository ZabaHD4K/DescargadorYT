# -*- coding: utf-8 -*-
"""Tests de regresión de la selección de formatos.

Se ejecutan con: python -m unittest discover -s tests -v
(no requieren dependencias externas: solo la stdlib y src/formatos.py).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from formatos import procesar_formatos_video, familia_codec  # noqa: E402


class TestProcesarFormatosVideo(unittest.TestCase):

    def test_descarta_hls_y_prefiere_dash(self):
        """Regresión v1.7.0: el HLS (m3u8) trae tbr inflado; NO debe ganar al
        DASH (https), porque su mp4 rompe el merge a MKV."""
        formats = [
            {'format_id': '270', 'height': 1080, 'fps': 30, 'vcodec': 'avc1.640028',
             'tbr': 6368, 'protocol': 'm3u8_native'},   # HLS -> descartar
            {'format_id': '137', 'height': 1080, 'fps': 30, 'vcodec': 'avc1.640028',
             'tbr': 2654, 'protocol': 'https'},          # DASH -> elegir
        ]
        res = procesar_formatos_video(formats)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['format_id'], '137')

    def test_todos_los_formatos_hls_se_ignoran(self):
        formats = [
            {'format_id': '232', 'height': 720, 'fps': 30, 'vcodec': 'avc1', 'tbr': 3426,
             'protocol': 'm3u8_native'},
            {'format_id': '270', 'height': 1080, 'fps': 30, 'vcodec': 'avc1', 'tbr': 6368,
             'protocol': 'm3u8'},
        ]
        self.assertEqual(procesar_formatos_video(formats), [])

    def test_hdr_no_colisiona_con_sdr(self):
        formats = [
            {'format_id': 'sdr', 'height': 2160, 'fps': 30, 'vcodec': 'vp09', 'tbr': 1000,
             'protocol': 'https', 'dynamic_range': 'SDR'},
            {'format_id': 'hdr', 'height': 2160, 'fps': 30, 'vcodec': 'vp09', 'tbr': 900,
             'protocol': 'https', 'dynamic_range': 'HDR'},
        ]
        res = procesar_formatos_video(formats)
        self.assertEqual(len(res), 2)

    def test_ignora_audio_only(self):
        formats = [
            {'format_id': '251', 'height': None, 'vcodec': 'none', 'acodec': 'opus',
             'protocol': 'https'},
        ]
        self.assertEqual(procesar_formatos_video(formats), [])

    def test_dedup_conserva_mayor_tbr(self):
        formats = [
            {'format_id': 'lo', 'height': 720, 'fps': 30, 'vcodec': 'avc1', 'tbr': 500,
             'protocol': 'https'},
            {'format_id': 'hi', 'height': 720, 'fps': 30, 'vcodec': 'avc1', 'tbr': 1500,
             'protocol': 'https'},
        ]
        res = procesar_formatos_video(formats)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['format_id'], 'hi')

    def test_orden_descendente_por_altura(self):
        formats = [
            {'format_id': 'a', 'height': 720, 'fps': 30, 'vcodec': 'avc1', 'tbr': 500,
             'protocol': 'https'},
            {'format_id': 'b', 'height': 1080, 'fps': 30, 'vcodec': 'avc1', 'tbr': 500,
             'protocol': 'https'},
        ]
        res = procesar_formatos_video(formats)
        self.assertEqual([r['height'] for r in res], [1080, 720])

    def test_lista_vacia_o_none(self):
        self.assertEqual(procesar_formatos_video([]), [])
        self.assertEqual(procesar_formatos_video(None), [])


class TestFamiliaCodec(unittest.TestCase):

    def test_familias_conocidas(self):
        self.assertEqual(familia_codec('avc1.640028'), 'avc1')
        self.assertEqual(familia_codec('vp09.00.40.08'), 'vp9')
        self.assertEqual(familia_codec('av01.0.08M.08'), 'av01')
        self.assertEqual(familia_codec('hev1.1.6'), 'hevc')

    def test_desconocido_o_vacio(self):
        self.assertEqual(familia_codec('none'), 'unknown')
        self.assertEqual(familia_codec(None), 'unknown')
        self.assertEqual(familia_codec(''), 'unknown')


if __name__ == '__main__':
    unittest.main()
