from PyQt4 import QtCore
from lxml import etree, objectify
#http://www.hardcoded.net/articles/using_qtreeview_with_qabstractitemmodel

class NodeModel(QtCore.QAbstractItemModel):
	def __init__(self, xmlobj, parser=None, validator=None):
		QtCore.QAbstractItemModel.__init__(self)
		self.xmlobj=xmlobj
		self.cache=list(self.xmlobj.iter())
		self._dragged_up = False

	def index(self, row, column, parent):
		#print(row, column, parent, parent.isValid())
		if not parent.isValid():
			if row >= self.xmlobj.countchildren():
				return QtCore.QModelIndex()
			data=self.xmlobj.getchildren()[row]
			#if data not in self.cache:
			#	print('might be garbage collected, adding it')
			self.cache.append(data)
			return self.createIndex(row, column, data)
		parentNode = parent.internalPointer()
		#print(parentNode.getchildren())
		if row >= parentNode.countchildren():
				return QtCore.QModelIndex()
		data=parentNode.getchildren()[row]
		#print(parentNode.tag, row, parentNode.countchildren())
		#print(data.tag)
		#if data not in self.cache:
		#	print('might be garbage collected, adding it')
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
		if row < 0 or row >= pnode.countchildren(): return False
		if self._dragged_up:
			items = pnode.getchildren()[row+1:row+1+count]
		else:
			items = pnode.getchildren()[row:row+count]
		#print(items)
		#print(self.index(row, 1, parent).internalPointer().getchildren()[row:row+count])
		self.beginRemoveRows(parent, row, row+count-1)
		for i in items:
			print('deleting',i.tag,i.attrib,'in',pnode.tag)
			pnode.remove(i)
			#self.cache.remove(i)
		#print(etree.tostring(self.xmlobj))
		self.endRemoveRows()
		self.dataChanged.emit(parent, parent)
		return True

	def mimeTypes(self):
		return ['lxml-objects']


	def supportedDropActions(self):
		return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction


	def mimeData( self, indices ):
		mimedata = QtCore.QMimeData()
		#print(indices)
		items = [idx.internalPointer() for idx in indices]
		wrapper='<wrapper prev_row="{}" prev_parent="{}">{}</wrapper>'
		str_items = '\n'.join([etree.tostring(i).decode('utf-8') for i in items])
		#print([etree.tostring(i) for i in items])
		prev_parent=self.xmlobj.getroottree().getpath(items[0].getparent())
		stuff = wrapper.format(indices[0].row(), prev_parent, str_items )
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
		prev_parent = data.attrib['prev_parent']
		place = self.index(row, column, parent).internalPointer()
		if place is None:
			new_parent = self.xmlobj.getroottree().getpath(self.xmlobj.getroottree().getroot())
		else:
			new_parent = self.xmlobj.getroottree().getpath(place.getparent())
		print(prev_parent, new_parent)
		if int(data.attrib['prev_row']) > row and prev_parent == new_parent:
			self._dragged_up = True
		else:
			self._dragged_up = False
		#print(row,column,items,etree.tostring(data),parent.internalPointer())
		return self.insertItems(row, items, parent)

	def insertItem(self, row, parent):
		return self.insertItems(row, [item], parent)

	def insertItems(self, row, items, parent):
		if not parent.isValid():
			pnode = self.xmlobj
		else:
			pnode = parent.internalPointer()
		self.beginInsertRows( parent, row, row+len(items)-1 )
		print(pnode.tag, row)
		print(etree.tostring(self.xmlobj))
		#print(row, items, pnode.tag)
		el = items[0]
		if row == -1:
			other_sib = pnode.getchildren()[-1]
			other_sib.addnext(el)
		else:
			if row >= pnode.countchildren():
				other_sib = pnode.getchildren()[-1]
				other_sib.addnext(el)
			else:
				other_sib = pnode.getchildren()[row]
				other_sib.addprevious(el)
		#pnode.insert(row, el)
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

class StringDictModel(QtCore.QAbstractTableModel):
	def __init__(self, dicty={}):
		QtCore.QAbstractItemModel.__init__(self)
		self.dicty=dicty
		self.sorted_keys = list(sorted(self.dicty.keys()))
	def data(self, index, role):
		if not index.isValid(): return None
		self.sorted_keys = list(sorted(self.dicty.keys()))
		key=self.sorted_keys[index.row()]
		if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
			if index.column() == 1:
				return str(self.dicty.get(key))
			else:
				return str(key)
		return None
	def flags(self, index):
		if not index.isValid():
				return None
		else:
				return QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable
	def setData(self, index, value, role):
		if not index.isValid(): return None
		print(index.column())
		if role == QtCore.Qt.EditRole:
			if index.column() == 0:
				key = index.data(role)
				preserved_val = self.dicty[key]
				del self.dicty[key]
				self.dicty[value]=preserved_val
			else:
				key = self.index(index.row(), 0).data(role)
				self.dicty[key] = value
			return True
		else: return False
	def rowCount(self, parent):
			return len(self.sorted_keys)
	def columnCount(self, parent):
			return 2

if __name__ == '__main__':
	from PyQt4 import QtGui
	app = QtGui.QApplication([])
	tabs = QtGui.QTabWidget()
	table = QtGui.QTableView()
	tree = QtGui.QTreeView()
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
	model = NodeModel(durp_xml)
	table.setModel(dict_model)
	table.verticalHeader().setVisible(False)
	table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
	tree.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
	table.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked)
	#tree.setDragEnabled(True)
	tree.setModel(model)
	tabs.addTab(tree, 'LXML model test')
	tabs.addTab(table, 'Dict model test')
	tabs.show()
	exit(app.exec())
