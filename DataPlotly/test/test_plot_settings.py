# coding=utf-8
"""Plot settings test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest

from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QDialog
)

from DataPlotly.core.plot_settings import PlotSettings


class DataPlotlySettings(unittest.TestCase):
    """Test plot settings"""

    def test_constructor(self):
        """
        Test settings constructor
        """

        # default plot settings
        settings = PlotSettings('test')
        self.assertEqual(settings.plot_properties['marker_size'], 10)
        self.assertEqual(settings.plot_layout['legend_orientation'], 'h')

        # inherit base settings
        settings = PlotSettings('test', plot_properties={'marker_width': 2}, plot_layout={'title': 'my plot'})
        # base settings should be inherited
        self.assertEqual(settings.plot_properties['marker_size'], 10)
        self.assertEqual(settings.plot_properties['marker_width'], 2)
        self.assertEqual(settings.plot_layout['legend_orientation'], 'h')
        self.assertEqual(settings.plot_layout['title'], 'my plot')

        # override base settings
        settings = PlotSettings('test', plot_properties={'marker_width': 2, 'marker_size': 5},
                                plot_layout={'title': 'my plot', 'legend_orientation': 'v'})
        # base settings should be inherited
        self.assertEqual(settings.plot_properties['marker_size'], 5)
        self.assertEqual(settings.plot_properties['marker_width'], 2)
        self.assertEqual(settings.plot_layout['legend_orientation'], 'v')
        self.assertEqual(settings.plot_layout['title'], 'my plot')


if __name__ == "__main__":
    suite = unittest.makeSuite(DataPlotlySettings)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
