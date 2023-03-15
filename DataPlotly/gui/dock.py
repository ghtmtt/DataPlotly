# -*- coding: utf-8 -*-
"""Dock widget

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
from qgis.PyQt.QtCore import QCoreApplication, Qt
from qgis.PyQt.QtXml import QDomDocument

from qgis.gui import (
    QgsDockWidget,
    QgsPanelWidgetStack
)

from DataPlotly.gui.plot_settings_widget import DataPlotlyPanelWidget

class DataPlotlyDock(QgsDockWidget):  # pylint: disable=too-few-public-methods
    """
    Plot settings dock widget
    """

    def __init__(self, parent=None, message_bar=None, title = 'DataPlotly', dock_id : str = 'DataPlotly', project : QDomDocument= None):
        super().__init__(parent)
        self.setWindowTitle(self.tr(title))
        self.setObjectName(f'DataPlotly-{dock_id}-Dock')

        self.panel_stack = QgsPanelWidgetStack()
        self.setWidget(self.panel_stack)

        self.main_panel = DataPlotlyPanelWidget(message_bar=message_bar, dock_id = dock_id, project = project)
        self.panel_stack.setMainPanel(self.main_panel)
        self.main_panel.setDockMode(True)

class DataPlotlyDockManager():
    """
    Manager to add multiple docks
    """
    def __init__(self, iface, dock_widgets):
        self.iface = iface
        self.dock_widgets = dock_widgets
    
    def tr(self, message):
        return QCoreApplication.translate('DataPlotly', message)

    def addNewDock(self, title='DataPlotly', dock_id='DataPlotly', hide = True, message_bar = None, project = None):
        if dock_id in self.dock_widgets:
            if dock_id == 'DataPlotly':
                return self.dock_widgets[dock_id]
            self.iface.messageBar().pushWarning(self.tr('Warning'), self.tr(f'DataPlotlyDock can not be added because {dock_id} is already present'))
            return False
        message_bar = message_bar or self.iface.messageBar()
        dock = DataPlotlyDock(title = title, message_bar=message_bar, dock_id = dock_id, project = project)
        self.dock_widgets[dock_id] = dock
        self.iface.addDockWidget(Qt.RightDockWidgetArea, dock)
        if hide:
            dock.hide()
        return dock
    
    def removeDock(self, dock_id):
        dock = self.dock_widgets.pop(dock_id, None)
        if dock:
            self.iface.removeDockWidget(dock)
        #TODO remove dock_id in project file

    def removeDocks(self):
        dock_widgets = self.dock_widgets.copy()
        for dock_id in dock_widgets.keys():
            if dock_id == 'DataPlotly':
                continue
            self.removeDock(dock_id)

        self.dock_project_empty = True

    def addDocksFromProject(self, document: QDomDocument):
        root_node = document.elementsByTagName("qgis").item(0)
        if root_node.isNull():
            return False
        #loop to find matching dock
        nodes = root_node.childNodes()
        for i in range(nodes.length()):
            tag_name = nodes.at(i).toElement().tagName()
            if tag_name.startswith('DataPlotly_'):
                tag_name = tag_name.replace('DataPlotly_', '', 1)
                self.addNewDock(title = tag_name, 
                                dock_id = tag_name, 
                                hide = False, 
                                message_bar = None, 
                                project = document)

    def getDock(self, dock_id: str) -> DataPlotlyDock:
        dock = self.dock_widgets.get(dock_id)
        if not dock:
            self.iface.messageBar().pushWarning(
                self.tr('Warning'), 
                self.tr(f'DataPlotlyDock {dock_id} can not be found'))
        return dock