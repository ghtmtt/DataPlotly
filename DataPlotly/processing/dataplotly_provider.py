# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotly
                                 A QGIS plugin
 D3 Plots for QGIS
                              -------------------
        begin                : 2017-03-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by matteo ghetta
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
from qgis.core import QgsProcessingProvider
from DataPlotly.gui.gui_utils import GuiUtils
from DataPlotly.processing.dataplotly_scatterplot import DataPlotlyProcessingScatterPlot


class DataPlotlyProvider(QgsProcessingProvider):

    def __init__(self, plugin_version):
        super().__init__()
        self.plugin_version = plugin_version

    def load(self):
        """In this method we add settings needed to configure our
        provider.
        """
        self.refreshAlgorithms()
        return True

    def id(self):
        """This is the name that will appear on the toolbox group.

        It is also used to create the command line name of all the
        algorithms from this provider.
        """
        return 'DataPlotly'

    def name(self):
        """This is the localised full name.
        """
        return 'DataPlotly'

    def longName(self):
        return 'DataPlotly'

    def icon(self):
        return GuiUtils.get_icon('dataplotly.svg')

    def svgIconPath(self) -> str:
        return GuiUtils.get_icon_svg('dataplotly.svg')

    def versionInfo(self) -> str:
        return self.plugin_version

    def loadAlgorithms(self):
        """Here we fill the list of algorithms in self.algs.

        This method is called whenever the list of algorithms should
        be updated. If the list of algorithms can change (for instance,
        if it contains algorithms from user-defined scripts and a new
        script might have been added), you should create the list again
        here.

        In this case, since the list is always the same, we assign from
        the pre-made list. This assignment has to be done in this method
        even if the list does not change, since the self.algs list is
        cleared before calling this method.
        """
        self.addAlgorithm(DataPlotlyProcessingScatterPlot())
