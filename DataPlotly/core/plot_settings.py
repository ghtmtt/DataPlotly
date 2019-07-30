# -*- coding: utf-8 -*-
"""Encapsulates settings for a plot

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.core import (
    QgsXmlUtils,
    QgsProperty
)


class PlotSettings:
    """
    The PlotSettings class encapsulates all settings relating to a plot, and contains
    methods for serializing and deserializing these settings.
    """

    def __init__(self, plot_type: str = 'scatter', properties: dict = None, layout: dict = None):
        # Define default plot dictionary used as a basis for plot initialization
        # prepare the default dictionary with None values
        # plot properties
        plot_base_properties = {
            'layer_id': None,
            'x': None,
            'y': None,
            'z': None,
            'marker': 'markers',
            'featureIds': None,
            'featureBox': None,
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
            'colorscale_in': None,
            'show_lines': False,
            'cumulative': False,
            'show_colorscale_legend': False,
            'invert_color_scale': False,
            'invert_hist': 'increasing',
            'bins': 0,
            'features_selected': False,
            'in_color_value': '0,0,0,255',
            'in_color_property': QgsProperty().toVariant(),
            'size_property': QgsProperty().toVariant(),
            'color_scale_data_defined_in': '',
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

    def write_xml(self, document: QDomDocument):
        """
        Writes the plot settings to an XML element
        """
        element = QgsXmlUtils.writeVariant({
            'plot_type': self.plot_type,
            'plot_properties': self.properties,
            'plot_layout': self.layout
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
