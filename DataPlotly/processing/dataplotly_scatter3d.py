"""
/***************************************************************************
 DataPlotly
                                 A QGIS plugin
 D3 Plots for QGIS
                              -------------------
        begin                : 2024-10-29
        git sha              : $Format:%H$
        copyright            : (C) 2024 by matteo ghetta
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

import os

from DataPlotly.processing.dataplotly_generic_plot import DataPlotlyProcessingPlot
from qgis.PyQt.QtGui import QIcon


class DataPlotlyProcessingScatter3D(DataPlotlyProcessingPlot):
    """
    Create a bar with DataPlotly plugin
    """

    def __init__(self):
        super().__init__(plot_type="scatter_3d")

    def name(self):
        return "scatter3d"

    def displayName(self):
        return "Scatter 3D Plot"

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "core",
                "plot_types",
                "icons",
                "scatter3d.svg",
            )
        )

    def createInstance(self):
        return DataPlotlyProcessingScatter3D()

    def initAlgorithm(self, config=None):

        # create the parameters list
        parameters = self.create_parameter_dictionary(self.plot_type)

        # loop and fill the parameters
        for param in parameters:
            self.addParameter(param)
