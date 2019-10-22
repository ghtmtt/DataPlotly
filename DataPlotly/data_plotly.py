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
import os.path

from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.core import QgsApplication
from qgis.gui import QgsGui

# Import the code for the dialog
from DataPlotly.gui.dock import DataPlotlyDock
from DataPlotly.gui.gui_utils import GuiUtils

# import processing provider
from DataPlotly.processing.dataplotly_provider import DataPlotlyProvider

# import layout classes
from DataPlotly.layouts.plot_layout_item import PlotLayoutItemMetadata
from DataPlotly.gui.layout_item_gui import PlotLayoutItemGuiMetadata


class DataPlotly:  # pylint: disable=too-many-instance-attributes
    """QGIS Plugin Implementation."""

    VERSION = '2.3'

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize processing provider
        self.provider = DataPlotlyProvider(plugin_version=DataPlotly.VERSION)

        # initialize locale
        locale = QSettings().value('locale/userLocale', 'en_US')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'DataPlotly_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.dock_widget = None
        self.show_dock_action = None
        self.menu = None
        self.toolbar = None

        self.plot_item_metadata = PlotLayoutItemMetadata()
        self.plot_item_gui_metadata = None
        QgsApplication.layoutItemRegistry().addLayoutItemType(self.plot_item_metadata)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):  # pylint: disable=no-self-use
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('DataPlotly', message)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.menu = QMenu(self.tr('&DataPlotly'))
        self.iface.pluginMenu().addMenu(self.menu)

        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar('DataPlotly')
        self.toolbar.setObjectName('DataPlotly')

        self.dock_widget = DataPlotlyDock(message_bar=self.iface.messageBar())
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        self.dock_widget.hide()

        self.show_dock_action = QAction(
            GuiUtils.get_icon('dataplotly.svg'),
            self.tr('DataPlotly'))
        self.show_dock_action.setToolTip(self.tr('Shows the DataPlotly dock'))
        self.show_dock_action.setCheckable(True)

        self.dock_widget.setToggleVisibilityAction(self.show_dock_action)

        self.menu.addAction(self.show_dock_action)
        self.toolbar.addAction(self.show_dock_action)

        # Add processing provider
        self.initProcessing()

        # Add layout gui utils
        self.plot_item_gui_metadata = PlotLayoutItemGuiMetadata()
        QgsGui.layoutItemGuiRegistry().addLayoutItemGuiMetadata(self.plot_item_gui_metadata)

    def initProcessing(self):
        """Create the Processing provider"""
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.show_dock_action.deleteLater()
        self.show_dock_action = None
        self.menu.deleteLater()
        self.menu = None
        self.toolbar.deleteLater()
        self.toolbar = None

        # Remove processing provider
        QgsApplication.processingRegistry().removeProvider(self.provider)

    def loadPlotFromDic(self, plot_dic):
        """
        Calls the method to load the DataPlotly dialog with a given dictionary
        """
        self.dock_widget.main_panel.showPlotFromDic(plot_dic)
        self.dock_widget.setUserVisible(True)
