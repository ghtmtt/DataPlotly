# -*- coding: utf-8 -*-
"""Dock widget

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtXml import QDomDocument, QDomElement

from qgis.core import QgsXmlUtils
from qgis.gui import (
    QgsDockWidget,
    QgsPanelWidgetStack
)
from DataPlotly.core.core_utils import restore, restore_safe_str_xml, safe_str_xml
from DataPlotly.gui.add_new_dock_dlg import DataPlotlyNewDockDialog
from DataPlotly.gui.remove_dock_dlg import DataPlotlyRemoveDockDialog
from DataPlotly.gui.plot_settings_widget import DataPlotlyPanelWidget


class DataPlotlyDock(QgsDockWidget):  # pylint: disable=too-few-public-methods
    """
    Plot settings dock widget
    """

    def __init__(self, parent=None, message_bar=None,  # pylint: disable=too-many-arguments
                 dock_title: str = 'DataPlotly', dock_id: str = 'DataPlotly',
                 project: QDomDocument = None, override_iface=None):
        super().__init__(parent)
        self.title = restore_safe_str_xml(dock_title)
        self.setWindowTitle(self.title)
        self.setObjectName(f'DataPlotly-{dock_id}-Dock')

        self.panel_stack = QgsPanelWidgetStack()
        self.setWidget(self.panel_stack)

        self.main_panel = DataPlotlyPanelWidget(
            message_bar=message_bar, dock_title=dock_title, dock_id=dock_id, project=project, override_iface=override_iface)
        self.panel_stack.setMainPanel(self.main_panel)
        self.main_panel.setDockMode(True)


class DataPlotlyDockManager():
    """
    Manager to add multiple docks
    """

    def __init__(self, iface, dock_widgets):
        self.iface = iface
        self.dock_widgets = dock_widgets
        self.state = None
        self.geometry = None

    @staticmethod
    def tr(message):
        """ Translate function"""
        return QCoreApplication.translate('DataPlotly', message)

    def addNewDockFromDlg(self):
        """ Open a dlg and add dock"""
        dlg = DataPlotlyNewDockDialog(self.dock_widgets)
        if dlg.exec_():
            dock_title, dock_id = dlg.get_params()
            self.addNewDock(dock_title, dock_id, False)

    def removeDockFromDlg(self):
        """ Open a dlg to remove a dock"""
        dlg = DataPlotlyRemoveDockDialog(self.dock_widgets)
        if dlg.exec_():
            dock_id = dlg.get_param()
            self.removeDock(dock_id)

    def addNewDock(self, dock_title='DataPlotly', dock_id='DataPlotly',  # pylint: disable=too-many-arguments
                   hide=True, message_bar=None, project=None):
        """ Add new dock """
        dock_title = safe_str_xml(dock_title)
        dock_id = safe_str_xml(dock_id)
        if dock_id in self.dock_widgets:
            if dock_id == 'DataPlotly':
                return self.dock_widgets[dock_id]
            self.iface.messageBar().pushWarning(self.tr('Warning'), self.tr(
                f'DataPlotlyDock can not be added because {dock_id} is already present'))
            return False
        message_bar = message_bar or self.iface.messageBar()
        dock = DataPlotlyDock(
            dock_title=dock_title, message_bar=message_bar, dock_id=dock_id, project=project, override_iface=self.iface)
        self.dock_widgets[dock_id] = dock
        self.iface.addDockWidget(Qt.RightDockWidgetArea, dock)
        if hide:
            dock.hide()
        return dock

    def removeDock(self, dock_id):
        """ Remove dock with id """
        dock = self.dock_widgets.pop(dock_id, None)
        if dock:
            self.iface.removeDockWidget(dock)
        # TODO remove dock_id in project file

    def removeDocks(self):
        """ Remove all docks except the main one """
        dock_widgets = self.dock_widgets.copy()
        for dock_id in dock_widgets.keys():
            if dock_id == 'DataPlotly':
                continue
            self.removeDock(dock_id)

        # self.dock_project_empty = True

    def addDocksFromProject(self, document: QDomDocument):
        """ Add docks from project instance """
        root_node = document.elementsByTagName("qgis").item(0)
        if root_node.isNull():
            return False
        # loop to find matching dock
        nodes = root_node.childNodes()
        for i in range(nodes.length()):
            tag_name = nodes.at(i).toElement().tagName()
            if tag_name.startswith('DataPlotly_'):
                _, dock_title, dock_id = tag_name.split('_')
                self.addNewDock(dock_title=restore_safe_str_xml(dock_title),
                                dock_id=restore_safe_str_xml(dock_id),
                                hide=False,
                                message_bar=None,
                                project=document)
                # FIXME : trigger the plot creation (not working)
                # main_panel = self.getDock(tag_name).main_panel
                # main_panel.create_plot()
        if self.read_from_project(document):
            self.iface.mainWindow().restoreGeometry(self.geometry)
            self.iface.mainWindow().restoreState(self.state, version=999)
        return True

    def getDock(self, dock_id: str) -> DataPlotlyDock:
        """ Return the dock from the dock_id """
        dock = self.dock_widgets.get(dock_id)
        if not dock:
            self.iface.messageBar().pushWarning(
                self.tr('Warning'),
                self.tr(f'DataPlotlyDock {dock_id} can not be found'))
        return dock

    # TODO: Refactor : this functions are almost the same in plot_settings.py
    def write_xml(self, document: QDomDocument):
        """
        Writes the docks position settings to an XML element
        """
        mw = self.iface.mainWindow()
        state = mw.saveState(version=999).toBase64()
        geometry = mw.saveGeometry().toBase64()

        element = QgsXmlUtils.writeVariant({
            'state': str(state, "utf-8"),
            'geometry': str(geometry, "utf-8")
        }, document)
        return element

    def read_xml(self, element: QDomElement) -> bool:
        """
        Reads the docs state settings from an XML element
        """
        res = QgsXmlUtils.readVariant(element)
        if not isinstance(res, dict) or \
                'geometry' not in res or \
                'state' not in res:
            return False

        self.state = restore(res['state'])
        self.geometry = restore(res['geometry'])
        return True

    def write_to_project(self, document: QDomDocument):
        """
        Writes the settings to a project (represented by the given DOM document)
        """
        elem = self.write_xml(document)
        parent_elem = document.createElement('StateDataPlotly')
        parent_elem.appendChild(elem)
        root_node = document.elementsByTagName("qgis").item(0)
        root_node.appendChild(parent_elem)

    def read_from_project(self, document: QDomDocument):
        """
        Reads the settings from a project (represented by the given DOM document)
        """
        root_node = document.elementsByTagName("qgis").item(0)
        if root_node.isNull():
            return False

        node = root_node.toElement().firstChildElement('StateDataPlotly')
        if node.isNull():
            return False

        elem = node.toElement()
        return self.read_xml(elem.firstChildElement())
