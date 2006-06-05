__copyright__ = "Copyright (c) 2003-2005 Open Source Applications Foundation"
__license__   = "http://osafoundation.org/Chandler_0.1_license_terms.htm"
__parcel__ = "photos"

from Photos import PhotoMixin, NewImageEvent
from application import schema
from osaf.pim.structs import RectType
from osaf.pim.notes import Note
from osaf.framework.blocks.detail import makeSubtree
from osaf.framework.blocks.MenusAndToolbars import MenuItem
from i18n import OSAFMessageFactory as _

def installParcel(parcel, old_version=None):
    blocks = schema.ns('osaf.framework.blocks', parcel)
    detail = schema.ns('osaf.framework.blocks.detail', parcel)

    makeSubtree(parcel, PhotoMixin, [
        detail.DetailSynchronizedAttributeEditorBlock.update(
            parcel, "photo_image",
            viewAttribute = u"photoBody",
            position = 0.86,
            stretchFactor = 1.0,
            border = RectType(2.0, 2.0, 2.0, 2.0),
            presentationStyle = blocks.PresentationStyle.update(
                parcel, "photo_image_presentation",
                format = "Image"
            )
        )])

    # Event to add a new image to the repository
    newImageEvent = NewImageEvent.update(
        parcel, 'NewImage',
        blockName = 'NewImage',
        dispatchToBlockName = 'MainView',
        dispatchEnum = 'SendToBlockByName',
        kindParameter = Note.getKind (parcel.itsView),
        allCollection = schema.ns ('osaf.pim', parcel.itsView).allCollection)

    # Add menu item to Chandler
    MenuItem.update(
        parcel, 'ImportImageItem',
        blockName = 'ImportImageItemMenuItem',
        title = _(u'Import an image from disk'),
        helpString = _(u'Import an image from disk'),
        event = newImageEvent,
        eventsForNamedLookup = [newImageEvent],
        parentBlock = schema.ns('osaf.views.main', parcel).ImportExportMenu)
 

