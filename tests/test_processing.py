"""Tests for processing algorithms.

__copyright__ = 'Copyright 2022, Faunalia'
__license__ = 'GPL version 3'
__email__ = 'info@faunalia.eu'
"""

import array
import base64
import json

from pathlib import Path

from qgis.core import (
    QgsProcessingContext,
    QgsProcessingFeedback,
    QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor


def decode_array_1d(spec: dict) -> array.array:
    binary = base64.decodebytes(spec["bdata"].encode())
    match spec["dtype"]:
        case "i2":
            return array.array("h", binary)
        case "i4":
            return array.array("l", binary)
        case "f8":
            return array.array("d", binary)
        case other:
            raise ValueError(f"Unhandled dtype {other}")


def test_scatterplot_figure(data: Path, output_dir: Path):
    """Test for the Processing scatterplot"""
    from qgis import processing

    class Feedback(QgsProcessingFeedback):
        def reportError(self, msg: str, fatalError: bool = False):
            print("\n::test_scatterplot_figure::error", msg)

    layer_path = data.joinpath("test_layer.shp")

    vl = QgsVectorLayer(str(layer_path), "test_layer", "ogr")

    context = QgsProcessingContext()
    context.setTemporaryFolder(str(output_dir))

    return

    result = processing.run(
        "DataPlotly:dataplotly_scatterplot",
        {
            "INPUT": vl,
            "XEXPRESSION": '"so4"',
            "YEXPRESSION": '"ca"',
            "SIZE": 10,
            "COLOR": QColor(142, 186, 217),
            "FACET_COL": "",
            "FACET_ROW": "",
            "OFFLINE": False,
            "OUTPUT_HTML_FILE": "TEMPORARY_OUTPUT",
            "OUTPUT_JSON_FILE": "TEMPORARY_OUTPUT",
        },
        context=context,
        feedback=Feedback(),
    )

    with open(result["OUTPUT_JSON_FILE"]) as f:
        result_dict = json.load(f)

    x = decode_array_1d(result_dict["data"][0]["x"])
    assert x.tolist() == [98, 88, 267, 329, 319, 137, 350, 151, 203]

    y = decode_array_1d(result_dict["data"][0]["y"])
    assert y.tolist() == [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45]
