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

from qgis.PyQt.QtGui import QIcon

import os

from .dataplotly_generic_plot import DataPlotlyProcessingPlot


class DataPlotlyProcessingBarPlot(DataPlotlyProcessingPlot):
    """
    Create a bar with DataPlotly plugin
    """

    def __init__(self):
        super().__init__(plot_type="bar")

    def name(self):
        return "barplot"

    def displayName(self):
        return "Bar Plot"

    def icon(self):
        return QIcon(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "core",
                "plot_types",
                "icons",
                "barplot.svg",
            )
        )

    def createInstance(self):
        return DataPlotlyProcessingBarPlot()

    def initAlgorithm(self, config=None):

        # create the parameters list
        parameters = self.create_parameter_dictionary(self.plot_type)

        # loop and fill the parameters
        for param in parameters:
            self.addParameter(param)
