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


class FilledLineFactory(PlotType):
    """
    Factory for filled line scatter plots
    """

    @staticmethod
    def type_name():
        return 'filledline'

    @staticmethod
    def name():
        return PlotType.tr('Filled Line Plot')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/filledline.svg'))

    @staticmethod
    def create_trace(settings):
        # Only add filled band if both arrays present and lengths match the x axis
        if settings.y and settings.z and isinstance(settings.y, (list, tuple)) and isinstance(settings.z, (list, tuple)):
            if len(settings.x) == len(settings.y) == len(settings.z):
                return [graph_objs.Scatter(
                    x=settings.x+settings.x[::-1], #forward and backward in reverse
                    y=settings.y+settings.z[::-1], #upper line + lower line in reverse order
                    mode='none', # no lines
                    fill='toself',
                    fillcolor=settings.data_defined_colors if settings.data_defined_colors else settings.properties.get('fill_color'),
                    showlegend=True,
                    hoverinfo='skip',
                    ids=settings.feature_ids,
                    name=settings.data_defined_legend_title if settings.data_defined_legend_title != '' else settings.properties['name']
                )]
            else:
                # lengths mismatch -> skip fill to avoid runtime errors (you may want to log/warn)
                pass

    @staticmethod
    def create_layout(settings):
        layout = super(FilledLineFactory, FilledLineFactory).create_layout(settings)

        layout['xaxis'].update(rangeslider=settings.layout['range_slider'])

        return layout
