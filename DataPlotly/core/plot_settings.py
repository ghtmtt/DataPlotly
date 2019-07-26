# -*- coding: utf-8 -*-
"""Encapsulates settings for a plot

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtXml import QDomDocument, QDomElement
from qgis.core import QgsXmlUtils


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
            'x': None,
            'y': None,
            'z': None,
            'marker': None,
            'featureIds': None,
            'featureBox': None,
            'custom': None,
            'hover_text': None,
            'additional_hover_text': None,
            'x_name': None,
            'y_name': None,
            'z_name': None,
            'in_color': None,
            'out_color': None,
            'marker_width': 1,
            'marker_size': 10,
            'marker_symbol': None,
            'line_dash': None,
            'box_orientation': 'v',
            'opacity': None,
            'box_stat': None,
            'box_outliers': False,
            'name': None,
            'normalization': None,
            'cont_type': None,
            'color_scale': None,
            'colorscale_in': None,
            'show_lines': False,
            'cumulative': False,
            'show_colorscale_legend': False,
            'invert_color_scale': False,
            'invert_hist': False,
            'bins': None
        }

        # layout nested dictionary
        plot_base_layout = {
            'title': 'Plot Title',
            'legend': True,
            'legend_title': None,
            'legend_orientation': 'h',
            'x_title': None,
            'y_title': None,
            'z_title': None,
            'xaxis': None,
            'bar_mode': None,
            'x_type': None,
            'y_type': None,
            'x_inv': None,
            'y_inv': None,
            'range_slider': {'visible': False},
            'bargaps': None,
            'polar': {'angularaxis': {'direction': 'clockwise'}}
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
