# -*- coding: utf-8 -*-
"""Encapsulates settings for a plot

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""


class PlotSettings:
    """
    The PlotSettings class encapsulates all settings relating to a plot, and contains
    methods for serializing and deserializing these settings.
    """

    def __init__(self, plot_type: str, properties: dict = None, layout: dict = None, widgets: dict = None):
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
        self.widgets = widgets

    def write_xml(self):
        """
        Writes the plot settings to an XML element
        """
        # TODO
        pass

    def read_xml(self):
        """
        Reads the plot settings from an XML element
        """
        # TODO
        pass
