from PyQt4 import QtCore
#http://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel

class LXMLModel(QtCore.QAbstractItemModel):
	def __init__(self, xmlobj):
		QtCore.QAbstractItemModel.__init__(self)
		self.xmlobj=xmlobj
		self.cache=list(self.xmlobj.iter())

	def index(self, row, column, parent):
		print(row, column, parent, parent.isValid())
		if not parent.isValid():
			data=self.xmlobj.getchildren()[row]
			if data not in cache:
				self.cache.append(data)
			return self.createIndex(row, column, data)
		parentNode = parent.internalPointer()
		#print(parentNode.getchildren())
		data=parentNode.getchildren()[row]
		if data not in cache:
			self.cache.append(data)
		return self.createIndex(row, column, data)

	def parent(self, index):
		#print('child', index)
		if not index.isValid():
			return QtCore.QModelIndex()
		node = index.internalPointer()
		if node.getparent() is None:
			return QtCore.QModelIndex()
		else:
			parent=node.getparent()
			grandparent=parent.getparent()
			if grandparent is None:
				return self.createIndex(parent.index(node), 0, parent)
			else:
				return self.createIndex(grandparent.index(parent), 0, parent)

	def reset(self):
		for i in self.xmlobject.iterchildren():
			self.xmlobject.remove(i)
		QtCore.QAbstractItemModel.reset(self)

	def rowCount(self, parent):
		#print('rowcount', parent, parent.isValid())
		if not parent.isValid():
			#print('counting root stuff', self.xmlobj.countchildren())
			return self.xmlobj.countchildren()
		#print('bx')
		node = parent.internalPointer()
		#print(node)
		return node.countchildren()
	
	def data(self, index, role):
		#print('data', index, role)
		if not index.isValid():
			return None
		node = index.internalPointer()
		if role == QtCore.Qt.DisplayRole:
			return node.tag+' - '+node.attrib.get('name', str(node.text))
		return None

	def columnCount(self, parent):
		return 1
