# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DataPlotly
                                 A QGIS plugin
 D3 Plots for QGIS
                              -------------------
        begin                : 2022-06-08
        git sha              : $Format:%H$
        copyright            : (C) 2020 by matteo ghetta
        email                : matteo.ghetta@faunalia.it
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

from qgis.utils import qgsfunction
from qgis.core import QgsRenderContext


@qgsfunction(args='auto', group='DataPlotly')
def get_symbol_colors(feature, parent, context):
    """
        Retrieve the color of each category as html code. You can use this function
        to set the plot items (pie slices, bars, points, etc) to the same color
        of the feature visible in the map.
        <h4>Syntax</h4>
        <p>
            get_symbol_colors() -> '#da1ddd'
        </p>
    """
    _ = parent
    layer = context.variable('layer')
    renderer_context = QgsRenderContext()
    renderer = layer.renderer()
    renderer.startRender(renderer_context, layer.fields())

    symbols = renderer.originalSymbolsForFeature(feature, renderer_context)

    if symbols:
        color = symbols[0].color().name()
    else:
        color = '#000000'

    renderer.stopRender(renderer_context)

    return color
