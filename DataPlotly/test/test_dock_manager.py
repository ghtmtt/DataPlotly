# coding=utf-8
"""Plot factory test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
from DataPlotly.test.utilities import get_qgis_app
from DataPlotly.gui.dock import (DataPlotlyDock, DataPlotlyDockManager)


QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class DataPlotlyDockManagerTest(unittest.TestCase):
    """
    Test DataPlotlyDockManager
    """

    def setUp(self):
        self.dock_widgets = {}
        self.dock_manager = DataPlotlyDockManager(
            iface=IFACE, dock_widgets=self.dock_widgets)

    def test_001_constructor(self):
        """
        Test the constructor of DataPlotlyDockManager
        """
        self.assertIs(self.dock_widgets, self.dock_manager.dock_widgets)

    def test_002_add_new_dock(self):
        """
        Test addNewDock of DataPlotlyDockManager
        """
        # checks DataPlotly main dock
        self.assertNotIn('DataPlotly', self.dock_widgets)
        dock_widget = self.dock_manager.addNewDock()
        self.assertIsInstance(dock_widget, DataPlotlyDock)
        self.assertIn('DataPlotly', self.dock_widgets)
        self.assertIs(dock_widget, self.dock_widgets['DataPlotly'])

        # checks it's not possible to add a new dock with DataPlotly as dock_id
        dock_widget2 = self.dock_manager.addNewDock(dock_title='NewDataPlotly',
                                                    dock_id='DataPlotly')
        self.assertIs(dock_widget2, dock_widget)

        # checks we can not add new dock with same dock_id
        dock_params = {'dock_title': 'DataPlotly2', 'dock_id': 'DataPlotly2'}
        self.dock_manager.addNewDock(**dock_params)
        self.assertIn('DataPlotly2', self.dock_widgets)
        new_dock_widget = self.dock_manager.addNewDock(
            dock_title='DataPlotly2b', dock_id='DataPlotly2')
        self.assertFalse(new_dock_widget)

    def test_003_remove_deck(self):
        """
        Test removeDock
        """
        dock_id = 'dock_to_remove'
        self.dock_manager.addNewDock(dock_id=dock_id)
        self.assertIn(dock_id, self.dock_widgets)
        self.dock_manager.removeDock(dock_id)
        self.assertNotIn(dock_id, self.dock_widgets)

    def test_004_remove_docks(self):
        """
        Test removeDocks
        """
        docks = ['DataPlotly', 'DataPlotly2', 'DataPlotly3']
        for dock in docks:
            self.dock_manager.addNewDock(dock_id=dock)
        self.dock_manager.removeDocks()
        # do not remove DataPlotly main dock
        self.assertIn('DataPlotly', self.dock_widgets)
        self.assertEqual(len(self.dock_widgets), 1)

    def test_005_get_dock(self):
        """
        Test getDock
        """
        docks = ['DataPlotly', 'DataPlotly2', 'DataPlotly3']
        for dock in docks:
            self.dock_manager.addNewDock(dock_id=dock)
        dock = self.dock_manager.getDock('DataPloty4_wrong_id')
        self.assertIsNone(dock)
        dock = self.dock_manager.getDock('DataPlotly3')
        self.assertIsInstance(dock, DataPlotlyDock)
        self.assertIs(dock, self.dock_widgets['DataPlotly3'])

    # TODO add others test (addDocksFromProject, read_from_project, write_to_project)


if __name__ == "__main__":
    suite = unittest.makeSuite(DataPlotlyDockManagerTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
