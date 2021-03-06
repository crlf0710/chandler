#   Copyright (c) 2004-2008 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHIN WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


""" Unit test for me address calculaton logic"""

from osaf.pim.mail import *
import osaf.pim.mail as mail
from application import schema
import unittest as unittest
import TestDomainModel
from osaf.framework import password
from osaf.framework.twisted import waitForDeferred

class TestMeAddress(TestDomainModel.DomainModelTestCase):

    def calc(self):
        pim_ns =  schema.ns("osaf.pim", self.view)
        pim_ns.currentMeEmailAddress.item = mail._calculateCurrentMeEmailAddress(self.view)

    def addIncoming(self, IN, emailAddress):
        IN.isActive = True
        IN.host = u"imap.test.com"
        IN.replyToAddress = emailAddress
        IN.username = u"test"
        IN.password = password.Password(itsView=IN.itsView, itsParent=IN)
        waitForDeferred(IN.password.encryptPassword(u'test'))

        self.calc()

    def clearIncoming(self, IN):
        IN.host = u""
        IN.replyToAddress = None
        IN.username = u""
        waitForDeferred(IN.password.clear())

        self.calc()

    def addOutgoing(self, OUT, emailAddress):
        OUT.isActive = True
        OUT.host = u"host.test.com"
        OUT.fromAddress = emailAddress
        OUT.username = u"test"
        OUT.password = password.Password(itsView=OUT.itsView, itsParent=OUT)
        waitForDeferred(OUT.password.encryptPassword(u'test'))
        OUT.userAuth = True

        self.calc()

    def clearOutgoing(self, OUT):
        OUT.host = u""
        OUT.fromAddress = None
        OUT.username = u""
        waitForDeferred(OUT.password.clear())
        OUT.useAuth = False

        self.calc()


    def testMeAddress(self):
        # The logic for osaf.pim.mail.getCurrentMeEmailAddress is:
        #
        # 1. use the default Outgoing account
        #
        # 2. If no default use the first Outgoing account
        #    with an email address
        #
        # 3. If no Outgoing email addresses then
        #    use the default Incoming Account
        #
        # 4. If the default Incoming Account does not
        #    have an address of the first Incoming account
        #    with an address.
        #
        # 5. Return None

        v = self.view
        e = EmailAddress


        # There is no meAddress setup yet
        # so this should return None
        me = getCurrentMeEmailAddress(v)

        self.assertEquals(me, None)

        # First test email address assigned to
        # a non-default Incoming Account

        inNonDefault = IMAPAccount(itsView=v)
        ea = EmailAddress.getEmailAddress(v, u"test@test.com", u"Test User")

        self.addIncoming(inNonDefault, ea)
        self.compareAddresses(ea)

        # Now assign an email address to the default Incoming Account
        inDefault = IMAPAccount(itsView=v)

        #Make this the default incoming account
        schema.ns('osaf.pim', v).currentIncomingAccount.item = inDefault

        ea1 = EmailAddress.getEmailAddress(v, u"test1@test.com", u"Test User1")

        self.addIncoming(inDefault, ea1)

        self.compareAddresses(ea1)

        # Now assign an email address to a non-default
        # Outgoing account

        outNonDefault = SMTPAccount(itsView=v)
        
        ea2 = EmailAddress.getEmailAddress(v, u"test2@test.com", u"Test User2")

        self.addOutgoing(outNonDefault, ea2)

        # Outgoing accounts don't contain a UI field
        # for assigning fullName so pass False to
        # the comapreAddresses method
        self.compareAddresses(ea2, False)

        # Now assign an email address to the default
        # Outgoing account
        outDefault = SMTPAccount(itsView=v)

        #Make this the default incoming account
        schema.ns('osaf.pim', v).currentOutgoingAccount.item = outDefault

        ea3 = EmailAddress.getEmailAddress(v, u"test3@test.com", u"Test User3")

        self.addOutgoing(outDefault, ea3)

        # Outgoing accounts don't contain a UI field
        # for assigning fullName so pass False to
        # the comapreAddresses method
        self.compareAddresses(ea3, False)

        # Now we reverse the process and remove accounts
        # to confirm that the me logic works

        self.clearOutgoing(outDefault)
        self.compareAddresses(ea2, False)

        self.clearOutgoing(outNonDefault)
        self.compareAddresses(ea1)

        self.clearIncoming(inDefault)
        self.compareAddresses(ea)

        self.clearIncoming(inNonDefault)

        me = getCurrentMeEmailAddress(v)
        self.assertEquals(me, None)


    def compareAddresses(self, ea, testFullName=True):
        me = getCurrentMeEmailAddress(self.view)

        if testFullName:
            self.assertEquals(me.fullName, ea.fullName)

        self.assertEquals(me.emailAddress, ea.emailAddress)

if __name__ == "__main__":
   unittest.main()
