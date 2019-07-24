# -*- coding: utf-8 -*-
"""Dock widget

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.gui import QgsDockWidget


class DataPlotlyDock(QgsDockWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr('DataPlotly'))
        self.setObjectName('DataPlotlyDock')

