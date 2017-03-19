# aggiungere un oggetto direttamente da codice e non da Designer
# va messo in __init__

self.labell = QLabel(self)
self.labell.setText("Dio")
self.labell.setAlignment(QtCore.Qt.AlignCenter)

# qui l'inghippo perché bisogna aggiungere anche i vari tab al layout
vbox = QVBoxLayout()
vbox.addWidget(self.labell)
vbox.addWidget(self.tab_property)
self.setLayout(vbox)
