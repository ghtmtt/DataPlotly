import plotly
import plotly.graph_objs as go
from plotly import tools
import tempfile
import os
import platform
import re


class Plot(object):

    plot_type = ''

    plot_properties = {}

    plot_layout = {}

    # path of javascript files
    if platform.system() == 'Windows':
        polyfillpath = 'file:///'
        plotlypath = 'file:///'
        polyfillpath += os.path.join(os.path.dirname(__file__), 'jsscripts/polyfill.min.js')
        plotlypath += os.path.join(os.path.dirname(__file__), 'jsscripts/plotly.min.js')
    else:
        polyfillpath = os.path.join(os.path.dirname(__file__), 'jsscripts/polyfill.min.js')
        plotlypath = os.path.join(os.path.dirname(__file__), 'jsscripts/plotly.min.js')

    def buildProperties(self, *args, **kwargs):
        '''
        dictionary with all the plot properties and return the object

        self.plot_properties is final objcet containing all the properties

        Console usage:

        p = Plot()
        p.buildProperties(x = ..., )  #all the kwargs arguments
        print(p.plot_properties) # returns the dictionary with all the values

        {'marker_width': 1, 'marker_size': 10, 'box_outliers': False .......}
        '''

        for k, v in kwargs.items():
            self.plot_properties[k] = v

        return self.plot_properties

    def buildTrace(self, *args, **kwargs):
        '''
        build the final trace calling the go.xxx plotly method
        this method here is the one performing the real job

        this method takes the dictionary with all the properties and build the
        plotly trace that is returned and available

        Console usage:
        p = Plot()
        # call the method that builds the dictionary of the properties
        p.buildProperties(x = ...)  #all the kwargs arguments
        p.buildTrace(plot_type='scatter') #plot_type needed to build the
        correct layout and it has to be a string like 'scatter', 'barplot', ...

        print(p.trace)
        # this is the final plotly object
        {['opacity': 1.0, 'type': 'bar', 'name': 'ID', ...]}
        '''

        # retieve the plot_type from the kwargs and assign it to the variable
        plot_type = kwargs['plot_type']

        if plot_type == 'scatter':

            self.trace = [go.Scatter(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                mode=self.plot_properties['marker'],
                name=self.plot_properties['name'],
                ids=self.plot_properties['featureIds'],
                text=self.plot_properties['additional_hover_text'],
                hoverinfo=self.plot_properties['hover_text'],
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
                opacity=self.plot_properties['opacity']
            )]

        elif plot_type == 'box':

            # NULL value in the Field is empty
            if not self.plot_properties['x']:
                self.plot_properties['x'] = None

            # flip the variables according to the box orientation
            if self.plot_properties['box_orientation'] == 'h':
                self.plot_properties['x'], self.plot_properties['y'] = self.plot_properties['y'], self.plot_properties['x']

            self.trace = [go.Box(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                name=self.plot_properties['name'],
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

        elif plot_type == 'bar':

            if self.plot_properties['box_orientation'] == 'h':
                self.plot_properties['x'], self.plot_properties['y'] = self.plot_properties['y'], self.plot_properties['x']

            self.trace = [go.Bar(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                name=self.plot_properties['name'],
                orientation=self.plot_properties['box_orientation'],
                marker=dict(
                    color=self.plot_properties['in_color'],
                    line=dict(
                        color=self.plot_properties['out_color'],
                        width=self.plot_properties['marker_width']
                    )
                ),
                opacity=self.plot_properties['opacity']
            )]

        elif plot_type == 'histogram':

            self.trace = [go.Histogram(
                x=self.plot_properties['x'],
                y=self.plot_properties['x'],
                name=self.plot_properties['name'],
                orientation=self.plot_properties['box_orientation'],
                marker=dict(
                    color=self.plot_properties['in_color'],
                    line=dict(
                        color=self.plot_properties['out_color'],
                        width=self.plot_properties['marker_width']
                    )
                ),
                histnorm=self.plot_properties['normalization'],
                opacity=self.plot_properties['opacity']
            )]

        elif plot_type == 'pie':

            self.trace = [go.Pie(
                labels=self.plot_properties['x'],
                values=self.plot_properties['y']
            )]

        elif plot_type == '2dhistogram':

            self.trace = [go.Histogram2d(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                colorscale=self.plot_properties['color_scale'],
            )]

        elif plot_type == 'polar':

            self.trace = [go.Scatter(
                r=self.plot_properties['x'],
                t=self.plot_properties['y'],
                ids=self.plot_properties['featureIds'],
                mode=self.plot_properties['marker'],
                name=self.plot_properties['y_name'],
                marker=dict(
                    color=self.plot_properties['in_color'],
                    size=self.plot_properties['marker_size'] + 100,
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

        elif plot_type == 'ternary':

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
                    size=self.plot_properties['marker_size'],
                    symbol=self.plot_properties['marker_symbol'],
                    line=dict(
                        color=self.plot_properties['out_color'],
                        width=self.plot_properties['marker_width']
                    )
                ),
                opacity=self.plot_properties['opacity']
            )]

        elif plot_type == 'contour':

            self.trace = [go.Contour(
                z=[self.plot_properties['x'], self.plot_properties['y']],
                contours=dict(
                    coloring=self.plot_properties['cont_type'],
                    showlines=self.plot_properties['show_lines']
                ),
                colorscale=self.plot_properties['color_scale'],
                opacity=self.plot_properties['opacity']
            )]

        return self.trace

    def layoutProperties(self, *args, **kwargs):
        '''
        build the layout customizations and return the object

        self.plot_layout is the final objcet containing the layout properties

        Console usage:

        p = Plot()
        p.layoutProperties()  #all the kwargs arguments
        print(p.plot_layout) # returns the dictionary with all the values


        {'title': 'Plot Title', 'legend': True, ..... }
        '''

        for k, v in kwargs.items():
            self.plot_layout[k] = v

        return self.plot_layout

    def buildLayout(self, *args, **kwargs):
        '''
        build the final layout calling the go.Layout plotly method

        this method takes the dictionary with all the layout properties and
        builds the final Layout that is returned and available

        depending on the plot_type, properties of specific plot will be added

        Console usage:
        p = Plot()
        # call the method that builds the dictionary of the properties
        p.layoutProperties(title = ...)  #all the kwarg arguments
        p.buildLayout(plot_type='scatter')  #plot_type needed to build the
        correct layout and it has to be a string like 'scatter', 'barplot', ...

        print(p.layout)
        # this is the final plotly object
        {'xaxis': {'title': 'VALORE'}, 'title': 'Title'...}
        '''

        # retieve the plot_type from the kwargs and assign it to the variable
        plot_type = kwargs['plot_type']

        # flip the variables according to the box orientation
        if self.plot_properties['box_orientation'] == 'h':
            self.plot_layout['x_title'], self.plot_layout['y_title'] = self.plot_layout['y_title'], self.plot_layout['x_title']

        self.layout = go.Layout(
            showlegend=self.plot_layout['legend'],
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
        if plot_type == 'scatter':
            self.layout['xaxis'].update(rangeslider=self.plot_layout['range_slider'])

        elif plot_type == 'bar':
            self.layout['barmode'] = self.plot_layout['bar_mode']

        elif plot_type == 'histogram':
            self.layout['barmode'] = self.plot_layout['bar_mode']

        elif plot_type == 'pie':
            self.layout['xaxis'].update(title=''),
            self.layout['xaxis'].update(showgrid=False),
            self.layout['xaxis'].update(zeroline=False),
            self.layout['xaxis'].update(showline=False),
            self.layout['xaxis'].update(autotick=False),
            self.layout['xaxis'].update(showticklabels=False),
            self.layout['yaxis'].update(title=''),
            self.layout['yaxis'].update(showgrid=False),
            self.layout['yaxis'].update(zeroline=False),
            self.layout['yaxis'].update(showline=False),
            self.layout['yaxis'].update(autotick=False),
            self.layout['yaxis'].update(showticklabels=False)

        elif plot_type == 'ternary':
            self.layout['xaxis'].update(title=''),
            self.layout['xaxis'].update(showgrid=False),
            self.layout['xaxis'].update(zeroline=False),
            self.layout['xaxis'].update(showline=False),
            self.layout['xaxis'].update(autotick=False),
            self.layout['xaxis'].update(showticklabels=False),
            self.layout['yaxis'].update(title=''),
            self.layout['yaxis'].update(showgrid=False),
            self.layout['yaxis'].update(zeroline=False),
            self.layout['yaxis'].update(showline=False),
            self.layout['yaxis'].update(autotick=False),
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
        return a string that will be used together with the plot creation

        WARNING! The string ReplaceTheDiv is a default string that will be
        replaced in a second moment
        '''

        js_str = '''
        <script>
        // additional js function to select and click on the data
        // returns the ids of the selected/clicked feature
        
        var plotly_div = document.getElementById('ReplaceTheDiv')
        var plotly_data = plotly_div.data
        //console.log(plotly_data)
        plotly_div.on('plotly_selected', function(data){
        featureId = plotly_data[0].ids[data.points[0].pointNumber]
        featureIds = []
        data.points.forEach(function(pt){
        featureIds.push(parseInt(pt.id))
            })
        //console.log(featureIds)
        window.status = JSON.stringify(featureIds)
        })
        plotly_div.on('plotly_click', function(data){
        featureId = plotly_data[0].ids[data.points[0].pointNumber]
        featureIds = []
        featureIds.push(parseInt(featureId))
        //console.log(featureIds)
        window.status = JSON.stringify(featureIds)
        });
        </script>'''

        return js_str


    def buildFigure(self, *args, **kwargs):
        '''
        draw the final plot (single plot)

        call the go.Figure plotly method and build the figure object
        adjust the html file and add some line
        save the html plot file in a temporary directory and return the path
        that can be loaded in the QWebView
        '''

        plot_type = kwargs['plot_type']

        fig = go.Figure(data=self.trace, layout=self.layout)

        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}"></script><script src="{}"></script></head>'.format(self.polyfillpath, self.plotlypath)
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False, show_link=False)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)
        # last line to close the html file
        self.raw_plot += '</body></html>'

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search('Plotly.newPlot\("([^"]+)', self.raw_plot)
        substr = match.group(1)
        self.raw_plot = self.raw_plot.replace('ReplaceTheDiv', substr)

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')

        with open(self.plot_path, "w") as f:
            f.write(self.raw_plot)

        return self.plot_path

    def buildFigures(self, *args, **kwargs):
        '''
        draw the final plot (multi plot)

        this method can take many arguments in order to correct render the plots
        depending on the plot type chosen.
        It is necessary because for bar and histogram plots, it the user wants
        to have stacked or overlayed plots, an unique self.layout layout is
        necessary. Without this addition these last options will be useless.

        For bar and histogram plots it deletes the existing layouts and creates
        the last and correct layout object

        Console usage:
        p = Plot()
        # call the method that builds the dictionary of the properties
        p.buildFigures(pl=pl, ptype=ptype)
        # pl (plot object) is the trace, so the plot object with all its
        properties
        # plot_type (string) is the plot_type ('scatter', 'bar')

        self.layout is DELETED, so the final layout is taken from the LAST plot
        configuration added
        '''

        # assign the variables from the kwargs arguments
        plot_type = kwargs['plot_type']
        ptrace = kwargs['pl']

        # check if the plot type and render the correct figure
        if plot_type == 'bar' or 'histogram':
            del self.layout
            self.layout = go.Layout(
                barmode=self.plot_layout['bar_mode']
            )
            figures = go.Figure(data=ptrace, layout=self.layout)

        else:
            figures = go.Figure(data=ptrace, layout=self.layout)

        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}"></script><script src="{}"></script></head>'.format(self.polyfillpath, self.plotlypath)
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(figures, output_type='div', include_plotlyjs=False, show_link=False)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)
        # last line to close the html file
        self.raw_plot += '</body></html>'

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
        draw subplots
        '''

        if grid == 'row':

            fig = tools.make_subplots(rows=row, cols=column, subplot_titles=tit_lst)

            for i, itm in enumerate(ptrace):
                fig.append_trace(itm, row, i + 1)

        elif grid == 'col':

            fig = tools.make_subplots(rows=row, cols=column)

            for i, itm in enumerate(ptrace):
                fig.append_trace(itm, i + 1, column)

        # plotly.offline.plot(fig)

        # first lines of additional html with the link to the local javascript
        self.raw_plot = '<head><meta charset="utf-8" /><script src="{}"></script><script src="{}"></script></head>'.format(self.polyfillpath, self.plotlypath)
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False, show_link=False)
        # insert callback for javascript events
        self.raw_plot += self.js_callback(self.raw_plot)
        # last line to close the html file
        self.raw_plot += '</body></html>'

        # use regex to replace the string ReplaceTheDiv with the correct plot id generated by plotly
        match = re.search('Plotly.newPlot\("([^"]+)', self.raw_plot)
        substr = match.group(1)
        self.raw_plot = self.raw_plot.replace('ReplaceTheDiv', substr)

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        with open(self.plot_path, "w") as f:
            f.write(self.raw_plot)

        return self.plot_path
