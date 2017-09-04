from qgis.core import *


def getFields(lay, exp):
    '''
    from a QgsFieldExpressionWidget to a list of data
    '''

    vl = lay.currentLayer()
    if exp:
        field = exp.currentText()
    else:
        field = None

    data = []

    # get the data from the layer
    # no expression
    if not field:
        for i in vl.getFeatures():
            data.append(i.id())
    elif not exp.currentField()[1]:
        for i in vl.getFeatures():
            data.append(i[field])
    # if expression is selected
    else:
        # expression name
        fil = exp.currentField()[0]
        # expr = QgsExpression(fil)
        # for i in vl.getFeatures():
            # data.append(expr.evaluate(i, vl.pendingFields()))

    return data


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

def getIdJs(layer, field):
    '''
    return a list of unique items that can be used as ids
    '''

    d_id = {}

    f1 = [i[field] for i in layer.getFeatures()]
    f2 = [i.id() for i in layer.getFeatures()]

    for i, j in zip(f1, f2):
        if i not in d_id:
            d_id[i] = []
        d_id[i].append(j)

    return d_id

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

    return ids
