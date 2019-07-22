# -*- coding: utf-8 -*-
"""
Violin chart factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from plotly import graph_objs
from DataPlotly.core.plot_types.plot_type import PlotType


class ViolinFactory(PlotType):
    """
    Factory for violin charts
    """

    @staticmethod
    def type_name():
        return 'violin'

    @staticmethod
    def create_trace(settings):
        # flip the variables according to the box orientation
        if settings.properties['box_orientation'] == 'h':
            y = settings.properties['x']
            x = settings.properties['y']
        else:
            x = settings.properties['x']
            y = settings.properties['y']

        return [graph_objs.Violin(
            x=x,
            y=y,
            name=settings.properties['name'],
            customdata=settings.properties['custom'],
            orientation=settings.properties['box_orientation'],
            points=settings.properties['box_outliers'],
            fillcolor=settings.properties['in_color'],
            line=dict(
                color=settings.properties['out_color'],
                width=settings.properties['marker_width']
            ),
            opacity=settings.properties['opacity'],
            meanline=dict(
                visible=settings.properties['show_mean_line']
            ),
            side=settings.properties['violin_side']
        )]
