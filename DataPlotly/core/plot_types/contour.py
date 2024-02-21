"""
Contour chart factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType


class ContourFactory(PlotType):
    """
    Factory for contour charts
    """

    @staticmethod
    def type_name():
        return 'contour'

    @staticmethod
    def name():
        return PlotType.tr('Contour Plot')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/contour.svg'))

    @staticmethod
    def create_trace(settings):
        return [graph_objs.Contour(
                z=[settings.x, settings.y],
                contours={
                    'coloring': settings.properties['cont_type'],
                    'showlines': settings.properties['show_lines']
                },
                colorscale=settings.properties['color_scale'],
                opacity=settings.properties['opacity']
                )]
