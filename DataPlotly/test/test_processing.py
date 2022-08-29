"""Tests for processing algorithms."""

import os
import json

import processing

from qgis.core import QgsApplication, QgsVectorLayer
from qgis.testing import unittest
from qgis.PyQt.QtGui import QColor

from DataPlotly.processing.dataplotly_provider import DataPlotlyProvider

__copyright__ = 'Copyright 2022, Faunalia'
__license__ = 'GPL version 3'
__email__ = 'info@faunalia.eu'


class TestProcessing(unittest.TestCase):
    """Tests for processing algorithms."""

    def setUp(self) -> None:
        """Set up the processing tests."""
        if not QgsApplication.processingRegistry().providers():
            self.provider = DataPlotlyProvider(plugin_version='2.3')
            QgsApplication.processingRegistry().addProvider(self.provider)
        self.maxDiff = None

    def test_scatterplot_figure(self):
        """Test for the Processing scatterplot"""

        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.shp')

        vl = QgsVectorLayer(layer_path, 'test_layer', 'ogr')

        plot_path = os.path.join(
            os.path.dirname(__file__), 'scatterplot.json')

        plot_param = {
            'INPUT': vl,
            'XEXPRESSION': '"so4"',
            'YEXPRESSION': '"ca"',
            'SIZE': 10,
            'COLOR': QColor(142, 186, 217),
            'FACET_COL': '',
            'FACET_ROW': '',
            'OFFLINE': False,
            'OUTPUT_HTML_FILE': 'TEMPORARY_OUTPUT',
            'OUTPUT_JSON_FILE': 'TEMPORARY_OUTPUT'
        }

        plot_json = processing.run("DataPlotly:dataplotly_scatterplot", plot_param)['OUTPUT_JSON_FILE']

        with open(plot_json, 'r', encoding='utf8') as f:
            plot_dict_result = json.load(f)

        with open(plot_path, 'r', encoding='utf8') as f:
            plot_dict_template = json.load(f)

        self.assertEqual(plot_dict_result, plot_dict_template)


if __name__ == '__main__':
    unittest.main()
