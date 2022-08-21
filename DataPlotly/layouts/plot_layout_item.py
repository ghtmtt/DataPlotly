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
    QgsMessageLog,
    QgsGeometry,
    QgsPropertyCollection
)
from qgis.PyQt.QtWebKitWidgets import QWebPage

from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.core.plot_factory import PlotFactory, FilterRegion
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
        self.plot_settings = []
        self.plot_settings.append(PlotSettings())
        self.linked_map_uuid = ''
        self.linked_map = None

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
        if self.linked_map == map:
            return

        self.disconnect_current_map()

        self.linked_map = map
        self.linked_map.extentChanged.connect(self.map_extent_changed)
        self.linked_map.mapRotationChanged.connect(self.map_extent_changed)
        self.linked_map.destroyed.connect(self.disconnect_current_map)

    def disconnect_current_map(self):
        if not self.linked_map:
            return

        try:
            self.linked_map.extentChanged.disconnect(self.map_extent_changed)
            self.linked_map.mapRotationChanged.disconnect(self.map_extent_changed)
            self.linked_map.destroyed.disconnect(self.disconnect_current_map)
        except RuntimeError:
            # c++ object already gone!
            pass
        self.linked_map = None

    def add_plot(self):
        """
        Adds a new plot to the item
        """
        plot_setting = PlotSettings()
        plot_setting.layout['bg_color'] = 'rgba(0,0,0,0)'
        self.plot_settings.append(plot_setting)
        return plot_setting

    def duplicate_plot(self, index):
        """
        Duplicates a plot and adds it to the item
        """
        if index < len(self.plot_settings):
            plot_setting = PlotSettings(self.plot_settings[index].plot_type, self.plot_settings[index].properties,
                                        self.plot_settings[index].layout, self.plot_settings[index].source_layer_id)
            plot_setting.data_defined_properties = QgsPropertyCollection(
                self.plot_settings[index].data_defined_properties)
            plot_setting.layout['bg_color'] = 'rgba(0,0,0,0)'
            self.plot_settings.insert(index + 1, plot_setting)
            return plot_setting

    def remove_plot(self, index):
        """
        Removes a plot from the item
        """
        return self.plot_settings.pop(index)

    def set_plot_settings(self, plot_id, settings):
        """
        Sets the plot settings to show in the item
        """
        if plot_id < len(self.plot_settings):
            self.plot_settings[plot_id] = settings
            self.plot_settings[plot_id].layout['bg_color'] = 'rgba(0,0,0,0)'
            self.html_loaded = False
            self.invalidateCache()

    def draw(self, context):
        if not self.html_loaded:
            self.load_content()

            if not self.layout().renderContext().isPreviewRender():
                # this is NOT safe to do when rendering in the gui (i.e. a preview render), but for exports we have
                # to loop around until the HTML has fully loaded
                while not self.html_loaded:
                    QCoreApplication.processEvents()

        # almost a direct copy from QgsLayoutItemLabel!
        painter = context.renderContext().painter()
        painter.save()

        # painter is scaled to dots, so scale back to layout units
        painter.scale(context.renderContext().scaleFactor() / self.html_units_to_layout_units,
                      context.renderContext().scaleFactor() / self.html_units_to_layout_units)
        self.web_page.mainFrame().render(painter)
        painter.restore()

    def create_plot(self):
        polygon_filter, visible_features_only = self.get_polygon_filter(0)

        config = {'displayModeBar': False, 'staticPlot': True}

        if len(self.plot_settings) == 1:
            plot_factory = PlotFactory(self.plot_settings[0], self, polygon_filter=polygon_filter)
            self.plot_settings[0].properties['visible_features_only'] = visible_features_only
            return plot_factory.build_html(config)

        # to plot many plots in the same figure
        elif len(self.plot_settings) > 1:
            # plot list ready to be called within go.Figure
            pl = []
            plot_factory = PlotFactory(self.plot_settings[0], self, polygon_filter=polygon_filter)

            for current, plot_setting in enumerate(self.plot_settings):
                polygon_filter, visible_features_only = self.get_polygon_filter(current)
                plot_setting.properties['visible_features_only'] = visible_features_only
                factory = PlotFactory(plot_setting, self, polygon_filter=polygon_filter)
                pl.append(factory.trace[0])

            plot_path = plot_factory.build_figures(self.plot_settings[0].plot_type, pl, config=config)
            with open(plot_path, 'r') as myfile:
                return myfile.read()

    def get_polygon_filter(self, index=0):
        polygon_filter = None
        visible_features_only = False

        if self.plot_settings:
            if self.linked_map and self.plot_settings[index].properties.get('layout_filter_by_map', False):
                polygon_filter = FilterRegion(QgsGeometry.fromQPolygonF(self.linked_map.visibleExtentPolygon()),
                                            self.linked_map.crs())
                visible_features_only = True
            elif self.plot_settings[index].properties.get('layout_filter_by_atlas', False) and \
                    self.layout().reportContext().layer() and self.layout().reportContext().feature().isValid():

                polygon_filter = FilterRegion(self.layout().reportContext().currentGeometry(), self.layout().reportContext().layer().crs())
                visible_features_only = True

        return polygon_filter, visible_features_only

    def load_content(self):
        self.html_loaded = False
        base_url = QUrl.fromLocalFile(self.layout().project().absoluteFilePath())
        self.web_page.setViewportSize(QSize(int(self.rect().width()) * self.html_units_to_layout_units,
                                            int(self.rect().height()) * self.html_units_to_layout_units))
        self.web_page.mainFrame().setHtml(self.create_plot(), base_url)

    def writePropertiesToElement(self, element, document, _) -> bool:
        for plot_setting in self.plot_settings:
            element.appendChild(plot_setting.write_xml(document))
        element.setAttribute('linked_map', self.linked_map.uuid() if self.linked_map else '')
        return True

    def readPropertiesFromElement(self, element, document, context) -> bool:
        self.plot_settings = []

        child = element.firstChildElement('Option')
        reading_result = True
        while reading_result:
            if child.isNull():
                break
            plot_setting = self.add_plot()
            reading_result = plot_setting.read_xml(child)

            # ensure layout plots from earlier versions always have transparent backgrounds
            plot_setting.layout['bg_color'] = 'rgba(0,0,0,0)'

            child = child.nextSiblingElement('Option')

        self.linked_map_uuid = element.attribute('linked_map')
        self.disconnect_current_map()

        self.html_loaded = False
        self.invalidateCache()
        return reading_result

    def finalizeRestoreFromXml(self):
        # has to happen after ALL items have been restored
        if self.layout() and self.linked_map_uuid:
            self.disconnect_current_map()
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

    def map_extent_changed(self):
        filter_by_map = False
        for setting in self.plot_settings:
            if setting.properties.get('layout_filter_by_map', False):
                filter_by_map = True
        if not self.linked_map or not filter_by_map:
            return

        self.html_loaded = False
        self.invalidateCache()

        self.update()


class PlotLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(ITEM_TYPE, QCoreApplication.translate('DataPlotly', 'Plot Item'))

    def createItem(self, layout):
        return PlotLayoutItem(layout)
