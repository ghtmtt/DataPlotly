# -*- coding: utf-8 -*-
"""
Bar plot

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType


class BarPlotFactory(PlotType):
    """
    Factory for bar plots
    """

    @staticmethod
    def type_name():
        return 'bar'

    @staticmethod
    def name():
        return PlotType.tr('Bar Plot')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/barplot.svg'))

    @staticmethod
    def create_trace(settings):
        # flip the variables according to the box orientation

        if settings.properties['box_orientation'] == 'h':
            y = settings.x
            x = settings.y
        else:
            x = settings.x
            y = settings.y

        return [graph_objs.Bar(
            x=x,
            y=y,
            text=settings.additional_hover_text,
            textposition=settings.properties.get('hover_label_position'),
            name=settings.data_defined_legend_title if settings.data_defined_legend_title != '' else settings.properties['name'],
            ids=settings.feature_ids,
            customdata=settings.properties['custom'],
            orientation=settings.properties['box_orientation'],
            marker={'color': settings.data_defined_colors if settings.data_defined_colors else settings.properties['in_color'],
                    'colorscale': settings.properties['color_scale'],
                    'showscale': settings.properties['show_colorscale_legend'],
                    'reversescale': settings.properties['invert_color_scale'],
                    'colorbar': {
                        'len': 0.8
                    },
                    'line': {
                        'color': settings.data_defined_stroke_colors if settings.data_defined_stroke_colors else settings.properties['out_color'],
                        'width': settings.data_defined_stroke_widths if settings.data_defined_stroke_widths else settings.properties['marker_width']}
                    },
            width=settings.data_defined_marker_sizes if settings.data_defined_marker_sizes else settings.properties['marker_size'],
            opacity=settings.properties['opacity']
        )]

    @staticmethod
    def create_layout(settings):
        layout = super(BarPlotFactory, BarPlotFactory).create_layout(settings)

        layout['barmode'] = settings.layout['bar_mode']

        return layout
