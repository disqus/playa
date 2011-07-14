"""
playa.ext.audio.index
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

from __future__ import absolute_import

import hashlib
import os.path
import re
import time
import threading

from collections import defaultdict
from mutagen.easymp4 import EasyMP4
from mutagen.mp3 import EasyMP3
from playa.common.storage import load, save

def get_metadata(full_path):
    metadata = {
        'filename': os.path.basename(full_path)[:-4],
    }
    
    if full_path.endswith('mp4') or full_path.endswith('m4a'):
        id3_cls = EasyMP4
    elif full_path.endswith('mp3'):
        id3_cls = EasyMP3
    else:
        id3_cls = None
    
    if id3_cls:
        try:
            audio = id3_cls(full_path)
        except Exception, e:
            print e
            audio = None
    
        if audio:
            for key in ('artist', 'title', 'album', 'genre'):
                try:
                    value = unicode(audio[key][0])
                except (IndexError, KeyError):
                    continue

                metadata[key] = value

            metadata['length'] = audio.info.length
    
    return metadata

def get_key(full_path):
    metadata = get_metadata(full_path)

    key = tuple([metadata.get(k) for k in ('artist', 'title', 'album')])

    if not any(key):
        key = hashlib.md5(full_path).hexdigest()

    return key

class AudioIndex(threading.Thread):
    RE_SEARCH_TOKENS = re.compile(r'\b([^\:]+):("[^"]*"|[^\s]*)')

    def __init__(self, app, filter_keys, text_keys):
        super(AudioIndex, self).__init__()
        self.app = app
        self.filter_keys = filter_keys
        self.text_keys = text_keys
        self.tokenized = defaultdict(lambda:defaultdict(int))
        self.filters = defaultdict(lambda:defaultdict(list))
        self.filters_ci = defaultdict(lambda:defaultdict(list))
        self.metadata = defaultdict(dict)
        self.files = {}
        self._data_file = os.path.join(self.app.config['DATA_PATH'], 'index.db')
        self._ready = False

    def __len__(self):
        return len(self.files)

    def run(self):
        if os.path.exists(self._data_file):
            self.load()
            self._ready = True
        
        while True:
            start = time.time()

            print "Building audio index"

            prev = self.files.keys()

            for key, full_path in self.files.iteritems():
                if not os.path.exists(full_path):
                    del self.files[key]

            for path in self.app.config['AUDIO_PATHS']:
                self.add_path(path)

            print "Done! (%d entries, took %.2fs)" % (len(self), time.time() - start)

            self._ready = True

            if self.files.keys() != prev:
                self.save()
            
            time.sleep(3)
        
    
    def load(self):
        results = load(self._data_file)
        if not results:
            return
        
        for k, v in results.iteritems():
            if k == 'files' and not isinstance(v, dict):
                continue
            
            if isinstance(v, dict):
                getattr(self, k).update(v)
            else:
                setattr(self, k, v)

    def save(self):
        save(self._data_file, {
            'tokenized': dict(self.tokenized),
            'filters': dict(self.filters),
            'filters_ci': dict(self.filters_ci),
            'metadata': dict(self.metadata),
            'files': self.files,
        })
    
    def add_path(self, path):
        dir_list = [path]
        
        while dir_list:
            path = dir_list.pop()
            for fn in os.listdir(path): 
                if fn.startswith('.'):
                    continue

                full_path = os.path.join(path, fn)

                try:
                    unicode(full_path)
                except:
                    continue
            
                if os.path.isdir(full_path):
                    dir_list.append(full_path)
                    continue
                elif full_path in self.files.values():
                    continue

                try:
                    metadata = get_metadata(full_path)
                except Exception, e:
                    print e
                    continue
                
                tokens = []

                for key, value in metadata.iteritems():
                    if key in self.text_keys:
                        tokens.extend(filter(None, value.lower().split(' ')))

                    if key in self.filter_keys:
                        self.filters[key][value].append(full_path)
                        self.filters_ci[key][value.lower()].append(full_path)

                self.metadata[full_path] = metadata
                self.files[get_key(full_path)] = full_path

                for token in tokens:
                    self.tokenized[token][full_path] += 1
                    
    def search(self, query):
        text_results = defaultdict(int)
        filter_results = defaultdict(int)

        tokens = self._get_search_query_tokens(query.lower())
        text_tokens = tokens.pop('', None)

        for token, value in tokens.iteritems():
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            if value in self.filters_ci[token]:
                for full_path in self.filters_ci[token][value]:
                    filter_results[full_path] += 1

        if tokens and not filter_results:
            return None

        if text_tokens:
            for token in text_tokens.split(' '):
                for full_path, count in self.tokenized[token].iteritems():
                    text_results[full_path] += count
        
        if filter_results:
            # We need to remove any results which didnt match filters
            results = {}
            for full_path, count in filter_results.iteritems():
                if not text_tokens or text_results[full_path]:
                    results[full_path] = text_results[full_path] + count
        else:
            results = text_results

        if not results:
            return None

        return sorted(results.items(), key=lambda x: -x[1])[:50]

    def _get_search_query_tokens(self, query):
        """
        Parses a search query for supported tokens and returns a dictionary.

        e.g., "author:test my message" -> {'author': 'test', '': 'my message'}

        """
        tokens = defaultdict(str)
        def _token_repl(matchobj):
            tokens[matchobj.group(1)] = matchobj.group(2)
            return ''
        query = self.RE_SEARCH_TOKENS.sub(_token_repl, query.strip()).strip()
        if query:
            tokens[''] = query
        return tokens