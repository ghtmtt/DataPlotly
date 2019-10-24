# -*- coding: utf-8 -*-
"""Encapsulates settings for a plot

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtCore import (
    QFile,
    QIODevice
)
from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.core import (
    QgsXmlUtils,
    QgsProperty,
    QgsPropertyCollection,
    QgsPropertyDefinition
)


class PlotSettings:  # pylint: disable=too-many-instance-attributes
    """
    The PlotSettings class encapsulates all settings relating to a plot, and contains
    methods for serializing and deserializing these settings.
    """

    PROPERTY_FILTER = 1
    PROPERTY_MARKER_SIZE = 2

    DYNAMIC_PROPERTIES = {
        PROPERTY_FILTER: QgsPropertyDefinition('filter', 'Feature filter', QgsPropertyDefinition.Boolean),
        PROPERTY_MARKER_SIZE: QgsPropertyDefinition('marker_size', 'Marker size', QgsPropertyDefinition.DoublePositive)
    }

    def __init__(self, plot_type: str = 'scatter', properties: dict = None, layout: dict = None,
                 source_layer_id=None):
        # Define default plot dictionary used as a basis for plot initialization
        # prepare the default dictionary with None values
        # plot properties
        plot_base_properties = {
            'marker': 'markers',
            'custom': None,
            'hover_text': None,
            'additional_hover_text': None,
            'x_name': '',
            'y_name': '',
            'z_name': '',
            'in_color': None,
            'out_color': 'rgb(0, 0, 0)',
            'marker_width': 1,
            'marker_size': 10,
            'marker_symbol': 0,
            'line_dash': 'solid',
            'box_orientation': 'v',
            'opacity': 0.99,
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
            'in_color_value': '0,0,0,255',
            'in_color_property': QgsProperty().toVariant(),
            'color_scale_data_defined_in_check': False,
            'color_scale_data_defined_in_invert_check': False,
            'out_color_combo': '0,0,0,255',
            'marker_type_combo': 'Points',
            'point_combo': '',
            'line_combo': 'Solid Line',
            'contour_type_combo': 'Fill',
            'show_lines_check': False,
            'alpha': 1,
            'violin_side': None,
            'show_mean_line': False
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
            'xaxis': None,
            'bar_mode': None,
            'x_type': None,
            'y_type': None,
            'x_inv': None,
            'y_inv': None,
            'range_slider': {'borderwidth': 1, 'visible': False},
            'bargaps': 0,
            'polar': {'angularaxis': {'direction': 'clockwise'}},
            'additional_info_expression': '',
            'bins_check': False
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
        self.source_layer_id = source_layer_id

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
        parent_elem = document.createElement('DataPlotly')
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

        node = root_node.toElement().firstChildElement('DataPlotly')
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
            with open(file_name, "w") as f:
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
