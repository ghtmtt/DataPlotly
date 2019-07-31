# -*- coding: utf-8 -*-
"""Plot Layout Gui Handling

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QPushButton,
    QVBoxLayout
)
from qgis.gui import (
    QgsLayoutItemAbstractGuiMetadata,
    QgsLayoutItemBaseWidget,
    QgsLayoutItemPropertiesWidget
)

from DataPlotly.layouts.plot_layout_item import ITEM_TYPE
from DataPlotly.gui.gui_utils import GuiUtils
from DataPlotly.gui.plot_settings_widget import DataPlotlyPanelWidget


class PlotLayoutItemWidget(QgsLayoutItemBaseWidget):

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)
        self.plot_item = layout_object

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)

        self.plot_properties_button = QPushButton(self.tr('Plot Properties'))
        vl.addWidget(self.plot_properties_button)
        self.plot_properties_button.clicked.connect(self.show_properties)

        self.panel = None
        self.setPanelTitle(self.tr('Plot Properties'))
        self.item_properties_widget = QgsLayoutItemPropertiesWidget(self, layout_object)
        vl.addWidget(self.item_properties_widget)
        self.setLayout(vl)

    def show_properties(self):
        self.panel = DataPlotlyPanelWidget()
        self.panel.set_settings(self.plot_item.plot_settings)
        # self.panel.set_settings(self.layoutItem().plot_settings)
        self.openPanel(self.panel)
        self.panel.panelAccepted.connect(self.set_item_settings)

    def set_item_settings(self):
        if not self.panel:
            return

        self.plot_item.plot_settings = self.panel.get_settings()
        self.panel = None
        self.plot_item.update()

    def setNewItem(self, item):
        if item.type() != ITEM_TYPE:
            return False

        self.plot_item = item
        self.item_properties_widget.setItem(item)

        if self.panel is not None:
            self.panel.set_settings(self.plot_item.plot_settings)

        return True


class PlotLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):

    def __init__(self):
        super().__init__(ITEM_TYPE, QCoreApplication.translate('DataPlotly', 'Plot Item'))

    def creationIcon(self):
        return GuiUtils.get_icon('dataplotly.svg')

    def createItemWidget(self, item):
        return PlotLayoutItemWidget(None, item)
