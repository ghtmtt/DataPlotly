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
from PyQt5.QtGui import QIcon
from qgis.core import QgsProcessingProvider, QgsApplication
from processing.core.ProcessingConfig import Setting, ProcessingConfig

from .dataplotly_algorithms import DataPlotlyProcessingPlot

class DataPlotlyProvider(QgsProcessingProvider):

    MY_DUMMY_SETTING = 'MY_DUMMY_SETTING'

    def __init__(self):
        super().__init__()

        self.algs = []

    def getAlgs(self):
        algs = [DataPlotlyProcessingPlot()]

        return algs

    def load(self):
        """In this method we add settings needed to configure our
        provider.
        """
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        # Deactivate provider by default
        ProcessingConfig.addSetting(Setting(self.name(), 'ACTIVATE_EXAMPLE',
                                            'Activate', False))
        ProcessingConfig.addSetting(Setting('Example algorithms',
                                            DataPlotlyProvider.MY_DUMMY_SETTING,
                                            'Example setting', 'Default value'))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def unload(self):
        """Setting should be removed here, so they do not appear anymore
        when the plugin is unloaded.
        """
        ProcessingConfig.removeSetting('ACTIVATE_EXAMPLE')
        ProcessingConfig.removeSetting(
            DataPlotlyProvider.MY_DUMMY_SETTING)

    def isActive(self):
        """Return True if the provider is activated and ready to run algorithms"""
        return ProcessingConfig.getSetting('ACTIVATE_EXAMPLE')

    def setActive(self, active):
        ProcessingConfig.setSettingValue('ACTIVATE_EXAMPLE', active)

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
        """We return the default icon.
        """
        return QIcon(":/plugins/DataPlotly/icon.png")

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
        self.algs = self.getAlgs()
        for a in self.algs:
            self.addAlgorithm(a)

