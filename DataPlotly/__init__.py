# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotly
                                 A QGIS plugin
 D3 Plots for QGIS
                             -------------------
        begin                : 2017-03-05
        copyright            : (C) 2017 by matteo ghetta
        email                : matteo.ghetta@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DataPlotly class from file DataPlotly.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    # pylint: disable=import-outside-toplevel
    from .data_plotly import DataPlotly
    return DataPlotly(iface)


def serverClassFactory(server_iface):
    """Load DataPlotly server.

    :param server_iface: A QGIS Server interface instance.
    :type server_iface: QgsServerInterface
    """
    _ = server_iface
    # pylint: disable=import-outside-toplevel
    from qgis.core import QgsApplication, QgsMessageLog, Qgis
    from DataPlotly.layouts.plot_layout_item import PlotLayoutItemMetadata

    QgsApplication.layoutItemRegistry().addLayoutItemType(PlotLayoutItemMetadata())
    QgsMessageLog.logMessage("Custom DataPlotly layout item loaded", "DataPlotly", Qgis.Info)
