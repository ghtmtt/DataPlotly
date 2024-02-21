"""
Histogram factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType


class HistogramFactory(PlotType):
    """
    Factory for histogram plots
    """

    @staticmethod
    def type_name():
        return 'histogram'

    @staticmethod
    def name():
        return PlotType.tr('Histogram')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/histogram.svg'))

    @staticmethod
    def create_trace(settings):
        return [
            graph_objs.Histogram(
                x=settings.x,
                y=settings.x,
                name=settings.data_defined_legend_title if settings.data_defined_legend_title != '' else settings.properties['name'],
                orientation=settings.properties['box_orientation'],
                nbinsx=settings.properties['bins'],
                nbinsy=settings.properties['bins'],
                marker={
                    'color': settings.data_defined_colors if settings.data_defined_colors else settings.properties['in_color'],
                    'line': {
                        'color': settings.data_defined_stroke_colors if settings.data_defined_stroke_colors else settings.properties['out_color'],
                        'width': settings.data_defined_stroke_widths if settings.data_defined_stroke_widths else settings.properties['marker_width']
                    }
                },
                histnorm=settings.properties['normalization'],
                opacity=settings.properties['opacity'],
                cumulative={
                    'enabled': settings.properties['cumulative'],
                    'direction': settings.properties['invert_hist']
                }
            )
        ]

    @staticmethod
    def create_layout(settings):
        layout = super(HistogramFactory, HistogramFactory).create_layout(settings)

        layout['barmode'] = settings.layout['bar_mode']
        layout['bargroupgap'] = settings.layout['bargaps']

        return layout
