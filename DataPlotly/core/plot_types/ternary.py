"""
Ternary plot factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import os
from plotly import graph_objs
from qgis.PyQt.QtGui import QIcon
from DataPlotly.core.plot_types.plot_type import PlotType


class TernaryFactory(PlotType):
    """
    Factory for ternary plots
    """

    @staticmethod
    def type_name():
        return 'ternary'

    @staticmethod
    def name():
        return PlotType.tr('Ternary Plot')

    @staticmethod
    def icon():
        return QIcon(os.path.join(os.path.dirname(__file__), 'icons/scatterternary.svg'))

    @staticmethod
    def create_trace(settings):
        # prepare the hover text to display if the additional combobox is empty or not
        # this setting is necessary to overwrite the standard hovering labels
        if not settings.additional_hover_text:
            text = [
                settings.properties['x_name'] + ': {}'.format(
                    settings.x[k]) + '<br>{}: {}'.format(
                    settings.properties['y_name'],
                    settings.y[k]) + '<br>{}: {}'.format(
                    settings.properties['z_name'], settings.z[k]) for k
                in
                range(len(settings.x))]
        else:
            text = [
                settings.properties['x_name'] + ': {}'.format(
                    settings.x[k]) + '<br>{}: {}'.format(
                    settings.properties['y_name'],
                    settings.y[k]) + '<br>{}: {}'.format(
                    settings.properties['z_name'],
                    settings.z[k]) + '<br>{}'.format(
                    settings.additional_hover_text[k]) for k in
                range(len(settings.x))]

        return [graph_objs.Scatterternary(
            a=settings.x,
            b=settings.y,
            c=settings.z,
            name='{} + {} + {}'.format(settings.properties['x_name'],
                                       settings.properties['y_name'],
                                       settings.properties['z_name']),
            hoverinfo='text',
            text=text,
            mode='markers',
            marker={
                'color': settings.data_defined_colors if settings.data_defined_colors else settings.properties['in_color'],
                'colorscale': settings.properties['color_scale'],
                'showscale': settings.properties['show_colorscale_legend'],
                'reversescale':settings.properties['invert_color_scale'],
                'colorbar': {
                    'len': 0.8
                },
                'size': settings.data_defined_marker_sizes if settings.data_defined_marker_sizes else settings.properties['marker_size'],
                'symbol': settings.properties['marker_symbol'],
                'line': {
                    'color': settings.data_defined_stroke_colors if settings.data_defined_stroke_colors else settings.properties['out_color'],
                    'width': settings.data_defined_stroke_widths if settings.data_defined_stroke_widths else settings.properties['marker_width']
                }
            },
            opacity=settings.properties['opacity']
        )]

    @staticmethod
    def create_layout(settings):
        layout = super(TernaryFactory, TernaryFactory).create_layout(settings)

        # flip the variables according to the box orientation
        if settings.properties['box_orientation'] == 'h':
            x_title = settings.data_defined_y_title if settings.data_defined_y_title != ''\
                else settings.layout['y_title']
            y_title = settings.data_defined_x_title if settings.data_defined_x_title != ''\
                else settings.layout['x_title']
        else:
            x_title = settings.data_defined_x_title if settings.data_defined_x_title != ''\
                else settings.layout['x_title']
            y_title = settings.data_defined_y_title if settings.data_defined_y_title != ''\
                else settings.layout['y_title']
        z_title = settings.data_defined_z_title if settings.data_defined_z_title != '' \
            else settings.layout['z_title']

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
        layout['ternary'] = {
            'sum': 100,
            'aaxis': {
                'title': x_title,
                'ticksuffix': '%',
            },
            'baxis': {
                'title': y_title,
                'ticksuffix': '%'
            },
            'caxis': {
                'title': z_title,
                'ticksuffix': '%'
            },
        }

        return layout
