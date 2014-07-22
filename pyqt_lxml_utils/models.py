from PyQt4 import QtCore
from lxml import etree, objectify
#http://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel

class NodeModel(QtCore.QAbstractItemModel):
	def __init__(self, xmlobj, parser=None, validator=None):
		QtCore.QAbstractItemModel.__init__(self)
		self.xmlobj=xmlobj
		self.cache=list(self.xmlobj.iter())

	def index(self, row, column, parent):
		#print(row, column, parent, parent.isValid())
		if not parent.isValid():
			if row > self.xmlobj.countchildren():
				return QtCore.QModelIndex()
			data=self.xmlobj.getchildren()[row]
			if data not in self.cache:
				self.cache.append(data)
			return self.createIndex(row, column, data)
		parentNode = parent.internalPointer()
		#print(parentNode.getchildren())
		if row >= parentNode.countchildren():
				return QtCore.QModelIndex()
		data=parentNode.getchildren()[row]
		if data not in self.cache:
			self.cache.append(data)
		return self.createIndex(row, column, data)

	def flags(self, index):
		if index.isValid():
			return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsDropEnabled
		else:
			return QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsDropEnabled

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
		#for i in self.xmlobject.iterchildren():
		#	self.xmlobject.remove(i)
		QtCore.QAbstractItemModel.reset(self)

	def removeRows(self, row, count, parent):
		print('removing stuff', row, count, parent)
		if not parent.isValid():
			pnode = self.xmlobject
		else:
			pnode = parent.internalPointer()
		if row < 0 or row > pnode.countchildren(): return False
		items = pnode.getchildren()[row:row+count]
		self.beginRemoveRows(parent, row, row+count-1)
		for i in items:
			print('deleting',i.tag,i.attrib,'in',pnode.tag)
			pnode.remove(i)
			self.cache.remove(i)
		self.endRemoveRows()
		return True

	def mimeTypes(self):
		return ['lxml-objects']


	def supportedDropActions(self):
		return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction


	def mimeData( self, indices ):
		mimedata = QtCore.QMimeData()
		print(indices)
		items = [idx.internalPointer() for idx in indices]
		wrapper='<wrapper>{}</wrapper>'
		print([etree.tostring(i) for i in items])
		stuff = wrapper.format('\n'.join([etree.tostring(i).decode('utf-8') for i in items] ))
		mimedata.setData('lxml-objects',stuff)
		return mimedata

	def dropMimeData( self, mimedata, action, row, column, parent ):
		#print(mimedata.hasText())
		if not mimedata.hasFormat('lxml-objects'):
			return False
		if isinstance(self.xmlobj, objectify.ObjectifiedElement):
			data = objectify.fromstring(mimedata.data('lxml-objects').data())
		else:
			data = etree.fromstring( mimedata.data('lxml-objects').data())
		items = data.getchildren()
		#print(row,column,items,etree.tostring(data),parent.internalPointer())
		self.insertItems(row, items, parent)
		return True

	def insertItems(self, row, items, parent):
		if not parent.isValid():
			pnode = self.xmlobj
		else:
			pnode = parent.internalPointer()
		self.beginInsertRows( parent, row, row+len(items)-1 )
		print(row, items, pnode.tag)
		if row == -1:
			pnode.extend(items)
		else:
			el = items[0]
			pnode.insert(row, el)
			for i in items[1:]:
				el.addnext(i)
				el = i
		print(etree.tostring(self.xmlobj))
		self.endInsertRows()
		self.dataChanged.emit(parent, parent)
		return True

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

class AttrModel(QtCore.QAbstractItemModel):
	def __init__(self, xmlobj):
		QtCore.QAbstractItemModel.__init__(self)

if __name__ == '__main__':
	from PyQt4 import QtGui
	app = QtGui.QApplication([])
	tree = QtGui.QTreeView()
	test="""
<deck>
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
	model = NodeModel(objectify.fromstring(test))
	tree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
	tree.setDragEnabled(True)
	tree.setModel(model)
	tree.show()
	exit(app.exec())
