# DataPlotly
DataPlotly plugins allows to create ![D3](https://d3js.org/) interactive like
plots thanks to the ![Plotly](https://plot.ly/python/) library and the python API.

DataPlotly makes plot creation and customization easy for every needs.

Besides all the plot and customizations available, the plot is **linked** with
the map canvas:

![Plot interactions](./help/source/img/readme/plot_interaction_scatter.gif)

![Plot interactions](./help/source/img/readme/plot_interaction_box.gif)

![Plot interactions](./help/source/img/readme/plot_interaction_scatter_box.gif)

## Usage
DataPlotly works **only with QGIS 3** (or current QGIS dev). No additional
libraries are necessary.

## Gallery

### Single Plot

Some examples of single plot type with some options. The list is far away to show all the possibilities.

#### Scatter Plot
![Plot interactions](./help/source/img/readme/plot_box.png)

#### Box Plot with statistics
![Plot interactions](./help/source/img/readme/plot_box.png)

#### Stacked Bar Plot
![Plot interactions](./help/source/img/readme/plot_bar_stack.png)

#### Probability Histogram
![Plot interactions](./help/source/img/readme/plot_histogram.png)

#### Pie Chart
![Plot interactions](./help/source/img/readme/plot_pie.png)

#### 2D Histogram
![Plot interactions](./help/source/img/readme/plot_2dhistogram.png)

#### Polar Plot
![Plot interactions](./help/source/img/readme/plot_polar.png)

#### Ternary Plot
![Plot interactions](./help/source/img/readme/plot_ternary.png)

#### Contour Plot with fire color scale
![Plot interactions](./help/source/img/readme/plot_contour.png)

### Multi Plots
DataPloty allows to create different plot type in the same *plot canvas* but allow also the chance to separate each plot in a different canvas.

<aside class="warning">
Some plot are not compatibles with overlapping or subplotting. A message will warn you when this happens.
</aside>


## Overlapped Plots
![Plot interactions](./help/source/img/readme/plot_scatter_bar.png)

## Subplots in row
![Plot interactions](./help/source/img/readme/plot_histogram_box.png)

## Subplots in column
![Plot interactions](./help/source/img/readme/plot_scatter_histogram.png)
