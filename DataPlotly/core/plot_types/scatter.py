"""
Base class for trace factories

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType


class ScatterPlotFactory(PlotType):
    """
    Factory for scatter plots
    """

    @staticmethod
    def type_name():
        return 'scatter'

    @staticmethod
    def name():
        return PlotType.tr('Scatter Plot')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/scatterplot.svg'))

    @staticmethod
    def create_trace(settings):

        if settings.properties.get('hover_label_text') is not None:
            mode = settings.properties.get('marker') + \
                settings.properties.get('hover_label_text')
        else:
            mode = settings.properties.get('marker')

        return [graph_objs.Scatter(
            x=settings.x,
            y=settings.y,
            mode=mode,
            textposition="top center",
            name=settings.data_defined_legend_title if settings.data_defined_legend_title != '' else settings.properties['name'],
            ids=settings.feature_ids,
            customdata=settings.properties['custom'],
            text=settings.additional_hover_text,
            hoverinfo=settings.properties['hover_text'],
            marker={'color': settings.data_defined_colors if settings.data_defined_colors else settings.properties['in_color'],
                    'colorscale': settings.properties['color_scale'],
                    'showscale': settings.properties['show_colorscale_legend'],
                    'reversescale': settings.properties['invert_color_scale'],
                    'colorbar': {
                        'len': 0.8},
                    'size': settings.data_defined_marker_sizes if settings.data_defined_marker_sizes else settings.properties['marker_size'],
                    'symbol': settings.properties['marker_symbol'],
                    'line': {'color': settings.data_defined_stroke_colors if settings.data_defined_stroke_colors else settings.properties['out_color'],
                             'width': settings.data_defined_stroke_widths if settings.data_defined_stroke_widths else settings.properties['marker_width']}
                    },
            line={'width': settings.properties['marker_width'],
                  'dash': settings.properties['line_dash']},
            opacity=settings.properties['opacity']
        )]

    @staticmethod
    def create_layout(settings):
        layout = super(ScatterPlotFactory, ScatterPlotFactory).create_layout(settings)

        layout['xaxis'].update(rangeslider=settings.layout['range_slider'])

        return layout
