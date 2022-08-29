"""Tests for processing algorithms."""

import os
import tempfile
import re

import processing

from qgis.core import QgsApplication, QgsVectorLayer
from qgis.testing import unittest
from qgis.PyQt.QtGui import QColor

from DataPlotly.processing.dataplotly_provider import DataPlotlyProvider

__copyright__ = 'Copyright 2021, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'


class TestProcessing(unittest.TestCase):
    """Tests for processing algorithms."""

    def setUp(self) -> None:
        """Set up the processing tests."""
        if not QgsApplication.processingRegistry().providers():
            self.provider = DataPlotlyProvider(plugin_version='2.3')
            QgsApplication.processingRegistry().addProvider(self.provider)


    def test_scatterplot_figure(self):
        """Test for the Processing scatterplot"""

        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.shp')

        vl = QgsVectorLayer(layer_path, 'test_layer', 'ogr')

        plot_path = os.path.join(tempfile.gettempdir(), 'scatterplot.html')

        plot_html = processing.run("DataPlotly:dataplotly_scatterplot",
            {
                'INPUT': vl,
                'XEXPRESSION':'"so4"',
                'YEXPRESSION':'"ca"',
                'SIZE':10,
                'COLOR':QColor(142, 186, 217),
                'FACET_COL':'',
                'FACET_ROW':'',
                'OFFLINE':False,
                'OUTPUT_HTML_FILE': plot_path
            }
        )['OUTPUT_HTML_FILE']

        # read the html file as a string
        with open(plot_html, 'r', encoding='utf-8') as f:
            plot_div = f.read()

        # find the UUID (random for each plot) and replace it with a custom div
        res = re.search('<div id="([^"]*)"', plot_div)
        div_id = res.groups()[0]
        plot_div = plot_div.replace(div_id, 'ReplaceTheDiv')

        # read the comparing html as a string
        with open(os.path.join(os.path.dirname(__file__), 'processing_scatter.html'), encoding='utf-8') as f:
            result = f.read()

        self.assertEqual(plot_div, result)

if __name__ == '__main__':
    unittest.main()
