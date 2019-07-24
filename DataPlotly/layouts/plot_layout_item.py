# -*- coding: utf-8 -*-
"""Plot Layout Item

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsLayoutItem,
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata
)
from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.gui.gui_utils import GuiUtils
ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 1337


class PlotLayoutItem(QgsLayoutItem):

    def __init__(self, layout):
        super().__init__(layout)
        self.plot_settings = PlotSettings()

    def type(self):
        return ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('dataplotly.svg')

    def draw(self, context):
        pass

    def writePropertiesToElement(self, element, document, _):
        element.appendChild(self.plot_settings.write_xml(document))
        return True

    def readPropertiesFromElement(self, element, document, context):
        return self.plot_settings.read_xml(element.firstChildElement('Option'))


class PlotLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(ITEM_TYPE, QCoreApplication.translate('DataPlotly', 'Plot Item'))

    def createItem(self, layout):
        return PlotLayoutItem(layout)
