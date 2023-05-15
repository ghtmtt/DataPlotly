"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'matteo.ghetta@gmail.com'
__date__ = '2017-03-05'
__copyright__ = 'Copyright 2017, matteo ghetta'

import os
import tempfile
import unittest

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsProperty,
    QgsPrintLayout,
    QgsReadWriteContext,
    QgsApplication
)

from DataPlotly.core.plot_settings import PlotSettings
from DataPlotly.gui.layout_item_gui import PlotLayoutItemWidget
from DataPlotly.gui.plot_settings_widget import DataPlotlyPanelWidget
from DataPlotly.layouts.plot_layout_item import PlotLayoutItem
from DataPlotly.layouts.plot_layout_item import PlotLayoutItemMetadata
from DataPlotly.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class DataPlotlyDialogTest(unittest.TestCase):
    """Test dialog works."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read_triggered = False

        self.plot_item_metadata = PlotLayoutItemMetadata()
        self.plot_item_gui_metadata = None
        QgsApplication.layoutItemRegistry().addLayoutItemType(self.plot_item_metadata)

    def test_get_settings(self):
        """
        Test retrieving settings from the dialog
        """
        dialog = DataPlotlyPanelWidget(None, override_iface=IFACE)
        settings = dialog.get_settings()
        # default should be scatter plot
        self.assertEqual(settings.plot_type, 'scatter')

        dialog.set_plot_type('violin')
        settings = dialog.get_settings()
        # default should be scatter plot
        self.assertEqual(settings.plot_type, 'violin')

    def test_set_default_settings(self):
        """
        Test setting dialog to a newly constructed settings object
        """
        settings = PlotSettings()
        dialog = DataPlotlyPanelWidget(None, override_iface=IFACE)
        dialog.set_settings(settings)

        self.assertEqual(dialog.get_settings().plot_type, settings.plot_type)
        for k in settings.properties.keys():
            if k in ['x', 'y', 'z', 'additional_hover_text', 'featureIds', 'featureBox', 'custom',
                     'marker_size', 'hover_text', 'hover_label_text']:
                continue

            self.assertEqual(dialog.get_settings().properties[k], settings.properties[k])
        for k in settings.layout.keys():
            self.assertEqual(dialog.get_settings().layout[k], settings.layout[k])

    def test_settings_round_trip(self):  # pylint: disable=too-many-statements
        """
        Test setting and retrieving settings results in identical results
        """
        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.geojson')

        vl1 = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        vl2 = QgsVectorLayer(layer_path, 'test_layer1', 'ogr')
        vl3 = QgsVectorLayer(layer_path, 'test_layer2', 'ogr')
        QgsProject.instance().addMapLayers([vl1, vl2, vl3])

        dialog = DataPlotlyPanelWidget(None, override_iface=IFACE)
        settings = dialog.get_settings()
        # default should be scatter plot
        self.assertEqual(settings.plot_type, 'scatter')
        # print('dialog loaded')

        # customise settings
        settings.plot_type = 'bar'
        settings.properties['name'] = 'my legend title'
        settings.properties['hover_text'] = 'y'
        settings.properties['box_orientation'] = 'h'
        settings.properties['normalization'] = 'probability'
        settings.properties['box_stat'] = 'sd'
        settings.properties['box_outliers'] = 'suspectedoutliers'
        settings.properties['violin_side'] = 'negative'
        settings.properties['show_mean_line'] = True
        settings.properties['cumulative'] = True
        settings.properties['invert_hist'] = 'decreasing'
        settings.source_layer_id = vl3.id()
        settings.properties['x_name'] = 'so4'
        settings.properties['y_name'] = 'ca'
        settings.properties['z_name'] = 'mg'
        settings.properties['color_scale'] = 'Earth'
        settings.properties['violin_box'] = True
        settings.properties['layout_filter_by_map'] = True
        settings.properties['layout_filter_by_atlas'] = True

        # TODO: likely need to test other settings.properties values here!

        settings.layout['legend'] = False
        settings.layout['legend_orientation'] = 'h'
        settings.layout['title'] = 'my title'
        settings.layout['x_title'] = 'my x title'
        settings.layout['y_title'] = 'my y title'
        settings.layout['z_title'] = 'my z title'
        settings.layout['font_title_size'] = 10
        settings.layout['font_title_family'] = "Arial"
        settings.layout['font_title_color'] = "#000000"
        settings.layout['font_xlabel_size'] = 10
        settings.layout['font_xlabel_family'] = "Arial"
        settings.layout['font_xlabel_color'] = "#000000"
        settings.layout['font_xticks_size'] = 10
        settings.layout['font_xticks_family'] = "Arial"
        settings.layout['font_xticks_color'] = "#000000"
        settings.layout['font_ylabel_size'] = 10
        settings.layout['font_ylabel_family'] = "Arial"
        settings.layout['font_ylabel_color'] = "#000000"
        settings.layout['font_yticks_size'] = 10
        settings.layout['font_yticks_family'] = "Arial"
        settings.layout['font_yticks_color'] = "#000000"
        settings.layout['range_slider']['visible'] = True
        settings.layout['bar_mode'] = 'overlay'
        settings.layout['x_type'] = 'log'
        settings.layout['y_type'] = 'category'
        settings.layout['x_inv'] = 'reversed'
        settings.layout['y_inv'] = 'reversed'
        settings.layout['bargaps'] = 0.8
        settings.layout['additional_info_expression'] = '1+2'
        settings.layout['bins_check'] = True
        settings.layout['gridcolor'] = '#bdbfc0'

        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                     QgsProperty.fromExpression('"ap">50'))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_MARKER_SIZE,
                                                     QgsProperty.fromExpression('5+64'))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_COLOR, QgsProperty.fromExpression("'red'"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_STROKE_WIDTH,
                                                     QgsProperty.fromExpression("12/2"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_title_', @some_var)"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_LEGEND_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_legend_', @some_var)"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_x_axis_', @some_var)"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_y_axis_', @some_var)"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_Z_TITLE,
                                                     QgsProperty.fromExpression("concat('my', '_z_axis_', @some_var)"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MIN, QgsProperty.fromExpression("-1*10"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_X_MAX, QgsProperty.fromExpression("+1*10"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MIN, QgsProperty.fromExpression("-1*10"))
        settings.data_defined_properties.setProperty(PlotSettings.PROPERTY_Y_MAX, QgsProperty.fromExpression("+1*10"))

        dialog2 = DataPlotlyPanelWidget(None, override_iface=IFACE)
        dialog2.set_settings(settings)

        # print('set settings')

        self.assertEqual(dialog2.get_settings().plot_type, settings.plot_type)
        for k in settings.properties.keys():
            # print(k)
            if k in ['x', 'y', 'z', 'additional_hover_text', 'featureIds', 'featureBox', 'custom']:
                continue
            self.assertEqual(dialog2.get_settings().properties[k], settings.properties[k])
        for k in settings.layout.keys():
            self.assertEqual(dialog2.get_settings().layout[k], settings.layout[k])
        self.assertEqual(dialog2.get_settings().source_layer_id, vl3.id())
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_FILTER))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_MARKER_SIZE))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_COLOR),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_COLOR))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_STROKE_WIDTH))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_X_MIN),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_X_MIN))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_X_MAX),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_X_MAX))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_Y_MIN))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_Y_MAX))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_TITLE),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_TITLE))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_LEGEND_TITLE))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_X_TITLE))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_Y_TITLE))
        self.assertEqual(dialog2.get_settings().data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE),
                         settings.data_defined_properties.property(PlotSettings.PROPERTY_Z_TITLE))

        dialog2.deleteLater()
        del dialog2

        settings = dialog.get_settings()
        dialog.deleteLater()
        del dialog

        dialog3 = DataPlotlyPanelWidget(None, override_iface=IFACE)
        # print('dialog 2')
        dialog3.set_settings(settings)
        # print('set settings')

        self.assertEqual(dialog3.get_settings().plot_type, settings.plot_type)
        for k in settings.properties.keys():
            # print(k)
            self.assertEqual(dialog3.get_settings().properties[k], settings.properties[k])
        self.assertEqual(dialog3.get_settings().properties, settings.properties)
        for k in settings.layout.keys():
            # print(k)
            self.assertEqual(dialog3.get_settings().layout[k], settings.layout[k])

        dialog3.deleteLater()
        del dialog3

        # print('done')
        QgsProject.instance().clear()
        # print('clear done')

    def test_settings_round_trip_secondary(self):  # pylint: disable=too-many-statements
        """
        Test setting and retrieving settings results in identical results -- this secondary test allows for
        different values to be checked (e.g. True if the first test checks for False)
        """
        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.geojson')

        vl1 = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        vl2 = QgsVectorLayer(layer_path, 'test_layer1', 'ogr')
        vl3 = QgsVectorLayer(layer_path, 'test_layer2', 'ogr')
        QgsProject.instance().addMapLayers([vl1, vl2, vl3])

        dialog = DataPlotlyPanelWidget(None, override_iface=IFACE)
        settings = dialog.get_settings()
        # default should be scatter plot
        self.assertEqual(settings.plot_type, 'scatter')
        # print('dialog loaded')

        # customise settings
        settings.plot_type = 'bar'
        settings.properties['violin_box'] = False

        dialog2 = DataPlotlyPanelWidget(None, override_iface=IFACE)
        dialog2.set_settings(settings)

        # print('set settings')

        self.assertEqual(dialog2.get_settings().plot_type, settings.plot_type)
        for k in settings.properties.keys():
            # print(k)
            if k in ['x', 'y', 'z', 'additional_hover_text', 'featureIds', 'featureBox', 'custom']:
                continue
            self.assertEqual(dialog2.get_settings().properties[k], settings.properties[k])
        for k in settings.layout.keys():
            self.assertEqual(dialog2.get_settings().layout[k], settings.layout[k])

        dialog2.deleteLater()
        del dialog2

        settings = dialog.get_settings()
        dialog.deleteLater()
        del dialog

        dialog3 = DataPlotlyPanelWidget(None, override_iface=IFACE)
        # print('dialog 2')
        dialog3.set_settings(settings)
        # print('set settings')

        self.assertEqual(dialog3.get_settings().plot_type, settings.plot_type)
        for k in settings.properties.keys():
            # print(k)
            self.assertEqual(dialog3.get_settings().properties[k], settings.properties[k])
        self.assertEqual(dialog3.get_settings().properties, settings.properties)
        for k in settings.layout.keys():
            # print(k)
            self.assertEqual(dialog3.get_settings().layout[k], settings.layout[k])

        dialog3.deleteLater()
        del dialog3

        # print('done')
        QgsProject.instance().clear()
        # print('clear done')

    @unittest.skip('causing crash?')
    def test_read_write_project(self):
        """
        Test saving/restoring dialog state in project
        """
        # print('read write project test')
        p = QgsProject.instance()
        dialog = DataPlotlyPanelWidget(None, override_iface=IFACE)
        dialog.set_plot_type('violin')

        # first, disable saving to project
        dialog.read_from_project = False
        dialog.save_to_project = False

        path = os.path.join(tempfile.gettempdir(), 'test_dataplotly_project.qgs')
        layer_path = os.path.join(
            os.path.dirname(__file__), 'test_layer.geojson')

        # create QgsVectorLayer from path and test validity
        vl = QgsVectorLayer(layer_path, 'test_layer', 'ogr')
        self.assertTrue(vl.isValid())

        # print(dialog.layer_combo.currentLayer())

        self.assertTrue(p.write(path))

        res = PlotSettings()

        # def read(doc):
        #    self.assertTrue(res.read_from_project(doc))
        #    self.assertEqual(res.plot_type, 'violin')
        #    self.read_triggered = True

        p.clear()
        for _ in range(100):
            QCoreApplication.processEvents()

        self.assertTrue(p.read(path))
        self.assertEqual(res.plot_type, 'scatter')

        # TODO - enable when dialog can restore properties and avoid this fragile test
        # # enable saving to project
        # dialog.save_to_project = True
        # dialog.read_from_project = True
        # self.assertTrue(p.write(path))
        # for _ in range(100):
        #     QCoreApplication.processEvents()

        # p.clear()

        # p.readProject.connect(read)
        # self.assertTrue(p.read(path))
        # for _ in range(100):
        #     QCoreApplication.processEvents()

        # self.assertTrue(self.read_triggered)

        # todo - test that dialog can restore properties, but requires the missing set_settings method
        dialog.x_combo.setExpression('"Ca"')
        dialog.layer_combo.setLayer(vl)

        dialog.x_combo.currentText()

        self.assertTrue(dialog.x_combo.expression(), '"Ca"')

    def test_read_write_project_with_layout(self):
        """
        Test saving/restoring dialog state of layout plot in project
        """
        # print('read write project with layout test')

        # create project and layout
        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        layout_name = "PrintLayoutReadWrite"
        layout.initializeDefaults()
        layout.setName(layout_name)
        layout_plot = PlotLayoutItem(layout)
        layout_plot.setId('plot_item')
        plot_item_id = layout_plot.id()
        self.assertEqual(len(layout_plot.plot_settings), 1)
        # self.assertEqual(len(layout.items()), 0)
        layout.addLayoutItem(layout_plot)
        # self.assertEqual(len(layout.items()), 1)
        plot_dialog = PlotLayoutItemWidget(None, layout_plot)

        # add second plot
        plot_dialog.add_plot()
        self.assertEqual(len(layout_plot.plot_settings), 2)

        # edit first plot
        plot_dialog.setDockMode(True)
        plot_dialog.show_properties()
        plot_property_panel = plot_dialog.panel
        plot_property_panel.set_plot_type('violin')
        self.assertEqual(plot_property_panel.ptype, 'violin')
        plot_property_panel.acceptPanel()
        plot_property_panel.destroy()

        # edit second plot
        plot_dialog.plot_list.setCurrentRow(1)
        plot_dialog.show_properties()
        plot_property_panel = plot_dialog.panel
        plot_property_panel.set_plot_type('bar')
        self.assertEqual(plot_property_panel.ptype, 'bar')
        plot_property_panel.acceptPanel()
        plot_property_panel.destroy()

        # write xml

        xml_doc = QDomDocument('layout')
        element = layout.writeXml(xml_doc, QgsReadWriteContext())

        layout_plot.remove_plot(0)
        self.assertEqual(len(layout_plot.plot_settings), 1)
        self.assertEqual(layout_plot.plot_settings[0].plot_type, 'bar')

        layout_plot.remove_plot(0)
        self.assertEqual(len(layout_plot.plot_settings), 0)

        # read xml
        layout2 = QgsPrintLayout(project)
        self.assertTrue(layout2.readXml(element, xml_doc, QgsReadWriteContext()))
        layout_plot2 = layout2.itemById(plot_item_id)
        self.assertTrue(layout_plot2)

        self.assertEqual(len(layout_plot2.plot_settings), 2)
        self.assertEqual(layout_plot2.plot_settings[0].plot_type, 'violin')
        self.assertEqual(layout_plot2.plot_settings[1].plot_type, 'bar')

    def test_move_chart_in_layout(self):
        """
        Test moving charts in layout plot up and down
        """
        # print('moving charts in layout plot up and down')

        # create project and layout
        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        layout_name = "PrintLayoutMovingUpDown"
        layout.initializeDefaults()
        layout.setName(layout_name)
        manager = project.layoutManager()
        self.assertEqual(True, manager.addLayout(layout))
        layout = manager.layoutByName(layout_name)
        layout_plot = PlotLayoutItem(layout)
        self.assertEqual(len(layout_plot.plot_settings), 1)
        # self.assertEqual(len(layout.items()), 0)
        layout.addLayoutItem(layout_plot)
        # self.assertEqual(len(layout.items()), 1)
        plot_dialog = PlotLayoutItemWidget(None, layout_plot)

        # add second plot
        plot_dialog.add_plot()
        self.assertEqual(len(layout_plot.plot_settings), 2)

        # edit first plot
        plot_dialog.setDockMode(True)
        plot_dialog.show_properties()
        plot_property_panel = plot_dialog.panel
        plot_property_panel.set_plot_type('violin')
        self.assertEqual(plot_property_panel.ptype, 'violin')
        plot_property_panel.acceptPanel()
        plot_property_panel.destroy()

        # edit second plot
        plot_dialog.plot_list.setCurrentRow(1)
        plot_dialog.show_properties()
        plot_property_panel = plot_dialog.panel
        plot_property_panel.set_plot_type('bar')
        self.assertEqual(plot_property_panel.ptype, 'bar')
        plot_property_panel.acceptPanel()
        plot_property_panel.destroy()

        # move up and down

        # cannot move up first item
        plot_dialog.plot_list.setCurrentRow(0)
        plot_dialog.move_up_plot()
        self.assertEqual(layout_plot.plot_settings[0].plot_type, 'violin')
        self.assertEqual(layout_plot.plot_settings[1].plot_type, 'bar')
        # move up second item
        plot_dialog.plot_list.setCurrentRow(1)
        plot_dialog.move_up_plot()
        self.assertEqual(layout_plot.plot_settings[0].plot_type, 'bar')
        self.assertEqual(layout_plot.plot_settings[1].plot_type, 'violin')

        # cannot move down second item
        plot_dialog.plot_list.setCurrentRow(1)
        plot_dialog.move_down_plot()
        self.assertEqual(layout_plot.plot_settings[0].plot_type, 'bar')
        self.assertEqual(layout_plot.plot_settings[1].plot_type, 'violin')
        # move down first item
        plot_dialog.plot_list.setCurrentRow(0)
        plot_dialog.move_down_plot()
        self.assertEqual(layout_plot.plot_settings[0].plot_type, 'violin')
        self.assertEqual(layout_plot.plot_settings[1].plot_type, 'bar')

        self.assertEqual(True, manager.removeLayout(layout))

    def test_duplicate_chart_in_layout(self):  # pylint: disable=too-many-statements
        """
        Test duplicate charts in layout plot up and down
        """
        print('duplicate charts in layout plot up and down')

        # create project and layout
        project = QgsProject.instance()
        layout = QgsPrintLayout(project)
        layout_name = "PrintLayoutDuplicatePlot"
        layout.initializeDefaults()
        layout.setName(layout_name)
        manager = project.layoutManager()
        self.assertEqual(True, manager.addLayout(layout))
        layout = manager.layoutByName(layout_name)
        layout_plot = PlotLayoutItem(layout)
        self.assertEqual(len(layout_plot.plot_settings), 1)
        # self.assertEqual(len(layout.items()), 0)
        layout.addLayoutItem(layout_plot)
        # self.assertEqual(len(layout.items()), 1)
        plot_dialog = PlotLayoutItemWidget(None, layout_plot)
        self.assertEqual(len(layout_plot.plot_settings), 1)

        # edit first plot
        plot_dialog.setDockMode(True)
        plot_dialog.show_properties()
        plot_property_panel = plot_dialog.panel
        plot_property_panel.set_plot_type('violin')
        self.assertEqual(plot_property_panel.ptype, 'violin')
        plot_property_panel.x_combo.setExpression('mid')
        plot_property_panel.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                                QgsProperty.fromExpression('"mid">20'))
        plot_property_panel.acceptPanel()
        plot_property_panel.destroy()

        # duplicate plot
        plot_dialog.duplicate_plot()
        self.assertEqual(len(layout_plot.plot_settings), 2)

        self.assertEqual(layout_plot.plot_settings[0].plot_type, 'violin')
        self.assertEqual(layout_plot.plot_settings[1].plot_type, 'violin')
        self.assertEqual((layout_plot.plot_settings[0]).properties['x_name'], 'mid')
        self.assertEqual((layout_plot.plot_settings[1]).properties['x_name'], 'mid')
        self.assertEqual(layout_plot.plot_settings[0].data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         QgsProperty.fromExpression('"mid">20'))
        self.assertEqual(layout_plot.plot_settings[1].data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         QgsProperty.fromExpression('"mid">20'))

        # edit second plot
        plot_dialog.plot_list.setCurrentRow(1)
        plot_dialog.show_properties()
        plot_property_panel = plot_dialog.panel
        plot_property_panel.set_plot_type('bar')
        self.assertEqual(plot_property_panel.ptype, 'bar')
        plot_property_panel.x_combo.setExpression('qid')
        plot_property_panel.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                                QgsProperty.fromExpression('"qid">20'))
        plot_property_panel.acceptPanel()
        plot_property_panel.destroy()

        self.assertEqual(layout_plot.plot_settings[0].plot_type, 'violin')
        self.assertEqual(layout_plot.plot_settings[1].plot_type, 'bar')
        self.assertEqual((layout_plot.plot_settings[0]).properties['x_name'], 'mid')
        self.assertEqual((layout_plot.plot_settings[1]).properties['x_name'], 'qid')
        self.assertEqual(layout_plot.plot_settings[0].data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         QgsProperty.fromExpression('"mid">20'))
        self.assertEqual(layout_plot.plot_settings[1].data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         QgsProperty.fromExpression('"qid">20'))

        # edit first plot
        plot_dialog.plot_list.setCurrentRow(0)
        plot_dialog.show_properties()
        plot_property_panel = plot_dialog.panel
        plot_property_panel.set_plot_type('scatter')
        self.assertEqual(plot_property_panel.ptype, 'scatter')
        plot_property_panel.x_combo.setExpression('uid')
        plot_property_panel.data_defined_properties.setProperty(PlotSettings.PROPERTY_FILTER,
                                                                QgsProperty.fromExpression('"uid">20'))
        plot_property_panel.acceptPanel()
        plot_property_panel.destroy()

        self.assertEqual(layout_plot.plot_settings[0].plot_type, 'scatter')
        self.assertEqual(layout_plot.plot_settings[1].plot_type, 'bar')
        self.assertEqual((layout_plot.plot_settings[0]).properties['x_name'], 'uid')
        self.assertEqual((layout_plot.plot_settings[1]).properties['x_name'], 'qid')
        self.assertEqual(layout_plot.plot_settings[0].data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         QgsProperty.fromExpression('"uid">20'))
        self.assertEqual(layout_plot.plot_settings[1].data_defined_properties.property(PlotSettings.PROPERTY_FILTER),
                         QgsProperty.fromExpression('"qid">20'))

        self.assertEqual(True, manager.removeLayout(layout))


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(DataPlotlyDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
