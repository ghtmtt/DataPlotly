from PyQt5 import QtCore, QtGui
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtCore import QUrl
from qgis.utils import iface

loadTest = """
plotWebView.log('Page loaded : ' + plotWebView.url);
"""

class plotWebView(QWebView):
    def __init__(self, parent=None):
        super(plotWebView, self).__init__(parent)

        self.page().mainFrame().addToJavaScriptWindowObject("plotWebView", self)

        self.iface = iface


    def loadUrl(self, url):
        print('carico')
        self.load(QUrl.fromLocalFile(url))
        print('finito')
