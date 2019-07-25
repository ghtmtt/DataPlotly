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

from qgis.core import QgsProject
from qgis.PyQt.QtCore import QCoreApplication

from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.data_plotly_dialog import DataPlotlyDockWidget

from DataPlotly.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class DataPlotlyDialogTest(unittest.TestCase):
    """Test dialog works."""

    def test_get_settings(self):
        """
        Test retrieving settings from the dialog
        """
        dialog = DataPlotlyDockWidget(None, iface=IFACE)
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
        dialog = DataPlotlyDockWidget(None, iface=IFACE)
        dialog.set_plot_type('violin')

        # first, disable saving to project
        dialog.read_from_project = False
        dialog.save_to_project = False

        path = os.path.join(tempfile.gettempdir(), 'test_dataplotly_project.qgs')
        self.assertTrue(p.write(path))

        res = PlotSettings()

        def read(doc):
            res.read_from_project(doc)
            print(res.plot_type)

        p.readProject.connect(read)
        p.clear()
        for _ in range(100):
            QCoreApplication.processEvents()

        self.assertTrue(p.read(path))
        self.assertEqual(res.plot_type, 'scatter')

        # enable saving to project
        dialog.save_to_project = True
        self.assertTrue(p.write(path))
        for _ in range(100):
            QCoreApplication.processEvents()

        p.clear()
        self.assertTrue(p.read(path))
        for _ in range(100):
            QCoreApplication.processEvents()

        self.assertEqual(res.plot_type, 'violin')

        # todo - test that dialog can restore properties, but requires the missing set_settings method


if __name__ == "__main__":
    suite = unittest.makeSuite(DataPlotlyDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
