# -*- coding: utf-8 -*-
"""GUI Utilities

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from qgis.PyQt.QtGui import QIcon


class GuiUtils:
    """
    Utilities for GUI plugin components
    """

    @staticmethod
    def get_icon(icon: str) -> QIcon:
        """
        Returns a plugin icon
        :param icon: icon name (svg file name)
        :return: QIcon
        """
        path = GuiUtils.get_icon_svg(icon)
        if not path:
            return QIcon()

        return QIcon(path)

    @staticmethod
    def get_icon_svg(icon: str) -> str:
        """
        Returns a plugin icon's SVG file path
        :param icon: icon name (svg file name)
        :return: icon svg path
        """
        path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'icons',
            icon)
        if not os.path.exists(path):
            return ''

        return path

    @staticmethod
    def get_ui_file_path(file: str) -> str:
        """
        Returns a UI file's path
        :param file: file name (uifile name)
        :return: ui file path
        """
        path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'ui',
            file)
        if not os.path.exists(path):
            return ''

        return path
