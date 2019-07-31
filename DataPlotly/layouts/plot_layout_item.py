# -*- coding: utf-8 -*-
"""Plot Layout Item

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtCore import (
    Qt,
    QCoreApplication,
    QRectF,
    QSize,
    QUrl,
    QEventLoop,
    QTimer
)
from qgis.PyQt.QtGui import QPalette

from qgis.core import (
    QgsLayoutItem,
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata,
    QgsNetworkAccessManager,
    QgsLayoutMeasurement,
    QgsUnitTypes
)
from qgis.PyQt.QtWebKitWidgets import QWebPage

from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.gui.gui_utils import GuiUtils

ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 1337


class PlotLayoutItem(QgsLayoutItem):

    def __init__(self, layout):
        super().__init__(layout)
        self.plot_settings = PlotSettings()
        self.web_page = QWebPage(self)
        self.web_page.setNetworkAccessManager(QgsNetworkAccessManager.instance())

        # This makes the background transparent. (copied from QgsLayoutItemLabel)
        palette = self.web_page.palette()
        palette.setBrush(QPalette.Base, Qt.transparent)
        self.web_page.setPalette(palette)
        self.web_page.mainFrame().setZoomFactor(10.0)
        self.web_page.mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self.web_page.mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)

        self.web_page.loadFinished.connect(self.loading_html_finished)
        self.html_loaded = False
        self.first_render = True
        self.html_units_to_layout_units = self.calculate_html_units_to_layout_units()

    def type(self):
        return ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('dataplotly.svg')

    def calculate_html_units_to_layout_units(self):
        if not self.layout():
            return 1

        # webkit seems to assume a standard dpi of 72
        return self.layout().convertToLayoutUnits(
            QgsLayoutMeasurement(self.layout().renderContext().dpi() / 72.0, QgsUnitTypes.LayoutMillimeters))

    def set_plot_settings(self, settings):
        """
        Sets the plot settings to show in the item
        """
        self.plot_settings = settings
        self.html_loaded = False
        self.update()

    def draw(self, context):
        # almost a direct copy from QgsLayoutItemLabel!
        painter = context.renderContext().painter()
        painter.save()

        # painter is scaled to dots, so scale back to layout units
        painter.scale(context.renderContext().scaleFactor(), context.renderContext().scaleFactor())
        pen_width = self.pen().widthF() / 2.0 if self.frameEnabled() else 0
        painter_rect = QRectF(pen_width, pen_width, self.rect().width() - 2 * pen_width,
                              self.rect().height() - 2 * pen_width)
        if self.first_render:
            self.load_content()
            self.first_render = False

        painter.scale(1.0 / self.html_units_to_layout_units / 10.0, 1.0 / self.html_units_to_layout_units / 10.0)
        self.web_page.setViewportSize(QSize(painter_rect.width() * self.html_units_to_layout_units * 10.0,
                                            painter_rect.height() * self.html_units_to_layout_units * 10.0))
        self.web_page.mainFrame().render(painter)
        painter.restore()

    def load_content(self):
        test = '<p>aaaa<b>AAAA</b>aaaaaaa</p>'
        self.html_loaded = False

        base_url = QUrl.fromLocalFile(self.layout().project().absoluteFilePath())
        self.web_page.mainFrame().setHtml(test, base_url)

        # For very basic html labels with no external assets, the html load will already be
        # complete before we even get a chance to start the QEventLoop. Make sure we check
        # this before starting the loop
        if not self.html_loaded:
            # Setup event loop and timeout for rendering html
            loop = QEventLoop()

            # Connect timeout and webpage loadFinished signals to loop
            self.web_page.loadFinished.connect(loop.quit)

            # Start a 20 second timeout in case html loading will never complete
            timeout_timer = QTimer()
            timeout_timer.setSingleShot(True)
            timeout_timer.timeout.connect(loop.quit)
            timeout_timer.start(20000)

            # Pause until html is loaded
            loop.exec(QEventLoop.ExcludeUserInputEvents)

    def writePropertiesToElement(self, element, document, _):
        element.appendChild(self.plot_settings.write_xml(document))
        return True

    def readPropertiesFromElement(self, element, document, context):
        return self.plot_settings.read_xml(element.firstChildElement('Option'))

    def loading_html_finished(self):
        self.html_loaded = True


class PlotLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(ITEM_TYPE, QCoreApplication.translate('DataPlotly', 'Plot Item'))

    def createItem(self, layout):
        return PlotLayoutItem(layout)
