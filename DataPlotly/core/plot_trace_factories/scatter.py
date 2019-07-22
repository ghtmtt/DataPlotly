# -*- coding: utf-8 -*-
"""
Base class for trace factories

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from plotly import graph_objs
from DataPlotly.core.plot_trace_factories.trace_factory import TraceFactory


class ScatterPlotFactory(TraceFactory):
    """
    Factory for scatter plots
    """

    @staticmethod
    def create_trace(settings):
        return [graph_objs.Scatter(
            x=settings.properties['x'],
            y=settings.properties['y'],
            mode=settings.properties['marker'],
            name=settings.properties['name'],
            ids=settings.properties['featureIds'],
            customdata=settings.properties['custom'],
            text=settings.properties['additional_hover_text'],
            hoverinfo=settings.properties['hover_text'],
            marker={'color': settings.properties['in_color'],
                    'colorscale': settings.properties['colorscale_in'],
                    'showscale': settings.properties['show_colorscale_legend'],
                    'reversescale': settings.properties['invert_color_scale'],
                    'colorbar': {
                        'len': 0.8},
                    'size': settings.properties['marker_size'],
                    'symbol': settings.properties['marker_symbol'],
                    'line': {'color': settings.properties['out_color'],
                             'width': settings.properties['marker_width']}
                    },
            line={'width': settings.properties['marker_width'],
                  'dash': settings.properties['line_dash']},
            opacity=settings.properties['opacity']
        )]
