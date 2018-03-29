# -*- coding: utf-8 -*-

"""
QR code that be scanned to allow login
"""

import qrcode
import tempfile
import webbrowser
from decimal import Decimal
from qrcode.image.svg import SvgPathImage
from .constants import JIKE_URI_SCHEME_FMT, RENDER2BROWSER_HTML_TEMPLATE


def make_qrcode(uuid, render_choice='browser'):
    qr = qrcode.QRCode(
        version=8,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=4,
    )
    qr.add_data(JIKE_URI_SCHEME_FMT.format(**uuid))
    qr.make()

    render_choices = {
        'browser': render2browser,
        'terminal': render2terminal,
        'viewer': render2viewer
    }

    assert render_choice in render_choices, 'Unsupported render choice'
    render_choices[render_choice](qr)


def render2terminal(qr):
    qr.print_tty()


def render2browser(qr):

    img = qr.make_image(image_factory=CustomedSvgPathImage)
    with tempfile.NamedTemporaryFile(suffix='.svg') as fp:
        img.save(fp)
        fp.seek(0)
        content = fp.read().decode('utf-8').splitlines()
    svg = content[1]
    assert svg.startswith('<svg') and svg.endswith('</svg>')
    html = RENDER2BROWSER_HTML_TEMPLATE.format(qrcode_svg=svg)

    _, path = tempfile.mkstemp(suffix='.html')
    with open(path, 'wt', encoding='utf-8') as fp:
        fp.write(html)
    webbrowser.open(f'file://{fp.name}')


def render2viewer(qr):
    img = qr.make_image()
    _, path = tempfile.mkstemp(suffix='.png')
    with open(path, 'wb') as fp:
        img.save(fp)
    webbrowser.open(f'file://{fp.name}')


class CustomedSvgPathImage(SvgPathImage):
    def units(self, pixels, text=True):
        """
        A box_size of 10 (default) equals 10mm.
        """
        units = Decimal(pixels) / 2
        if not text:
            return units
        return '%smm' % units

