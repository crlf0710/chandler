#!/usr/bin/python
#   Copyright (c) 2003-2008 Open Source Applications Foundation
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

from twisted.internet.protocol import Factory
from twisted.protocols import basic
#from twisted.test.ssl_helpers import ServerTLSContext
from twisted.internet import reactor
import sys

USER = "test"
PASS = "test"

CERT_FILE = "./cert/server.pem"

PORT = 1100
SSL_PORT = 9930

SSL_SUPPORT = True
START_SSL = False
UIDL_SUPPORT = True
INVALID_SERVER_RESPONSE = False
NO_CAPABILITY_RESPONSE = False
INVALID_LOGIN_RESPONSE = False
DENY_CONNECTION = False
DROP_CONNECTION = False
BAD_TLS_RESPONSE = False
TIMEOUT_RESPONSE = False
TIMEOUT_DEFERRED = False
SLOW_GREETING = False

"""Commands"""
CONNECTION_MADE = "+OK POP3 localhost v2003.83 server ready" 

CAPABILITIES = [
"TOP",
"LOGIN-DELAY 180",
"USER",
"SASL LOGIN"
]

CAPABILITIES_SSL = "STLS"
CAPABILITIES_UIDL = "UIDL"

 
INVALID_RESPONSE = "-ERR Unknown request"
VALID_RESPONSE = "+OK Command Completed"
AUTH_DECLINED = "-ERR LOGIN failed"
AUTH_ACCEPTED = "+OK Mailbox open, 0 messages"
TLS_ERROR = "-ERR server side error start TLS handshake"
LOGOUT_COMPLETE = "+OK quit completed"
BEGIN_TLS = "+OK Begin TLS negotiation now"
TLS_NOT_AVAILABLE = "-ERR TLS nnot available"
NOT_LOGGED_IN = "-ERR Unknown AUHORIZATION state command"
STAT = "+OK 0 0"
UIDL = "+OK Unique-ID listing follows\r\n."
LIST = "+OK Mailbox scan listing follows\r\n."
CAP_START = "+OK Capability list follows:"


class POP3TestServer(basic.LineReceiver):
    def __init__(self, contextFactory = None):
        self.loggedIn = False
        self.caps = None
        self.tmpUser = None
        self.ctx = contextFactory 

    def sendSTATResp(self, req):
        self.sendLine(STAT)

    def sendUIDLResp(self, req):
        self.sendLine(UIDL)

    def sendLISTResp(self, req):
        self.sendLine(LIST)

    def sendCapabilities(self):
        if self.caps is None:
            self.caps = [CAP_START]

        if UIDL_SUPPORT:
            self.caps.append(CAPABILITIES_UIDL)

        if SSL_SUPPORT:
            self.caps.append(CAPABILITIES_SSL)

        for cap in CAPABILITIES:
            self.caps.append(cap)
        resp = '\r\n'.join(self.caps)
        resp += "\r\n."

        self.sendLine(resp)


    def connectionMade(self):
        if DENY_CONNECTION:
            self.transport.loseConnection()
            return

        if SLOW_GREETING:
            reactor.callLater(20, self.sendGreeting)

        else:
            self.sendGreeting()

    def sendGreeting(self):
        self.sendLine(CONNECTION_MADE)

    def lineReceived(self, line):
        """Error Conditions"""
        if TIMEOUT_RESPONSE:
            """Do not respond to clients request"""
            return

        if DROP_CONNECTION:
            self.transport.loseConnection()
            return

        elif "CAPA" in line.upper():
            if NO_CAPABILITY_RESPONSE:
                self.sendLine(INVALID_RESPONSE)
            else:
                self.sendCapabilities()

        elif "STLS" in line.upper() and SSL_SUPPORT:
            if BAD_TLS_RESPONSE: 
                self.sendLine("+OK here is some garbage TLS not started")
            else:
                self.startTLS()

        elif "USER" in line.upper():
            if INVALID_LOGIN_RESPONSE:
                self.sendLine(INVALID_RESPONSE)
                return

            resp = None
            try:
                self.tmpUser = line.split(" ")[1]
                resp = VALID_RESPONSE
            except:
                resp = AUTH_DECLINED

            self.sendLine(resp)

        elif "PASS" in line.upper():
            resp = None
            try:
                pwd = line.split(" ")[1]

                if self.tmpUser is None or pwd is None:
                    resp = AUTH_DECLINED
                elif self.tmpUser == USER and pwd == PASS:
                    resp = AUTH_ACCEPTED
                    self.loggedIn = True
                else:
                    resp = AUTH_DECLINED
            except:
                resp = AUTH_DECLINED

            self.sendLine(resp)

        elif "QUIT" in line.upper():
            self.loggedIn = False
            self.sendLine(LOGOUT_COMPLETE)
            self.disconnect()

        elif INVALID_SERVER_RESPONSE:
            self.sendLine(INVALID_RESPONSE)

        elif not self.loggedIn:
            self.sendLine(NOT_LOGGED_IN)

        elif "NOOP" in line.upper():
            self.sendLine(VALID_RESPONSE)

        elif "STAT" in line.upper():
            if TIMEOUT_DEFERRED:
                return
            self.sendLine(STAT)

        elif "LIST" in line.upper():
            if TIMEOUT_DEFERRED:
                return
            self.sendLine(LIST)

        elif "UIDL" in line.upper():
            if TIMEOUT_DEFERRED:
                return
            elif not UIDL_SUPPORT:
                self.sendLine(INVALID_RESPONSE)
                return

            self.sendLine(UIDL)

    def startTLS(self):
        if self.ctx is None:
            return
            #self.ctx = ServerTLSContext(CERT_FILE)

        if SSL_SUPPORT and self.ctx is not None:
            self.sendLine(BEGIN_TLS)
            self.transport.startTLS(self.ctx)
        else:
            self.sendLine(TLS_NOT_AVAILABLE)

    def disconnect(self):
        self.transport.loseConnection()


usage = """popServer.py [arg] (default is Standard POP Server with no messages)
start_ssl  - Start in SSL mode only accept encypted traffic
no_ssl  - Start with no SSL support
no_uidl - Start with no UIDL support
bad_resp - Send a non-RFC compliant response to the Client
no_cap   - send a "-ERR" response to a 'CAPA' request
bad_login_resp - send a non-RFC compliant response when the Client sends a 'LOGIN' request
deny - Deny the connection
drop - Drop the connection after sending the greeting
bad_tls - Send a bad response to a STARTTLS
timeout - Do not return a response to a Client request
to_deferred - Do not return a response on a 'Select' request. This
              will test Deferred callback handling
slow - Wait 20 seconds after the connection is made to return a Server Greeting
"""

def printMessage(msg):
    print "Server Starting in %s mode" % msg

def processArg(arg):

    if arg.lower() == 'no_ssl':
        global SSL_SUPPORT
        SSL_SUPPORT = False
        printMessage("NON-SSL")

    elif arg.lower() == 'start_ssl':
        global START_SSL
        START_SSL = True
        printMessage("Starting in SSL Mode")

    elif arg.lower() == 'no_uidl':
        global UIDL_SUPPORT
        UIDL_SUPPORT = False
        printMessage("NON-UIDL")

    elif arg.lower() == 'bad_resp':
        global INVALID_SERVER_RESPONSE
        INVALID_SERVER_RESPONSE = True
        printMessage("Invalid Server Response")

    elif arg.lower() == 'no_cap':
        global NO_CAPABILITY_RESPONSE
        NO_CAPABILITY_RESPONSE = True
        printMessage("No Capability Response")

    elif arg.lower() == 'bad_login_resp':
        global INVALID_LOGIN_RESPONSE
        INVALID_LOGIN_RESPONSE = True
        printMessage("Invalid Capability Response")

    elif arg.lower() == 'deny':
        global DENY_CONNECTION 
        DENY_CONNECTION = True
        printMessage("Deny Connection")

    elif arg.lower() == 'drop':
        global DROP_CONNECTION 
        DROP_CONNECTION = True
        printMessage("Drop Connection")


    elif arg.lower() == 'bad_tls':
        global BAD_TLS_RESPONSE 
        BAD_TLS_RESPONSE = True
        printMessage("Bad TLS Response")

    elif arg.lower() == 'timeout':
        global TIMEOUT_RESPONSE
        TIMEOUT_RESPONSE = True
        printMessage("Timeout Response")

    elif arg.lower() == 'to_deferred':
        global TIMEOUT_DEFERRED
        TIMEOUT_DEFERRED = True
        printMessage("Timeout Deferred Response")

    elif arg.lower() == 'slow':
        global SLOW_GREETING
        SLOW_GREETING = True
        printMessage("Slow Greeting")

    elif arg.lower() == '--help':
        print usage
        sys.exit()

    else:
        print usage
        sys.exit()

def main():

    if len(sys.argv) < 2:
        printMessage("POP3 with no messages")
    else:
        args = sys.argv[1:]

        for arg in args:
            processArg(arg)

    f = Factory()
    f.protocol = POP3TestServer

    #if START_SSL:
    #    reactor.listenSSL(SSL_PORT, f, ServerTLSContext(CERT_FILE))
    #else:
    reactor.listenTCP(PORT, f)

    reactor.run()

if __name__ == '__main__':
    main()
