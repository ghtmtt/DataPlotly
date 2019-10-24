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
                                layout={'title': 'my plot', 'legend_orientation': 'v'})
        # base settings should be inherited
        self.assertEqual(settings.properties['marker_size'], 5)
        self.assertEqual(settings.properties['marker_width'], 2)
        self.assertEqual(settings.layout['legend_orientation'], 'v')
        self.assertEqual(settings.layout['title'], 'my plot')

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

    def test_read_write_project(self):
        """
        Test reading and writing to project document
        """
        # fake project document
        doc = QDomDocument("test")
        doc.appendChild(doc.createElement('qgis'))
        original = PlotSettings('test', properties={'marker_width': 2, 'marker_size': 5},
                                layout={'title': 'my plot', 'legend_orientation': 'v'})
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                     QgsProperty.fromExpression('"ap">50'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_MARKER_SIZE,
                                                     QgsProperty.fromExpression('5+6'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_COLOR,
                                                     QgsProperty.fromExpression("'red'"))

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

    def test_read_write_project2(self):
        """
        Test reading and writing to project, signals based
        """
        p = QgsProject()
        original = PlotSettings('test', properties={'marker_width': 2, 'marker_size': 5},
                                layout={'title': 'my plot', 'legend_orientation': 'v'})
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                     QgsProperty.fromExpression('"ap">50'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_MARKER_SIZE,
                                                     QgsProperty.fromExpression('5+6'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_COLOR,
                                                     QgsProperty.fromExpression("'red'"))

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

    def test_read_write_file(self):
        """
        Test reading and writing configuration to files
        """
        original = PlotSettings('test', properties={'marker_width': 2, 'marker_size': 5},
                                layout={'title': 'my plot', 'legend_orientation': 'v'})
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                     QgsProperty.fromExpression('"ap">50'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_MARKER_SIZE,
                                                     QgsProperty.fromExpression('5+6'))
        original.data_defined_properties.setProperty(PlotSettings.PROPERTY_COLOR,
                                                     QgsProperty.fromExpression("'red'"))

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


if __name__ == "__main__":
    suite = unittest.makeSuite(DataPlotlySettings)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
