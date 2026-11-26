"""Core Utilities

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
import uuid

import requests

from qgis.PyQt.QtCore import QByteArray

DOC_URL = "https://ghtmtt.github.io/DataPlotly/"

def help_doc_url(locale):
    """return the correct help url with locale
    """
    generic_url = f"https://ghtmtt.github.io/DataPlotly/{locale}/"
    response = requests.get(generic_url)

    # fallback to en if there are no translations
    if response.status_code != 200:
        return "https://ghtmtt.github.io/DataPlotly/en/"
    else:
        return generic_url

def safe_str_xml(s):
    """ replaces spaces by .
    """
    return s.replace(" ", ".")


def restore_safe_str_xml(s):
    """ replaces . by spaces
    """
    return s.replace(".", " ")


def restore(b_str_64):
    """state and geom are stored in  str(Base64) in project xml file"""
    return QByteArray.fromBase64(QByteArray(b_str_64.encode()))


def uuid_suffix(string: str) -> str:
    """ uuid4 suffix"""
    return f"{string}{uuid.uuid4()}"
