
__revision__  = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2002 Open Source Applications Foundation"
__license__   = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

from cStringIO import StringIO

from repository.item.ItemRef import RefDict
from repository.item.Indexes import NumericIndex
from repository.util.UUID import UUID


class XMLRefDict(RefDict):

    def __init__(self, view, item, name, otherName, readOnly):
        
        self._item = None
        self._uuid = UUID()
        self.view = view
        self._changedRefs = {}
        
        super(XMLRefDict, self).__init__(item, name, otherName, readOnly)

    def _getRepository(self):

        return self.view

    def _getRefs(self):

        return self.view.repository.store._refs

    def _loadRef(self, key):

        view = self.view
        
        if view is not view.repository.view:
            raise RepositoryError, 'current thread is not owning thread'

        try:
            if self._changedRefs[key][0] == 1:
                return None
        except KeyError:
            pass

        return self._getRefs().loadRef(self._key, self._item._version, key)

    def _changeRef(self, key, alias=None, noMonitors=False):

        super(XMLRefDict, self)._changeRef(key, alias, noMonitors)

        if not self.view.isLoading():
            self._changedRefs[key] = (0, alias)
        
    def _removeRef(self, key, _detach=False):

        link = super(XMLRefDict, self)._removeRef(key, _detach)

        if not self.view.isLoading():
            self._changedRefs[key] = (1, link._alias)
        else:
            raise ValueError, 'detach during load'

    def _writeRef(self, key, version, previous, next, alias):

        self._getRefs().saveRef(self._key, self._value, version, key,
                                previous, next, alias)

    def _deleteRef(self, key, version):

        self._getRefs().deleteRef(self._key, self._value, version, key)

    def _eraseRef(self, key):

        self._getRefs().eraseRef(self._key, key)

    def resolveAlias(self, alias, load=True):

        load = load and not self._item.isNew()
        key = None
        
        if self._aliases:
            key = self._aliases.get(alias)

        if load and key is None:
            view = self.view
            key = view.repository.store.readName(view.version, self._uuid,
                                                 alias)

        return key

    def _setItem(self, item):

        if self._item is not None and self._item is not item:
            raise ValueError, 'Item is already set'
        
        self._item = item
        if item is not None:
            self._prepareBuffers(item._uuid, self._uuid)

    def _prepareBuffers(self, uItem, uuid):

        self._uuid = uuid
        self._key = self._getRefs().prepareKey(uItem, uuid)
        self._value = StringIO()

    def _xmlValues(self, generator, version, mode):

        if mode == 'save':
            store = self.view.repository.store
            for key, (op, oldAlias) in self._changedRefs.iteritems():
                try:
                    value = self._get(key, load=False)
                except KeyError:
                    value = None
    
                if op == 0:               # change
                    if value is not None:
                        ref = value._value
                        previous = value._previousKey
                        next = value._nextKey
                        alias = value._alias
    
                        self._writeRef(key, version, previous, next, alias)
                        if oldAlias is not None:
                            store.writeName(version, self._uuid, oldAlias,
                                            None)
                        if alias is not None:
                            store.writeName(version, self._uuid, alias,
                                            key)
                        
                elif op == 1:             # remove
                    self._deleteRef(key, version)
                    if oldAlias is not None:
                        store.writeName(version, key, oldAlias, None)

                else:                     # error
                    raise ValueError, op

            if self._changedRefs:
                self.view._notifications.changed(self._item._uuid, self._name)

            self._changedRefs.clear()
            
            if len(self) > 0:
                generator.startElement('db', {})
                generator.characters(self._uuid.str64())
                generator.endElement('db')

            if self._indexes:
                for name, index in self._indexes.iteritems():
                    attrs = { 'name': name, 'type': index.getIndexType() }
                    index._xmlValues(generator, version, attrs, mode)

        elif mode == 'serialize':
            super(XMLRefDict, self)._xmlValues(generator, version, mode)

        else:
            raise ValueError, mode

    def _createIndex(self, indexType, **kwds):

        if indexType == 'numeric':
            return XMLNumericIndex(self._getRepository(), **kwds)

        return super(XMLRefDict, self)._createIndex(indexType, **kwds)


class XMLNumericIndex(NumericIndex):

    def __init__(self, view, **kwds):

        self.view = view
        self._changedKeys = {}
        
        if 'uuid' in kwds:
            self._uuid = UUID(kwds['uuid'])
            self._headKey = UUID(kwds['head'])
            self._tailKey = UUID(kwds['tail'])
        else:
            self._uuid = UUID()
            self._headKey = UUID()
            self._tailKey = UUID()

        self._key = self._getIndexes().prepareKey(self._uuid)
        self._value = StringIO()
        self._version = 0
        
        super(XMLNumericIndex, self).__init__(**kwds)

    def _keyChanged(self, key):

        self._changedKeys[key] = self[key]

    def removeKey(self, key):

        super(XMLNumericIndex, self).removeKey(key)
        self._changedKeys[key] = None

    def __getitem__(self, key):

        try:
            return super(XMLNumericIndex, self).__getitem__(key)
        except KeyError:
            if self._loadKey(key):
                return super(XMLNumericIndex, self).__getitem__(key)
            raise

    def __contains__(self, key):

        return self.has_key(key)

    def has_key(self, key):

        has = super(XMLNumericIndex, self).has_key(key)
        if not has:
            node = self._loadKey(key)
            has = node is not None

        return has

    def get(self, key, default=None):

        node = super(XMLNumericIndex, self).get(key, default)
        if node is default:
            node = self._loadKey(key)
            if node is None:
                node = default

        return node

    def isPersistent(self):

        return True

    def _restore(self, version):

        indexes = self._getIndexes()
        
        self._version = version
        self._head = indexes.loadKey(self, self._key, version, self._headKey)
        self._tail = indexes.loadKey(self, self._key, version, self._tailKey)

    def _loadKey(self, key):

        node = None
        version = self._version

        if version > 0:
            try:
                if self._changedKeys[key] is None:   # removed key
                    return None
            except KeyError:
                pass

            node = self._getIndexes().loadKey(self, self._key, version, key)
            if node is not None:
                self[key] = node

        return node

    def _getIndexes(self):

        return self.view.repository.store._indexes

    def _xmlValues(self, generator, version, attrs, mode):

        attrs['count'] = str(len(self))
        attrs['uuid'] = self._uuid.str64()
        attrs['head'] = self._headKey.str64()
        attrs['tail'] = self._tailKey.str64()

        super(XMLNumericIndex, self)._xmlValues(generator, version, attrs,
                                                mode)

        if mode == 'save':
            indexes = self._getIndexes()

            indexes.saveKey(self._key, self._value,
                            version, self._headKey, self._head)
            indexes.saveKey(self._key, self._value,
                            version, self._tailKey, self._tail)
            for key, node in self._changedKeys.iteritems():
                indexes.saveKey(self._key, self._value,
                                version, key, node)

            self._changedKeys.clear()
            self._version = version
            
        elif mode == 'serialize':
            raise NotImplementedError, 'serialize'

        else:
            raise ValueError, mode
        
