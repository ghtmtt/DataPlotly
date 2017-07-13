.. _scatterplot:

Scatter Plot
============
Here you will find the guide to every parameter of the scatter plot. If you need
more generic information please see :ref:`basic_usage`.

.. image:: /img/scatter/scatterplot.png
  :scale: 50%

Plot Properties
---------------
``Layer``: the combobox will display all the vector layer loaded in QGIS

``X Field``: the X field

``Y Field``: the Y field

``Marker Color``: marker color

``Marker Size``: the size of the marker

``Stroke Color``: border color

``Stroke Width``: the width of the border

``Marker Type``: choose between **Points**, **Lines** or **Points and Lines**

``Point Type``: if ``Marker Type`` is **Points** or **Points and Lines**, the marker type

``Line Type``: if ``Marker Type`` is **Lines** or **Points and Lines**, the line type

``Transparency``: transparecy level of the marker/line

Plot Customizations
-------------------
``Show Legend``: show the legend of the current plot

``Show Range Slider``: add a slider below the plot

.. image:: /img/scatter/scatter.png
  :scale: 50%

``Plot Title``: the plot title

``Legend Title``: the title of the legend

``X Label``: X label text

``Y Label``: Y Label text

``Hover Infos``: choose the information that will be shown when hovering on
the Plot Canvas

``Additional Hover Label``: choose another field of the plot (or other values)
that will be shown together with the other informations. This field supports
expressions: e.g. ``'The ID of this point is ' || ID``:

.. image:: /img/scatter/scatter2.png
  :scale: 50%

``Invert X Axis``: check if you want to invert the ordering of the x axis

``X Axis Mode``: choose between Linear, Logarithmic or Categorized

``Invert Y Axis``: check if you want to invert the ordering of the y axis

``Y Axis Mode``: choose between Linear, Logarithmic or Categorized
