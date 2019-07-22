# -*- coding: utf-8 -*-
"""
Histogram factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from plotly import graph_objs
from DataPlotly.core.plot_types.plot_type import PlotType


class HistogramFactory(PlotType):
    """
    Factory for histogram plots
    """

    @staticmethod
    def type_name():
        return 'histogram'

    @staticmethod
    def create_trace(settings):
        return [graph_objs.Histogram(
                x=settings.properties['x'],
                y=settings.properties['x'],
                name=settings.properties['name'],
                orientation=settings.properties['box_orientation'],
                nbinsx=settings.properties['bins'],
                nbinsy=settings.properties['bins'],
                marker=dict(
                    color=settings.properties['in_color'],
                    line=dict(
                        color=settings.properties['out_color'],
                        width=settings.properties['marker_width']
                    )
                ),
                histnorm=settings.properties['normalization'],
                opacity=settings.properties['opacity'],
                cumulative=dict(
                    enabled=settings.properties['cumulative'],
                    direction=settings.properties['invert_hist']
                )
            )]

    @staticmethod
    def create_layout(settings):
        layout = super(HistogramFactory, HistogramFactory).create_layout(settings)

        layout['barmode'] = settings.layout['bar_mode']
        layout['bargroupgap'] = settings.layout['bargaps']

        return layout
