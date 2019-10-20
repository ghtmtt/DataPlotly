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

from .data_plotly import DataPlotly


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DataPlotly class from file DataPlotly.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    return DataPlotly(iface)
