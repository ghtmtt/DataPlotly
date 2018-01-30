.. _processing:

DataPlotly as Processing provider
=================================
From version 1.4 DataPlotly has been added as Processing provider thank to the
work of `Michaël Douchin of 3Liz <https://www.3liz.com/>`_.

This opens the doors to infinite possibilities:

* using all the Processing methods with DataPlotly
* creating batch plots with one click
* adding DataPlotly in the Processing Graphical Modeler

Activating DataPlotly for Processing
------------------------------------
First thing to do is activating Processing and add DataPlotly as provider.
If not added by default you can go in ``Settings -> Options`` and
click on the last tab named Processing.

Expand the Provider menu and activate the DataPlotly provider:

.. image:: /img/processing/processing_provider.png
  :scale: 50%


And then you will see the DataPltoly provider in the Processing Toolbox:

.. image:: /img/processing/processing_provider_active.png
  :scale: 50%


Simple DataPlotly usage
-----------------------
The ``Build a generic plot`` algorithm is a simplified version of DataPlotly plugin:
this means you don't have all the customizations available, but still you can
create awesome plots.

The interface is very simple and the plot creation process is very straightforward:

* choose the layer
* choose the plot type
* adjust the additional options (plot title, X axis, Y axis and color)

.. image:: /img/processing/plot_configuration.png
  :scale: 50%


DataPlotly will create 2 results:

* ``html`` file with the final plot
* ``json`` file with all the plot specifications


The plot can be opened in the ``Processing -> Result Viewer``:

.. image:: /img/processing/processing_result_viewer.png
  :scale: 50%

And by simple double clicking on the menu entry, the plot will be opened in your
default browser:

.. image:: /img/processing/dataplotly_result.png
  :scale: 50%

If you want to save also the ``json`` file, you have to specify the path in the
DataPlotly Processing Window.
