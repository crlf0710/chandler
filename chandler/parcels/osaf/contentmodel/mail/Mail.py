""" Classes used for Mail parcel kinds
"""

__revision__  = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2003-2004 Open Source Applications Foundation"
__license__   = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

import application
import repository.item.Item as Item
import osaf.contentmodel.ContentModel as ContentModel
import osaf.contentmodel.Notes as Notes
import application.Globals as Globals
import repository.query.Query as Query
import repository.item.Query as ItemQuery
import repository.util.UUID as UUID

from repository.util.Path import Path


class MailParcel(application.Parcel.Parcel):

    def startupParcel(self):
        super(MailParcel, self).startupParcel()

        repository = self.itsView
        itemKind = repository.findPath('//Schema/Core/Item')
        contentitemsPath = ContentModel.ContentModel.contentitemsPath
        
        def makeContainer(parent, name, child):
            if child is None:
                return itemKind.newItem(name, parent)
            else:
                return child
        
        repository.walk(Path(contentitemsPath, 'inboundMailItems'),
                        makeContainer)
        repository.walk(Path(contentitemsPath, 'outboundMailItems'),
                        makeContainer)
            
        self._setUUIDs()
        
    def getMailItemParent(cls, inbound=False):

        parent = ContentModel.ContentModel.getContentItemParent()
        if inbound:
            return parent['inboundMailItems']
        else:
            return parent['outboundMailItems']

    getMailItemParent = classmethod(getMailItemParent)

    def onItemLoad(self):
        super(MailParcel, self).onItemLoad()
        self._setUUIDs()

    def _setUUIDs(self):
        accountBaseKind = self['AccountBase']
        MailParcel.accountBaseKindID = accountBaseKind.itsUUID

        imapAccountKind = self['IMAPAccount']
        MailParcel.imapAccountKindID = imapAccountKind.itsUUID

        smtpAccountKind = self['SMTPAccount']
        MailParcel.smtpAccountKindID = smtpAccountKind.itsUUID

        mailDeliveryErrorKind = self['MailDeliveryError']
        MailParcel.mailDeliveryErrorKindID = mailDeliveryErrorKind.itsUUID

        mailDeliveryBaseKind = self['MailDeliveryBase']
        MailParcel.mailDeliveryBaseKindID = mailDeliveryBaseKind.itsUUID

        smtpDeliveryKind = self['SMTPDelivery']
        MailParcel.smtpDeliveryKindID = smtpDeliveryKind.itsUUID

        imapDeliveryKind = self['IMAPDelivery']
        MailParcel.imapDeliveryKindID = imapDeliveryKind.itsUUID

        mimeBaseKind = self['MIMEBase']
        MailParcel.mimeBaseKindID = mimeBaseKind.itsUUID

        mimeNoteKind = self['MIMENote']
        MailParcel.mimeNoteKindID = mimeNoteKind.itsUUID

        mailMessageKind = self['MailMessage']
        MailParcel.mailMessageKindID = mailMessageKind.itsUUID

        mailMessageMixinKind = self['MailMessageMixin']
        MailParcel.mailMessageMixinKindID = mailMessageMixinKind.itsUUID

        mimeBinaryKind = self['MIMEBinary']
        MailParcel.mimeBinaryKindID = mimeBinaryKind.itsUUID

        mimeTextKind = self['MIMEText']
        MailParcel.mimeTextKindID = mimeTextKind.itsUUID

        mimeContainerKind = self['MIMEContainer']
        MailParcel.mimeContainerKindID = mimeContainerKind.itsUUID

        mimeSecurityKind = self['MIMESecurity']
        MailParcel.mimeSecurityKindID = mimeSecurityKind.itsUUID

        emailAddressKind = self['EmailAddress']
        MailParcel.emailAddressKindID = emailAddressKind.itsUUID

    def getAccountBaseKind(cls):
        assert cls.accountBaseKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.accountBaseKindID]

    getAccountBaseKind = classmethod(getAccountBaseKind)

    def getIMAPAccountKind(cls):
        assert cls.imapAccountKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.imapAccountKindID]

    getIMAPAccountKind = classmethod(getIMAPAccountKind)

    def getSMTPAccountKind(cls):
        assert cls.smtpAccountKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.smtpAccountKindID]

    getSMTPAccountKind = classmethod(getSMTPAccountKind)

    def getMailDeliveryErrorKind(cls):
        assert cls.mailDeliveryErrorKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.mailDeliveryErrorKindID]

    getMailDeliveryErrorKind = classmethod(getMailDeliveryErrorKind)

    def getMailDeliveryBaseKind(cls):
        assert cls.mailDeliveryBaseKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.mailDeliveryBaseKindID]

    getMailDeliveryBaseKind = classmethod(getMailDeliveryBaseKind)


    def getSMTPDeliveryKind(cls):
        assert cls.smtpDeliveryKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.smtpDeliveryKindID]

    getSMTPDeliveryKind = classmethod(getSMTPDeliveryKind)

    def getIMAPDeliveryKind(cls):
        assert cls.imapDeliveryKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.imapDeliveryKindID]

    getIMAPDeliveryKind = classmethod(getIMAPDeliveryKind)

    def getMIMEBaseKind(cls):
        assert cls.mimeBaseKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.mimeBaseKindID]

    getMIMEBaseKind = classmethod(getMIMEBaseKind)

    def getMIMENoteKind(cls):
        assert cls.mimeNoteKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.mimeNoteKindID]

    getMIMENoteKind = classmethod(getMIMENoteKind)

    def getMailMessageKind(cls):
        assert cls.mailMessageKindID, "Mail message not yet loaded"
        return Globals.repository[cls.mailMessageKindID]

    getMailMessageKind = classmethod(getMailMessageKind)

    def getMailMessageMixinKind(cls):
        assert cls.mailMessageMixinKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.mailMessageMixinKindID]

    getMailMessageMixinKind = classmethod(getMailMessageMixinKind)

    def getMIMEBinaryKind(cls):
        assert cls.mimeBinaryKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.mimeBinaryKindID]

    getMIMEBinaryKind = classmethod(getMIMEBinaryKind)

    def getMIMETextKind(cls):
        assert cls.mimeTextKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.mimeTextKindID]

    getMIMETextKind = classmethod(getMIMETextKind)

    def getMIMEContainerKind(cls):
        assert cls.mimeContainerKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.mimeContainerKindID]

    getMIMEContainerKind = classmethod(getMIMEContainerKind)

    def getMIMESecurityKind(cls):
        assert cls.mimeSecurityKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.mimeSecurityKindID]

    getMIMESecurityKind = classmethod(getMIMESecurityKind)

    def getEmailAddressKind(cls):
        assert cls.emailAddressKindID, "Mail parcel not yet loaded"
        return Globals.repository[cls.emailAddressKindID]

    getEmailAddressKind = classmethod(getEmailAddressKind)

    accountBaseKindID = None
    imapAccountKindID = None
    smtpAccountKindID = None
    mailDeliveryErrorKindID = None
    mailDeliveryBaseKindID = None
    smtpDeliveryKindID = None
    imapDeliveryKindID = None
    mimeBaseKindID = None
    mimeNoteKindID = None
    mailMessageKindID = None
    mailMessageMixinKindID = None
    mimeBinaryKindID = None
    mimeTextKindID = None
    mimeContainerKindID = None
    mimeSecurityKindID = None
    emailAddressKindID = None

class AccountBase(Item.Item):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getAccountBaseKind()
        super (AccountBase, self).__init__(name, parent, kind)

class SMTPAccount(AccountBase):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getSMTPAccountKind()
        super (SMTPAccount, self).__init__(name, parent, kind)

        self.accountType = "SMTP"

class IMAPAccount(AccountBase):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getIMAPAccountKind()
        super (IMAPAccount, self).__init__(name, parent, kind)

        self.accountType = "IMAP"


class MailDeliveryError(Item.Item):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getMailDeliveryErrorKind()
        super (MailDeliveryError, self).__init__(name, parent, kind)

    def __str__(self):
        return "| %d | %s | %s |" % (self.errorCode, self.errorString, self.errorDate.strftime())


class MailDeliveryBase(Item.Item):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getMailDeliveryBaseKind()
        super (MailDeliveryBase, self).__init__(name, parent, kind)


class SMTPDelivery(MailDeliveryBase):
    """
    SMTP Delivery Notification Class
    Some of these methods are called from Twisted, some from 
    the UI Thread.
    """
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getSMTPDeliveryKind()
        super (SMTPDelivery, self).__init__(name, parent, kind)

        self.deliveryType = "SMTP"
        self.state = "DRAFT"

    #XXX: Will want to expand state to an object with error or sucess code 
    #     desc string, and date
    def sendFailed(self):
        """
          Called from the Twisted thread to log errors in Send.
        """
        self.history.append("FAILED")
        self.state = "FAILED"
        self.tries += 1

        # announce to the UI thread that an error occurred
        self.announceSMTPSendError (self.mailMessage.itsUUID)

    #XXX: See comments above
    def sendSucceeded(self):
        """
          Called from the Twisted thread to log successes in Send.
        """
        self.history.append("SENT")
        self.state = "SENT"
        self.tries += 1

        # announce to the UI thread that an error occurred
        self.announceSMTPSendSuccess (self.mailMessage.itsUUID)

    def announceSMTPSendError (cls, uuid):
        """ 
          Call this method to announce that an SMTP sending error has
        occurred. This method is non-blocking.
        Called from the Twisted thread.
        """
    
        def _announceSMTPSendError (uuid):
            # post a Chandler event to get back to the UI Thread
            ContentModel.ContentItem.messageMainView ('displaySMTPSendError', uuid)
    
        # post an application event to call above
        Globals.wxApplication.PostAsyncEvent(_announceSMTPSendError, uuid)
    announceSMTPSendError = classmethod (announceSMTPSendError)

    def announceSMTPSendSuccess (cls, uuid):
        """ Call this method to announce that SMTP sending was
            a success. This method is non-blocking. """
    
        def _announceSMTPSendSuccess (uuid):
            # post a Chandler event to get back to the UI Thread
            ContentModel.ContentItem.messageMainView ('displaySMTPSendSuccess', uuid)
    
        Globals.wxApplication.PostAsyncEvent(_announceSMTPSendSuccess, uuid)
    announceSMTPSendSuccess = classmethod (announceSMTPSendSuccess)


class IMAPDelivery(MailDeliveryBase):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getIMAPDeliveryKind()
        super (IMAPDelivery, self).__init__(name, parent, kind)

        self.deliveryType = "IMAP"

class MIMEBase(Item.Item):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getMIMEBaseKind()
        super (MIMEBase, self).__init__(name, parent, kind)

class MIMENote(Notes.Note, MIMEBase):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getMIMENoteKind()
        super (MIMENote, self).__init__(name, parent, kind)

class MIMEContainer(MIMEBase):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getMIMEContainerKind()
        super (MIMEContainer, self).__init__(name, parent, kind)

class MailMessageMixin(MIMEContainer):
    """
      Mail Message Mixin is the bag of Message-specific attributes.

    """
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getMailMessageMixinKind()
        super (MailMessageMixin, self).__init__(name, parent, kind)

        self.mimeType = "MESSAGE"

    def InitOutgoingAttributes(self):
        """ Init any attributes on ourself that are appropriate for
        a new outgoing item.
        """
        try:
            super(MailMessageMixin, self).InitOutgoingAttributes ()
        except AttributeError:
            pass

        self.outgoingMessage()

    def defaultSMTPAccount (self):
        import osaf.mail.smtp as smtp

        account, replyAddress = smtp.getSMTPAccount ()
        return account

    def outgoingMessage(self, type="SMTP", account=None):
        if type != "SMTP":
            raise TypeError("Only SMTP currently supported")

        if account is None:
            account = self.defaultSMTPAccount ()

        #XXX:SAdd test to make sure it is an item
        elif not account.isItemOf(MailParcel.getSMTPAccountKind()):
            raise TypeError("Only SMTP Accounts Supported")

        self.deliveryExtension = SMTPDelivery()
        self.isOutbound = True
        self.parentAccount = account
        self.fromAddress = self.getCurrentMeEmailAddress ()


    def incomingMessage(self, type="IMAP", account=None):
        if type != "IMAP":
            raise TypeError("Only IMAP currently supported")

        if account is None:
            import osaf.mail.imap as imap
            account = imap.getIMAPAccount ()

        #XXX:SAdd test to make sure it is an item
        elif not account.isItemOf(MailParcel.getIMAPAccountKind()):
            raise TypeError("Only IMAP Accounts Supported")

        self.deliveryExtension = IMAPDelivery()
        self.isInbound = True
        self.parentAccount = account

class MailMessage(Notes.Note, MailMessageMixin):
    # DLDTBD - fix MI ordering issue
    def __init__(self, name=None, parent=None, kind=None):
        if not kind:
            kind = MailParcel.getMailMessageKind()
        super (MailMessage, self).__init__(name, parent, kind)

    def shareSend (self):
        """
          Share this item, or Send if it's an Email
        We assume we want to send this MailMessage here.
        DLDTBD - move to MailMessageMixin
        """
        # put a "committing" message into the status bar
        self.setStatusText ('Committing changes...')

        # commit changes, since we'll be switching to Twisted thread
        Globals.repository.commit()
    
        # get default SMTP account
        account = self.defaultSMTPAccount ()

        # put a sending message into the status bar
        self.setStatusText ('Sending mail...')

        # Now send the mail
        import osaf.mail.smtp as smtp
        smtp.SMTPSender(account, self).sendMail()

class MIMEBinary(MIMENote):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getMIMEBinaryKind()
        super (MIMEBinary, self).__init__(name, parent, kind)

class MIMEText(MIMENote):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getMIMETextKind()
        super (MIMEText, self).__init__(name, parent, kind)


class MIMESecurity(MIMEContainer):
    def __init__(self, name=None, parent=None, kind=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getMIMESecurityKind()
        super (MIMESecurity, self).__init__(name, parent, kind)

class EmailAddress(Item.Item):
    def __init__(self, name=None, parent=None, kind=None, clone=None):
        if not parent:
            parent = MailParcel.getMailItemParent()
        if not kind:
            kind = MailParcel.getEmailAddressKind()
        super (EmailAddress, self).__init__(name, parent, kind)

        # copy the attributes if a clone was supplied
        if clone is not None:
            try:
                self.emailAddress = clone.emailAddress[:]
            except AttributeError:
                pass
            try:
                self.fullName = clone.fullName[:]
            except AttributeError:
                pass

    def __str__ (self):
        """
          User readable string version of this address
        """
        if self.emailAddress == self._getTheMeAddress():
            return 'me'
        try:
            fullName = self.fullName
        except AttributeError:
            fullName = ''
        if fullName is not None and len (fullName) > 0:
            return fullName + ' <' + self.emailAddress + '>'
        else:
            return self.getItemDisplayName ()

        """
        Factory Methods
        --------------
        When creating a new EmailAddress, we check for an existing item first.
        We do look them up in the repository to prevent duplicates, but there's
        nothing to keep bad ones from accumulating, although repository
        garbage collection should eventually remove them.
        The "me" entity is used for Items created by the user, and it
        gets a reasonable emailaddress filled in when a send is done.
        This code needs to be reworked!
        """
        
    def getEmailAddress (cls, nameOrAddressString, fullName=''):
        """
          Lookup or create an EmailAddress based
        on the supplied string.
        @param nameOrAddressString: emailAddress string, or fullName for lookup
        @type nameOrAddressString: C{String}
        @param fullName: the fullName to use when a new item is created
        @type fullName: C{String}
        @return: C{EmailAddress} or None if not found, and nameOrAddressString is\
               not a valid email address.
        """
        import osaf.mail.message as message # avoid circularity

        # strip the address string of whitespace and question marks
        address = nameOrAddressString.strip ().strip ('?')

        # check for "me"
        if address == 'me':
            return cls.getCurrentMeEmailAddress ()

        # if no fullName specified, parse apart the fullName and emailAddress if we can
        if fullName == '':
            try:
                address.index ('<')
            except ValueError:
                pass
            else:
                fullName, address = address.split ('<')
                address = address.strip ('>').strip ()
                fullName = fullName.strip ()

        # check if it looks like a valid email address
        isValidAddress = message.isValidEmailAddress (address)

        # DLDTBD - switch on the better queries
        # Need to override compare operators to use emailAddressesAreEqual, etc
        useBetterQuery = False
        if useBetterQuery:

            # get all addresses whose emailAddress or fullName match the param
            queryString = u'for i in "//parcels/osaf/contentmodel/mail/EmailAddress" \
                          where i.emailAddress =="$0" or i.fullName =="$0"'
            addrQuery = Query.Query (Globals.repository, queryString)
            addrQuery.args = [ address ]
            addresses = addrQuery

        else:
            # old slow query method
            emailAddressKind = MailParcel.getEmailAddressKind ()
            allAddresses = ItemQuery.KindQuery().run([emailAddressKind])
            addresses = []
            for candidate in allAddresses:
                if isValidAddress:
                    if message.emailAddressesAreEqual(candidate.emailAddress, address):
                        # found an existing address!
                        addresses.append (candidate)
                elif address != '' and address == candidate.fullName:
                    # full name match
                    addresses.append (candidate)

        # process the result(s)
        for candidate in addresses:
            if isValidAddress:
                if message.emailAddressesAreEqual(candidate.emailAddress, address):
                    # found an existing address!
                    if fullName != '':
                        # update the fullname with what the caller supplied.
                        candidate.fullName = fullName
                    return candidate
            elif address == candidate.fullName:
                # full name match
                return candidate
        else:
            if isValidAddress:
                # make a new EmailAddress
                newAddress = EmailAddress()
                newAddress.emailAddress = address
                newAddress.fullName = fullName
                return newAddress
            else:
                return None
    getEmailAddress = classmethod (getEmailAddress)

    # theMeAddress is cached here.  It's an emailAddress string.
    _theMeAddress = None

    def _getTheMeAddress (cls):
        """
          Lookup the "me" emailAddress string.
        @return: C{String} the email address of the default account, or None
        """
        if cls._theMeAddress is not None:
            return cls._theMeAddress

        # get the default IMAP address, and use it to find/build "me"
        import osaf.mail.imap as imap
    
        try:
            account = imap.getIMAPAccount ()
        except imap.IMAPException:
            return None
        try:
            address = account.emailAddress
        except AttributeError:
            return None
        cls._theMeAddress = address
        return address
    _getTheMeAddress = classmethod (_getTheMeAddress)

    def getCurrentMeEmailAddress (cls):
        """
          Lookup or create the "me" EmailAddress.
        The "me" EmailAddress is whichever entry is the current IMAP default address.
        """
        meAddress = cls._getTheMeAddress()
        # if there is no account, we'll get None, and just create an EmailAddress for it
        return cls.getEmailAddress (meAddress)
    getCurrentMeEmailAddress = classmethod (getCurrentMeEmailAddress)

    def captureCurrentMeEmailAddress (cls):
        """
          Prepare for editing of the "me" EmailAddress.
        Since many messages refer to "me" we'd like it to be preserved
        across the edit, rather than change all those messages, which
        would make it look like sent mail was sent from the new address.
        """
        
        # get the account that owns the "me" address
        meEmailAddress = cls.getCurrentMeEmailAddress ()
        imapAccounts = meEmailAddress.accounts
        assert len (imapAccounts) == 1, "The EmailAddress %s is not being used in %d accounts!" \
                  %  (len (imapAccounts), meEmailAddress.emailAddress)
        account = imapAccounts.first()
        if account:
            # Create a fresh unused EmailAddress for editing
            newMe = EmailAddress(clone=meEmailAddress) # a fresh unused EmailAddress
    
            # Put the new EmailAddress into the account that owns "me",
            account.replyToAddress = newMe
            assert cls._capturedAccount is None, "capturedAccount error"
            cls._capturedAccount = account
    captureCurrentMeEmailAddress = classmethod (captureCurrentMeEmailAddress)

    # the captured IMAP account is save here during capture/release
    _capturedAccount = None

    def releaseCurrentMeEmailAddress (cls):
        """
          If the "me" address was changed by editing, we'll start using a new one.
        If unchanged, we revert back to the old one.
        """
        # get the new user-edited "me" address out of the account
        if cls._capturedAccount is not None:
            account = cls._capturedAccount
            cls._capturedAccount = None
            newMeCandidate = account.replyToAddress
    
            """
              We'll want to use whatever existing address matches the user's edit.
            Could be the new fresh one, could be an existing reuse, 
            and could be the old one if no edit was made. 
            If we're not using the new fresh copy, then we delete it.
            """
            theNewMe = cls.getEmailAddress (newMeCandidate.emailAddress)
            account.replyToAddress = theNewMe
            if theNewMe is not newMeCandidate:
                newMeCandidate.delete ()
    
            # Invalidate the "me" emailAddress string cache in case there was an edit.
            cls._theMeAddress = None
    releaseCurrentMeEmailAddress = classmethod (releaseCurrentMeEmailAddress)

