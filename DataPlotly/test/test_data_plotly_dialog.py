# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'matteo.ghetta@gmail.com'
__date__ = '2017-03-05'
__copyright__ = 'Copyright 2017, matteo ghetta'

import unittest
import tempfile
import os

from qgis.core import (
    QgsProject,
    QgsVectorLayer
)
from qgis.PyQt.QtCore import QCoreApplication

from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.data_plotly_dialog import DataPlotlyPanelWidget

from DataPlotly.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class DataPlotlyDialogTest(unittest.TestCase):
    """Test dialog works."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read_triggered = False

    def test_get_settings(self):
        """
        Test retrieving settings from the dialog
        """
        dialog = DataPlotlyPanelWidget(None, iface=IFACE)
        settings = dialog.get_settings()
        # default should be scatter plot
        self.assertEqual(settings.plot_type, 'scatter')

        dialog.set_plot_type('violin')
        settings = dialog.get_settings()
        # default should be scatter plot
        self.assertEqual(settings.plot_type, 'violin')

    def test_read_write_project(self):
        """
        Test saving/restoring dialog state in project
        """
        p = QgsProject.instance()
        dialog = DataPlotlyPanelWidget(None, iface=IFACE)
        dialog.set_plot_type('violin')

        # first, disable saving to project
        dialog.read_from_project = False
        dialog.save_to_project = False

        path = os.path.join(tempfile.gettempdir(), 'test_dataplotly_project.qgs')
        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.geojson')

        # create QgsVectorLayer from path and test validity
        vl = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        self.assertTrue(vl.isValid())

        # print(dialog.layer_combo.currentLayer())

        self.assertTrue(p.write(path))

        res = PlotSettings()

        # def read(doc):
        #    self.assertTrue(res.read_from_project(doc))
        #    self.assertEqual(res.plot_type, 'violin')
        #    self.read_triggered = True

        p.clear()
        for _ in range(100):
            QCoreApplication.processEvents()

        self.assertTrue(p.read(path))
        self.assertEqual(res.plot_type, 'scatter')

        # TODO - enable when dialog can restore properties and avoid this fragile test
        # # enable saving to project
        # dialog.save_to_project = True
        # dialog.read_from_project = True
        # self.assertTrue(p.write(path))
        # for _ in range(100):
        #     QCoreApplication.processEvents()

        # p.clear()

        # p.readProject.connect(read)
        # self.assertTrue(p.read(path))
        # for _ in range(100):
        #     QCoreApplication.processEvents()

        # self.assertTrue(self.read_triggered)

        # todo - test that dialog can restore properties, but requires the missing set_settings method
        dialog.x_combo.setExpression('"Ca"')
        dialog.layer_combo.setLayer(vl)

        print('--------')
        dialog.x_combo.currentText()

        self.assertTrue(dialog.x_combo.expression(), '"Ca"')



if __name__ == "__main__":
    suite = unittest.makeSuite(DataPlotlyDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
