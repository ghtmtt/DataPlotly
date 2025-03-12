"""
Radar chart factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType
import plotly.colors as pc
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
class RadarChartFactory(PlotType):
    """
    Factory for radar charts
    """

    @staticmethod
    def type_name():
        return 'radar'

    @staticmethod
    def name():
        return PlotType.tr('Radar Plot')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/radar.svg'))

    @staticmethod
    def create_trace(settings):

        radar_plot_list = []
        x = settings.x[0]

        # Sample colors from the color scale based on the length of settings.y  
        colors_list = pc.sample_colorscale(settings.properties['color_scale'], np.linspace(0, 1, len(settings.y)))

        # List repeating the line type for each element in settings.y
        line_type_list = [settings.properties['line_dash']] * len(settings.y[0])

        # Add a black color and a threshold line to the data 
        if settings.properties['threshold'] is True :
            colors_list.append('#000000')
            settings.y.append([settings.properties['threshold_value']] * len(settings.y[0]))
            settings.y_radar_labels.append('threshold')
            line_type_list.append(settings.properties['line_type_threshold'])

        for (y, name, colors_list, line_type_list) in zip(settings.y, settings.y_radar_labels, colors_list, line_type_list):

            # If the marker type includes lines, close the plot by repeating the first (x, y) point  
            if settings.properties['marker'] in ('lines', 'lines+markers'):
                x= x+[x[0]]
                y = y+[y[0]]

            radar_plot_list.append(graph_objs.Scatterpolar(
                r=y,
                theta=x,
                mode=settings.properties['marker'],
                name=name,
                marker={
                    "color": colors_list,
                    "size": settings.data_defined_marker_sizes if settings.data_defined_marker_sizes else settings.properties['marker_size'],
                    "symbol": settings.properties['marker_symbol'],
                    "line": {
                        "color": settings.properties['out_color'],
                        "width": settings.properties['marker_width']
                    }
                },
                line={
                    "color": colors_list,
                    "width": settings.data_defined_stroke_widths if settings.data_defined_stroke_widths else settings.properties['marker_width'],
                    "dash": line_type_list 
                    
                },
                opacity=settings.properties['opacity'],
                fill="toself" if settings.properties['fill'] else None
                ))
            
        return radar_plot_list
    
    @staticmethod
    def create_layout(settings):
        layout = super(RadarChartFactory, RadarChartFactory).create_layout(settings)

        layout['polar'] = settings.layout['radar']

        return layout
