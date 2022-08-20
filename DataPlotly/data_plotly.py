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

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QAction
from qgis.core import Qgis, QgsApplication, QgsExpression
from qgis.gui import QgsGui

# Import the code for the dialog
from DataPlotly.gui.dock import DataPlotlyDock
from DataPlotly.gui.gui_utils import GuiUtils

# import processing provider
from DataPlotly.processing.dataplotly_provider import DataPlotlyProvider

# import layout classes
from DataPlotly.layouts.plot_layout_item import PlotLayoutItemMetadata
from DataPlotly.gui.layout_item_gui import PlotLayoutItemGuiMetadata

# import custom expressions
from .core.plot_expressions import get_symbol_colors


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
            'application_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.dock_widget = None
        self.show_dock_action = None
        self.help_action = None
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
        icon = GuiUtils.get_icon('dataplotly.svg')

        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar('DataPlotly')
        self.toolbar.setObjectName('DataPlotly')

        self.dock_widget = DataPlotlyDock(message_bar=self.iface.messageBar())
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)
        self.dock_widget.hide()

        self.show_dock_action = QAction(icon, self.tr('DataPlotly'))
        self.show_dock_action.setToolTip(self.tr('Shows the DataPlotly dock'))
        self.show_dock_action.setCheckable(True)

        self.dock_widget.setToggleVisibilityAction(self.show_dock_action)

        self.iface.pluginMenu().addAction(self.show_dock_action)
        self.toolbar.addAction(self.show_dock_action)

        # Add processing provider
        self.initProcessing()

        # Add layout gui utils
        self.plot_item_gui_metadata = PlotLayoutItemGuiMetadata()
        QgsGui.layoutItemGuiRegistry().addLayoutItemGuiMetadata(self.plot_item_gui_metadata)

        # Open the online help
        if Qgis.QGIS_VERSION_INT >= 31000:
            self.help_action = QAction(icon, 'DataPlotly', self.iface.mainWindow())
            self.iface.pluginHelpMenu().addAction(self.help_action)
            self.help_action.triggered.connect(self.open_help)

        # register the function
        QgsExpression.registerFunction(get_symbol_colors)

    def initProcessing(self):
        """Create the Processing provider"""
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.pluginMenu().removeAction(self.show_dock_action)
        self.show_dock_action.deleteLater()
        self.show_dock_action = None
        self.toolbar.deleteLater()
        self.toolbar = None

        if Qgis.QGIS_VERSION_INT >= 31000 and self.help_action:
            self.iface.pluginHelpMenu().removeAction(self.help_action)
            self.help_action = None

        # Remove processing provider
        QgsApplication.processingRegistry().removeProvider(self.provider)

        # unregister the function
        QgsExpression.unregisterFunction('get_symbol_colors')

    @staticmethod
    def open_help():
        """ Open the online help. """
        QDesktopServices.openUrl(QUrl('https://github.com/ghtmtt/DataPlotly/blob/master/README.md'))

    def loadPlotFromDic(self, plot_dic):
        """
        Calls the method to load the DataPlotly dialog with a given dictionary
        """
        self.dock_widget.main_panel.showPlotFromDic(plot_dic)
        self.dock_widget.setUserVisible(True)
