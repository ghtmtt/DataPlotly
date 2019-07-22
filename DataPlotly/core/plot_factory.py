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
import platform
import re
import plotly
import plotly.graph_objs as go
from plotly import tools
from DataPlotly.core.plot_settings import PlotSettings


class PlotFactory:  # pylint:disable=too-many-instance-attributes
    """
    Plot factory which creates Plotly Plot objects

    Console usage:
    # create the object
    p = Plot(plot_type, plot_properties, layout_properties)
    # where:
        # plot_type (string): 'scatter'
        # plot_properties (dictionary): {'x':[1,2,3], 'marker_width': 10}
        # layout_properties (dictionary): {'legend'; True, 'title': 'Plot Title'}

    The object created is ready to be elaborated by the other methods
    """

    # create fixed class variables as paths for local javascript files
    POLY_FILL_PATH = os.path.join(os.path.dirname(__file__), 'jsscripts/polyfill.min.js')
    PLOTLY_PATH = os.path.join(os.path.dirname(__file__), 'jsscripts/plotly-1.34.0.min.js')

    if platform.system() == 'Windows':
        POLY_FILL_PATH = 'file:///{}'.format(POLY_FILL_PATH)
        PLOTLY_PATH = 'file:///{}'.format(PLOTLY_PATH)

    def __init__(self, settings: PlotSettings = None):
        if settings is None:
            settings = PlotSettings('scatter')

        self.settings = settings
        self.trace = None
        self.layout = None
        self.raw_plot = None
        self.plot_path = None

    def build_trace(self):  # pylint:disable=too-many-branches
        """
        Builds the final trace calling the go.xxx plotly method
        this method here is the one performing the real job

        From the initial object created (e.g. p = Plot(plot_type, plot_properties,
        layout_properties)) this methods checks the plot_type and elaborates the
        plot_properties dictionary passed

        Console usage:
        # create the initial object
        p = Plot(plot_type, plot_properties, layout_properties)
        # call the method
        p.buildTrace()

        Returns the final Plot Trace (final Plot object, AKA go.xxx plot type)
        """

        if self.settings.plot_type == 'scatter':

            self.trace = [go.Scatter(
                x=self.settings.properties['x'],
                y=self.settings.properties['y'],
                mode=self.settings.properties['marker'],
                name=self.settings.properties['name'],
                ids=self.settings.properties['featureIds'],
                customdata=self.settings.properties['custom'],
                text=self.settings.properties['additional_hover_text'],
                hoverinfo=self.settings.properties['hover_text'],
                marker={'color': self.settings.properties['in_color'],
                        'colorscale': self.settings.properties['colorscale_in'],
                        'showscale': self.settings.properties['show_colorscale_legend'],
                        'reversescale': self.settings.properties['invert_color_scale'],
                        'colorbar': {
                            'len': 0.8},
                        'size': self.settings.properties['marker_size'],
                        'symbol': self.settings.properties['marker_symbol'],
                        'line': {'color': self.settings.properties['out_color'],
                                 'width': self.settings.properties['marker_width']}
                        },
                line={'width': self.settings.properties['marker_width'],
                      'dash': self.settings.properties['line_dash']},
                opacity=self.settings.properties['opacity']
            )]

        elif self.settings.plot_type == 'box':

            # flip the variables according to the box orientation
            if self.settings.properties['box_orientation'] == 'h':
                self.settings.properties['x'], self.settings.properties['y'] = \
                    self.settings.properties['y'], self.settings.properties[
                        'x']

            self.trace = [go.Box(
                x=self.settings.properties['x'],
                y=self.settings.properties['y'],
                name=self.settings.properties['name'],
                customdata=self.settings.properties['custom'],
                boxmean=self.settings.properties['box_stat'],
                orientation=self.settings.properties['box_orientation'],
                boxpoints=self.settings.properties['box_outliers'],
                fillcolor=self.settings.properties['in_color'],
                line={'color': self.settings.properties['out_color'],
                      'width': self.settings.properties['marker_width']},
                opacity=self.settings.properties['opacity']
            )]

        elif self.settings.plot_type == 'bar':

            if self.settings.properties['box_orientation'] == 'h':
                self.settings.properties['x'], self.settings.properties['y'] = \
                    self.settings.properties['y'], self.settings.properties[
                        'x']

            self.trace = [go.Bar(
                x=self.settings.properties['x'],
                y=self.settings.properties['y'],
                name=self.settings.properties['name'],
                ids=self.settings.properties['featureBox'],
                customdata=self.settings.properties['custom'],
                orientation=self.settings.properties['box_orientation'],
                marker={'color': self.settings.properties['in_color'],
                        'colorscale': self.settings.properties['colorscale_in'],
                        'showscale': self.settings.properties['show_colorscale_legend'],
                        'reversescale': self.settings.properties['invert_color_scale'],
                        'colorbar': {
                            'len': 0.8
                        },
                        'line': {
                            'color': self.settings.properties['out_color'],
                            'width': self.settings.properties['marker_width']}
                        },
                opacity=self.settings.properties['opacity']
            )]

        elif self.settings.plot_type == 'histogram':

            self.trace = [go.Histogram(
                x=self.settings.properties['x'],
                y=self.settings.properties['x'],
                name=self.settings.properties['name'],
                orientation=self.settings.properties['box_orientation'],
                nbinsx=self.settings.properties['bins'],
                nbinsy=self.settings.properties['bins'],
                marker=dict(
                    color=self.settings.properties['in_color'],
                    line=dict(
                        color=self.settings.properties['out_color'],
                        width=self.settings.properties['marker_width']
                    )
                ),
                histnorm=self.settings.properties['normalization'],
                opacity=self.settings.properties['opacity'],
                cumulative=dict(
                    enabled=self.settings.properties['cumulative'],
                    direction=self.settings.properties['invert_hist']
                )
            )]

        elif self.settings.plot_type == 'pie':

            self.trace = [go.Pie(
                labels=self.settings.properties['x'],
                values=self.settings.properties['y'],
                name=self.settings.properties['custom'][0],
            )]

        elif self.settings.plot_type == '2dhistogram':

            self.trace = [go.Histogram2d(
                x=self.settings.properties['x'],
                y=self.settings.properties['y'],
                colorscale=self.settings.properties['color_scale']
            )]

        elif self.settings.plot_type == 'polar':

            self.trace = [go.Scatterpolar(
                r=self.settings.properties['y'],
                theta=self.settings.properties['x'],
                mode=self.settings.properties['marker'],
                name=self.settings.properties['y_name'],
                marker=dict(
                    color=self.settings.properties['in_color'],
                    size=self.settings.properties['marker_size'],
                    symbol=self.settings.properties['marker_symbol'],
                    line=dict(
                        color=self.settings.properties['out_color'],
                        width=self.settings.properties['marker_width']
                    )
                ),
                line=dict(
                    color=self.settings.properties['in_color'],
                    width=self.settings.properties['marker_width'],
                    dash=self.settings.properties['line_dash']
                ),
                opacity=self.settings.properties['opacity'],
            )]

        elif self.settings.plot_type == 'ternary':

            # prepare the hover text to display if the additional combobox is empty or not
            # this setting is necessary to overwrite the standard hovering labels
            if not self.settings.properties['additional_hover_text']:
                text = [
                    self.settings.properties['x_name'] + ': {}'.format(
                        self.settings.properties['x'][k]) + '<br>{}: {}'.format(
                        self.settings.properties['y_name'],
                        self.settings.properties['y'][k]) + '<br>{}: {}'.format(
                        self.settings.properties['z_name'], self.settings.properties['z'][k]) for k
                    in
                    range(len(self.settings.properties['x']))]
            else:
                text = [
                    self.settings.properties['x_name'] + ': {}'.format(
                        self.settings.properties['x'][k]) + '<br>{}: {}'.format(
                        self.settings.properties['y_name'],
                        self.settings.properties['y'][k]) + '<br>{}: {}'.format(
                        self.settings.properties['z_name'],
                        self.settings.properties['z'][k]) + '<br>{}'.format(
                        self.settings.properties['additional_hover_text'][k]) for k in
                    range(len(self.settings.properties['x']))]

            self.trace = [go.Scatterternary(
                a=self.settings.properties['x'],
                b=self.settings.properties['y'],
                c=self.settings.properties['z'],
                name='{} + {} + {}'.format(self.settings.properties['x_name'],
                                           self.settings.properties['y_name'],
                                           self.settings.properties['z_name']),
                hoverinfo='text',
                text=text,
                mode='markers',
                marker=dict(
                    color=self.settings.properties['in_color'],
                    colorscale=self.settings.properties['colorscale_in'],
                    showscale=self.settings.properties['show_colorscale_legend'],
                    reversescale=self.settings.properties['invert_color_scale'],
                    colorbar=dict(
                        len=0.8
                    ),
                    size=self.settings.properties['marker_size'],
                    symbol=self.settings.properties['marker_symbol'],
                    line=dict(
                        color=self.settings.properties['out_color'],
                        width=self.settings.properties['marker_width']
                    )
                ),
                opacity=self.settings.properties['opacity']
            )]

        elif self.settings.plot_type == 'contour':

            self.trace = [go.Contour(
                z=[self.settings.properties['x'], self.settings.properties['y']],
                contours=dict(
                    coloring=self.settings.properties['cont_type'],
                    showlines=self.settings.properties['show_lines']
                ),
                colorscale=self.settings.properties['color_scale'],
                opacity=self.settings.properties['opacity']
            )]

        elif self.settings.plot_type == 'violin':

            # flip the variables according to the box orientation
            if self.settings.properties['box_orientation'] == 'h':
                self.settings.properties['x'], self.settings.properties['y'] = \
                    self.settings.properties['y'], self.settings.properties[
                        'x']

            self.trace = [go.Violin(
                x=self.settings.properties['x'],
                y=self.settings.properties['y'],
                name=self.settings.properties['name'],
                customdata=self.settings.properties['custom'],
                orientation=self.settings.properties['box_orientation'],
                points=self.settings.properties['box_outliers'],
                fillcolor=self.settings.properties['in_color'],
                line=dict(
                    color=self.settings.properties['out_color'],
                    width=self.settings.properties['marker_width']
                ),
                opacity=self.settings.properties['opacity'],
                meanline=dict(
                    visible=self.settings.properties['show_mean_line']
                ),
                side=self.settings.properties['violin_side']
            )]

        return self.trace

    def build_layout(self):
        """
        Builds the final layout calling the go.Layout plotly method

        From the initial object created (e.g. p = Plot(plot_type, plot_properties,
        layout_properties)) this methods checks the plot_type and elaborates the
        layout_properties dictionary passed

        Console usage:
        # create the initial object
        p = Plot(plot_type, plot_properties, layout_properties)
        # call the method
        p.buildLayout()

        Returns the final Plot Layout (final Layout object, AKA go.Layout)
        """

        # flip the variables according to the box orientation
        if self.settings.properties['box_orientation'] == 'h':
            self.settings.layout['x_title'], self.settings.layout['y_title'] = \
                self.settings.layout['y_title'], self.settings.layout[
                    'x_title']

        self.layout = go.Layout(
            showlegend=self.settings.layout['legend'],
            legend=dict(
                orientation=self.settings.layout['legend_orientation']
            ),
            title=self.settings.layout['title'],
            xaxis=dict(
                title=self.settings.layout['x_title'],
                autorange=self.settings.layout['x_inv']
            ),
            yaxis=dict(
                title=self.settings.layout['y_title'],
                autorange=self.settings.layout['y_inv']
            )
        )

        # update the x and y axis and add the linear and log only if the data are numeric
        # pass if field is empty
        try:
            if isinstance(self.settings.properties['x'][0], (int, float)):
                self.layout['xaxis'].update(type=self.settings.layout['x_type'])
        except:  # pylint:disable=bare-except  # noqa: F401
            pass
        try:
            if isinstance(self.settings.properties['y'][0], (int, float)):
                self.layout['yaxis'].update(type=self.settings.layout['y_type'])
        except:  # pylint:disable=bare-except  # noqa: F401
            pass

        # update layout properties depending on the plot type
        if self.settings.plot_type == 'scatter':
            self.layout['xaxis'].update(rangeslider=self.settings.layout['range_slider'])

        elif self.settings.plot_type == 'bar':
            self.layout['barmode'] = self.settings.layout['bar_mode']

        elif self.settings.plot_type == 'polar':
            self.layout['polar'] = self.settings.layout['polar']

        elif self.settings.plot_type == 'histogram':
            self.layout['barmode'] = self.settings.layout['bar_mode']
            self.layout['bargroupgap'] = self.settings.layout['bargaps']

        elif self.settings.plot_type == 'pie':
            self.layout['xaxis'].update(title='')
            self.layout['xaxis'].update(showgrid=False)
            self.layout['xaxis'].update(zeroline=False)
            self.layout['xaxis'].update(showline=False)
            self.layout['xaxis'].update(showticklabels=False)
            self.layout['yaxis'].update(title='')
            self.layout['yaxis'].update(showgrid=False)
            self.layout['yaxis'].update(zeroline=False)
            self.layout['yaxis'].update(showline=False)
            self.layout['yaxis'].update(showticklabels=False)

        elif self.settings.plot_type == 'ternary':
            self.layout['xaxis'].update(title='')
            self.layout['xaxis'].update(showgrid=False)
            self.layout['xaxis'].update(zeroline=False)
            self.layout['xaxis'].update(showline=False)
            self.layout['xaxis'].update(showticklabels=False)
            self.layout['yaxis'].update(title='')
            self.layout['yaxis'].update(showgrid=False)
            self.layout['yaxis'].update(zeroline=False)
            self.layout['yaxis'].update(showline=False)
            self.layout['yaxis'].update(showticklabels=False)
            self.layout['ternary'] = dict(
                sum=100,
                aaxis=dict(
                    title=self.settings.layout['x_title'],
                    ticksuffix='%',
                ),
                baxis=dict(
                    title=self.settings.layout['y_title'],
                    ticksuffix='%'
                ),
                caxis=dict(
                    title=self.settings.layout['z_title'],
                    ticksuffix='%'
                ),
            )

        return self.layout

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

    def build_figure(self):
        """
        draw the final plot (single plot)

        call the go.Figure plotly method and build the figure object adjust the
        html file and add some line (including the js_string for the interaction)
        save the html plot file in a temporary directory and return the path
        that can be loaded in the QWebView

        This method is directly usable after the plot object has been created and
        the 2 methods (buildTrace and buildLayout) have been called

        Returns the final html path containing the plot

        Console usage:
        # create the initial object
        p = Plot(plot_type, plot_properties, layout_properties)
        # call the methods to create the Trace and the Layout
        p.buildTrace()
        p.buildLayout()

        # finally create the Figure
        fig = p.buildFigure()
        """

        fig = go.Figure(data=self.trace, layout=self.layout)

        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}">' \
                        '</script><script src="{}"></script></head>'.format(
                            self.POLY_FILL_PATH, self.PLOTLY_PATH)
        # set some configurations
        config = {'scrollZoom': True, 'editable': True}
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

    def build_figures(self, plot_type, ptrace):
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

        Returns the final html path containing the plot with the js_string for
        the interaction

        Console usage:
        # create the initial object
        p = Plot(plot_type, plot_properties, layout_properties)
        # call the methods to create the Trace and the Layout
        p.buildTrace()
        p.buildLayout()

        # finally create the Figure
        fig = p.buildFigures(plot_type, ptrace)
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
        match = re.search(r'Plotly.newPlot\("([^"]+)', self.raw_plot)
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

        Returns the final html path containing the plot with the js_string for
        the interaction

        Console usage:
        # create the initial object
        p = Plot(plot_type, plot_properties, layout_properties)
        # call the methods to create the Trace and the Layout
        p.buildTrace()
        p.buildLayout()

        # finally create the Figure
        fig = p.buildSubPlots('row', 1, gr, pl, tt)
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
