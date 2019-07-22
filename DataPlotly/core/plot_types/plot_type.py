# -*- coding: utf-8 -*-
"""
Base class for plot type subclasses

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from plotly import graph_objs


class PlotType:
    """
    Base class for plot subclasses
    """

    @staticmethod
    def type_name():
        """
        Returns the unique type name for this plot type
        """
        return ''

    @staticmethod
    def create_trace(settings):  # pylint: disable=W0613
        """
        Returns a new trace using the specified plot settings
        """
        return None

    @staticmethod
    def create_layout(settings):
        """
        Returns a new layout using the specified plot settings
        """

        # flip the variables according to the box orientation
        if settings.properties['box_orientation'] == 'h':
            x_title = settings.layout['y_title']
            y_title = settings.layout['x_title']
        else:
            x_title = settings.layout['x_title']
            y_title = settings.layout['y_title']

        layout = graph_objs.Layout(
            showlegend=settings.layout['legend'],
            legend={'orientation': settings.layout['legend_orientation']},
            title=settings.layout['title'],
            xaxis={'title': x_title, 'autorange': settings.layout['x_inv']},
            yaxis={'title': y_title, 'autorange': settings.layout['y_inv']}
        )

        # update the x and y axis and add the linear and log only if the data are numeric
        # pass if field is empty
        try:
            if isinstance(settings.properties['x'][0], (int, float)):
                layout['xaxis'].update(type=settings.layout['x_type'])
        except:  # pylint:disable=bare-except  # noqa: F401
            pass
        try:
            if isinstance(settings.properties['y'][0], (int, float)):
                layout['yaxis'].update(type=settings.layout['y_type'])
        except:  # pylint:disable=bare-except  # noqa: F401
            pass

        return layout
