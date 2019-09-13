# -*- coding: utf-8 -*-
"""
2D histogram factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType


class Histogram2dFactory(PlotType):
    """
    Factory for 2D histograms
    """

    @staticmethod
    def type_name():
        return '2dhistogram'

    @staticmethod
    def name():
        return PlotType.tr('2D Histogram')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/2dhistogram.svg'))

    @staticmethod
    def create_trace(settings):
        return [graph_objs.Histogram2d(
                x=settings.x,
                y=settings.y,
                colorscale=settings.properties['color_scale']
            )]
