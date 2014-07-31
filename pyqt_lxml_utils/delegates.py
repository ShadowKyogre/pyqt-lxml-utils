from PyQt4 import QtCore, QtGui
from collections import defaultdict

class ElementDelegate(QtGui.QAbstractItemDelegate):
	def __init__(self, parent=None, eltypes={}):
		super().__init__(parent)
		self.eltypes=eltypes

	def paint(self, painter, option, index):
		el = index.internalPointer()
		default = self.eltypes[el.tag]
		return default['paint'](painter, option, index, el)

	def sizeHint(self, option, index):
		el = index.internalPointer()
		default = self.eltypes[el.tag]
		return default['sizeHint'](option, index, el)
