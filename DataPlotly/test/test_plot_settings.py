# coding=utf-8
"""Plot settings test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
import os
import tempfile
from qgis.core import QgsProject, QgsProperty
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from DataPlotly.core.plot_settings import PlotSettings


class DataPlotlySettings(unittest.TestCase):
    """Test plot settings"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_read_write_project2_written = False
        self.test_read_write_project2_read = False

    def test_constructor(self):
        """
        Test settings constructor
        """

        # default plot settings
        settings = PlotSettings('test')
        self.assertEqual(settings.properties['marker_size'], 10)
        self.assertEqual(settings.layout['legend_orientation'], 'h')

        # inherit base settings
        settings = PlotSettings('test', properties={'marker_width': 2}, layout={'title': 'my plot'})
        # base settings should be inherited
        self.assertEqual(settings.properties['marker_size'], 10)
        self.assertEqual(settings.properties['marker_width'], 2)
        self.assertEqual(settings.layout['legend_orientation'], 'h')
        self.assertEqual(settings.layout['title'], 'my plot')

        # override base settings
        settings = PlotSettings('test', properties={'marker_width': 2, 'marker_size': 5},
                                layout={'title': 'my plot', 'legend_orientation': 'v', 'font_title_size': 20})
        # base settings should be inherited
        self.assertEqual(settings.properties['marker_size'], 5)
        self.assertEqual(settings.properties['marker_width'], 2)
        self.assertEqual(settings.layout['legend_orientation'], 'v')
        self.assertEqual(settings.layout['title'], 'my plot')
        self.assertEqual(settings.layout['font_title_size'], 20)

    def test_readwrite(self):
        """
        Test reading and writing plot settings from XML
        """
        doc = QDomDocument("properties")
        original = PlotSettings('test', properties={'marker_width': 2, 'marker_size': 5},
                                layout={'title': 'my plot', 'legend_orientation': 'v'})
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                     QgsProperty.fromExpression('"ap">50'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_MARKER_SIZE,
                                                     QgsProperty.fromExpression('5+6'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_COLOR,
                                                     QgsProperty.fromExpression("'red'"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_STROKE_WIDTH,
                                                     QgsProperty.fromExpression('12/2'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_title')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_LEGEND_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_legend')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_x_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_y_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Z_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_z_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MIN, QgsProperty.fromExpression("-1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MAX, QgsProperty.fromExpression("+1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MIN, QgsProperty.fromExpression("-1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MAX, QgsProperty.fromExpression("+1*10"))
        elem = original.write_xml(doc)
        self.assertFalse(elem.isNull())

        res = PlotSettings('gg')
        # test reading a bad element
        bad_elem = QDomElement()
        self.assertFalse(res.read_xml(bad_elem))

        self.assertTrue(res.read_xml(elem))
        self.assertEqual(res.plot_type, original.plot_type)
        self.assertEqual(res.properties, original.properties)
        self.assertEqual(res.layout, original.layout)
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_FILTER))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_COLOR),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_COLOR))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX))

    def test_read_write_project(self):
        """
        Test reading and writing to project document
        """
        # fake project document
        doc = QDomDocument("test")
        doc.appendChild(doc.createElement('qgis'))
        original = PlotSettings('test', properties={'marker_width': 2, 'marker_size': 5},
                                layout={'title': 'my plot', 'legend_orientation': 'v', 'font_xlabel_color': "#00FFFF"})
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                     QgsProperty.fromExpression('"ap">50'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_MARKER_SIZE,
                                                     QgsProperty.fromExpression('5+6'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_COLOR,
                                                     QgsProperty.fromExpression("'red'"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_STROKE_WIDTH,
                                                     QgsProperty.fromExpression('12/2'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_title')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_LEGEND_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_legend')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_x_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_y_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Z_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_z_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MIN, QgsProperty.fromExpression("-1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MAX, QgsProperty.fromExpression("+1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MIN, QgsProperty.fromExpression("-1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MAX, QgsProperty.fromExpression("+1*10"))

        original.write_to_project(doc)

        res = PlotSettings('gg')
        res.read_from_project(doc)
        self.assertEqual(res.plot_type, original.plot_type)
        self.assertEqual(res.properties, original.properties)
        self.assertEqual(res.layout, original.layout)
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_FILTER))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_COLOR),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_COLOR))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX))

    @unittest.skip('Fragile')
    def test_read_write_project2(self):
        """
        Test reading and writing to project, signals based
        """
        p = QgsProject()
        original = PlotSettings('test', properties={'marker_width': 2, 'marker_size': 5},
                                layout={'title': 'my plot', 'legend_orientation': 'v', 'font_xlabel_color': '#00FFFF'})
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                     QgsProperty.fromExpression('"ap">50'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_MARKER_SIZE,
                                                     QgsProperty.fromExpression('5+6'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_COLOR,
                                                     QgsProperty.fromExpression("'red'"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_STROKE_WIDTH,
                                                     QgsProperty.fromExpression('12/2'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_title')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_LEGEND_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_legend')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_x_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_y_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Z_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_z_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MIN, QgsProperty.fromExpression("-1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MAX, QgsProperty.fromExpression("+1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MIN, QgsProperty.fromExpression("-1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MAX, QgsProperty.fromExpression("+1*10"))

        self.test_read_write_project2_written = False

        def write(doc):
            self.test_read_write_project2_written = True
            original.write_to_project(doc)

        p.writeProject.connect(write)

        path = os.path.join(tempfile.gettempdir(), 'test_dataplotly_project.qgs')
        self.assertTrue(p.write(path))
        for _ in range(100):
            QCoreApplication.processEvents()
        self.assertTrue(self.test_read_write_project2_written)

        p2 = QgsProject()
        res = PlotSettings('gg')
        self.test_read_write_project2_read = False

        def read(doc):
            res.read_from_project(doc)
            self.test_read_write_project2_read = True

        p2.readProject.connect(read)
        self.assertTrue(p2.read(path))
        for _ in range(100):
            QCoreApplication.processEvents()
        self.assertTrue(self.test_read_write_project2_read)

        self.assertEqual(res.plot_type, original.plot_type)
        self.assertEqual(res.properties, original.properties)
        self.assertEqual(res.layout, original.layout)
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_FILTER))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_COLOR),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_COLOR))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX))

    def test_read_write_file(self):
        """
        Test reading and writing configuration to files
        """
        original = PlotSettings('test', properties={'marker_width': 2, 'marker_size': 5},
                                layout={'title': 'my plot', 'legend_orientation': 'v', 'font_xlabel_color': '#00FFFF'})
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                     QgsProperty.fromExpression('"ap">50'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_MARKER_SIZE,
                                                     QgsProperty.fromExpression('5+6'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_COLOR,
                                                     QgsProperty.fromExpression("'red'"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_STROKE_WIDTH,
                                                     QgsProperty.fromExpression('12/2'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_title')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_LEGEND_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_legend')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_x_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_y_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Z_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_z_axis')"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MIN, QgsProperty.fromExpression("-1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MAX, QgsProperty.fromExpression("+1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MIN, QgsProperty.fromExpression("-1*10"))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MAX, QgsProperty.fromExpression("+1*10"))

        path = os.path.join(tempfile.gettempdir(), 'plot_config.xml')

        self.assertFalse(original.write_to_file('/nooooooooo/nooooooooooo.xml'))
        self.assertTrue(original.write_to_file(path))

        res = PlotSettings()
        self.assertFalse(res.read_from_file('/nooooooooo/nooooooooooo.xml'))
        self.assertTrue(res.read_from_file(path))

        self.assertEqual(res.plot_type, original.plot_type)
        self.assertEqual(res.properties, original.properties)
        self.assertEqual(res.layout, original.layout)
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_FILTER))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_COLOR),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_COLOR))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN))
        self.assertEqual(res.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX),
                         original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX))


if __name__ == "__main__":
    suite = unittest.makeSuite(DataPlotlySettings)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
