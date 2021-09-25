from qgis.core import QgsApplication, QgsMessageLog, Qgis

from DataPlotly.layouts.plot_layout_item import PlotLayoutItemMetadata


class DataPlotlyServer:

    def __init__(self):
        self.plot_item_metadata = PlotLayoutItemMetadata()
        QgsApplication.layoutItemRegistry().addLayoutItemType(self.plot_item_metadata)
        QgsMessageLog.logMessage("Custom DataPlotly layout item loaded", "DataPlotly", Qgis.Info)
