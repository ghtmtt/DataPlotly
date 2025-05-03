"""
Base class for plot type subclasses

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from plotly import graph_objs
from qgis.PyQt.QtCore import QCoreApplication


def from_qfont_to_plotly(style, color):
    """
    Converts a QFont to a Plotly basic font settings dictionary
    """
    if style is not None and color is not None:
        return {
            "size": style.pointSize() or 10,
            "color": color.name() or "black",
            "family": style.family() or "Arial",
        }
    return {
        "size": 10,
        "color": "black",
        "family": "Arial",
    }


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
    def name():
        """
        Returns the friendly translated name for the plot type
        """
        return ''

    @staticmethod
    def icon():
        """
        Returns a path to an icon for this chart type
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
            y_title = settings.data_defined_y_title if settings.data_defined_y_title != ''\
                else settings.layout['y_title']
            x_title = settings.data_defined_x_title if settings.data_defined_x_title != ''\
                else settings.layout['x_title']
        else:
            x_title = settings.data_defined_x_title if settings.data_defined_x_title != ''\
                else settings.layout['x_title']
            y_title = settings.data_defined_y_title if settings.data_defined_y_title != ''\
                else settings.layout['y_title']

        range_x = None
        if settings.layout.get('x_min', None) is not None and settings.layout.get('x_max', None) is not None:
            range_x = [
                settings.data_defined_x_min if settings.data_defined_x_min else settings.layout['x_min'],
                settings.data_defined_x_max if settings.data_defined_x_max else settings.layout['x_max']
            ]
        range_y = None
        if settings.layout.get('y_min', None) is not None and settings.layout.get('y_max', None) is not None:
            range_y = [
                settings.data_defined_y_min if settings.data_defined_y_min else settings.layout['y_min'],
                settings.data_defined_y_max if settings.data_defined_y_max else settings.layout['y_max']
            ]

        bg_color = settings.layout.get('bg_color', 'rgb(255,255,255)')

        # add font size parameter from the title setting
        title = settings.data_defined_title if settings.data_defined_title else settings.layout['title']
        if isinstance(title, str):
            title = {"text": title}
        title["font"] = {
            "size": settings.layout.get('font_title_size', 10),
            "color": settings.layout.get('font_title_color', "#000"),
            "family": settings.layout.get('font_title_family', "Arial"),
        }

        layout = graph_objs.Layout(
            showlegend=settings.layout['legend'],
            legend={'orientation': settings.layout['legend_orientation']},
            title=title,
            xaxis={
                'title': {
                    'text': x_title,
                    'font': {
                        "size": settings.layout.get('font_xlabel_size', 10),
                        "color": settings.layout.get('font_xlabel_color', "#000"),
                        "family": settings.layout.get('font_xlabel_family', "Arial"),
                },
                },
                'autorange': settings.layout['x_inv'],
                'range': range_x,
                'tickfont': {
                    "size": settings.layout.get('font_xticks_size', 10),
                    "color": settings.layout.get('font_xticks_color', "#000"),
                    "family": settings.layout.get('font_xticks_family', "Arial"),
                },
                'gridcolor': settings.layout.get('gridcolor', '#bdbfc0')
            },
            yaxis={
                'title': {
                    'text': y_title,
                    'font': {
                        "size": settings.layout.get('font_ylabel_size', 10),
                        "color": settings.layout.get('font_ylabel_color', "#000"),
                        "family": settings.layout.get('font_ylabel_family', "Arial"),
                    },
                },
                'autorange': settings.layout['y_inv'],
                'range': range_y,
                'tickfont': {
                    "size": settings.layout.get('font_yticks_size', 10),
                    "color": settings.layout.get('font_yticks_color', "#000"),
                    "family": settings.layout.get('font_yticks_family', "Arial"),
                },
                'gridcolor': settings.layout.get('gridcolor', '#bdbfc0')
            },
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color
        )

        # update the x and y axis and add the linear and log only if the data are numeric
        # pass if field is empty
        try:
            if isinstance(settings.x[0], (int, float)):
                layout['xaxis'].update(type=settings.layout['x_type'])
        except:  # pylint:disable=bare-except  # noqa: F401
            pass
        try:
            if isinstance(settings.y[0], (int, float)):
                layout['yaxis'].update(type=settings.layout['y_type'])
        except:  # pylint:disable=bare-except  # noqa: F401
            pass

        return layout

    @staticmethod
    def tr(string, context=''):
        """
        Translates a string
        """
        if context == '':
            context = 'Types'
        return QCoreApplication.translate(context, string)
