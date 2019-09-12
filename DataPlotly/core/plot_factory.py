# -*- coding: utf-8 -*-
"""
Plot creation

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

import tempfile
import os
import re
import plotly
import plotly.graph_objs as go
from plotly import tools

from qgis.PyQt.QtCore import QUrl
from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.core.plot_types.plot_type import PlotType
from DataPlotly.core.plot_types import *  # pylint: disable=W0401,W0614


class PlotFactory:  # pylint:disable=too-many-instance-attributes
    """
    Plot factory which creates Plotly Plot objects

    Console usage:

    .. code-block:: python
        # create (and customize) plot settings, where
        # plot_type (string): 'scatter'
        # plot_properties (dictionary): {'x':[1,2,3], 'marker_width': 10}
        # layout_properties (dictionary): {'legend'; True, 'title': 'Plot Title'}
        settings = PlotSettings(plot_type, plot_properties, layout_properties)
        # create the factory, which will create plots using the specified settings
        factory = PlotFactory(settings)
        # Use the factory to build a plot
        output_file_path = factory.build_figure()
    """

    # create fixed class variables as paths for local javascript files
    POLY_FILL_PATH = QUrl.fromLocalFile(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'jsscripts/polyfill.min.js'))).toString()
    PLOTLY_PATH = QUrl.fromLocalFile(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'jsscripts/plotly-1.34.0.min.js'))).toString()

    PLOT_TYPES = {
        t.type_name(): t for t in PlotType.__subclasses__()
    }

    def __init__(self, settings: PlotSettings = None):
        if settings is None:
            settings = PlotSettings('scatter')

        self.settings = settings
        self.raw_plot = None
        self.plot_path = None

        self.trace = self._build_trace()
        self.layout = self._build_layout()

    def _build_trace(self):
        """
        Builds the final trace calling the go.xxx plotly method
        this method here is the one performing the real job

        From the initial object created (e.g. p = Plot(plot_type, plot_properties,
        layout_properties)) this methods checks the plot_type and elaborates the
        plot_properties dictionary passed

        :return: the final Plot Trace (final Plot object, AKA go.xxx plot type)
        """
        assert self.settings.plot_type in PlotFactory.PLOT_TYPES

        return PlotFactory.PLOT_TYPES[self.settings.plot_type].create_trace(self.settings)

    def _build_layout(self):
        """
        Builds the final layout calling the go.Layout plotly method

        From the initial object created (e.g. p = Plot(plot_type, plot_properties,
        layout_properties)) this methods checks the plot_type and elaborates the
        layout_properties dictionary passed

        :return: the final Plot Layout (final Layout object, AKA go.Layout)
        """
        assert self.settings.plot_type in PlotFactory.PLOT_TYPES

        return PlotFactory.PLOT_TYPES[self.settings.plot_type].create_layout(self.settings)

    @staticmethod
    def js_callback(_):
        """
        Returns a string that is added to the end of the plot. This string is
        necessary for the interaction between plot and map objects

        WARNING! The string ReplaceTheDiv is a default string that will be
        replaced in a second moment
        """

        js_str = '''
        <script>
        // additional js function to select and click on the data
        // returns the ids of the selected/clicked feature

        var plotly_div = document.getElementById('ReplaceTheDiv')
        var plotly_data = plotly_div.data

        // selecting function
        plotly_div.on('plotly_selected', function(data){
        var dds = {};
        dds["mode"] = 'selection'
        dds["type"] = data.points[0].data.type

        featureIds = [];
        featureIdsTernary = [];

        data.points.forEach(function(pt){
        featureIds.push(parseInt(pt.id))
        featureIdsTernary.push(parseInt(pt.pointNumber))
        dds["id"] = featureIds
        dds["tid"] = featureIdsTernary
            })
        //console.log(dds)
        window.status = JSON.stringify(dds)
        })

        // clicking function
        plotly_div.on('plotly_click', function(data){
        var featureIds = [];
        var dd = {};
        dd["fidd"] = data.points[0].id
        dd["mode"] = 'clicking'

        // loop and create dictionary depending on plot type
        for(var i=0; i < data.points.length; i++){

        // scatter plot
        if(data.points[i].data.type == 'scatter'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type

            data.points.forEach(function(pt){
            dd["fid"] = pt.id
            })
        }

        // pie

        else if(data.points[i].data.type == 'pie'){
          dd["type"] = data.points[i].data.type
          dd["label"] = data.points[i].label
          dd["field"] = data.points[i].data.name
          console.log(data.points[i].label)
          console.log(data.points[i])
        }

        // histogram
        else if(data.points[i].data.type == 'histogram'){
            dd["type"] = data.points[i].data.type
            dd["uid"] = data.points[i].data.uid
            dd["field"] = data.points[i].data.name

            // correct axis orientation
            if(data.points[i].data.orientation == 'v'){
                dd["id"] = data.points[i].x
                dd["bin_step"] = data.points[i].data.xbins.size
            }
            else {
                dd["id"] = data.points[i].y
                dd["bin_step"] = data.points[i].data.ybins.size
            }
        }

        // box plot
        else if(data.points[i].data.type == 'box'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type
            dd["field"] = data.points[i].data.customdata[0]

                // correct axis orientation
                if(data.points[i].data.orientation == 'v'){
                    dd["id"] = data.points[i].x
                }
                else {
                    dd["id"] = data.points[i].y
                }
            }

        // violin plot
        else if(data.points[i].data.type == 'violin'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type
            dd["field"] = data.points[i].data.customdata[0]

                // correct axis orientation (for violin is viceversa)
                if(data.points[i].data.orientation == 'v'){
                    dd["id"] = data.points[i].x
                }
                else {
                    dd["id"] = data.points[i].y
                }
            }

        // bar plot
        else if(data.points[i].data.type == 'bar'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type
            dd["field"] = data.points[i].data.customdata[0]

                // correct axis orientation
                if(data.points[i].data.orientation == 'v'){
                    dd["id"] = data.points[i].x
                }
                else {
                    dd["id"] = data.points[i].y
                }
            }

        // ternary
        else if(data.points[i].data.type == 'scatterternary'){
            dd["uid"] = data.points[i].data.uid
            dd["type"] = data.points[i].data.type
            dd["field"] = data.points[i].data.customdata
            dd["fid"] = data.points[i].pointNumber
            }

            }
        window.status = JSON.stringify(dd)
        });
        </script>'''

        return js_str

    def build_html(self, config) -> str:
        """
        Creates the HTML for the plot

        Calls the go.Figure plotly method and builds the figure object adjust the
        html file and add some line (including the js_string for the interaction)
        save the html plot file in a temporary directory and return the path
        that can be loaded in the QWebView

        This method is directly usable after the plot object has been created and
        the 2 methods (buildTrace and buildLayout) have been called

        params:
            config (dict): config = {'scrollZoom': True, 'editable': False}

        config argument is necessary to specify which buttons should appear in
        the plotly toolbar, if the user can edit the plot inline, etc.
        With this parameter is possible to hide the toolbar only in print layouts
        and not in the normal plot canvas.

        :return: the final html content representing the plot

        Console usage:
        .. code-block:: python
            # create the initial object
            settings = PlotSettings(plot_type, plot_properties, layout_properties)
            factory = PlotFactory(settings)
            # finally create the Figure
            html_content  = factory.build_html()
        """
        fig = go.Figure(data=self.trace, layout=self.layout)

        # first lines of additional html with the link to the local javascript
        raw_plot = '<head><meta charset="utf-8" /><script src="{}">' \
                        '</script><script src="{}"></script></head>'.format(
            self.POLY_FILL_PATH, self.PLOTLY_PATH)
        # set some configurations
        # call the plot method without all the javascript code
        raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False, show_link=False,
                                             config=config)
        # insert callback for javascript events
        raw_plot += self.js_callback(raw_plot)

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search(r'Plotly.newPlot\(\s*[\'"](.+?)[\'"]', raw_plot)
        substr = match.group(1)
        raw_plot = raw_plot.replace('ReplaceTheDiv', substr)
        return raw_plot

    def build_figure(self) -> str:
        """
        Creates the final plot (single plot)

        Calls the go.Figure plotly method and builds the figure object adjust the
        html file and add some line (including the js_string for the interaction)
        save the html plot file in a temporary directory and return the path
        that can be loaded in the QWebView

        This method is directly usable after the plot object has been created and
        the 2 methods (buildTrace and buildLayout) have been called

        :return: the final html path containing the plot

        Console usage:
        .. code-block:: python
            # create the initial object
            settings = PlotSettings(plot_type, plot_properties, layout_properties)
            factory = PlotFactory(settings)
            # finally create the Figure
            path_to_output = factory.build_figure()
        """

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        config = {
            'scrollZoom': True,
            'editable': True,
            'modeBarButtonsToRemove': ['toImage', 'sendDataToCloud', 'editInChartStudio']
        }

        with open(self.plot_path, "w") as f:
            f.write(self.build_html(config))

        return self.plot_path

    def build_figures(self, plot_type, ptrace) -> str:
        """
        Overlaps plots on the same map canvas

        params:
            plot_type (string): 'scatter'
            ptrace (list of Plot Traces): list of all the different Plot Traces

        plot_type argument in necessary for Bar and Histogram plots when the
        options stack is chosen.
        In this case the layouts of the firsts plot are deleted and only the last
        one is taken into account (so to have the stack option).

        self.layout is DELETED, so the final layout is taken from the LAST plot
        configuration added

        :return: the final html path containing the plot with the js_string for
        the interaction

        Console usage:
        .. code-block:: python
            # create the initial object
            settings = PlotSettings(plot_type, plot_properties, layout_properties)
            factory = PlotFactory(settings)
            # finally create the Figures
            path_to_output = factory.build_figures(plot_type, ptrace)
        """

        # assign the variables from the kwargs arguments
        # plot_type = kwargs['plot_type']
        # ptrace = kwargs['pl']

        # check if the plot type and render the correct figure
        if plot_type == 'bar' or 'histogram':
            del self.layout
            self.layout = go.Layout(
                barmode=self.settings.layout['bar_mode']
            )
            figures = go.Figure(data=ptrace, layout=self.layout)

        else:
            figures = go.Figure(data=ptrace, layout=self.layout)

        # set some configurations
        config = {'scrollZoom': True, 'editable': True}
        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}">' \
                        '</script><script src="{}"></script></head>'.format(
            self.POLY_FILL_PATH, self.PLOTLY_PATH)
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(figures, output_type='div', include_plotlyjs=False, show_link=False,
                                             config=config)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search(r'Plotly.newPlot\(\s*[\'"](.+?)[\'"]', self.raw_plot)
        substr = match.group(1)
        self.raw_plot = self.raw_plot.replace('ReplaceTheDiv', substr)

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        with open(self.plot_path, "w") as f:
            f.write(self.raw_plot)

        return self.plot_path

    def build_sub_plots(self, grid, row, column, ptrace):  # pylint:disable=too-many-arguments
        """
        Draws plot in different plot canvases (not overlapping)

        params:
            grid (string): 'row' or 'col'. Plot are created in rows or columns
            row (int): number of rows (if row is selected)
            column (int): number of columns (if column is selected)
            ptrace (list of Plot Traces): list of all the different Plot Traces

        :return: the final html path containing the plot with the js_string for
        the interaction

        Console usage:
        .. code-block:: python
            # create the initial object
            settings = PlotSettings(plot_type, plot_properties, layout_properties)
            factory = PlotFactory(settings)
            # finally create the Figures
            path_to_output = factory.build_sub_plots('row', 1, gr, pl, tt)
        """

        if grid == 'row':

            fig = tools.make_subplots(rows=row, cols=column)

            for i, itm in enumerate(ptrace):
                fig.append_trace(itm, row, i + 1)

        elif grid == 'col':

            fig = tools.make_subplots(rows=row, cols=column)

            for i, itm in enumerate(ptrace):
                fig.append_trace(itm, i + 1, column)

        # set some configurations
        config = {'scrollZoom': True, 'editable': True}
        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}"></script>' \
                        '<script src="{}"></script></head>'.format(
            self.POLY_FILL_PATH, self.PLOTLY_PATH)
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False, show_link=False,
                                             config=config)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search(r'Plotly.newPlot\("([^"]+)', self.raw_plot)
        substr = match.group(1)
        self.raw_plot = self.raw_plot.replace('ReplaceTheDiv', substr)

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        with open(self.plot_path, "w") as f:
            f.write(self.raw_plot)

        return self.plot_path
