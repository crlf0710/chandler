__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2005 Open Source Applications Foundation"
__license__ = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

import httplib
import socket
import mimetypes
import base64
import libxml2
import urlparse
import logging
import crypto.ssl as ssl
import M2Crypto.httpslib as httpslib

logger = logging.getLogger('WebDAV')
logger.setLevel(logging.DEBUG)

XML_CONTENT_TYPE = 'text/xml; charset="utf-8"'
XML_DOC_HEADER = '<?xml version="1.0" encoding="utf-8"?>'

DEFAULT_RETRIES = 3

class Client(object):

    def __init__(self, host, port=80, username=None, password=None,
     useSSL=False, ctx=None, retries=DEFAULT_RETRIES):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.useSSL = useSSL
        self.ctx = ctx
        self.conn = None
        self.retries = retries

    def connect(self):
        logger.debug("Opening connection")

        if self.useSSL:
            if self.ctx is None:
                self.ctx = ssl.getSSLContext()
            self.conn = httpslib.HTTPSConnection(self.host,
                                                 self.port,
                                                 ssl_context=self.ctx)
        else:
            self.conn = httplib.HTTPConnection(self.host, self.port)

        self.conn.debuglevel = 0

    def mkcol(self, url, extraHeaders={ }):
        return self._request('MKCOL', url, extraHeaders=extraHeaders)

    def get(self, url, extraHeaders={ }):
        return self._request('GET', url, extraHeaders=extraHeaders)

    def put(self, url, body, contentType=None, contentEncoding=None,
     extraHeaders={ }):
        extraHeaders = extraHeaders.copy()
        if not contentType:
            contentType, contentEncoding = mimetypes.guess_type(url)
        if contentType:
            extraHeaders['Content-Type'] = contentType
        if contentEncoding:
            extraHeaders['Content-Encoding'] = contentEncoding
        return self._request('PUT', url, body=body, extraHeaders=extraHeaders)

    def head(self, url, extraHeaders={ }):
        return self._request('HEAD', url, extraHeaders=extraHeaders)

    def delete(self, url, extraHeaders={ }):
        return self._request('DELETE', url, extraHeaders=extraHeaders)

    def propfind(self, url, body=None, depth=None, extraHeaders={ }):
        extraHeaders = extraHeaders.copy()
        extraHeaders['Content-Type'] = XML_CONTENT_TYPE
        if depth is not None:
            extraHeaders['Depth'] = str(depth)
        return self._request('PROPFIND', url, body, extraHeaders=extraHeaders)

    def ls(self, url, extraHeaders={ }):
        # A helper method which parses a PROPFIND response and returns a
        # list of (path, etag) tuples, providing an easy way to get the
        # contents of a collection

        resources = []
        resp = self.propfind(url, depth=1, extraHeaders=extraHeaders)
        if resp.status != httplib.MULTI_STATUS:
            raise WebDAVException() # @@@MOR Any way to recover from this?

        # Parse the propfind, pulling out the URLs for each child along
        # with their ETAGs, and storing them in the resourceList dictionary:
        text = resp.read()
        # @@@ Hack to avoid libxml2 complaints:
        text = text.replace('="DAV:"', '="http://osafoundation.org/dav"')
        try:
            doc = libxml2.parseDoc(text)
        except:
            logging.error("Parsing response failed: %s" % text)
            raise
        node = doc.children.children
        while node:
            if node.type == "element":
                if node.name == "response":
                    path = None
                    etag = None
                    child = node.children
                    while child:
                        if child.name == "href":
                            # use only the path portion of the url:
                            path = urlparse.urlparse(child.content)[2]
                        elif child.name == "propstat":
                            gchild = child.children
                            while gchild:
                                if gchild.name == "prop":
                                    ggchild = gchild.children
                                    while ggchild:
                                        if ggchild.name == "getetag":
                                            etag = ggchild.content
                                        ggchild = ggchild.next
                                gchild = gchild.next
                        child = child.next
                    if path and not path.endswith("/"):
                        resources.append( (path, etag) )
            node = node.next
        doc.freeDoc()
        return resources

    def getacl(self, url, extraHeaders={ }):
        # Strictly speaking this method is not needed, you could use
        # propfind, or getprops.
        body = XML_DOC_HEADER + \
               '<D:propfind xmlns:D="DAV:"><D:prop><D:acl/></D:prop></D:propfind>'
        return self.propfind(url, body, extraHeaders=extraHeaders)

    def setacl(self, url, acl, extraHeaders={ }):
        # url is the resource who's acl we are changing
        # acl is an ACL object that sets the actual ACL
        body = XML_DOC_HEADER + str(acl)
        headers = extraHeaders.copy()
        headers['Content-Type'] = XML_CONTENT_TYPE
        return self._request('ACL', url, body, headers)

    def _request(self, method, url, body=None, extraHeaders={ }):
        logger.debug("_request: %s %s" % (method, url))

        if self.conn is None:
            self.connect()

        if self.username:
            auth = 'Basic ' + \
             base64.encodestring(self.username + ':' + self.password).strip()
            extraHeaders = extraHeaders.copy()
            extraHeaders['Authorization'] = auth

        triesLeft = self.retries
        while triesLeft > 0:
            logger.debug("%d tries left" % triesLeft)
            triesLeft -= 1

            try:
                logger.debug("Sending request: %s %s" % (method, url))
                self.conn.request(method, url, body, extraHeaders)
            except httplib.CannotSendRequest:
                logger.debug("Got CannotSendRequest")
                self.connect()
                continue
            except socket.error, e:
                logger.debug("Got socket error: %s" % e)
                self.connect()
                continue

            try:
                response = self.conn.getresponse()
            except httplib.BadStatusLine, e:
                if not e.line:
                    # This condition means the server closed a keepalive
                    # connection.  Reopen.
                    logger.debug("Server closed keepalive connection")
                    self.connect()
                    continue
                else:
                    # We must have gotten a garbled status line
                    raise
            except socket.error, e:
                logger.debug("Got socket error: %s" % e)
                self.connect()
                continue

            # Check for HTTP redirects (30X codes)
            if response.status in (httplib.MOVED_PERMANENTLY, httplib.FOUND,
             httplib.SEE_OTHER, httplib.TEMPORARY_REDIRECT):
                response.read() # Always need to read each response
                url = response.getheader('Location')
                logger.debug("Redirecting to: %s" % url)
                continue

            return response

        # After the retries, we didn't succeed.
        # @@@MOR What sort of exceptions do we want to raise here?
        raise ConnectionError()

class WebDAVException(Exception):
    pass

class ConnectionError(WebDAVException):
    pass

class NotFound(WebDAVException):
    pass

class NotAuthorized(WebDAVException):
    pass
