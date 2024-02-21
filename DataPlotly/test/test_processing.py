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

        # plot_path = os.path.join(
        #     os.path.dirname(__file__), 'scatterplot.json')
        # with open(plot_path, 'r') as f:
        #     template_dict = json.load(f)

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

        result = processing.run("DataPlotly:dataplotly_scatterplot", plot_param)

        with open(result['OUTPUT_JSON_FILE'], encoding='utf8') as f:
            result_dict = json.load(f)

        self.assertListEqual(
            result_dict['data'][0]['x'],
            [98, 88, 267, 329, 319, 137, 350, 151, 203]
        )
        self.assertListEqual(
            result_dict['data'][0]['y'],
            [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45]
        )


if __name__ == '__main__':
    unittest.main()
