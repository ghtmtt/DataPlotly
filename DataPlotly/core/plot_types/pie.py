# -*- coding: utf-8 -*-
"""
Pie chart factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType


class PieChartFactory(PlotType):
    """
    Factory for pie charts
    """

    @staticmethod
    def type_name():
        return 'pie'

    @staticmethod
    def name():
        return PlotType.tr('Pie Chart')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/pie.svg'))

    @staticmethod
    def create_trace(settings):
        return [graph_objs.Pie(
                labels=settings.x,
                values=settings.y,
                marker={
                    'colors': settings.data_defined_colors if settings.data_defined_colors else [settings.properties['in_color']]
                },
                name=settings.properties['custom'][0],
                hole=settings.properties['pie_hole']
                )]

    @staticmethod
    def create_layout(settings):
        layout = super(PieChartFactory, PieChartFactory).create_layout(settings)

        layout['xaxis'].update(title='')
        layout['xaxis'].update(showgrid=False)
        layout['xaxis'].update(zeroline=False)
        layout['xaxis'].update(showline=False)
        layout['xaxis'].update(showticklabels=False)
        layout['yaxis'].update(title='')
        layout['yaxis'].update(showgrid=False)
        layout['yaxis'].update(zeroline=False)
        layout['yaxis'].update(showline=False)
        layout['yaxis'].update(showticklabels=False)

        return layout
