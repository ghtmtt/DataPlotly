# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotlyDialog
                                 A QGIS plugin
 D3 Plots for QGIS
                             -------------------
        begin                : 2017-03-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by matteo ghetta
        email                : matteo.ghetta@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import plotly
import plotly.graph_objs as go
from plotly import tools
import tempfile
import os
import platform
import re


class Plot(object):
    '''
    Plot Class that creates the initial Plot object

    Console usage:
    # create the object
    p = Plot(plot_type, plot_properties, layout_properties)
    # where:
        # plot_type (string): 'scatter'
        # plot_properties (dictionary): {'x':[1,2,3], 'marker_width': 10}
        # layout_properties (dictionary): {'legend'; True, 'title': 'Plot Title'}

    The object created is ready to be elaborated by the other methods
    '''

    # create fixed class variables as paths for local javascript files
    if platform.system() == 'Windows':
        polyfillpath = 'file:///'
        plotlypath = 'file:///'
        polyfillpath += os.path.join(os.path.dirname(__file__), 'jsscripts/polyfill.min.js')
        plotlypath += os.path.join(os.path.dirname(__file__), 'jsscripts/plotly-1.34.0.min.js')
    else:
        polyfillpath = os.path.join(os.path.dirname(__file__), 'jsscripts/polyfill.min.js')
        plotlypath = os.path.join(os.path.dirname(__file__), 'jsscripts/plotly-1.34.0.min.js')


    def __init__(self, plot_type, plot_properties, plot_layout):

        # Define default plot dictionnary used as a basis for plot initilization
        # prepare the default dictionary with None values
        # plot properties
        plotBaseProperties = {
            'x': None,
            'y': None,
            'z': None,
            'marker': None,
            'featureIds': None,
            'featureBox': None,
            'custom': None,
            'hover_text': None,
            'additional_hover_text': None,
            'x_name': None,
            'y_name': None,
            'z_name': None,
            'in_color': None,
            'out_color': None,
            'marker_width': 1,
            'marker_size': 10,
            'marker_symbol': None,
            'line_dash': None,
            'box_orientation': 'v',
            'opacity': None,
            'box_stat': None,
            'box_outliers': False,
            'name': None,
            'normalization': None,
            'cont_type': None,
            'color_scale': None,
            'colorscale_in': None,
            'show_lines': False,
            'cumulative': False,
            'show_colorscale_legend': False,
            'invert_color_scale': False,
            'invert_hist': False,
            'bins': None
        }

        # layout nested dictionary
        plotBaseLayout = {
            'title': 'Plot Title',
            'legend': True,
            'legend_orientation': 'h',
            'x_title': None,
            'y_title': None,
            'z_title': None,
            'xaxis': None,
            'bar_mode': None,
            'x_type': None,
            'y_type': None,
            'x_inv': None,
            'y_inv': None,
            'range_slider': {'visible': False},
            'bargaps': None
        }
        self.plotBaseDic = {
            'plot_type': None,
            'layer': None,
            'plot_prop': plotBaseProperties,
            'layout_prop': plotBaseLayout
        }

        # Set needed properties which are not yet set
        # update the plot_prop
        for k in self.plotBaseDic["plot_prop"]:
            if k not in plot_properties:
                plot_properties[k] = self.plotBaseDic["plot_prop"][k]
        # update the layout_prop
        for k in self.plotBaseDic["layout_prop"]:
            if k not in plot_layout:
                plot_layout[k] = self.plotBaseDic["layout_prop"][k]

        # Set class properties
        self.plot_type = plot_type
        self.plot_properties = plot_properties
        self.plot_layout = plot_layout


    def buildTrace(self):
        '''
        build the final trace calling the go.xxx plotly method
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
        '''

        if self.plot_type == 'scatter':

            self.trace = [go.Scatter(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                mode=self.plot_properties['marker'],
                name=self.plot_properties['name'],
                ids=self.plot_properties['featureIds'],
                customdata=self.plot_properties['custom'],
                text=self.plot_properties['additional_hover_text'],
                hoverinfo=self.plot_properties['hover_text'],
                marker=dict(
                    color=self.plot_properties['in_color'],
                    colorscale=self.plot_properties['colorscale_in'],
                    showscale=self.plot_properties['show_colorscale_legend'],
                    reversescale=self.plot_properties['invert_color_scale'],
                    colorbar=dict(
                        len=0.8
                    ),
                    size=self.plot_properties['marker_size'],
                    symbol=self.plot_properties['marker_symbol'],
                    line=dict(
                        color=self.plot_properties['out_color'],
                        width=self.plot_properties['marker_width']
                    )
                ),
                line=dict(
                    width=self.plot_properties['marker_width'],
                    dash=self.plot_properties['line_dash']
                ),
                opacity=self.plot_properties['opacity']
            )]

        elif self.plot_type == 'box':


            # flip the variables according to the box orientation
            if self.plot_properties['box_orientation'] == 'h':
                self.plot_properties['x'], self.plot_properties['y'] = self.plot_properties['y'], self.plot_properties['x']

            self.trace = [go.Box(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                name=self.plot_properties['name'],
                customdata=self.plot_properties['custom'],
                boxmean=self.plot_properties['box_stat'],
                orientation=self.plot_properties['box_orientation'],
                boxpoints=self.plot_properties['box_outliers'],
                fillcolor=self.plot_properties['in_color'],
                line=dict(
                    color=self.plot_properties['out_color'],
                    width=self.plot_properties['marker_width']
                ),
                opacity=self.plot_properties['opacity']
            )]

        elif self.plot_type == 'bar':

            if self.plot_properties['box_orientation'] == 'h':
                self.plot_properties['x'], self.plot_properties['y'] = self.plot_properties['y'], self.plot_properties['x']

            self.trace = [go.Bar(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                name=self.plot_properties['name'],
                ids=self.plot_properties['featureBox'],
                customdata=self.plot_properties['custom'],
                orientation=self.plot_properties['box_orientation'],
                marker=dict(
                    color=self.plot_properties['in_color'],
                    colorscale=self.plot_properties['colorscale_in'],
                    showscale=self.plot_properties['show_colorscale_legend'],
                    reversescale=self.plot_properties['invert_color_scale'],
                    colorbar=dict(
                        len=0.8
                    ),
                    line=dict(
                        color=self.plot_properties['out_color'],
                        width=self.plot_properties['marker_width']
                    )
                ),
                opacity=self.plot_properties['opacity']
            )]

        elif self.plot_type == 'histogram':

            self.trace = [go.Histogram(
                x=self.plot_properties['x'],
                y=self.plot_properties['x'],
                name=self.plot_properties['name'],
                orientation=self.plot_properties['box_orientation'],
                nbinsx=self.plot_properties['bins'],
                nbinsy=self.plot_properties['bins'],
                marker=dict(
                    color=self.plot_properties['in_color'],
                    line=dict(
                        color=self.plot_properties['out_color'],
                        width=self.plot_properties['marker_width']
                    )
                ),
                histnorm=self.plot_properties['normalization'],
                opacity=self.plot_properties['opacity'],
                cumulative=dict(
                    enabled=self.plot_properties['cumulative'],
                    direction=self.plot_properties['invert_hist']
                    )
            )]

        elif self.plot_type == 'pie':

            self.trace = [go.Pie(
                labels=self.plot_properties['x'],
                values=self.plot_properties['y'],
                name=self.plot_properties['custom'][0],
            )]

        elif self.plot_type == '2dhistogram':

            self.trace = [go.Histogram2d(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                colorscale=self.plot_properties['color_scale']
            )]

        elif self.plot_type == 'polar':

            self.trace = [go.Scatterpolar(
                r=self.plot_properties['x'],
                theta=self.plot_properties['y'],
                mode=self.plot_properties['marker'],
                name=self.plot_properties['y_name'],
                marker=dict(
                    color=self.plot_properties['in_color'],
                    size=self.plot_properties['marker_size'],
                    symbol=self.plot_properties['marker_symbol'],
                    line=dict(
                        color=self.plot_properties['out_color'],
                        width=self.plot_properties['marker_width']
                    )
                ),
                line=dict(
                    color=self.plot_properties['in_color'],
                    width=self.plot_properties['marker_width'],
                    dash=self.plot_properties['line_dash']
                ),
                opacity=self.plot_properties['opacity'],
            )]

        elif self.plot_type == 'ternary':

            # prepare the hover text to display if the additional combobox is empty or not
            # this setting is necessary to overwrite the standard hovering labels
            if self.plot_properties['additional_hover_text'] == []:
                text = [self.plot_properties['x_name'] + ': {}'.format(self.plot_properties['x'][k]) + '<br>{}: {}'.format(self.plot_properties['y_name'], self.plot_properties['y'][k]) + '<br>{}: {}'.format(self.plot_properties['z_name'], self.plot_properties['z'][k]) for k in range(len(self.plot_properties['x']))]
            else:
                text = [self.plot_properties['x_name'] + ': {}'.format(self.plot_properties['x'][k]) + '<br>{}: {}'.format(self.plot_properties['y_name'], self.plot_properties['y'][k]) + '<br>{}: {}'.format(self.plot_properties['z_name'], self.plot_properties['z'][k]) + '<br>{}'.format(self.plot_properties['additional_hover_text'][k]) for k in range(len(self.plot_properties['x']))]

            self.trace = [go.Scatterternary(
                a=self.plot_properties['x'],
                b=self.plot_properties['y'],
                c=self.plot_properties['z'],
                name=self.plot_properties['x_name'] + ' + ' + self.plot_properties['y_name'] + ' + ' + self.plot_properties['z_name'],
                hoverinfo='text',
                text=text,
                mode='markers',
                marker=dict(
                    color=self.plot_properties['in_color'],
                    colorscale=self.plot_properties['colorscale_in'],
                    showscale=self.plot_properties['show_colorscale_legend'],
                    reversescale=self.plot_properties['invert_color_scale'],
                    colorbar=dict(
                        len=0.8
                    ),
                    size=self.plot_properties['marker_size'],
                    symbol=self.plot_properties['marker_symbol'],
                    line=dict(
                        color=self.plot_properties['out_color'],
                        width=self.plot_properties['marker_width']
                    )
                ),
                opacity=self.plot_properties['opacity']
            )]

        elif self.plot_type == 'contour':

            self.trace = [go.Contour(
                z=[self.plot_properties['x'], self.plot_properties['y']],
                contours=dict(
                    coloring=self.plot_properties['cont_type'],
                    showlines=self.plot_properties['show_lines']
                ),
                colorscale=self.plot_properties['color_scale'],
                opacity=self.plot_properties['opacity']
            )]

        elif self.plot_type == 'violin':

            # flip the variables according to the box orientation
            if self.plot_properties['box_orientation'] == 'h':
                self.plot_properties['x'], self.plot_properties['y'] = self.plot_properties['y'], self.plot_properties['x']

            self.trace = [go.Violin(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                name=self.plot_properties['name'],
                customdata=self.plot_properties['custom'],
                orientation=self.plot_properties['box_orientation'],
                points=self.plot_properties['box_outliers'],
                fillcolor=self.plot_properties['in_color'],
                line=dict(
                    color=self.plot_properties['out_color'],
                    width=self.plot_properties['marker_width']
                ),
                opacity=self.plot_properties['opacity'],
                meanline=dict(
                    visible=self.plot_properties['show_mean_line']
                ),
                side=self.plot_properties['violin_side']
                )]

        return self.trace

    def buildLayout(self):
        '''
        build the final layout calling the go.Layout plotly method

        From the initial object created (e.g. p = Plot(plot_type, plot_properties,
        layout_properties)) this methods checks the plot_type and elaborates the
        layout_properties dictionary passed

        Console usage:
        # create the initial object
        p = Plot(plot_type, plot_properties, layout_properties)
        # call the method
        p.buildLayout()

        Returns the final Plot Layout (final Layout object, AKA go.Layout)
        '''

        # flip the variables according to the box orientation
        if self.plot_properties['box_orientation'] == 'h':
            self.plot_layout['x_title'], self.plot_layout['y_title'] = self.plot_layout['y_title'], self.plot_layout['x_title']

        self.layout = go.Layout(
            showlegend=self.plot_layout['legend'],
            legend=dict(
                orientation=self.plot_layout['legend_orientation']
            ),
            title=self.plot_layout['title'],
            xaxis=dict(
                title=self.plot_layout['x_title'],
                autorange=self.plot_layout['x_inv']
            ),
            yaxis=dict(
                title=self.plot_layout['y_title'],
                autorange=self.plot_layout['y_inv']
            )
        )

        # update the x and y axis and add the linear and log only if the data are numeric
        # pass if field is empty
        try:
            if isinstance(self.plot_properties['x'][0], (int, float)):
                self.layout['xaxis'].update(type=self.plot_layout['x_type'])
        except:
            pass
        try:
            if isinstance(self.plot_properties['y'][0], (int, float)):
                self.layout['yaxis'].update(type=self.plot_layout['y_type'])
        except:
            pass

        # update layout properties depending on the plot type
        if self.plot_type == 'scatter':
            self.layout['xaxis'].update(rangeslider=self.plot_layout['range_slider'])

        elif self.plot_type == 'bar':
            self.layout['barmode'] = self.plot_layout['bar_mode']

        elif self.plot_type == 'histogram':
            self.layout['barmode'] = self.plot_layout['bar_mode']
            self.layout['bargroupgap'] = self.plot_layout['bargaps']

        elif self.plot_type == 'pie':
            self.layout['xaxis'].update(title=''),
            self.layout['xaxis'].update(showgrid=False),
            self.layout['xaxis'].update(zeroline=False),
            self.layout['xaxis'].update(showline=False),
            self.layout['xaxis'].update(showticklabels=False),
            self.layout['yaxis'].update(title=''),
            self.layout['yaxis'].update(showgrid=False),
            self.layout['yaxis'].update(zeroline=False),
            self.layout['yaxis'].update(showline=False),
            self.layout['yaxis'].update(showticklabels=False)

        elif self.plot_type == 'ternary':
            self.layout['xaxis'].update(title=''),
            self.layout['xaxis'].update(showgrid=False),
            self.layout['xaxis'].update(zeroline=False),
            self.layout['xaxis'].update(showline=False),
            self.layout['xaxis'].update(showticklabels=False),
            self.layout['yaxis'].update(title=''),
            self.layout['yaxis'].update(showgrid=False),
            self.layout['yaxis'].update(zeroline=False),
            self.layout['yaxis'].update(showline=False),
            self.layout['yaxis'].update(showticklabels=False)
            self.layout['ternary'] = dict(
                sum=100,
                aaxis=dict(
                    title=self.plot_layout['x_title'],
                    ticksuffix='%',
                ),
                baxis=dict(
                    title=self.plot_layout['y_title'],
                    ticksuffix='%'
                ),
                caxis=dict(
                    title=self.plot_layout['z_title'],
                    ticksuffix='%'
                ),
            )

        return self.layout

    def js_callback(self, code_string):
        '''
        returns a string that is added to the end of the plot. This string is
        necessary for the interaction between plot and map objects

        WARNING! The string ReplaceTheDiv is a default string that will be
        replaced in a second moment
        '''

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
            dd["field"] = data.points[i].data.customdata

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


    def buildFigure(self):
        '''
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
        '''

        fig = go.Figure(data=self.trace, layout=self.layout)

        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}"></script><script src="{}"></script></head>'.format(self.polyfillpath, self.plotlypath)
        # set some configurations
        config = {'scrollZoom': True, 'editable': True}
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False, show_link=False, config=config)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search('Plotly.newPlot\("([^"]+)', self.raw_plot)
        substr = match.group(1)
        self.raw_plot = self.raw_plot.replace('ReplaceTheDiv', substr)

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')

        with open(self.plot_path, "w") as f:
            f.write(self.raw_plot)

        return self.plot_path

    def buildFigures(self, plot_type, ptrace):
        '''
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
        '''

        # assign the variables from the kwargs arguments
        # plot_type = kwargs['plot_type']
        # ptrace = kwargs['pl']

        # check if the plot type and render the correct figure
        if plot_type == 'bar' or 'histogram':
            del self.layout
            self.layout = go.Layout(
                barmode=self.plot_layout['bar_mode']
            )
            figures = go.Figure(data=ptrace, layout=self.layout)

        else:
            figures = go.Figure(data=ptrace, layout=self.layout)

        # set some configurations
        config = {'scrollZoom': True, 'editable': True}
        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}"></script><script src="{}"></script></head>'.format(self.polyfillpath, self.plotlypath)
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(figures, output_type='div', include_plotlyjs=False, show_link=False, config=config)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search('Plotly.newPlot\("([^"]+)', self.raw_plot)
        substr = match.group(1)
        self.raw_plot = self.raw_plot.replace('ReplaceTheDiv', substr)

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        with open(self.plot_path, "w") as f:
            f.write(self.raw_plot)

        return self.plot_path

    def buildSubPlots(self, grid, row, column, ptrace, tit_lst):
        '''
        Draws plot in different plot canvases (not overlapping)

        params:
            grid (string): 'row' or 'col'. Plot are created in rows or columns
            row (int): number of rows (if row is selected)
            column (int): number of columns (if column is selected)
            ptrace (list of Plot Traces): list of all the different Plot Traces
            tit_lst (tuple): tuple containing the plot titles

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
        '''

        if grid == 'row':

            fig = tools.make_subplots(rows=row, cols=column, subplot_titles=tit_lst)

            for i, itm in enumerate(ptrace):
                fig.append_trace(itm, row, i + 1)

        elif grid == 'col':

            fig = tools.make_subplots(rows=row, cols=column)

            for i, itm in enumerate(ptrace):
                fig.append_trace(itm, i + 1, column)

        # set some configurations
        config = {'scrollZoom': True, 'editable': True}
        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}"></script><script src="{}"></script></head>'.format(self.polyfillpath, self.plotlypath)
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False, show_link=False, config=config)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search('Plotly.newPlot\("([^"]+)', self.raw_plot)
        substr = match.group(1)
        self.raw_plot = self.raw_plot.replace('ReplaceTheDiv', substr)

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        with open(self.plot_path, "w") as f:
            f.write(self.raw_plot)

        return self.plot_path
