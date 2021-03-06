#   Copyright (c) 2003-2007 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from new import classobj

from chandlerdb.util.c import \
    UUID, _hash, _combine, isuuid, Nil, Default
from chandlerdb.persistence.c import Record
from chandlerdb.schema.c import CDescriptor, CAttribute, CKind
from chandlerdb.item.c import isitem, CItem, isitemref, ItemRef, ItemValue
from chandlerdb.item.ItemError import NoSuchAttributeError

from chandlerdb.item.Item import Item, MissingClass, override
from chandlerdb.item.RefCollections import RefList
from chandlerdb.item.Sets import AbstractSet
from chandlerdb.item.Values import Values, References
from chandlerdb.item.PersistentCollections import PersistentCollection
from chandlerdb.util.Path import Path
from chandlerdb.schema.TypeHandler import TypeHandler
from chandlerdb.schema.Correlation import Correlation
from chandlerdb.persistence.RepositoryError import RecursiveLoadItemError

CORE=Path('//Schema/Core')


class Kind(Item):

    def __init__(self, *args, **kw):

        super(Kind, self).__init__(*args, **kw)
        self.__init()
        self._createExtent(self.itsView)

    def __init(self):

        if self.c is None:
            self.c = CKind(self)

        self._initialValues = None
        self._initialReferences = None
        self.c.notify = True

        self._status |= Item.SCHEMA

    @override(Item)
    def _fillItem(self, name, parent, kind, uuid, view,
                  values, references, status, version, hooks, update):

        super(Kind, self)._fillItem(name, parent, kind, uuid, view,
                                    values, references, status, version,
                                    hooks, update)
        if not update:
            self.__init()
            if self._references.get('extent') is None:
                hooks.append(self._createExtent)

        self.flushCaches('unload', False)        

    def onViewClear(self, view):

        c = self.c
        c.descriptors.clear()
        c.descriptorsInstalled = False

    def _createExtent(self, view):

        core = view.find(CORE)
        extent = Extent(None, core['extents'], core['Extent'],
                        fireChanges=False)
        self._references._setValue('extent', extent, 'kind')

        return extent

    def _setupDescriptors(self, sync=None):

        c = self.c

        if not c.descriptorsInstalling:
            c.descriptorsInstalling = True
        else:
            return True

        try:
            try:
                withSchema = self._isWithSchema()

                descriptors = c.descriptors
                attributes = dict((a.itsUUID, (n, a))
                                  for n, a, k in self.iterAttributes())
            
                if sync is not None:
                    for name, descriptor in descriptors.items():
                        if descriptor.attr.attrID not in attributes:
                            del descriptors[name]

                for name, attribute in attributes.itervalues():
                    if descriptors.get(name, None) is None:
                        descriptors[name] = CDescriptor(name, attribute.c)
                        if withSchema and not attribute._isWithSchema():
                            attribute._status |= CItem.WITHSCHEMA

                c.descriptorsInstalled = True
                return True

            except RecursiveLoadItemError:
                return False

        finally:
            c.descriptorsInstalling = False

    def _setupClass(self, cls):

        c = self.c

        if not c.descriptorsInstalled:
            if self._setupDescriptors():
                if self._status & CItem.CORESCHEMA:
                    cls.__core_schema__ = c.descriptors
            else:
                return False

        uuid = self.itsUUID
        kinds = Kind._kinds
        classes = Kind._classes

        clss = kinds.get(uuid)
        if clss is None:
            kinds[uuid] = set((cls,))
            self._setupDelegates(cls)
        elif cls not in clss:
            clss.add(cls)
            self._setupDelegates(cls)

        uuids = classes.get(cls)
        if uuids is None:
            classes[cls] = set((uuid,))
        else:
            uuids.add(uuid)

        c.monitorSchema = True

        return True

    def _setupDelegates(self, cls):

        delegates = getattr(cls, '__delegates__', None)
        if delegates:
            for delegate in delegates:
                attribute = self.getAttribute(delegate)
                cardinality = attribute.getAspect('cardinality', 'single')
                if cardinality == 'single':
                    type = attribute.type.getImplementationType()
                elif (cardinality == 'list' and
                      self.getOtherName(delegate, None, None) is not None):
                    type = RefList
                elif (cardinality == 'set' and
                      self.getOtherName(delegate, None, None) is not None):
                    type = AbstractSet
                else:
                    raise NotImplementedError, ('value delegate', delegate)

                for name in dir(type):
                    if (not hasattr(cls, name) and
                        callable(getattr(type, name))):
                        setattr(cls, name, DelegateDescriptor(name, delegate))

    def newItem(self, name=None, parent=None, cls=None, **values):
        """
        Create an new item of this kind.

        The python class instantiated is taken from the Kind's classes
        attribute if it is set. The Item class is used otherwise.

        The item's constructor is invoked.

        @param name: The name of the item. It must be unique among the names
        this item's siblings. C{name} may be C{None}.
        @type name: a string or C{None} to create an anonymous item.
        @param parent: The parent of this item. C{parent} is
        optional. When ommitted, the item is made a root of either the
        C{kind}'s view or of the global null view.
        @type parent: an item or the item's repository view
        @param cls: an optional python class to instantiate the item with,
        defaults to the class set on this kind.
        @type cls: a python new style class, that is, a type instance
        """

        if cls is None:
            cls = self.getItemClass()
        
        return cls(name, parent, self, **values)

    def instantiateItem(self, name, parent, uuid,
                        cls=None, version=0, withInitialValues=False,
                        fireChanges=True, **values):
        """
        Instantiate an existing item of this kind.

        This method is intended to help in instantiating an existing item,
        that is an item in this or another repository for which there
        already exists a UUID.

        The item's constructor is not invoked, the item's onItemLoad
        method is invoked if defined.

        @param name: The name of the item. It must be unique among the names
        this item's siblings. C{name} may be C{None}.
        @type name: a string or C{None} to create an anonymous item.
        @param parent: The parent of this item. All items require a parent
        unless they are a repository root in which case C{parent} is a
        repository view.
        @type parent: an item or the item's repository view
        @param uuid: The uuid for the item.
        @type uuid: L{UUID<chandlerdb.util.c.UUID>}
        @param cls: an optional python class to instantiate the item with,
        defaults to the class set on this kind.
        @type cls: a python new style class, that is, a type instance
        @param version: the optional version of this item instance, zero by
        default.
        @type version: integer
        @param withInitialValues: optionally set the initial values for
        attributes as specified in this Kind's attribute definitions.
        @type withInitialValues: boolean
        """

        if cls is None:
            cls = self.getItemClass()

        item = cls.__new__(cls)
        item._fillItem(name, parent, self, uuid, self.itsView,
                       Values(), References(), 0, version,
                       [], False)

        self._setupClass(cls)

        if withInitialValues:
            self.getInitialValues(item, False)

        if values:
            try:
                item._status |= CItem.NODIRTY
                item._setInitialValues(values, fireChanges)
            finally:
                item._status &= ~CItem.NODIRTY
            
        if hasattr(cls, 'onItemLoad'):
            item.onItemLoad(self.itsView)

        if fireChanges:
            self.itsView._notifyChange(self.extent._collectionChanged,
                                       'add', 'collection', 'extent',
                                       item.itsUUID, ())

        return item
            
    def getItemClass(self):
        """
        Return the class used to create items of this Kind.

        If this Kind has superKinds and C{self.classes['python']} is not set
        a composite class is generated and cached from the superKinds.

        The L{Item<chandlerdb.item.Item.Item>} class is returned by default.
        """

        missing = False
        try:
            cls = self._values['classes']['python']
            if cls is not MissingClass:
                return cls
            missing = True
        except KeyError:
            pass
        except TypeError:
            pass

        superClasses = []
        
        for superKind in self._references.get('superKinds', Nil):
            c = superKind.getItemClass()
            if c is not Item and c not in superClasses:
                superClasses.append(c)

        count = len(superClasses)

        if count == 0:
            c = self.itsView.classLoader.getItemClass()

        elif count == 1:
            c = superClasses[0]

        else:
            # Filter out redundant superclasses that may cause MRO wonkiness.
            # A redundant superclass is one with a subclass occurring later
            # in the superclass list.
            classes = superClasses
            superClasses = []
            while classes:
                cls = classes.pop(0)
                for c in classes:
                    if issubclass(c, cls):
                        break
                else:
                    superClasses.append(cls)

            hash = 0
            for c in superClasses:
                hash = _combine(hash, _hash('.'.join((c.__module__,
                                                      c.__name__))))
            if hash < 0:
                hash = ~hash
            name = "class_%08x" %(hash)
            c = classobj(name, tuple(superClasses), {})

        self._values['classes'] = { 'python': c }
        self._values._setTransient('classes')
        self._setupClass(c)

        if missing:
            self.itsView.logger.warn('Missing class for Kind %s replaced by %s.%s', self.itsPath, c.__module__, c.__name__)

        return c

    def check(self, recursive=False, repair=False):

        result = super(Kind, self).check(recursive, repair)
        
        if not self.getAttributeValue('superKinds', self._references):
            if self is not self.getItemKind():
                self.itsView.logger.warn('No superKinds for %s', self.itsPath)
                result = False

        itemClass = self.getItemClass()
        result = self._checkClass(itemClass, True, repair)

        classes = Kind._kinds.get(self.itsUUID)
        if classes is not None:
            for cls in classes:
                if cls is not itemClass:
                    result = self._checkClass(cls, False, repair) and result

        attrs = self._references.get('attributes', None)
        if attrs:
            if attrs._aliases is None or len(attrs) != len(attrs._aliases):
                self.itsView.logger.warn("Attributes list aliases for %s doesn't attributes list", self.itsPath)
                result = False

        return result

    def _checkClass(self, cls, isItemClass, repair):

        result = True

        def checkInheritance(cls):
            if cls is not Item:
                if not (isinstance(cls, type) and issubclass(cls, Item)):
                    return cls
                for base in cls.__bases__:
                    if checkInheritance(base) is not None:
                        return base
            return None

        problemCls = checkInheritance(cls)
        if problemCls is not None:
            self.itsView.logger.warn('Kind %s has an item class or superclass that is not a subclass of Item: %s %s', self.itsPath, problemCls, type(problemCls))
            result = False

        descriptors = self.c.descriptors
        if descriptors is None:
            if not isItemClass:
                self.itsView.logger.warn("No descriptors for class %s but Kind %s seems to think otherwise", cls, self.itsPath)
                result = False
        else:
            for name, descriptor in descriptors.iteritems():
                attr = descriptor.attr
                attribute = self.getAttribute(name, True)
                if attribute is None:
                    self.itsView.logger.warn("Descriptor for attribute '%s' on class %s doesn't correspond to an attribute on Kind %s", name, cls, self.itsPath)
                    result = False
                else:
                    if attr.attrID != attribute.itsUUID:
                        self.itsView.logger.warn("Descriptor for attribute '%s' on class %s doesn't correspond to the attribute of the same name on Kind %s", name, cls, self)
                        result = False

        return result
        
    def getAttribute(self, name, noError=False, item=None):
        """
        Get an attribute definition item.

        The attribute is sought on the kind and on its superKinds in a left
        to right depth-first manner. If no attribute is found a subclass of
        C{AttributeError} is raised.

        @param name: the name of the attribute sought
        @type name: a string
        @return: an L{Attribute<chandlerdb.schema.Attribute.Attribute>} item
        instance
        """

        c = self.c

        if c.attributesCached:
            attr = c.allAttributes.get(name)
            if attr is None:
                if noError:
                    return None
                raise NoSuchAttributeError, (self, name)
            return self.itsView[attr[0]]

        if item is not None:
            attribute = c.getAttribute(item, name)
            if attribute is not None:
                return attribute

        refs = self._references
        attrs = refs.get('attributes', None)

        if attrs is not None:
            attribute = attrs.getByAlias(name)
        else:
            attribute = None
            
        if attribute is None:
            attribute = self.c.inheritedAttributes.get(name)
            if attribute is not None:
                return self.itsView[attribute]
            attribute = self._inheritAttribute(name)
            if attribute is None and noError is False:
                raise NoSuchAttributeError, (self, name)

        return attribute

    def hasAttribute(self, name):
        
        c = self.c

        if c.attributesCached:
            return name in c.allAttributes

        attributes = self._references.get('attributes', None)
        if attributes is not None:
            uuid = attributes.resolveAlias(name)
        else:
            uuid = None

        if uuid is not None:
            return True
        elif name in c.inheritedAttributes:
            return True

        return self._inheritAttribute(name) is not None

    def getOtherName(self, name, item, default=Default):

        if item is not None:
            otherName = item.getAttributeAspect(name, 'otherName',
                                                False, None, None)
        else:
            otherName = self.getAttribute(name).getAspect('otherName', None)

        if otherName is None:
            if default is not Default:
                return default
            raise TypeError, 'Undefined otherName for attribute %s on kind %s' %(name, self.itsPath)

        return otherName

    def iterAttributes(self, inherited=True, localOnly=False, globalOnly=False):
        """
        Return a generator of C{(name, attribute, kind)} tuples for
        iterating over the Chandler attributes defined for and inherited by
        this kind. The C{kind} element is the kind the attribute was
        inherited from or this kind.

        The name of an attribute is defined to be the alias with which it was
        added into the kind's C{attributes} attribute. This alias name may
        of course be the same as the corresponding attribute's item name.

        @param inherited: if C{True}, iterate also over attributes that are
        inherited by this kind via its superKinds.
        @type inherited: boolean
        @param localOnly: if C{True}, only pairs for local attributes are
        returned. Local attributes are defined as direct children items
        of the kinds they're defined on and are not meant to be shared
        except through inheritance.
        @type localOnly: boolean
        @param globalOnly: if C{True}, only pairs for the global attributes
        are returned. Global attributes are not defined as direct children
        items and are intended to be shareable by multiple kinds.
        @type globalOnly: boolean
        """

        c = self.c
        allAttributes = c.allAttributes

        if not c.attributesCached:
            allNames = c.allNames
            notifyAttributes = c.notifyAttributes
            allCorrelations = c.allCorrelations

            allAttributes.clear()
            allCorrelations.clear()
            allNames.clear()
            notifyAttributes.clear()
            notify = False

            references = self.itsRefs
            for superKind in references['superKinds']:
                notify = notify or superKind.c.notify
                for name, attribute, kind in superKind.iterAttributes():
                    if name not in allAttributes:
                        allAttributes[name] = (attribute.itsUUID, kind.itsUUID,
                                               False, False)
                        h = _hash(name)

                        if h in allNames:
                            if allNames[h] != name:
                                raise AssertionError, ('clash', allNames[h], name)
                        allNames[h] = name
                        if attribute.getAspect('notify', False):
                            notifyAttributes.add(name)
                allCorrelations.update(superKind.c.allCorrelations)
            else:
                notify = True

            attributes = references.get('attributes', None)
            if attributes is not None:
                correlations = references.get('correlations', None)
                uuid = self.itsUUID
                for attribute in attributes:
                    name = attributes.getAlias(attribute)
                    allAttributes[name] = (attribute.itsUUID, uuid,
                                           attribute.itsParent is self, True)
                    allNames[_hash(name)] = name
                    if attribute.getAspect('notify', False):
                        notifyAttributes.add(name)
                    elif name in notifyAttributes:
                        notifyAttributes.remove(name)

                    if correlations:
                        uuids = [corr.itsUUID for corr in correlations
                                 if name in corr.itsValues['names']]
                        if uuids:
                            if name in allCorrelations:
                                allCorrelations[name].extend(uuids)
                            else:
                                allCorrelations[name] = uuids

            c.attributesCached = True
            c.notify = self.itsValues.get('notify', notify)

        view = self.itsView
        for name, (aUUID, kUUID, local, defined) in allAttributes.iteritems():
            if not ((globalOnly and local) or
                    (localOnly and not local) or
                    (not inherited and not defined)):
                yield (name, view[aUUID], view[kUUID])

    def _nameTuple(self, hashTuple):

        c = self.c

        if c.attributesCached:
            allNames = c.allNames
            return tuple([allNames[hash] for hash in hashTuple])
        else:
            return tuple([name for name, a, k in self.iterAttributes()
                          if name in hashTuple])

    def _iterNotifyAttributes(self):

        c = self.c

        if not c.attributesCached:
            self.iterAttributes()

        return iter(c.notifyAttributes)

    def getInheritedSuperKindIDs(self):

        c = self.c
        references = self._references
        inherited = c.inheritedSuperKinds

        if not c.superKindsCached:
            for superKind in references['superKinds']:
                inherited.add(superKind.itsUUID)
                inherited.update(superKind.getInheritedSuperKindIDs())
            c.superKindsCached = True

        return inherited

    def getInheritedSuperKinds(self):

        view = self.itsView
        return (view[uuid] for uuid in self.getInheritedSuperKindIDs())

    def _inheritAttribute(self, name):

        c = self.c

        if name in c.notFoundAttributes:
            return None

        cache = True
        inheritedAttributes = c.inheritedAttributes
        for superKind in self._references.get('superKinds', Nil):
            if superKind is not None:
                attribute = superKind.getAttribute(name, True)
                if attribute is not None:
                    inheritedAttributes[name] = attribute.itsUUID
                    return attribute
            else:
                cache = False
                    
        if cache:
            c.notFoundAttributes.append(name)

        return None

    def iterItems(self, recursive=True):

        return self.extent.iterItems(recursive)

    def iterKeys(self, recursive=True):

        return self.extent.iterKeys(recursive)

    def getItemKind(self):

        return self.find(CORE)['Item']

    def getKindKind(self):

        return self.find(CORE)['Kind']

    def isKindKind(self):

        return self.itsKind is self

    def mixin(self, superKinds):
        """
        Find or generate a mixin kind.

        The mixin kind is defined as the combination of this kind and the
        additional kind items specified with C{superKinds}.
        A new kind is generated if the corresponding mixin kind doesn't yet
        exist. The item class of the resulting mixin kind is a composite of
        the superKinds' item classes. See L{getItemClass} for more
        information.

        @param superKinds: the kind items added to this kind to form the mixin
        @type superKinds: list
        @return: a L{Kind<chandlerdb.schema.Kind.Kind>} instance
        """

        duplicates = {}
        for superKind in superKinds:
            if superKind.itsUUID in duplicates:
                raise ValueError, 'Kind %s is duplicated' %(superKind.itsPath)
            else:
                duplicates[superKind.itsUUID] = superKind
                
        hash = self.hashItem()
        for superKind in superKinds:
            hash = _combine(hash, superKind.hashItem())
        if hash < 0:
            hash = ~hash
        name = "mixin_%08x" %(hash)
        parent = self.getItemKind().itsParent['Mixins']

        kind = parent.getItemChild(name)
        if kind is None:
            kind = self.itsKind.newItem(name, parent)

            kind.addValue('superKinds', self)
            kind.superKinds.extend(superKinds)
            kind.mixins = [sk.itsPath for sk in kind.superKinds]
            
        return kind
        
    def isMixin(self):

        return 'mixins' in self._values

    def isAlias(self):

        return False

    def kindForKey(self, uuid):

        return self.itsView.kindForKey(uuid)

    def isKeyForInstance(self, uuid, recursive=True):

        kind = self.kindForKey(uuid)
        if kind is not None:
            if recursive:
                return kind.isKindOf(self)
            return kind is self

        return False

    def isKindOf(self, superKind):

        if self is superKind:
            return True

        if not isinstance(superKind, Kind):
            raise TypeError, (superKind, 'is not a kind')

        return superKind.itsUUID in self.getInheritedSuperKindIDs()

    def getInitialValues(self, item, isNew):

        initialValues = self._initialValues
        initialReferences = self._initialReferences

        # setup cache
        if initialValues is None:
            self._initialValues = initialValues = {}
            self._initialReferences = initialReferences = {}
            for name, attribute, k in self.iterAttributes():
                value = attribute.getAspect('initialValue', Nil)
                if value is not Nil:
                    otherName = self.getOtherName(name, item, None)
                    if otherName is None:
                        initialValues[name] = value
                    else:
                        initialReferences[name] = value

        if initialValues:
            values = item._values
            for name, value in initialValues.iteritems():
                if name not in values:
                    if isinstance(value, ItemValue):
                        value = value._copy(item, name, 'copy')

                    values[name] = value
                    if not isNew:   # __setKind case
                        item.setDirty(Item.VDIRTY, name, values, True)

        if initialReferences:
            references = item._references
            for name, value in initialReferences.iteritems():
                if name not in references:
                    otherName = self.getOtherName(name, item)
                    if isinstance(value, PersistentCollection):
                        references[name] = refList = item._refList(name,
                                                                   otherName)
                        for other in value.itervalues():
                            refList.append(other)
                    else:
                        references._setValue(name, value, otherName)
                    if not isNew:   # __setKind case
                        item.setDirty(Item.RDIRTY, name, references, True)

    def flushCaches(self, reason, recursive=True):
        """
        Flush the caches setup on this Kind and its subKinds.
        """
        c = self.c

        if c.attributesCached:
            c.allAttributes.clear()
            c.allCorrelations.clear()
            c.allNames.clear()
            c.notifyAttributes.clear()
            c.attributesCached = False

        if c.superKindsCached:
            c.inheritedSuperKinds.clear()
            c.superKindsCached = False

        c.inheritedAttributes.clear()
        del c.notFoundAttributes[:]

        self._initialValues = None
        self._initialReferences = None

        # clear auto-generated composite class
        if self._values._isTransient('classes'):
            self._values._clearTransient('classes')
            del self._values['classes']

        if 'schemaHash' in self._values:
            del self.schemaHash

        if reason != 'unload':
            self._setupDescriptors(reason)

        if recursive:
            for subKind in self._references.get('subKinds', Nil):
                subKind.flushCaches(reason)


    # begin typeness of Kind as ItemRef
    
    def isValueReady(self, itemHandler):
        return True

    def startValue(self, itemHandler):
        pass

    def getParsedValue(self, itemHandler, data):
        return self.makeValue(data)
    
    def makeValue(self, data):

        if data == Kind.NoneString:
            return None
        
        return ItemRef(UUID(data), self.itsView)

    def makeString(self, value):

        if value is None:
            return Kind.NoneString
        
        return str(value.itsUUID)

    def typeXML(self, value, generator, withSchema):

        if value is None:
            data = Kind.NoneString
        else:
            data = value.itsUUID.str64()
            
        generator.characters(data)

    def writeValue(self, itemWriter, record, item, version, value, withSchema):

        if value is None:
            record += (Record.UUID_OR_NONE, None)
        else:
            record += (Record.UUID_OR_NONE, value.itsUUID)

        return 0

    def readValue(self, itemReader, offset, data, withSchema, view, name,
                  afterLoadHooks):

        value = data[offset]
        if isuuid(value):
            value = ItemRef(value, view)
        
        return offset+1, value

    def hashValue(self, value):

        if value is None:
            return 0

        return TypeHandler.hashValue(self.itsView, value.itsUUID._hash)

    def indexValue(self, itemWriter, item, name, version, value):

        pass

    def handlerName(self):

        return 'ref'
    
    def recognizes(self, value):

        if value is None:
            return True

        if isitemref(value):
            item = value(True)
            if isitem(item):
                return item.isItemOf(self)
            return True

        if isitem(value):
            return value.isItemOf(self)
    
        return False

    def getFlags(self):

        return CAttribute.KIND | CAttribute.PROCESS

    # end typeness of Kind as ItemRef

    def getClouds(self, cloudAlias):
        """
        Get clouds for this kind, inheriting them if necessary.

        If there are no matching clouds, the matching clouds of the direct
        superKinds are returned, recursively.

        @return: a L{Cloud<chandlerdb.schema.Cloud.Cloud>} list, possibly empty
        """

        results = []
        clouds = self.getAttributeValue('clouds', self._references, None, None)

        if clouds is None or clouds.resolveAlias(cloudAlias) is None:
            for superKind in self.getAttributeValue('superKinds',
                                                    self._references):
                results.extend(superKind.getClouds(cloudAlias))

        else:
            results.append(clouds.getByAlias(cloudAlias))

        return results

    def _hashItem(self):

        hash = 0
        isMixin = self.isMixin()

        if not isMixin:
            hash = _combine(hash, _hash(str(self.itsPath)))

        for superKind in self.getAttributeValue('superKinds', self._references):
            hash = _combine(hash, superKind.hashItem())

        if not isMixin:
            attributes = list(self.iterAttributes(False))
            attributes.sort()
            for name, attribute, kind in attributes:
                hash = _combine(hash, _hash(name))
                hash = _combine(hash, attribute.hashItem())

        return hash

    def hashItem(self):
        """
        Compute a hash value from this kind's schema.

        The hash value is computed from the kind's path (unless it is a
        mixin kind), superKind and locally defined name - attribute item
        hashes.

        @return: an integer
        """

        if 'schemaHash' in self._values:
            return self.schemaHash

        self.schemaHash = hash = self._hashItem()
        return hash

    def _afterSchemaChange(self, op, attrName):

        if not self.isDeleting():
            c = getattr(self, 'c', None)
            if c is not None:
                if c.monitorSchema or c.attributesCached:
                    self.flushCaches(attrName)

    # notify value is used to turn on or off 'refresh' notifs on extents.
    # notify value is inherited via superKinds and cached on CKind.
    # top default is True.
    def _afterNotifyChange(self, op, attrName):

        if not self.isDeleting():
            if op == 'set':
                if attrName == 'notify':
                    self.c.notify = notify = self.notify
                elif 'notify' not in self.itsValues:
                    self.c.notify = notify = attrName # True or False
                else:
                    return
            elif op == 'remove':
                if attrName == 'notify':
                    notify = False
                    for superKind in self.itsRefs.get('superKinds', Nil):
                        notify = notify or superKind.c.notify
                    else:
                        notify = True
                elif 'notify' not in self.itsValues:
                    self.c.notify = notify = attrName # True or False
                else:
                    return

            for subKind in self.itsRefs.get('subKinds', Nil):
                subKind._afterNotifyChange(op, notify)

    def _afterAttributeHashChange(self):

        if 'schemaHash' in self._values:
            del self.schemaHash

    def _printItemBody(self, _level):

        print ' ' * (_level + 2), "attributes for this kind:"

        displayedAttrs = {}
        for (name, attr, k) in self.iterAttributes():
            displayedAttrs[name] = attr

        keys = displayedAttrs.keys()
        keys.sort()
        indent = ' ' * (_level + 4)
        for key in keys:
            print indent, key, displayedAttrs[key].itsPath

        super(Kind, self)._printItemBody(_level)

    def declareCorrelation(self, names):

        return Correlation(None, self, self.itsView.find(CORE)['Correlation'],
                           names=names, kind=self)


    NoneString = "__NONE__"
    _kinds = {}
    _classes = {}
    

class Extent(Item):

    def iterItems(self, recursive=True):

        view = self.itsView
        changed = CItem.KDIRTY | CItem.NEW | CItem.DEFERRED
        changedItems = set(item for item in view.dirtyItems()
                           if item._status & changed)

        def _query(kinds):
            for kind in kinds:
                for item in changedItems:
                    if item.itsKind is kind:
                        if not item.isDeferred():
                            yield item
                for item in view.queryItems(kind):
                    if item not in changedItems: 
                        yield item
                if recursive:
                    subKinds = kind._references.get('subKinds', None)
                    if subKinds:
                        for item in _query(list(subKinds)):
                            yield item

        matches = set()
        for item in _query((self.kind,)):
            if item not in matches:
                matches.add(item)
                yield item

    def iterKeys(self, recursive=True):

        view = self.itsView
        changed = CItem.KDIRTY | CItem.NEW | CItem.DEFERRED
        changedItems = {}
        for item in view.dirtyItems():
            if item._status & changed:
                changedItems[item.itsUUID] = item

        def _query(kinds):
            for kind in kinds:
                for key, item in changedItems.iteritems():
                    if item.itsKind is kind:
                        if not item.isDeferred():
                            yield key
                for key in view.queryItemKeys(kind):
                    if key not in changedItems: 
                        yield key
                if recursive:
                    subKinds = kind._references.get('subKinds', None)
                    if subKinds:
                        for key in _query(list(subKinds)):
                            yield key

        matches = set()
        for key in _query((self.kind,)):
            if key not in matches:
                matches.add(key)
                yield key

    @override(Item)
    def _collectionChanged(self, op, change, name, other, dirties,
                           filterKind=None):

        view = self.itsView
        callable = Item._collectionChanged

        if name == 'extent':
            kind = self.kind

            if filterKind is not None:
                filterKindIDs = filterKind.getInheritedSuperKindIDs()
                if not (kind is filterKind or
                        kind.itsUUID in filterKindIDs):
                    callable(self, op, change, name, other, dirties)
                    for superKindID in kind.getInheritedSuperKindIDs():
                        superKind = view[superKindID]
                        if not (superKind is filterKind or
                                superKindID in filterKindIDs):
                            callable(superKind.extent, op, change, name, other,
                                     dirties)

            else:
                callable(self, op, change, name, other, dirties)
                for superKindID in kind.getInheritedSuperKindIDs():
                    callable(view[superKindID].extent, op, change, name, other,
                             dirties)

        else:
            callable(self, op, change, name, other, dirties)


class DelegateDescriptor(object):

    def __init__(self, name, delegate):

        self.name = name
        self.delegate = delegate

    def __get__(self, obj, type=None):

        if obj is None:
            return self

        return getattr(getattr(obj, self.delegate), self.name)
