"""Plot factory test

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from pathlib import Path

import pytest

from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsReferencedRectangle,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsExpressionContextGenerator,
    QgsExpressionContext,
    QgsExpressionContextScope,
    QgsProperty
)
from qgis.PyQt.QtTest import QSignalSpy
from qgis.PyQt.QtCore import (
    QDate,
    QDateTime,
    Qt
)
from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.core.plot_factory import PlotFactory


def set_test_layer(data: Path) -> QgsVectorLayer:
    layer_path = data.joinpath("test_layer.shp")

    vl1 = QgsVectorLayer(str(layer_path), 'test_layer', 'ogr')
    vl1.setSubsetString('id < 10')

    assert vl1.isValid()

    QgsProject.instance().addMapLayer(vl1)

    return vl1


def test_values(data: Path):
    """
    Test value collection
    """
    vl1 = set_test_layer(data)

    # default plot settings
    settings = PlotSettings('scatter')

    # no source layer, fixed values must be used
    settings.source_layer_id = ''
    settings.x = [1, 2, 3]
    settings.y = [4, 5, 6]
    settings.z = [7, 8, 9]

    factory = PlotFactory(settings)
    assert factory.settings.x == [1, 2, 3]
    assert factory.settings.y == [4, 5, 6]
    assert factory.settings.z ==  [7, 8, 9]
    assert factory.settings.additional_hover_text == []

    # use source layer
    settings.source_layer_id = vl1.id()

    # no source set => no values
    factory = PlotFactory(settings)
    assert factory.settings.x == []
    assert factory.settings.y == []
    assert factory.settings.z == []
    assert factory.settings.additional_hover_text == []

    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'ca'
    factory = PlotFactory(settings)
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [
        81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45,
    ]
    assert factory.settings.z == []
    assert factory.settings.additional_hover_text == []

    # with z
    settings.properties['z_name'] = 'mg'
    factory = PlotFactory(settings)
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45]
    assert factory.settings.z == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.additional_hover_text == []

    # with expressions
    settings.properties['x_name'] = '"so4"/10'
    settings.properties['y_name'] = 'case when "profm" >-16 then "ca" else "mg" end'
    settings.properties['z_name'] = 'case when $x < 10.5 then 1 else 0 end'

    factory = PlotFactory(settings)
    assert factory.settings.x == [9.8, 8.8, 26.7, 32.9, 31.9, 13.7, 35.0, 15.1, 20.3]
    assert factory.settings.y == [81.87, 86.03, 85.26, 35.05, 131.59, 95.36, 112.88, 108.25, 78.34]
    assert factory.settings.z == [0, 1, 0, 0, 0, 0, 0, 1, 1]
    assert factory.settings.additional_hover_text == []

    # with some nulls
    settings.properties['x_name'] = '"so4"/10'
    settings.properties['y_name'] = 'case when "profm" >-16 then "ca" else "mg" end'
    settings.properties['z_name'] = 'case when $x < 10.5 then NULL else 1 end'
    factory = PlotFactory(settings)
    assert factory.settings.x == [9.8, 26.7, 32.9, 31.9, 13.7, 35.0]
    assert factory.settings.y == [81.87, 85.26, 35.05, 131.59, 95.36, 112.88]
    assert factory.settings.z == [1, 1, 1, 1, 1, 1]
    assert factory.settings.additional_hover_text == []

    # with additional values
    settings.layout['additional_info_expression'] = 'id'
    factory = PlotFactory(settings)
    assert factory.settings.x == [9.8, 26.7, 32.9, 31.9, 13.7, 35.0]
    assert factory.settings.y == [81.87, 85.26, 35.05, 131.59, 95.36, 112.88]
    assert factory.settings.z == [1, 1, 1, 1, 1, 1]
    assert factory.settings.additional_hover_text == [9, 7, 6, 5, 4, 3]


def test_expression_context(data: Path):
    """
    Test that correct expression context is used when evaluating expressions
    """
    vl1 = set_test_layer(data)

    settings = PlotSettings('scatter')
    settings.source_layer_id = vl1.id()
    settings.properties['x_name'] = '"so4"/@some_var'
    settings.properties['y_name'] = 'mg'

    factory = PlotFactory(settings)
    # should be empty, variable is not available
    assert factory.settings.x == []
    assert factory.settings.y == []
    assert factory.settings.z == []
    assert factory.settings.additional_hover_text == []

    class TestGenerator(QgsExpressionContextGenerator):

        def createExpressionContext(self) -> QgsExpressionContext:
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            scope.setVariable('some_var', 10)
            context.appendScope(scope)
            return context

    generator = TestGenerator()
    factory = PlotFactory(settings, context_generator=generator)
    assert factory.settings.x == [9.8, 8.8, 26.7, 32.9, 31.9, 13.7, 35.0, 15.1, 20.3]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.z == []
    assert factory.settings.additional_hover_text == []


def test_filter(data: Path):
    """
    Test that filters are correctly applied
    """
    vl1 = set_test_layer(data)
    
    settings = PlotSettings('scatter')
    settings.source_layer_id = vl1.id()
    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'mg'
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_FILTER,
        QgsProperty.fromExpression('so4/@some_var > 20'),
    )

    factory = PlotFactory(settings)
    # should be empty, variable is not available
    assert factory.settings.x == []
    assert factory.settings.y == []
    assert factory.settings.z == []
    assert factory.settings.additional_hover_text == []

    class TestGenerator(QgsExpressionContextGenerator):

        def createExpressionContext(self) -> QgsExpressionContext:
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            scope.setVariable('some_var', 10)
            context.appendScope(scope)
            return context

    generator = TestGenerator()
    factory = PlotFactory(settings, context_generator=generator)
    assert factory.settings.x == [267, 329, 319, 350, 203]
    assert factory.settings.y == [85.26, 81.11, 131.59, 112.88, 78.34]
    assert factory.settings.z == []
    assert factory.settings.additional_hover_text == []


def test_selected_feature_values(data: Path):
    """
    Test value collection for selected features
    """
    vl1 = set_test_layer(data)

    # default plot settings
    settings = PlotSettings('scatter')
    settings.properties['selected_features_only'] = True
    settings.source_layer_id = vl1.id()

    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'ca'
    factory = PlotFactory(settings)
    # no selection, no values
    assert factory.settings.x == []
    assert factory.settings.y == []
    assert factory.settings.z == []
    assert factory.settings.additional_hover_text == []

    vl1.selectByIds([1, 3, 4])
    factory = PlotFactory(settings)
    assert factory.settings.x == [88, 329, 319]
    assert factory.settings.y == [22.26, 35.05, 46.64]

    vl1.selectByIds([])
    factory = PlotFactory(settings)
    assert factory.settings.x == []
    assert factory.settings.y == []


def test_selected_feature_values_dynamic(data: Path):
    """
    Test that factory proactively updates when a selection changes, when desired
    """
    vl1 = set_test_layer(data)

    # not using selected features
    settings = PlotSettings('scatter')
    settings.properties['selected_features_only'] = False
    settings.source_layer_id = vl1.id()

    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'ca'
    factory = PlotFactory(settings)
    spy = QSignalSpy(factory.plot_built)
    vl1.selectByIds([1, 3, 4])
    assert len(spy) == 0

    # using selected features
    settings = PlotSettings('scatter')
    settings.properties['selected_features_only'] = True
    settings.source_layer_id = vl1.id()
    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'ca'
    factory = PlotFactory(settings)
    spy = QSignalSpy(factory.plot_built)

    vl1.selectByIds([1])
    assert len(spy) == 1
    assert factory.settings.x == [88]
    assert factory.settings.y == [22.26]

    vl1.selectByIds([1, 3, 4])
    assert len(spy) == 2
    assert factory.settings.x == [88, 329, 319]
    assert factory.settings.y == [22.26, 35.05, 46.64]

    vl1.selectByIds([])
    assert len(spy) == 3
    assert factory.settings.x == []
    assert factory.settings.y == []


def test_changed_feature_values_dynamic(data: Path):
    """
    Test that factory proactively updates when a layer changes
    """
    vl1 = set_test_layer(data)

    # not using selected features
    settings = PlotSettings('scatter')
    settings.source_layer_id = vl1.id()

    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'ca'
    factory = PlotFactory(settings)
    spy = QSignalSpy(factory.plot_built)
    assert len(spy) == 0
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [
        81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45,
    ]

    assert vl1.startEditing()
    vl1.changeAttributeValue(1, vl1.fields().lookupField('so4'), 500)
    assert len(spy) == 1
    assert factory.settings.x == [98, 500, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45]

    vl1.rollBack()


def test_visible_features(data: Path):
    """
    Test filtering to visible features only
    """
    vl1 = set_test_layer(data)
    
    # not using visible features
    settings = PlotSettings('scatter')
    settings.source_layer_id = vl1.id()

    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'ca'

    rect = QgsReferencedRectangle(QgsRectangle(10.1, 43.5, 10.8, 43.85), QgsCoordinateReferenceSystem(4326))
    factory = PlotFactory(settings, visible_region=rect)
    spy = QSignalSpy(factory.plot_built)
    assert len(spy) == 0
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [81.87, 22.26, 74.16, 35.05, 46.64, 126.73, 116.44, 108.25, 110.45]

    settings.properties['visible_features_only'] = True
    factory = PlotFactory(settings, visible_region=rect)
    spy = QSignalSpy(factory.plot_built)
    assert factory.settings.x == [88, 350, 151, 203]
    assert factory.settings.y == [22.26, 116.44, 108.25, 110.45]

    factory.set_visible_region(
        QgsReferencedRectangle(QgsRectangle(10.6, 43.1, 12, 43.8), QgsCoordinateReferenceSystem(4326))
    )
    assert len(spy) == 1
    assert factory.settings.x == [98, 267, 319, 137]
    assert factory.settings.y == [81.87, 74.16, 46.64, 126.73]

    # with reprojection
    factory.set_visible_region(
        QgsReferencedRectangle(
            QgsRectangle(1167379, 5310986, 1367180, 5391728),
            QgsCoordinateReferenceSystem(3857),
        ),
    )
    assert len(spy) == 2
    assert factory.settings.x == [98, 267, 329, 319, 137]
    assert factory.settings.y == [81.87, 74.16, 35.05, 46.64, 126.73]


def test_data_defined_sizes(data: Path):
    """
    Test data defined marker sizes
    """
    vl1 = set_test_layer(data)

    settings = PlotSettings('scatter')
    settings.source_layer_id = vl1.id()
    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'mg'
    settings.properties['marker_size'] = 15

    factory = PlotFactory(settings)
    # should be empty, not using data defined size
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_marker_sizes == []

    class TestGenerator(QgsExpressionContextGenerator):

        def createExpressionContext(self) -> QgsExpressionContext:
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            scope.setVariable('some_var', 10)
            context.appendScope(scope)
            context.appendScope(vl1.createExpressionContextScope())
            return context

    generator = TestGenerator()
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_MARKER_SIZE,
        QgsProperty.fromExpression('round("ca"/@some_var *@value)'),
    )

    factory = PlotFactory(settings, context_generator=generator)
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_marker_sizes == [
        123.0, 33.0, 111.0, 53.0, 70.0, 190.0, 175.0, 162.0, 166.0,
    ]


def test_data_defined_stroke_width(data: Path):
    """
    Test data defined stroke width
    """
    vl1 = set_test_layer(data)

    settings = PlotSettings('scatter')
    settings.source_layer_id = vl1.id()
    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'mg'
    settings.properties['marker_width'] = 3

    factory = PlotFactory(settings)
    # should be empty, not using data defined size
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_stroke_widths == []

    class TestGenerator(QgsExpressionContextGenerator):

        def createExpressionContext(self) -> QgsExpressionContext:
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            scope.setVariable('some_var', 10)
            context.appendScope(scope)
            context.appendScope(vl1.createExpressionContextScope())
            return context

    generator = TestGenerator()
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_STROKE_WIDTH,
        QgsProperty.fromExpression('round("ca"/@some_var *@value)'),
    )

    factory = PlotFactory(settings, context_generator=generator)
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_stroke_widths == [
        25.0, 7.0, 22.0, 11.0, 14.0, 38.0, 35.0, 32.0, 33.0,
    ]


def test_data_defined_color(data: Path):
    """
    Test data defined color
    """
    vl1 = set_test_layer(data)

    settings = PlotSettings('scatter')
    settings.source_layer_id = vl1.id()
    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'mg'
    settings.properties['in_color'] = 'red'

    factory = PlotFactory(settings)
    # should be empty, not using data defined size
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_colors == []

    class TestGenerator(QgsExpressionContextGenerator):

        def createExpressionContext(self) -> QgsExpressionContext:
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            scope.setVariable('some_var', 10)
            context.appendScope(scope)
            context.appendScope(vl1.createExpressionContextScope())
            return context

    generator = TestGenerator()
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_COLOR, 
        QgsProperty.fromExpression(
            'case when round("ca"/@some_var)>10 then \'yellow\' else \'blue\' end',
        ),
    )
    factory = PlotFactory(settings, context_generator=generator)
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_colors == [
        '#0000ff',
        '#0000ff',
        '#0000ff',
        '#0000ff',
        '#0000ff',
        '#ffff00',
        '#ffff00',
        '#ffff00',
        '#ffff00',
    ]


def test_data_defined_stroke_color(data: Path):
    """
    Test data defined stroke color
    """
    vl1 = set_test_layer(data)

    settings = PlotSettings('scatter')
    settings.source_layer_id = vl1.id()
    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'mg'
    settings.properties['in_color'] = 'red'

    factory = PlotFactory(settings)
    # should be empty, not using data defined size
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_colors == []

    class TestGenerator(QgsExpressionContextGenerator):

        def createExpressionContext(self) -> QgsExpressionContext:
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            scope.setVariable('some_var', 10)
            context.appendScope(scope)
            context.appendScope(vl1.createExpressionContextScope())
            return context

    generator = TestGenerator()
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_STROKE_COLOR, 
        QgsProperty.fromExpression(
            'case when round("ca"/@some_var)>10 then \'yellow\' else \'blue\' end'
        ),
    )
    factory = PlotFactory(settings, context_generator=generator)
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_stroke_colors == [
        '#0000ff',
        '#0000ff',
        '#0000ff',
        '#0000ff',
        '#0000ff',
        '#ffff00',
        '#ffff00',
        '#ffff00',
        '#ffff00',
    ]


def test_data_defined_layout_properties(data: Path):
    """
    Test data defined stroke color
    """
    vl1 = set_test_layer(data)
    
    settings = PlotSettings('scatter')
    settings.source_layer_id = vl1.id()
    settings.properties['x_name'] = 'so4'
    settings.properties['y_name'] = 'mg'
    settings.layout['title'] = 'title'
    settings.layout['legend_title'] = 'legend_title'
    settings.layout['x_title'] = 'x_title'
    settings.layout['y_title'] = 'y_title'
    settings.layout['z_title'] = 'z_title'
    settings.layout['x_min'] = 0
    settings.layout['x_max'] = 1
    settings.layout['y_min'] = 0
    settings.layout['y_max'] = 1

    factory = PlotFactory(settings)
    # should be empty, not using data defined size
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_title == ''
    assert factory.settings.data_defined_legend_title == ''
    assert factory.settings.data_defined_x_title == ''
    assert factory.settings.data_defined_y_title == ''
    assert factory.settings.data_defined_z_title == ''
    assert factory.settings.data_defined_x_min is None
    assert factory.settings.data_defined_x_max is None
    assert factory.settings.data_defined_y_min is None
    assert factory.settings.data_defined_y_max is None

    class TestGenerator(QgsExpressionContextGenerator):

        def createExpressionContext(self) -> QgsExpressionContext:
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            scope.setVariable('some_var', 10)
            context.appendScope(scope)
            context.appendScope(vl1.createExpressionContextScope())
            return context

    generator = TestGenerator()
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_TITLE,
        QgsProperty.fromExpression("concat('my', '_title_', @some_var)"),
    )
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_LEGEND_TITLE,
        QgsProperty.fromExpression("concat('my', '_legend_', @some_var)"),
    )
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_TITLE,
        QgsProperty.fromExpression("concat('my', '_x_axis_', @some_var)"),
    )
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_TITLE,
        QgsProperty.fromExpression("concat('my', '_y_axis_', @some_var)"),
    )
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Z_TITLE,
        QgsProperty.fromExpression("concat('my', '_z_axis_', @some_var)"),
    )
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MIN,
        QgsProperty.fromExpression("-1*@some_var"),
    )
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_X_MAX,
        QgsProperty.fromExpression("+1*@some_var"),
    )
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MIN,
        QgsProperty.fromExpression("-1*@some_var"),
    )
    settings.data_defined_properties.setProperty(
        PlotSettings.PROPERTY_Y_MAX,
        QgsProperty.fromExpression("+1*@some_var"),
    )
    factory = PlotFactory(settings, context_generator=generator)
    assert factory.settings.x == [98, 88, 267, 329, 319, 137, 350, 151, 203]
    assert factory.settings.y == [72.31, 86.03, 85.26, 81.11, 131.59, 95.36, 112.88, 80.55, 78.34]
    assert factory.settings.data_defined_title == 'my_title_10'
    assert factory.settings.data_defined_legend_title ==  'my_legend_10'
    assert factory.settings.data_defined_x_title == 'my_x_axis_10'
    assert factory.settings.data_defined_y_title == 'my_y_axis_10'
    assert factory.settings.data_defined_z_title == 'my_z_axis_10'
    assert factory.settings.data_defined_x_min == -10
    assert factory.settings.data_defined_x_max == 10
    assert factory.settings.data_defined_y_min == -10
    assert factory.settings.data_defined_y_max == 10


def test_dates():  # pylint: disable=too-many-statements
    """
    Test handling of dates
    """
    # default plot settings
    settings = PlotSettings('scatter')

    # no source layer, fixed values must be used
    settings.source_layer_id = ''
    settings.x = [QDate(2020, 1, 1), QDate(2020, 2, 1), QDate(2020, 3, 1)]
    settings.y = [4, 5, 6]
    factory = PlotFactory(settings)

    # Build the dictionary from teh figure
    plot_dict = factory.build_plot_dict()

    # get the x and y fields as list
    for items in plot_dict['data']:
        # converts the QDate into strings
        x = [str(i.toPyDate()) for i in items['x']]
        y = items['y']

    assert x == ["2020-01-01", "2020-02-01", "2020-03-01"]
    assert y == [4, 5, 6]

    settings.x = [
        QDateTime(2020, 1, 1, 11, 21), 
        QDateTime(2020, 2, 1, 0, 15),
        QDateTime(2020, 3, 1, 17, 23, 11),
    ]
    settings.y = [4, 5, 6]
    factory = PlotFactory(settings)

    # Build the dictionary from teh figure
    plot_dict = factory.build_plot_dict()

    # get the x and y fields as list
    for items in plot_dict['data']:
        # converts the QDate into strings
        x = [str(i.toString(Qt.ISODate)) for i in items['x']]
        y = items['y']

    assert x == ["2020-01-01T11:21:00", "2020-02-01T00:15:00", "2020-03-01T17:23:11"]
    assert y == [4, 5, 6]


@pytest.mark.skip(reason="Fragile")
def test_data_defined_histogram_color(data: Path):
    """
    Test data defined stroke color
    """
    layer_path = data.joinpath("test_layer.geojson")

    vl1 = QgsVectorLayer(str(layer_path), 'test_layer', 'ogr')
    QgsProject.instance().addMapLayer(vl1)

    settings = PlotSettings('histogram')
    settings.source_layer_id = vl1.id()
    settings.properties['x_name'] = 'so4'

    factory = PlotFactory(settings)

    assert factory.settings.x == [
        1322, 1055, 632, 1122, 536, 680, 296, 265, 788, 
        791, 683, 457, 267, 513, 306, 627, 100, 84, 98, 
        88, 267, 329, 319, 137, 350, 151, 203,
    ]
    assert factory.settings.data_defined_colors == []

    class TestGenerator(QgsExpressionContextGenerator):

        def createExpressionContext(self) -> QgsExpressionContext:
            context = QgsExpressionContext()
            scope = QgsExpressionContextScope()
            context.appendScope(scope)
            context.appendScope(vl1.createExpressionContextScope())
            return context

    generator = TestGenerator()
    settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_COLOR, QgsProperty.fromExpression(
        """array('215,25,28,255',
                 '241,124,74,255',
                 '254,201,128,255',
                 '255,255,191,255',
                 '199,230,219,255',
                 '129,186,216,255',
                 '44,123,182,255')"""))
    factory = PlotFactory(settings, context_generator=generator)
    assert factory.settings.x == [
        1322, 1055, 632, 1122, 536, 680, 296, 265, 788, 791, 683, 
        457, 267, 513, 306, 627, 100, 84, 98, 88, 267, 329, 
        319, 137, 350, 151, 203,
    ]
    assert factory.settings.y == []
    assert factory.settings.data_defined_colors == [
        "#d7191c",
        "#f17c4a",
        "#fec980",
        "#ffffbf",
        "#c7e6db",
        "#81bad8",
        "#2c7bb6",
    ]
