# -*- coding: utf-8 -*-
"""Dock widget

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.gui import (
    QgsDockWidget,
    QgsPanelWidgetStack
)
from DataPlotly.gui.plot_settings_widget import DataPlotlyPanelWidget


class DataPlotlyDock(QgsDockWidget):  # pylint: disable=too-few-public-methods
    """
    Plot settings dock widget
    """

    def __init__(self, parent=None, message_bar=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr('DataPlotly'))
        self.setObjectName('DataPlotlyDock')

        self.panel_stack = QgsPanelWidgetStack()
        self.setWidget(self.panel_stack)

        self.main_panel = DataPlotlyPanelWidget(message_bar=message_bar)
        self.panel_stack.setMainPanel(self.main_panel)
        self.main_panel.setDockMode(True)
