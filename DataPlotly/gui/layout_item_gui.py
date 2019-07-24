# -*- coding: utf-8 -*-
"""Plot Layout Gui Handling

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QWidget,
    QVBoxLayout
)
from qgis.gui import (
    QgsLayoutItemAbstractGuiMetadata,
    QgsLayoutItemBaseWidget
)

from DataPlotly.layouts.plot_layout_item import ITEM_TYPE
from DataPlotly.gui.gui_utils import GuiUtils
from DataPlotly.data_plotly_dialog import DataPlotlyPanelWidget

class PlotLayoutItemWidget(QgsLayoutItemBaseWidget):

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)

        vl = QVBoxLayout()
        vl.setContentsMargins(0,0,0,0)

        self.widget = DataPlotlyPanelWidget()
        vl.addWidget(self.widget)
        self.setLayout(vl)


class PlotLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(ITEM_TYPE, QCoreApplication.translate('DataPlotly', 'Plot Item'))

    def creationIcon(self):
        return GuiUtils.get_icon('dataplotly.svg')

    def createItemWidget(self, item):
        return PlotLayoutItemWidget(None, item)
