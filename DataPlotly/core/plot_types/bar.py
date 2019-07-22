# -*- coding: utf-8 -*-
"""
Bar plot

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from plotly import graph_objs
from DataPlotly.core.plot_types.plot_type import PlotType


class BarPlotFactory(PlotType):
    """
    Factory for bar plots
    """

    @staticmethod
    def type_name():
        return 'bar'

    @staticmethod
    def create_trace(settings):
        # flip the variables according to the box orientation

        if settings.properties['box_orientation'] == 'h':
            y = settings.properties['x']
            x = settings.properties['y']
        else:
            x = settings.properties['x']
            y = settings.properties['y']

        return [graph_objs.Bar(
            x=x,
            y=y,
            name=settings.properties['name'],
            ids=settings.properties['featureBox'],
            customdata=settings.properties['custom'],
            orientation=settings.properties['box_orientation'],
            marker={'color': settings.properties['in_color'],
                    'colorscale': settings.properties['colorscale_in'],
                    'showscale': settings.properties['show_colorscale_legend'],
                    'reversescale': settings.properties['invert_color_scale'],
                    'colorbar': {
                        'len': 0.8
                    },
                    'line': {
                        'color': settings.properties['out_color'],
                        'width': settings.properties['marker_width']}
                    },
            opacity=settings.properties['opacity']
        )]

    @staticmethod
    def create_layout(settings):
        layout = super(BarPlotFactory, BarPlotFactory).create_layout(settings)

        layout['barmode'] = settings.layout['bar_mode']

        return layout
