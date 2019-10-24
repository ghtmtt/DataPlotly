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
from qgis.PyQt.QtWidgets import QGraphicsItem

from qgis.core import (
    QgsLayoutItem,
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata,
    QgsNetworkAccessManager,
    QgsLayoutMeasurement,
    QgsUnitTypes,
    QgsMessageLog,
    QgsProject,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsExpressionContextGenerator
)
from qgis.PyQt.QtWebKitWidgets import QWebPage

from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.core.plot_factory import PlotFactory
from DataPlotly.gui.gui_utils import GuiUtils

ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 1337


class LoggingWebPage(QWebPage):

    def __init__(self, parent=None):
        super().__init__(parent)

    def javaScriptConsoleMessage(self, message, lineNumber, source):
        QgsMessageLog.logMessage('{}:{} {}'.format(source, lineNumber, message), 'DataPlotly')


class PlotLayoutItem(QgsLayoutItem):

    def __init__(self, layout):
        super().__init__(layout)
        self.setCacheMode(QGraphicsItem.NoCache)
        self.plot_settings = PlotSettings()
        self.linked_map_uuid = ''
        self.linked_map = None

        self.filter_by_map = False
        self.filter_by_atlas = False

        self.web_page = LoggingWebPage(self)
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
        self.html_units_to_layout_units = self.calculate_html_units_to_layout_units()

        self.sizePositionChanged.connect(self.refresh)

    def type(self):
        return ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('dataplotly.svg')

    def calculate_html_units_to_layout_units(self):
        if not self.layout():
            return 1

        # Hm - why is this? Something internal in Plotly which is auto-scaling the html content?
        # we may need to expose this as a "scaling" setting

        return 72

    def set_linked_map(self, map):
        """
        Sets the map linked to the plot item
        """
        self.linked_map = map

    def set_plot_settings(self, settings):
        """
        Sets the plot settings to show in the item
        """
        self.plot_settings = settings
        self.html_loaded = False
        self.invalidateCache()

    def draw(self, context):
        if not self.html_loaded:
            self.load_content()

        # almost a direct copy from QgsLayoutItemLabel!
        painter = context.renderContext().painter()
        painter.save()

        # painter is scaled to dots, so scale back to layout units
        painter.scale(context.renderContext().scaleFactor() / self.html_units_to_layout_units,
                      context.renderContext().scaleFactor() / self.html_units_to_layout_units)
        self.web_page.mainFrame().render(painter)
        painter.restore()

    def create_plot(self):
        factory = PlotFactory(self.plot_settings, self)
        config = {'displayModeBar': False, 'staticPlot': True}
        return factory.build_html(config)

    def load_content(self):
        self.html_loaded = False
        base_url = QUrl.fromLocalFile(self.layout().project().absoluteFilePath())
        self.web_page.setViewportSize(QSize(self.rect().width() * self.html_units_to_layout_units,
                                            self.rect().height() * self.html_units_to_layout_units))
        self.web_page.mainFrame().setHtml(self.create_plot(), base_url)

    def writePropertiesToElement(self, element, document, _):
        element.appendChild(self.plot_settings.write_xml(document))
        element.setAttribute('filter_by_map', 1 if self.filter_by_map else 0)
        element.setAttribute('filter_by_atlas', 1 if self.filter_by_atlas else 0)
        element.setAttribute('linked_map', self.linked_map.uuid() if self.linked_map else '')
        return True

    def readPropertiesFromElement(self, element, document, context):
        res = self.plot_settings.read_xml(element.firstChildElement('Option'))

        self.filter_by_map = bool(int(element.attribute('filter_by_map', '0')))
        self.filter_by_atlas = bool(int(element.attribute('filter_by_atlas', '0')))
        self.linked_map_uuid = element.attribute('linked_map')

        self.html_loaded = False
        self.invalidateCache()
        return res

    def finalizeRestoreFromXml(self):
        # has to happen after ALL items have been restored
        if self.layout() and self.linked_map_uuid:
            map = self.layout().itemByUuid(self.linked_map_uuid)
            if map:
                self.set_linked_map(map)

    def loading_html_finished(self):
        self.html_loaded = True
        self.invalidateCache()
        self.update()

    def refresh(self):
        super().refresh()
        self.html_loaded = False
        self.invalidateCache()


class PlotLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(ITEM_TYPE, QCoreApplication.translate('DataPlotly', 'Plot Item'))

    def createItem(self, layout):
        return PlotLayoutItem(layout)
