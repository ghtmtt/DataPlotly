import plotly
import plotly.graph_objs as go
from plotly import tools
import tempfile
import os


class Plot(object):

    plot_type = ''

    plot_properties = {}

    plot_layout = {}

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

    def buildTrace(self, plot_type):
        '''
        build the final trace calling the go.xxx plotly method
        this method here is the one performing the real job

        this method takes the dictionary with all the properties and build the
        plotly trace that is returned and available

        Console usage:
        p = Plot()
        # call the method that builds the dictionary of the properties
        p.buildProperties(x = ...)  #all the kwargs arguments
        p.buildTrace(plot_type)  #plot_type needed to build the correct plot

        print(p.trace)
        # this is the final plotly object
        {['opacity': 1.0, 'type': 'bar', 'name': 'ID', ...]}
        '''

        self.plot_type = plot_type

        if plot_type == 'scatter':

            self.trace = [go.Scatter(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
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
                name=self.plot_properties['y_name'],
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

            self.trace = [go.Bar(
                x=self.plot_properties['x'],
                y=self.plot_properties['y'],
                name=self.plot_properties['bar_name'],
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
                name=self.plot_properties['x_name'],
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
                y=self.plot_properties['y']
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

    def buildLayout(self, plot_type):
        '''
        build the final layout calling the go.Layout plotly method

        this method takes the dictionary with all the layout properties and
        builds the final Layout that is returned and available

        depending on the plot_type, properties of specific plot will be added

        Console usage:
        p = Plot()
        # call the method that builds the dictionary of the properties
        p.layoutProperties(title = ...)  #all the kwarg arguments
        p.buildLayout(plot_type)  #plot_type needed to build the correct layout

        print(p.layout)
        # this is the final plotly object
        {'xaxis': {'title': 'VALORE'}, 'title': 'Title'...}

        '''

        self.plot_type = plot_type

        # flip the variables according to the box orientation
        if self.plot_properties['box_orientation'] == 'h':
            self.plot_layout['x_title'], self.plot_layout['y_title'] = self.plot_layout['y_title'], self.plot_layout['x_title']

        self.layout = go.Layout(
            showlegend=self.plot_layout['legend'],
            title=self.plot_layout['title'],
            xaxis=dict(
                title=self.plot_layout['x_title']
            ),
            yaxis=dict(
                title=self.plot_layout['y_title']
            )
        )

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
            self.layout['yaxis'].update(showticklabels=False),

        return self.layout
        print(self.layout)

    def buildFigure(self):
        '''
        draw the final plot (single plot)

        call the go.Figure plotly method and build the figure object
        adjust the html file and add some line
        save the html plot file in a temporary directory and return the path
        that can be loaded in the QWebView
        '''

        fig = go.Figure(data=self.trace, layout=self.layout)

        # first lines of additional html with the link to the plotly javascrit
        self.raw_plot = '<head><meta charset="utf-8" /></head>''<head><meta charset="utf-8" /><script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False)
        # last line to close the html file
        self.raw_plot += '</body></html>'

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        self.plot_file = open(self.plot_path, "w")
        self.plot_file.write(self.raw_plot)
        self.plot_file.close()

        return self.plot_path

    def buildFigures(self, ptrace):
        '''
        draw the final plot (multi plot)
        '''

        figures = go.Figure(data=ptrace, layout=self.layout)

        # first lines of additional html with the link to the plotly javascrit
        self.raw_plot = '<head><meta charset="utf-8" /></head>''<head><meta charset="utf-8" /><script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(figures, output_type='div', include_plotlyjs=False)
        # last line to close the html file
        self.raw_plot += '</body></html>'

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        self.plot_file = open(self.plot_path, "w")
        self.plot_file.write(self.raw_plot)
        self.plot_file.close()

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

        # first lines of additional html with the link to the plotly javascrit
        self.raw_plot = '<head><meta charset="utf-8" /></head>''<head><meta charset="utf-8" /><script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        # call the plot method without all the javascript code
        self.raw_plot += plotly.offline.plot(fig, output_type='div', include_plotlyjs=False)
        # last line to close the html file
        self.raw_plot += '</body></html>'

        self.plot_path = os.path.join(tempfile.gettempdir(), 'temp_plot_name.html')
        self.plot_file = open(self.plot_path, "w")
        self.plot_file.write(self.raw_plot)
        self.plot_file.close()

        return self.plot_path
