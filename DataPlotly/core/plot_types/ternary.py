# -*- coding: utf-8 -*-
"""
Ternary plot factory

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from plotly import graph_objs
from DataPlotly.core.plot_types.plot_type import PlotType


class TernaryFactory(PlotType):
    """
    Factory for ternary plots
    """

    @staticmethod
    def create_trace(settings):
        # prepare the hover text to display if the additional combobox is empty or not
        # this setting is necessary to overwrite the standard hovering labels
        if not settings.properties['additional_hover_text']:
            text = [
                settings.properties['x_name'] + ': {}'.format(
                    settings.properties['x'][k]) + '<br>{}: {}'.format(
                    settings.properties['y_name'],
                    settings.properties['y'][k]) + '<br>{}: {}'.format(
                    settings.properties['z_name'], settings.properties['z'][k]) for k
                in
                range(len(settings.properties['x']))]
        else:
            text = [
                settings.properties['x_name'] + ': {}'.format(
                    settings.properties['x'][k]) + '<br>{}: {}'.format(
                    settings.properties['y_name'],
                    settings.properties['y'][k]) + '<br>{}: {}'.format(
                    settings.properties['z_name'],
                    settings.properties['z'][k]) + '<br>{}'.format(
                    settings.properties['additional_hover_text'][k]) for k in
                range(len(settings.properties['x']))]

        return [graph_objs.Scatterternary(
            a=settings.properties['x'],
            b=settings.properties['y'],
            c=settings.properties['z'],
            name='{} + {} + {}'.format(settings.properties['x_name'],
                                       settings.properties['y_name'],
                                       settings.properties['z_name']),
            hoverinfo='text',
            text=text,
            mode='markers',
            marker=dict(
                color=settings.properties['in_color'],
                colorscale=settings.properties['colorscale_in'],
                showscale=settings.properties['show_colorscale_legend'],
                reversescale=settings.properties['invert_color_scale'],
                colorbar=dict(
                    len=0.8
                ),
                size=settings.properties['marker_size'],
                symbol=settings.properties['marker_symbol'],
                line=dict(
                    color=settings.properties['out_color'],
                    width=settings.properties['marker_width']
                )
            ),
            opacity=settings.properties['opacity']
        )]

    @staticmethod
    def create_layout(settings):
        layout = super(TernaryFactory, TernaryFactory).create_layout(settings)

        # flip the variables according to the box orientation
        if settings.properties['box_orientation'] == 'h':
            x_title = settings.layout['y_title']
            y_title = settings.layout['x_title']
        else:
            x_title = settings.layout['x_title']
            y_title = settings.layout['y_title']

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
        layout['ternary'] = dict(
            sum=100,
            aaxis=dict(
                title=x_title,
                ticksuffix='%',
            ),
            baxis=dict(
                title=y_title,
                ticksuffix='%'
            ),
            caxis=dict(
                title=settings.layout['z_title'],
                ticksuffix='%'
            ),
        )

        return layout
