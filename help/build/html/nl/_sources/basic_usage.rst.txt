.. _basic_usage:

DataPlotly Basic Usage
======================
DataPlotly interface has been designed in order to be simple but, at the same time,
complete and with many options and customizations available.

Creating a plot is just easy as it sounds: choose the plot type, ``x`` and ``y``
columns, colors, labels, etc and press the ``Create Plot`` button.
The plot is immediately shown in the plot canvas.

If you want to change some setting, e.g. the marker color or size, the ``x``
column, go ahead and the hit the ``Update Plot`` button: the plot is then
updated in the plot canvas.

DataPlotly is a docket widget meaning that you can move it within the QGIS interface.
It is made up by 5 different widgets:

|properties| **fundamental plot settings**

|custom| **additional plot customizations**

|plot| **plot canvas**

|help| **user guide and help for each plot**

|code| **raw html code**

.. image:: /img/basic_usage/overview.png
  :scale: 50%

.. _add_plot:

Add a Plot
----------
DataPlotly workflow is pretty straightforward:

1. choose the plot type (1)
2. set the layer and the field(s) you want to plot (2)
3. show the plot with the ``Create Plot`` button (3). The plot canvas is automatically visible.

.. image:: /img/basic_usage/basic1.png
  :scale: 50%


You can change some plot settings and click on the ``Update`` button to update
the plot with the changes.

If you want to start again, just click the ``Clean Plot Canvas`` button and the
plot canvas will be empty.


Multi Plots
-----------
DataPlotly allows the creation of many different plots. Plots can be shown on
the same plot canvas (**overlapping**) or each plot can be drawn in different rows
or columns (**subplots**).

Overlapping Plots
.................
You can add as many plots as you want within the same plot view. Plot types can be
different and also the source layer can be different.

.. note:: results can be very strange depending on the plot type and on the fields you choose. Be careful!

To add other plot just repeat the steps of :ref:`add_plot` by choosing different
plot types and/or just different layer fields, etc..

In the following picture, same plot type (scatterplot) and different fields of the
same layer:

.. image:: /img/basic_usage/basic2.png
  :scale: 50%

The following pictures show 2 different overlapping plot types (boxplot and
scatterplot):

.. image:: /img/basic_usage/basic3.png
  :scale: 50%


Subplots
........
You can choose to separate the plots in different plot canvas. It is particularly
useful when the scales are very different or when overlapping too many data results
in a messy plot canvas.

You just have to choose the plots and the fields as described in the section
:ref:`add_plot` but you have to specify the ``SubPlots`` parameter from the
combobox and choose if the plots have to be drawn in rows (default parameter)
or in columns.

The following pictures show plots in rows and in columns:

.. image:: /img/basic_usage/basic4.png
  :scale: 50%

|
|

.. image:: /img/basic_usage/basic5.png
  :scale: 50%


.. _save:

Save Plot
---------
Saving a plot, technically the plot canvas, is very simple. You can choose to save
the plot as a ``png`` image or as ``html`` file.

.. note:: saving the image as ``html`` file will keep the interactivity of the plot

You just have to click on the correct button and choose the path where to save
the image, both static or interactive.

.. image:: /img/basic_usage/basic6.png
  :scale: 50%


Raw Plot Code
-------------
In addition to saving the plot as image or html file (see :ref:`save`) you can
also copy the raw ``html`` code of the plot and embed it somewhere else.

A good place where to copy/paste the raw code is the html frame of the print
composer of QGIS.

In order to copy the plot code, after the plot creation, just go in the ``Raw Plot``
tab: here you can see a long string. **Right Click** on the tab and
choose ``Select All``, then **Right Click** again and choose ``Copy`` (of course
you can use keyboard shortcuts ``Ctrl + A`` for select all and ``Ctrl + C`` for copy):

.. image:: /img/basic_usage/basic7.png
  :scale: 50%


Then you have your plot code copied in memory: you just have to choose where to
paste it.

In the following example, the ``html code`` is pasted in the **html frame** of
the print composer:

1. open the print composer and add an ``html frame`` (1)
2. paste the code in the ``Source`` space (2)
3. refresh the ``html`` code (3)
4. results will be shown in the frame (4)

.. image:: /img/basic_usage/basic8.png
  :scale: 50%


Layer fields tips
-----------------
Using Expressions
.................
DataPlotly supports all the fields type (integers, floats, text, etc..) and
will elaborate the data so that they can be correctly displayed.

Thanks to the QGIS API and custom widget, it is possible to add also **Expressions**
instead of pure layer fields (e.g. ``field + 10``, ``field1 * field2``, etc).

You can use the Expression editor to add complex expressions (e.g. ``(field1 + 10) * (field2 * 10)``)
or you can type the expression directly in the combo box. Expressions are evaluated
*on the fly*, so if the string is red, then the expression is not valid.

.. image:: /img/basic_usage/basic9.png
  :scale: 50%

Use only selected features
..........................
Another very handy options is to work only with the selected features on the
layer.

Just check the ``Use only selected features`` check box and only the attributes
of the selected features will be taken.
