"""
playa.common.storage
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

try:
    import cPickle as pickle
except:
    import pickle

import time

def save(path, data):
    start = time.time()

    print "Saving %s" % path

    with open(path, 'wb') as fp:
        pickle.dump(data, fp)
    
    print "Done! (took %.2fs)" % (time.time() - start)

def load(path):
    start = time.time()

    print "Loading %s" % path

    with open(path, 'rb') as fp:
        try:
            result = pickle.load(fp)
        except EOFError:
            return

    print "Done! (took %.2fs)" % (time.time() - start)

    return result