# -*- coding: utf-8 -*-
"""
Pie chart factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from plotly import graph_objs
from DataPlotly.core.plot_trace_factories.trace_factory import TraceFactory


class PieChartFactory(TraceFactory):
    """
    Factory for pie charts
    """

    @staticmethod
    def create_trace(settings):
        return [graph_objs.Pie(
                labels=settings.properties['x'],
                values=settings.properties['y'],
                name=settings.properties['custom'][0],
            )]
