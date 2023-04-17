# -*- coding: utf-8 -*-
"""Encapsulates settings for a plot

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.core import QgsXmlUtils, QgsPropertyCollection, QgsPropertyDefinition


class PlotSettings:  # pylint: disable=too-many-instance-attributes
    """
    The PlotSettings class encapsulates all settings relating to a plot, and contains
    methods for serializing and deserializing these settings.
    """

    PROPERTY_FILTER = 1
    PROPERTY_MARKER_SIZE = 2
    PROPERTY_COLOR = 3
    PROPERTY_STROKE_COLOR = 4
    PROPERTY_STROKE_WIDTH = 5
    PROPERTY_X_MIN = 6
    PROPERTY_X_MAX = 7
    PROPERTY_Y_MIN = 8
    PROPERTY_Y_MAX = 9
    PROPERTY_TITLE = 10
    PROPERTY_LEGEND_TITLE = 11
    PROPERTY_X_TITLE = 12
    PROPERTY_Y_TITLE = 13
    PROPERTY_Z_TITLE = 14
    PROPERTY_FONT_TITLE_SIZE = 15
    PROPERTY_FONT_TITLE_FAMILY = 16
    PROPERTY_FONT_TITLE_COLOR = 17
    PROPERTY_FONT_XLABEL_SIZE = 18
    PROPERTY_FONT_XLABEL_FAMILY = 19
    PROPERTY_FONT_XLABEL_COLOR = 20
    PROPERTY_FONT_XTICKS_SIZE = 21
    PROPERTY_FONT_XTICKS_FAMILY = 22
    PROPERTY_FONT_XTICKS_COLOR = 23
    PROPERTY_FONT_YLABEL_SIZE = 24
    PROPERTY_FONT_YLABEL_FAMILY = 25
    PROPERTY_FONT_YLABEL_COLOR = 26
    PROPERTY_FONT_YTICKS_SIZE = 27
    PROPERTY_FONT_YTICKS_FAMILY = 28
    PROPERTY_FONT_YTICKS_COLOR = 29

    DYNAMIC_PROPERTIES = {
        PROPERTY_FILTER: QgsPropertyDefinition('filter', 'Feature filter', QgsPropertyDefinition.Boolean),
        PROPERTY_MARKER_SIZE: QgsPropertyDefinition('marker_size', 'Marker size', QgsPropertyDefinition.DoublePositive),
        PROPERTY_COLOR: QgsPropertyDefinition('color', 'Color', QgsPropertyDefinition.ColorWithAlpha),
        PROPERTY_STROKE_COLOR: QgsPropertyDefinition('stroke_color', 'Stroke color',
                                                     QgsPropertyDefinition.ColorWithAlpha),
        PROPERTY_STROKE_WIDTH: QgsPropertyDefinition('stroke_width', 'Stroke width',
                                                     QgsPropertyDefinition.DoublePositive),
        PROPERTY_TITLE: QgsPropertyDefinition('title', 'Plot title', QgsPropertyDefinition.String),
        PROPERTY_LEGEND_TITLE: QgsPropertyDefinition('legend_title', 'Legend title', QgsPropertyDefinition.String),
        PROPERTY_FONT_TITLE_SIZE: QgsPropertyDefinition('font_title_size', 'Font title size', QgsPropertyDefinition.String),
        PROPERTY_FONT_TITLE_FAMILY: QgsPropertyDefinition('font_title_family', 'Font title family', QgsPropertyDefinition.String),
        PROPERTY_FONT_TITLE_COLOR: QgsPropertyDefinition('font_title_color', 'Font title color', QgsPropertyDefinition.ColorWithAlpha),
        PROPERTY_FONT_XLABEL_SIZE: QgsPropertyDefinition('font_xlabel_size', 'Font xlabel size', QgsPropertyDefinition.String),
        PROPERTY_FONT_XLABEL_FAMILY: QgsPropertyDefinition('font_xlabel_family', 'Font xlabel family', QgsPropertyDefinition.String),
        PROPERTY_FONT_XLABEL_COLOR: QgsPropertyDefinition('font_xlabel_color', 'Font xlabel color', QgsPropertyDefinition.ColorWithAlpha),
        PROPERTY_FONT_XTICKS_SIZE: QgsPropertyDefinition('font_xticks_size', 'Font xticks size', QgsPropertyDefinition.String),
        PROPERTY_FONT_XTICKS_FAMILY: QgsPropertyDefinition('font_xticks_family', 'Font xticks family', QgsPropertyDefinition.String),
        PROPERTY_FONT_XTICKS_COLOR: QgsPropertyDefinition('font_xticks_color', 'Font xticks color', QgsPropertyDefinition.ColorWithAlpha),
        PROPERTY_FONT_YLABEL_SIZE: QgsPropertyDefinition('font_ylabel_size', 'Font ylabel size', QgsPropertyDefinition.String),
        PROPERTY_FONT_YLABEL_FAMILY: QgsPropertyDefinition('font_ylabel_family', 'Font ylabel family', QgsPropertyDefinition.String),
        PROPERTY_FONT_YLABEL_COLOR: QgsPropertyDefinition('font_ylabel_color', 'Font ylabel color', QgsPropertyDefinition.ColorWithAlpha),
        PROPERTY_FONT_YTICKS_SIZE: QgsPropertyDefinition('font_yticks_size', 'Font yticks size', QgsPropertyDefinition.String),
        PROPERTY_FONT_YTICKS_FAMILY: QgsPropertyDefinition('font_yticks_family', 'Font yticks family', QgsPropertyDefinition.String),
        PROPERTY_FONT_YTICKS_COLOR: QgsPropertyDefinition('font_yticks_color', 'Font yticks color', QgsPropertyDefinition.ColorWithAlpha),
        PROPERTY_X_TITLE: QgsPropertyDefinition('x_title', 'X title', QgsPropertyDefinition.String),
        PROPERTY_Y_TITLE: QgsPropertyDefinition('y_title', 'Y title', QgsPropertyDefinition.String),
        PROPERTY_Z_TITLE: QgsPropertyDefinition('z_title', 'Z title', QgsPropertyDefinition.String),
        PROPERTY_X_MIN: QgsPropertyDefinition('x_min', 'X axis minimum', QgsPropertyDefinition.Double),
        PROPERTY_X_MAX: QgsPropertyDefinition('x_max', 'X axis maximum', QgsPropertyDefinition.Double),
        PROPERTY_Y_MIN: QgsPropertyDefinition('y_min', 'Y axis minimum', QgsPropertyDefinition.Double),
        PROPERTY_Y_MAX: QgsPropertyDefinition('y_max', 'Y axis maximum', QgsPropertyDefinition.Double)
    }

    # pylint: disable=too-many-arguments
    def __init__(self, plot_type: str = 'scatter', properties: dict = None, layout: dict = None,
                 source_layer_id=None, dock_title: str = None, dock_id: str = None):
        # Define default plot dictionary used as a basis for plot initialization
        # prepare the default dictionary with None values
        # plot properties
        plot_base_properties = {
            'marker': 'markers',
            'custom': None,
            'hover_text': None,
            'additional_hover_text': None,
            'hover_label_text': None,
            'x_name': '',
            'y_name': '',
            'z_name': '',
            'in_color': '#8ebad9',
            'out_color': '#1f77b4',
            'marker_width': 1,
            'marker_size': 10,
            'marker_symbol': 0,
            'line_dash': 'solid',
            'box_orientation': 'v',
            'box_stat': None,
            'box_outliers': False,
            'name': '',
            'normalization': None,
            'cont_type': 'fill',
            'color_scale': None,
            'show_lines': False,
            'cumulative': False,
            'show_colorscale_legend': False,
            'invert_color_scale': False,
            'invert_hist': 'increasing',
            'bins': 0,
            'selected_features_only': False,
            'visible_features_only': False,
            'color_scale_data_defined_in_check': False,
            'color_scale_data_defined_in_invert_check': False,
            'marker_type_combo': 'Points',
            'point_combo': '',
            'line_combo': 'Solid Line',
            'contour_type_combo': 'Fill',
            'show_lines_check': False,
            'opacity': 1,
            'violin_side': None,
            'violin_box': False,
            'show_mean_line': False,
            'layout_filter_by_map': False,
            'layout_filter_by_atlas': False,
            'pie_hole': 0
        }

        # layout nested dictionary
        plot_base_layout = {
            'title': 'Plot Title',
            'legend': True,
            'legend_title': None,
            'legend_orientation': 'h',
            'x_title': '',
            'y_title': '',
            'z_title': '',
            'font_title_size': 10,
            'font_title_family': "Arial",
            'font_title_color': "#000000",
            'font_xlabel_size': 10,
            'font_xlabel_family': "Arial",
            'font_xlabel_color': "#000000",
            'font_xticks_size': 10,
            'font_xticks_family': "Arial",
            'font_xticks_color': "#000000",
            'font_ylabel_size': 10,
            'font_ylabel_family': "Arial",
            'font_ylabel_color': "#000000",
            'font_yticks_size': 10,
            'font_yticks_family': "Arial",
            'font_yticks_color': "#000000",
            'xaxis': None,
            'bar_mode': None,
            'x_type': None,
            'y_type': None,
            'x_inv': None,
            'y_inv': None,
            'x_min': None,
            'x_max': None,
            'y_min': None,
            'y_max': None,
            'range_slider': {'borderwidth': 1, 'visible': False},
            'bargaps': 0,
            'polar': {'angularaxis': {'direction': 'clockwise'}},
            'additional_info_expression': '',
            'bins_check': False,
            'gridcolor': '#bdbfc0'
        }

        self.plot_base_dic = {
            'plot_type': None,
            'layer': None,
            'plot_prop': plot_base_properties,
            'layout_prop': plot_base_layout
        }

        self.data_defined_properties = QgsPropertyCollection()

        # Set class properties - we use the base dictionaries, replacing base values with
        # those from the passed properties dicts
        if properties is None:
            self.properties = plot_base_properties
        else:
            self.properties = {**plot_base_properties, **properties}
        if layout is None:
            self.layout = plot_base_layout
        else:
            self.layout = {**plot_base_layout, **layout}

        self.plot_type = plot_type

        self.x = []
        self.y = []
        self.z = []
        self.feature_ids = []
        self.additional_hover_text = []
        self.data_defined_marker_sizes = []
        self.data_defined_colors = []
        self.data_defined_stroke_colors = []
        self.data_defined_stroke_widths = []

        # layout properties
        self.data_defined_title = ""
        self.data_defined_legend_title = ""
        self.data_defined_x_title = ""
        self.data_defined_y_title = ""
        self.data_defined_z_title = ""
        self.data_defined_x_min = None
        self.data_defined_x_max = None
        self.data_defined_y_min = None
        self.data_defined_y_max = None
        self.source_layer_id = source_layer_id

        # multiple_dock
        self.dock_title = dock_title
        self.dock_id = dock_id

    def write_xml(self, document: QDomDocument):
        """
        Writes the plot settings to an XML element
        """
        element = QgsXmlUtils.writeVariant({
            'plot_type': self.plot_type,
            'plot_properties': self.properties,
            'plot_layout': self.layout,
            'source_layer_id': self.source_layer_id,
            'dynamic_properties': self.data_defined_properties.toVariant(PlotSettings.DYNAMIC_PROPERTIES)
        }, document)
        return element

    def read_xml(self, element: QDomElement) -> bool:
        """
        Reads the plot settings from an XML element
        """
        res = QgsXmlUtils.readVariant(element)
        if not isinstance(res, dict) or \
                'plot_type' not in res or \
                'plot_properties' not in res or \
                'plot_layout' not in res:
            return False

        self.plot_type = res['plot_type']
        self.properties = res['plot_properties']
        self.layout = res['plot_layout']
        self.source_layer_id = res.get('source_layer_id', None)
        self.data_defined_properties.loadVariant(res.get('dynamic_properties', None), PlotSettings.DYNAMIC_PROPERTIES)

        return True

    def write_to_project(self, document: QDomDocument):
        """
        Writes the settings to a project (represented by the given DOM document)
        """
        elem = self.write_xml(document)
        if self.dock_id == 'DataPlotly':
            parent_elem = document.createElement('DataPlotly')
        else:
            parent_elem = document.createElement(f'DataPlotly_{self.dock_title}_{self.dock_id}')
        parent_elem.appendChild(elem)

        root_node = document.elementsByTagName("qgis").item(0)
        root_node.appendChild(parent_elem)

    def read_from_project(self, document: QDomDocument):
        """
        Reads the settings from a project (represented by the given DOM document)
        """
        root_node = document.elementsByTagName("qgis").item(0)
        if root_node.isNull():
            return False
        if self.dock_id == 'DataPlotly':
            tag = "DataPlotly"
        else:
            tag = f'DataPlotly_{self.dock_title}_{self.dock_id}'
        node = root_node.toElement().firstChildElement(tag)
        if node.isNull():
            return False

        elem = node.toElement()
        return self.read_xml(elem.firstChildElement())

    def write_to_file(self, file_name: str) -> bool:
        """
        Writes the settings to an XML file
        """
        document = QDomDocument("dataplotly")
        elem = self.write_xml(document)
        document.appendChild(elem)

        try:
            with open(file_name, "w", encoding="utf8") as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(document.toString())
                return True
        except FileNotFoundError:
            return False

    def read_from_file(self, file_name: str) -> bool:
        """
        Reads the settings from an XML file
        """
        f = QFile(file_name)
        if f.open(QIODevice.ReadOnly):
            document = QDomDocument()
            if document.setContent(f):
                if self.read_xml(document.firstChildElement()):
                    return True

        return False
