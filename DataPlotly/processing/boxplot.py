"""
/***************************************************************************
 DataPlotly
                                 A QGIS plugin
 D3 Plots for QGIS
                              -------------------
        begin                : 2025-10-30
        git sha              : $Format:%H$
        copyright            : (C) 2025 by matteo ghetta
        email                : matteo.ghetta@gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtGui import QIcon

import os

from .dataplotly_generic_plot import DataPlotlyProcessingPlot


class DataPlotlyProcessingBoxPlot(DataPlotlyProcessingPlot):
    """
    Create a bar with DataPlotly plugin
    """

    def __init__(self):
        super().__init__(plot_type="box")

    def name(self):
        return "boxplot"

    def displayName(self):
        return "Box Plot"

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "core",
                "plot_types",
                "icons",
                "boxplot.svg",
            )
        )

    def createInstance(self):
        return DataPlotlyProcessingBoxPlot()
