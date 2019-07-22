# -*- coding: utf-8 -*-
"""
Contour chart factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from plotly import graph_objs
from DataPlotly.core.plot_types.plot_type import PlotType


class ContourFactory(PlotType):
    """
    Factory for contour charts
    """

    @staticmethod
    def create_trace(settings):
        return [graph_objs.Contour(
                z=[settings.properties['x'], settings.properties['y']],
                contours=dict(
                    coloring=settings.properties['cont_type'],
                    showlines=settings.properties['show_lines']
                ),
                colorscale=settings.properties['color_scale'],
                opacity=settings.properties['opacity']
            )]
