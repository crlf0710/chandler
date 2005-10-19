
__revision__  = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2003-2004 Open Source Applications Foundation"
__license__   = "http://osafoundation.org/Chandler_0.1_license_terms.htm"


from threading import currentThread, Semaphore


class ThreadSemaphore(object):

    def __init__(self):

        self._semaphore = Semaphore(1)
        self._thread = None

    def acquire(self, wait=True):

        if self._thread is not currentThread():
            result = self._semaphore.acquire(wait)
            if result:
                self._thread = currentThread()

            return result

        return False

    def release(self):

        if self._thread is currentThread():
            self._thread = None
            self._semaphore.release()
        else:
            raise ValueError, 'current thread did not acquire semaphore'
