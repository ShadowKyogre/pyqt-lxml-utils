from PyQt4 import QtCore, QtGui
from lxml import etree, objectify

from collections import defaultdict

from .models import NodeModel, StringDictModel, XPathModel
from .delegates import ElementDelegate

class DeckDelegate(ElementDelegate):
	def __init__(self, parent=None):
		eltypes = defaultdict(lambda: {
					'paint' : self.paintDeck,
					'sizeHint' : self.sizeHintDeck,
				})
		super().__init__(parent=parent, eltypes=eltypes)
	
	def textForElement(self, el):
		if el.tag == 'deck':
			return  "Deck - {}".format(el.attrib.get('name', '{no name}'))
		elif el.tag == 'author':
			return  "Author - {}".format(str(el.text))
		elif el.tag == 'source':
			return  "Source - {}".format(str(el.text))
		elif el.tag == 'suit':
			return  "Suit - {}".format(el.attrib.get('name', '{no name}'))
		elif el.tag == 'card':
			return  "Card - {}".format(el.attrib.get('name', '{no name}'))
		else:
			return "<unknown element>"

	def paintDeck(self, painter, option, index, el):
		painter.save()
		r = option.rect
		if option.state & QtGui.QStyle.State_Selected:
			bg_color = self.parent().palette().highlight()
			text_color = self.parent().palette().color(QtGui.QPalette.HighlightedText)
		else:
			bg_color = self.parent().palette().base()
			text_color = self.parent().palette().color(QtGui.QPalette.Text)
		painter.setBrush(bg_color)
		painter.fillRect(r, bg_color)
		fontPen = QtGui.QPen(text_color, 1, QtCore.Qt.SolidLine)
		painter.setFont(self.parent().font())
		painter.setPen(fontPen)
		painter.drawText(r.left(), r.top(), r.width(), r.height(), 
				QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeft, self.textForElement(el))
		painter.restore()

	def sizeHintDeck(self, option, index, el):
		return QtGui.QFontMetrics(self.parent().font()).boundingRect(self.textForElement(el)).size()

def main():
	app = QtGui.QApplication([])
	tabs = QtGui.QTabWidget()
	table = QtGui.QTableView()
	tree = QtGui.QTreeView()
	xpath_sample = QtGui.QListView()
	delegate=DeckDelegate(tree)
	tree.setItemDelegate(delegate)
	test="""
<deck name='a sample deck' mememe='no' sss='yes'>
	<author>ShadowKyogre</author>
	<source>Durp durp durp</source>
	<suit name='s'>
		<card name='dip'></card>
	</suit>
	<suit name='sip'>
		<card name='dip'></card>
	</suit>
</deck>
"""
	durp_xml = objectify.fromstring(test)
	dict_model = StringDictModel(durp_xml.attrib)
	xpath_model = XPathModel(durp_xml,'/deck/suit')
	model = NodeModel(durp_xml)
	table.setModel(dict_model)
	xpath_sample.setModel(xpath_model)
	table.verticalHeader().setVisible(False)
	table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
	tree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
	table.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
	#tree.setDragEnabled(True)
	tree.setModel(model)
	tabs.addTab(tree, 'LXML model test')
	tabs.addTab(xpath_sample, 'XPath model test')
	tabs.addTab(table, 'Dict model test')
	tabs.show()
	exit(app.exec())

main()
