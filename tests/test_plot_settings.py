"""Plot settings test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from pathlib import Path

import pytest

from qgis.core import QgsProject, QgsProperty
from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from DataPlotly.core.plot_settings import PlotSettings

# Work around undefined properties set empty strings
def assert_properties_equals(left: dict, right: dict):
    for k, v in left.items():
        assert k in right, f"Missing key {k}"
        vr = right[k]
        if vr is None:
            assert v is None or v == ""
        else:
            assert vr == v


def test_constructor():
    """
    Test settings constructor
    """

    # default plot settings
    settings = PlotSettings("test")
    assert settings.properties["marker_size"] == 10
    assert settings.layout["legend_orientation"] == "h"

    # inherit base settings
    settings = PlotSettings("test", properties={"marker_width": 2}, layout={"title": "my plot"})
    # base settings should be inherited
    assert settings.properties["marker_size"] == 10
    assert settings.properties["marker_width"] == 2
    assert settings.layout["legend_orientation"] == "h"
    assert settings.layout["title"] == "my plot"

    # override base settings
    settings = PlotSettings(
        "test",
        properties={"marker_width": 2, "marker_size": 5},
        layout={"title": "my plot", "legend_orientation": "v", "font_title_size": 20},
    )
    # base settings should be inherited
    assert settings.properties["marker_size"] == 5
    assert settings.properties["marker_width"] == 2
    assert settings.layout["legend_orientation"] == "v"
    assert settings.layout["title"] == "my plot"
    assert settings.layout["font_title_size"] == 20


def test_readwrite():
    """
    Test reading and writing plot settings from XML
    """
    doc = QDomDocument("properties")
    original = PlotSettings(
        "test",
        properties={"marker_width": 2, "marker_size": 5},
        layout={"title": "my plot", "legend_orientation": "v"},
    )

    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_FILTER,
        QgsProperty.fromExpression('"ap">50'),
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_MARKER_SIZE,
        QgsProperty.fromExpression("5+6"),
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_COLOR,
        QgsProperty.fromExpression("'red'"),
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_STROKE_WIDTH,
        QgsProperty.fromExpression("12/2"),
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_TITLE,
        QgsProperty.fromExpression("concat('my', '_title')"),
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_LEGEND_TITLE,
        QgsProperty.fromExpression("concat('my', '_legend')"),
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_TITLE,
        QgsProperty.fromExpression("concat('my', '_x_axis')"),
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_TITLE,
        QgsProperty.fromExpression("concat('my', '_y_axis')"),
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Z_TITLE,
        QgsProperty.fromExpression("concat('my', '_z_axis')"),
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MIN, QgsProperty.fromExpression("-1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MAX, QgsProperty.fromExpression("+1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MIN, QgsProperty.fromExpression("-1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MAX, QgsProperty.fromExpression("+1*10")
    )
    elem = original.write_xml(doc)

    assert not elem.isNull()

    res = PlotSettings("gg")
    # test reading a bad element
    bad_elem = QDomElement()
    assert not res.read_xml(bad_elem)

    assert res.read_xml(elem)
    assert res.plot_type == original.plot_type
    # NOTE res has undefined values set to empty strings 
    # while original as undefined values set to `None`
    #assert res.properties == original.properties
    #assert res.layout == original.layout
    assert_properties_equals(original.properties, res.properties)
    assert_properties_equals(original.layout, res.layout)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_FILTER
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_FILTER)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_MARKER_SIZE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_COLOR
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_COLOR)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_STROKE_WIDTH
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_LEGEND_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Z_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_MIN
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_MAX
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_MIN
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_MAX
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX)


def test_read_write_project():
    """
    Test reading and writing to project document
    """
    # fake project document
    doc = QDomDocument("test")
    doc.appendChild(doc.createElement("qgis"))
    original = PlotSettings(
        "test",
        properties={"marker_width": 2, "marker_size": 5},
        layout={"title": "my plot", "legend_orientation": "v", "font_xlabel_color": "#00FFFF"},
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_FILTER, QgsProperty.fromExpression('"ap">50')
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_MARKER_SIZE, QgsProperty.fromExpression("5+6")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_COLOR, QgsProperty.fromExpression("'red'")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_STROKE_WIDTH, QgsProperty.fromExpression("12/2")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_TITLE, QgsProperty.fromExpression("concat('my', '_title')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_LEGEND_TITLE, QgsProperty.fromExpression("concat('my', '_legend')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_TITLE, QgsProperty.fromExpression("concat('my', '_x_axis')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_TITLE, QgsProperty.fromExpression("concat('my', '_y_axis')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Z_TITLE, QgsProperty.fromExpression("concat('my', '_z_axis')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MIN, QgsProperty.fromExpression("-1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MAX, QgsProperty.fromExpression("+1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MIN, QgsProperty.fromExpression("-1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MAX, QgsProperty.fromExpression("+1*10")
    )

    original.write_to_project(doc)

    res = PlotSettings("gg")
    res.read_from_project(doc)
    assert res.plot_type == original.plot_type
    # NOTE See above
    #assert res.properties == original.properties
    #assert res.layout == original.layout
    assert_properties_equals(original.properties, res.properties)
    assert_properties_equals(original.layout, res.layout)
 
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_FILTER
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_FILTER)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_MARKER_SIZE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_COLOR
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_COLOR)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_STROKE_WIDTH
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_LEGEND_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Z_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_MIN
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_MAX
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_MIN
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_MAX
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX)


@pytest.mark.skip("Fragile")
def test_read_write_project2(output_dir: Path):
    """
    Test reading and writing to project, signals based
    """
    p = QgsProject()
    original = PlotSettings(
        "test",
        properties={"marker_width": 2, "marker_size": 5},
        layout={"title": "my plot", "legend_orientation": "v", "font_xlabel_color": "#00FFFF"},
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_FILTER, QgsProperty.fromExpression('"ap">50')
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_MARKER_SIZE, QgsProperty.fromExpression("5+6")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_COLOR, QgsProperty.fromExpression("'red'")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_STROKE_WIDTH, QgsProperty.fromExpression("12/2")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_TITLE, QgsProperty.fromExpression("concat('my', '_title')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_LEGEND_TITLE, QgsProperty.fromExpression("concat('my', '_legend')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_TITLE, QgsProperty.fromExpression("concat('my', '_x_axis')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_TITLE, QgsProperty.fromExpression("concat('my', '_y_axis')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Z_TITLE, QgsProperty.fromExpression("concat('my', '_z_axis')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MIN, QgsProperty.fromExpression("-1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MAX, QgsProperty.fromExpression("+1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MIN, QgsProperty.fromExpression("-1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MAX, QgsProperty.fromExpression("+1*10")
    )

    test_read_write_project2_written = False

    def write(doc):
        nonlocal test_read_write_project2_written
        test_read_write_project2_written = True
        original.write_to_project(doc)

    p.writeProject.connect(write)

    path = str(output_dir.joinpath("test_dataplotly_project.qgs"))
    assert p.write(path)
    for _ in range(100):
        QCoreApplication.processEvents()
    assert test_read_write_project2_written

    p2 = QgsProject()
    res = PlotSettings("gg")

    test_read_write_project2_read = False

    def read(doc):
        nonlocal test_read_write_project2_read
        res.read_from_project(doc)
        test_read_write_project2_read = True

    p2.readProject.connect(read)
    assert p2.read(path)
    for _ in range(100):
        QCoreApplication.processEvents()
    assert test_read_write_project2_read

    assert res.plot_type == original.plot_type
    # NOTE see above
    #assert res.properties == original.properties
    #assert res.layout == original.layout
    assert_properties_equals(original.properties, res.properties)
    assert_properties_equals(original.layout, res.layout)
    
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_FILTER
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_FILTER)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_MARKER_SIZE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_COLOR
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_COLOR)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_STROKE_WIDTH
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_LEGEND_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Z_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_MIN
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_MAX
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_MIN
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_MAX
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX)


def test_read_write_file(output_dir: Path):
    """
    Test reading and writing configuration to files
    """
    original = PlotSettings(
        "test",
        properties={"marker_width": 2, "marker_size": 5},
        layout={"title": "my plot", "legend_orientation": "v", "font_xlabel_color": "#00FFFF"},
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_FILTER, QgsProperty.fromExpression('"ap">50')
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_MARKER_SIZE, QgsProperty.fromExpression("5+6")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_COLOR, QgsProperty.fromExpression("'red'")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_STROKE_WIDTH, QgsProperty.fromExpression("12/2")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_TITLE, QgsProperty.fromExpression("concat('my', '_title')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_LEGEND_TITLE, QgsProperty.fromExpression("concat('my', '_legend')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_TITLE, QgsProperty.fromExpression("concat('my', '_x_axis')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_TITLE, QgsProperty.fromExpression("concat('my', '_y_axis')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Z_TITLE, QgsProperty.fromExpression("concat('my', '_z_axis')")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MIN, QgsProperty.fromExpression("-1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MAX, QgsProperty.fromExpression("+1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MIN, QgsProperty.fromExpression("-1*10")
    )
    original.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MAX, QgsProperty.fromExpression("+1*10")
    )

    path = str(output_dir.joinpath("plot_config.xml"))

    assert not original.write_to_file("/nooooooooo/nooooooooooo.xml")
    assert original.write_to_file(path)

    res = PlotSettings()
    assert not res.read_from_file("/nooooooooo/nooooooooooo.xml")
    assert res.read_from_file(path)

    assert res.plot_type == original.plot_type
    # NOTE see above
    #assert res.properties == original.properties
    #assert res.layout == original.layout
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_FILTER
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_FILTER)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_MARKER_SIZE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_COLOR
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_COLOR)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_STROKE_WIDTH
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_LEGEND_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Z_TITLE
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_MIN
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_X_MAX
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_MIN
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN)
    assert res.data_defined_properties.property(
        PlotSettings.PROPERTY_Y_MAX
    ) == original.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX)
