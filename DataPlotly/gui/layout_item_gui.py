# -*- coding: utf-8 -*-
"""Plot Layout Gui Handling

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.gui import (
    QgsLayoutItemAbstractGuiMetadata
)

from DataPlotly.layouts.plot_layout_item import ITEM_TYPE
from DataPlotly.gui.gui_utils import GuiUtils


class PlotLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(ITEM_TYPE, QCoreApplication.translate('DataPlotly', 'Plot Item'))

    def creationIcon(self):
        return GuiUtils.get_icon('dataplotly.svg')

    def createItemWidget(self, item):
        # todo
        return None
