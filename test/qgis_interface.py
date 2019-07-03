# coding=utf-8
"""QGIS plugin implementation.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. note:: This source code was copied from the 'postgis viewer' application
     with original authors:
     Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk
     Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org
     Copyright (c) 2014 Tim Sutton, tim@linfiniti.com

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = (
    'Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk and '
    'Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org'
    'Copyright (c) 2014 Tim Sutton, tim@linfiniti.com'
)

import logging
from typing import List
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QSize
from qgis.PyQt.QtWidgets import QDockWidget
from qgis.core import QgsProject, QgsMapLayer
from qgis.gui import (QgsMapCanvas,
                      QgsMessageBar)

LOGGER = logging.getLogger('QGIS')


# noinspection PyMethodMayBeStatic,PyPep8Naming
class QgisInterface(QObject):
    """Class to expose QGIS objects and functions to plugins.

    This class is here for enabling us to run unit tests only,
    so most methods are simply stubs.
    """
    currentLayerChanged = pyqtSignal(QgsMapLayer)

    def __init__(self, canvas: QgsMapCanvas):
        """Constructor
        :param canvas:
        """
        QObject.__init__(self)
        self.canvas = canvas
        # Set up slots so we can mimic the behaviour of QGIS when layers
        # are added.
        LOGGER.debug('Initialising canvas...')
        # noinspection PyArgumentList
        QgsProject.instance().layersAdded.connect(self.addLayers)
        # noinspection PyArgumentList
        QgsProject.instance().layerWasAdded.connect(self.addLayer)
        # noinspection PyArgumentList
        QgsProject.instance().removeAll.connect(self.removeAllLayers)

        # For processing module
        self.destCrs = None

        self.message_bar = QgsMessageBar()

    def addLayers(self, layers: List[QgsMapLayer]):
        """Handle layers being added to the registry so they show up in canvas.

        :param layers: list<QgsMapLayer> list of map layers that were added

        .. note:: The QgsInterface api does not include this method,
            it is added here as a helper to facilitate testing.
        """
        # LOGGER.debug('addLayers called on qgis_interface')
        # LOGGER.debug('Number of layers being added: %s' % len(layers))
        # LOGGER.debug('Layer Count Before: %s' % len(self.canvas.layers()))
        current_layers = self.canvas.layers()
        final_layers = []
        for layer in current_layers:
            final_layers.append(layer)
        for layer in layers:
            final_layers.append(layer)

        self.canvas.setLayers(final_layers)
        # LOGGER.debug('Layer Count After: %s' % len(self.canvas.layers()))

    def addLayer(self, layer: QgsMapLayer):
        """Handle a layer being added to the registry so it shows up in canvas.

        :param layer: list<QgsMapLayer> list of map layers that were added

        .. note: The QgsInterface api does not include this method, it is added
                 here as a helper to facilitate testing.

        .. note: The addLayer method was deprecated in QGIS 1.8 so you should
                 not need this method much.
        """
        pass  # pylint: disable=unnecessary-pass

    @pyqtSlot()
    def removeAllLayers(self):  # pylint: disable=no-self-use
        """Remove layers from the canvas before they get deleted."""
        self.canvas.setLayers([])

    def newProject(self):  # pylint: disable=no-self-use
        """Create new project."""
        # noinspection PyArgumentList
        QgsProject.instance().clear()

    # ---------------- API Mock for QgsInterface follows -------------------

    def zoomFull(self):
        """Zoom to the map full extent."""
        pass  # pylint: disable=unnecessary-pass

    def zoomToPrevious(self):
        """Zoom to previous view extent."""
        pass  # pylint: disable=unnecessary-pass

    def zoomToNext(self):
        """Zoom to next view extent."""
        pass  # pylint: disable=unnecessary-pass

    def zoomToActiveLayer(self):
        """Zoom to extent of active layer."""
        pass  # pylint: disable=unnecessary-pass

    def addVectorLayer(self, path: str, base_name: str, provider_key: str):
        """Add a vector layer.

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str

        :param provider_key: Provider key e.g. 'ogr'
        :type provider_key: str
        """
        pass  # pylint: disable=unnecessary-pass

    def addRasterLayer(self, path: str, base_name: str):
        """Add a raster layer given a raster layer file name

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str
        """
        pass  # pylint: disable=unnecessary-pass

    def activeLayer(self) -> QgsMapLayer:  # pylint: disable=no-self-use
        """Get pointer to the active layer (layer selected in the legend)."""
        # noinspection PyArgumentList
        layers = QgsProject.instance().mapLayers()
        for item in layers:
            return layers[item]

    def addToolBarIcon(self, action):
        """Add an icon to the plugins toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass  # pylint: disable=unnecessary-pass

    def removeToolBarIcon(self, action):
        """Remove an action (icon) from the plugin toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass  # pylint: disable=unnecessary-pass

    def addToolBar(self, name):
        """Add toolbar with specified name.

        :param name: Name for the toolbar.
        :type name: str
        """
        pass  # pylint: disable=unnecessary-pass

    def mapCanvas(self) -> QgsMapCanvas:
        """Return a pointer to the map canvas."""
        return self.canvas

    def mainWindow(self):
        """Return a pointer to the main window.

        In case of QGIS it returns an instance of QgisApp.
        """
        pass  # pylint: disable=unnecessary-pass

    def addDockWidget(self, area, dock_widget: QDockWidget):
        """Add a dock widget to the main window.

        :param area: Where in the ui the dock should be placed.
        :type area:

        :param dock_widget: A dock widget to add to the UI.
        :type dock_widget: QDockWidget
        """
        pass  # pylint: disable=unnecessary-pass

    def legendInterface(self):
        """Get the legend."""
        return self.canvas

    def iconSize(self, dockedToolbar) -> int:
        """
        Returns the toolbar icon size.
        :param dockedToolbar: If True, the icon size
        for toolbars contained within docks is returned.
        """
        if dockedToolbar:
            return QSize(16, 16)

        return QSize(24, 24)

    def messageBar(self) -> QgsMessageBar:
        """
        Return the message bar of the main app
        """
        return self.message_bar
