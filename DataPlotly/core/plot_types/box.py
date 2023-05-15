"""
Box plot

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType


class BoxPlotFactory(PlotType):
    """
    Factory for box plots
    """

    @staticmethod
    def type_name():
        return 'box'

    @staticmethod
    def name():
        return PlotType.tr('Box Plot')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/boxplot.svg'))

    @staticmethod
    def create_trace(settings):
        # flip the variables according to the box orientation

        if settings.properties['box_orientation'] == 'h':
            y = settings.x
            x = settings.y
        else:
            x = settings.x
            y = settings.y

        return [graph_objs.Box(
            x=x or None,
            y=y,
            name=settings.data_defined_legend_title if settings.data_defined_legend_title != '' else settings.properties['name'],
            customdata=settings.properties['custom'],
            boxmean=settings.properties['box_stat'],
            orientation=settings.properties['box_orientation'],
            boxpoints=settings.properties['box_outliers'],
            fillcolor=settings.data_defined_colors[0] if settings.data_defined_colors else settings.properties['in_color'],
            line={'color': settings.data_defined_stroke_colors[0] if settings.data_defined_stroke_colors else settings.properties['out_color'],
                  'width': settings.data_defined_stroke_widths[0] if settings.data_defined_stroke_widths else settings.properties['marker_width']},
            opacity=settings.properties['opacity']
        )]
