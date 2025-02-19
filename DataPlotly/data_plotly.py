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
from functools import partial

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QUrl
from qgis.PyQt.QtGui import QDesktopServices, QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton
from qgis.core import QgsApplication, QgsExpression, QgsProject
from qgis.gui import QgsGui

# Help
from DataPlotly.core.core_utils import DOC_URL

# Import the code for the dialog
from DataPlotly.gui.dock import DataPlotlyDockManager
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

    VERSION = '4.0'

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
            f'application_{locale}.qm')

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.dock_widget = None
        self.show_dock_action = None
        self.help_action = None
        self.toolbar = None
        self.dock_project_empty = True

        # initialize variable setup in initGui
        self.actions = None
        self.toolButton = None
        self.toolButtonMenu = None
        self.toolBtnAction = None

        # dock_widgets
        self.dock_widgets = {}
        self.dock_manager = DataPlotlyDockManager(
            self.iface, self.dock_widgets)

        self.plot_item_metadata = PlotLayoutItemMetadata()
        self.plot_item_gui_metadata = None
        QgsApplication.layoutItemRegistry().addLayoutItemType(self.plot_item_metadata)
        QgsProject.instance().cleared.connect(self.dock_manager.removeDocks)
        QgsProject.instance().readProject.connect(
            self.dock_manager.addDocksFromProject)
        QgsProject.instance().writeProject.connect(self.dock_manager.write_to_project)

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

        # # TODO: We are going to let the user set this up in a future iteration
        # self.toolbar = self.iface.addToolBar('DataPlotly')
        # self.toolbar.setObjectName('DataPlotly')

        self.actions = []

        self.dock_widget = self.dock_manager.addNewDock()

        self.show_dock_action = QAction(icon, self.tr('DataPlotly'))
        self.show_dock_action.setToolTip(self.tr('Shows the DataPlotly dock'))
        self.show_dock_action.setCheckable(True)

        self.dock_widget.setToggleVisibilityAction(self.show_dock_action)

        self.toolButton = QToolButton()
        self.toolButtonMenu = QMenu()
        self.toolButton.setMenu(self.toolButtonMenu)
        self.toolButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.toolBtnAction = self.iface.addToolBarWidget(self.toolButton)
        self.toolButton.setDefaultAction(self.show_dock_action)

        sub_actions = [
            {
                "text": self.tr("Add a new dock"),
                "icon_path": icon,
                "callback": self.dock_manager.addNewDockFromDlg,
                "parent": self.iface.mainWindow(),
                "toolbutton": self.toolButton
            },
            {
                "text": self.tr("Remove a dock"),
                "icon_path": icon,
                "callback": self.dock_manager.removeDockFromDlg,
                "parent": self.iface.mainWindow(),
                "toolbutton": self.toolButton
            }
        ]

        for action in sub_actions:
            self.add_action(**action)

        # Add processing provider
        self.initProcessing()

        # Add layout gui utils
        self.plot_item_gui_metadata = PlotLayoutItemGuiMetadata()
        QgsGui.layoutItemGuiRegistry().addLayoutItemGuiMetadata(self.plot_item_gui_metadata)

        # Open the online help
        self.help_action = QAction(
            icon, 'DataPlotly', self.iface.mainWindow())
        self.iface.pluginHelpMenu().addAction(self.help_action)
        self.help_action.triggered.connect(self.open_help)

        # register the function
        QgsExpression.registerFunction(get_symbol_colors)

    def add_action(  # pylint: disable = too-many-arguments
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_toolbar=True,
            toolbutton=None,
            status_tip=None,
            whats_this=None,
            parent=None,
            args=None):
        """Add a toolbar icon to the toolbar.
        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str
        :param text: Text that should be shown in menu items for this action.
        :type text: str
        :param callback: Function to be called when the action is triggered.
        :type callback: function
        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool
        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool
        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool
        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str
        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget
        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        if not icon_path:
            action = QAction(text, parent)
        else:
            icon = QIcon(icon_path) if isinstance(
                icon_path, str) else icon_path
            action = QAction(icon, text, parent)
        if args:
            callback = partial(callback, action, *args)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if toolbutton:
            self.toolButtonMenu.addAction(action)
        else:
            if add_to_toolbar:
                # Adds plugin icon to Plugins toolbar
                self.iface.addToolBarIcon(action)

        self.actions.append(action)

        return action

    def initProcessing(self):
        """Create the Processing provider"""
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.pluginMenu().removeAction(self.show_dock_action)
        self.show_dock_action.deleteLater()
        self.show_dock_action = None
        self.toolButton.deleteLater()
        self.toolButton = None

        self.iface.pluginHelpMenu().removeAction(self.help_action)
        self.help_action = None

        # Remove processing provider
        QgsApplication.processingRegistry().removeProvider(self.provider)

        # unregister the function
        QgsExpression.unregisterFunction('get_symbol_colors')

        # disconnect signals for easy dev when using plugin reloader
        QgsProject.instance().cleared.disconnect(self.dock_manager.removeDocks)
        QgsProject.instance().readProject.disconnect(
            self.dock_manager.addDocksFromProject)
        QgsProject.instance().writeProject.disconnect(
            self.dock_manager.write_to_project)

        # remove all docks
        for dock in self.dock_widgets.values():
            self.iface.removeDockWidget(dock)

    @staticmethod
    def open_help():
        """ Open the online help. """
        QDesktopServices.openUrl(QUrl(DOC_URL))

    def loadPlotFromDic(self, plot_dic, dock_id='DataPlotly'):
        """
        Calls the method to load the DataPlotly dialog with a given dictionary
        """
        dock = self.dock_manager.getDock(dock_id)
        if dock:
            dock.main_panel.showPlotFromDic(plot_dic)
            dock.setUserVisible(True)
