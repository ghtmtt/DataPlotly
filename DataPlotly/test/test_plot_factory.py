# coding=utf-8
"""Plot factory test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
import os
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsReferencedRectangle,
    QgsRectangle,
    QgsCoordinateReferenceSystem
)
from qgis.PyQt.QtTest import QSignalSpy
from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.core.plot_factory import PlotFactory


class DataPlotlyFactory(unittest.TestCase):
    """Test plot factory"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_values(self):  # pylint: disable=too-many-statements
        """
        Test value collection
        """

        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.shp')

        vl1 = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        vl1.setSubsetString('id < 10')
        self.assertTrue(vl1.isValid())
        QgsProject.instance().addMapLayer(vl1)

        # default plot settings
        settings = PlotSettings('scatter')

        # no source layer, fixed values must be used
        settings.source_layer_id = ''
        settings.x = [1, 2, 3]
        settings.y = [4, 5, 6]
        settings.z = [7, 8, 9]

        factory = PlotFactory(settings)
        self.assertEqual(factory.settings.x, [1, 2, 3])
        self.assertEqual(factory.settings.y, [4, 5, 6])
        self.assertEqual(factory.settings.z, [7, 8, 9])
        self.assertEqual(factory.settings.additional_hover_text, [])

        # use source layer
        settings.source_layer_id = vl1.id()

        # no source set => no values
        factory = PlotFactory(settings)
        self.assertEqual(factory.settings.x, [])
        self.assertEqual(factory.settings.y, [])
        self.assertEqual(factory.settings.z, [])
        self.assertEqual(factory.settings.additional_hover_text, [])

        settings.properties['x_name'] = 'so4'
        settings.properties['y_name'] = 'ca'
        factory = PlotFactory(settings)
        self.assertEqual(factory.settings.x, [98, 88, 267, 329, 319, 137, 350, 151, 203])
        self.assertEqual(factory.settings.y, [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45])
        self.assertEqual(factory.settings.z, [])
        self.assertEqual(factory.settings.additional_hover_text, [])

        # with z
        settings.properties['z_name'] = 'mg'
        factory = PlotFactory(settings)
        self.assertEqual(factory.settings.x, [98, 88, 267, 329, 319, 137, 350, 151, 203])
        self.assertEqual(factory.settings.y, [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45])
        self.assertEqual(factory.settings.z, [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34])
        self.assertEqual(factory.settings.additional_hover_text, [])

        # with expressions
        settings.properties['x_name'] = '"so4"/10'
        settings.properties['y_name'] = 'case when "profm" >-16 then "ca" else "mg" end'
        settings.properties['z_name'] = 'case when $x < 10.5 then 1 else 0 end'
        factory = PlotFactory(settings)
        self.assertEqual(factory.settings.x, [9.8, 8.8, 26.7, 32.9, 31.9, 13.7, 35.0, 15.1, 20.3])
        self.assertEqual(factory.settings.y, [81.87, 86.03, 85.26, 35.05, 131.59, 95.36, 112.88, 108.25, 78.34])
        self.assertEqual(factory.settings.z, [0, 1, 0, 0, 0, 0, 0, 1, 1])
        self.assertEqual(factory.settings.additional_hover_text, [])

        # with some nulls
        settings.properties['x_name'] = '"so4"/10'
        settings.properties['y_name'] = 'case when "profm" >-16 then "ca" else "mg" end'
        settings.properties['z_name'] = 'case when $x < 10.5 then NULL else 1 end'
        factory = PlotFactory(settings)
        self.assertEqual(factory.settings.x, [9.8, 26.7, 32.9, 31.9, 13.7, 35.0])
        self.assertEqual(factory.settings.y, [81.87, 85.26, 35.05, 131.59, 95.36, 112.88])
        self.assertEqual(factory.settings.z, [1, 1, 1, 1, 1, 1])
        self.assertEqual(factory.settings.additional_hover_text, [])

        # with additional values
        settings.layout['additional_info_expression'] = 'id'
        factory = PlotFactory(settings)
        self.assertEqual(factory.settings.x, [9.8, 26.7, 32.9, 31.9, 13.7, 35.0])
        self.assertEqual(factory.settings.y, [81.87, 85.26, 35.05, 131.59, 95.36, 112.88])
        self.assertEqual(factory.settings.z, [1, 1, 1, 1, 1, 1])
        self.assertEqual(factory.settings.additional_hover_text, [9, 7, 6, 5, 4, 3])

    def test_selected_feature_values(self):
        """
        Test value collection for selected features
        """

        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.shp')

        vl1 = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        vl1.setSubsetString('id < 10')
        self.assertTrue(vl1.isValid())
        QgsProject.instance().addMapLayer(vl1)

        # default plot settings
        settings = PlotSettings('scatter')
        settings.properties['selected_features_only'] = True
        settings.source_layer_id = vl1.id()

        settings.properties['x_name'] = 'so4'
        settings.properties['y_name'] = 'ca'
        factory = PlotFactory(settings)
        # no selection, no values
        self.assertEqual(factory.settings.x, [])
        self.assertEqual(factory.settings.y, [])
        self.assertEqual(factory.settings.z, [])
        self.assertEqual(factory.settings.additional_hover_text, [])

        vl1.selectByIds([1, 3, 4])
        factory = PlotFactory(settings)
        self.assertEqual(factory.settings.x, [88, 329, 319])
        self.assertEqual(factory.settings.y, [22.26, 35.05, 46.64])

        vl1.selectByIds([])
        factory = PlotFactory(settings)
        self.assertEqual(factory.settings.x, [])
        self.assertEqual(factory.settings.y, [])

    def test_selected_feature_values_dynamic(self):
        """
        Test that factory proactively updates when a selection changes, when desired
        """

        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.shp')

        vl1 = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        vl1.setSubsetString('id < 10')
        self.assertTrue(vl1.isValid())
        QgsProject.instance().addMapLayer(vl1)

        # not using selected features
        settings = PlotSettings('scatter')
        settings.properties['selected_features_only'] = False
        settings.source_layer_id = vl1.id()

        settings.properties['x_name'] = 'so4'
        settings.properties['y_name'] = 'ca'
        factory = PlotFactory(settings)
        spy = QSignalSpy(factory.plot_built)
        vl1.selectByIds([1, 3, 4])
        self.assertEqual(len(spy), 0)

        # using selected features
        settings = PlotSettings('scatter')
        settings.properties['selected_features_only'] = True
        settings.source_layer_id = vl1.id()
        settings.properties['x_name'] = 'so4'
        settings.properties['y_name'] = 'ca'
        factory = PlotFactory(settings)
        spy = QSignalSpy(factory.plot_built)

        vl1.selectByIds([1])
        self.assertEqual(len(spy), 1)
        self.assertEqual(factory.settings.x, [88])
        self.assertEqual(factory.settings.y, [22.26])

        vl1.selectByIds([1, 3, 4])
        self.assertEqual(len(spy), 2)
        self.assertEqual(factory.settings.x, [88, 329, 319])
        self.assertEqual(factory.settings.y, [22.26, 35.05, 46.64])

        vl1.selectByIds([])
        self.assertEqual(len(spy), 3)
        self.assertEqual(factory.settings.x, [])
        self.assertEqual(factory.settings.y, [])

    def test_changed_feature_values_dynamic(self):
        """
        Test that factory proactively updates when a layer changes
        """

        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.shp')

        vl1 = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        vl1.setSubsetString('id < 10')
        self.assertTrue(vl1.isValid())
        QgsProject.instance().addMapLayer(vl1)

        # not using selected features
        settings = PlotSettings('scatter')
        settings.source_layer_id = vl1.id()

        settings.properties['x_name'] = 'so4'
        settings.properties['y_name'] = 'ca'
        factory = PlotFactory(settings)
        spy = QSignalSpy(factory.plot_built)
        self.assertEqual(len(spy), 0)
        self.assertEqual(factory.settings.x, [98, 88, 267, 329, 319, 137, 350, 151, 203])
        self.assertEqual(factory.settings.y, [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45])

        self.assertTrue(vl1.startEditing())
        vl1.changeAttributeValue(1, vl1.fields().lookupField('so4'), 500)
        self.assertEqual(len(spy), 1)
        self.assertEqual(factory.settings.x, [98, 500, 267, 329, 319, 137, 350, 151, 203])
        self.assertEqual(factory.settings.y, [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45])

        vl1.rollBack()

    def test_visible_features(self):
        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.shp')

        vl1 = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        vl1.setSubsetString('id < 10')
        self.assertTrue(vl1.isValid())
        QgsProject.instance().addMapLayer(vl1)

        # not using visible features
        settings = PlotSettings('scatter')
        settings.source_layer_id = vl1.id()

        settings.properties['x_name'] = 'so4'
        settings.properties['y_name'] = 'ca'

        rect = QgsReferencedRectangle(QgsRectangle(10.1, 43.5, 10.8, 43.85), QgsCoordinateReferenceSystem(4326))
        factory = PlotFactory(settings, visible_region=rect)
        spy = QSignalSpy(factory.plot_built)
        self.assertEqual(len(spy), 0)
        self.assertEqual(factory.settings.x, [98, 88, 267, 329, 319, 137, 350, 151, 203])
        self.assertEqual(factory.settings.y, [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45])

        settings.properties['visible_features_only'] = True
        factory = PlotFactory(settings, visible_region=rect)
        spy = QSignalSpy(factory.plot_built)
        self.assertEqual(factory.settings.x, [88, 350, 151, 203])
        self.assertEqual(factory.settings.y, [22.26, 116.44, 108.25, 110.45])

        factory.set_visible_region(
            QgsReferencedRectangle(QgsRectangle(10.6, 43.1, 12, 43.8), QgsCoordinateReferenceSystem(4326)))
        self.assertEqual(len(spy), 1)
        self.assertEqual(factory.settings.x, [98, 267, 319, 137])
        self.assertEqual(factory.settings.y, [81.87, 74.16, 46.64, 126.73])

        # with reprojection
        factory.set_visible_region(
            QgsReferencedRectangle(QgsRectangle(1167379, 5310986, 1367180, 5391728),
                                   QgsCoordinateReferenceSystem(3857)))
        self.assertEqual(len(spy), 2)
        self.assertEqual(factory.settings.x, [98, 267, 329, 319, 137])
        self.assertEqual(factory.settings.y, [81.87, 74.16, 35.05, 46.64, 126.73])


if __name__ == "__main__":
    suite = unittest.makeSuite(DataPlotlyFactory)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
