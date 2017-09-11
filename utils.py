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

from qgis.core import *


def hex_to_rgb(value):
    '''
    convert hex string to rgb tuple directly from a QgsColorButton
    '''
    name = value.color().name()
    value = name.lstrip('#')
    lv = len(value)
    col = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    final = 'rgb' + str(col)
    return final

def getSortedId(layer, field_list):
    '''
    return a list with values needed for js interaction

    the function creates the list so that the final order of the items is the
    same of that visible in the Plot Canvas and so the clicked element returns
    the correct id

    layer: a valid QgsVectorLayer, useful with self.layer_combo.currentLayer()
    field_list: a list of values (e.g. taken from the attribute table)
    '''

    l = []

    # don't sort the list if the item is integer or float (check the first item)
    if type(field_list[0]) == (int or float):
        l = list(set(field_list))

    # sort the list if items are strings
    else:
        l = sorted(set(field_list), key=field_list.index)

    return l

def getIds(layer, checkstate):
    '''
    get the ids list by checking if features are selectedFeatures
    '''

    ids = []

    if checkstate:
        for i in layer.selectedFeatures():
            ids.append(i.id())
    else:
        for i in layer.getFeatures():
            ids.append(i.id())

    ids.sort()

    return ids
