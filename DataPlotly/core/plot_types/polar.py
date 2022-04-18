# -*- coding: utf-8 -*-
"""
Polar chart factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType


class PolarChartFactory(PlotType):
    """
    Factory for polar charts
    """

    @staticmethod
    def type_name():
        return 'polar'

    @staticmethod
    def name():
        return PlotType.tr('Polar Plot')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/polar.svg'))

    @staticmethod
    def create_trace(settings):
        return [graph_objs.Scatterpolar(
                r=settings.y,
                theta=settings.x,
                mode=settings.properties['marker'],
                name=settings.properties['y_name'],
                marker={
                    "color": settings.data_defined_colors if settings.data_defined_colors else settings.properties['in_color'],
                    "size": settings.data_defined_marker_sizes if settings.data_defined_marker_sizes else settings.properties['marker_size'],
                    "symbol": settings.properties['marker_symbol'],
                    "line": {
                        "color": settings.properties['out_color'],
                        "width": settings.properties['marker_width']
                    }
                },
                line={
                    "color": settings.properties['in_color'],
                    "width": settings.data_defined_stroke_widths if settings.data_defined_stroke_widths else settings.properties['marker_width'],
                    "dash": settings.properties['line_dash']
                },
                opacity=settings.properties['opacity'],
                )]

    @staticmethod
    def create_layout(settings):
        layout = super(PolarChartFactory, PolarChartFactory).create_layout(settings)

        layout['polar'] = settings.layout['polar']

        return layout
