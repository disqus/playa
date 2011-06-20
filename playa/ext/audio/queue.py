import random

class Queue(object):
    def __init__(self):
        self.clear()
    
    def __getitem__(self, *args):
        return self.queue.__getitem__(*args)
    
    def __len__(self):
        return len(self.queue)
    
    def __ne__(self):
        return bool(self.queue)

    def add(self, item):
        self.queue.append(item)

    def extend(self, items):
        self.queue.extend(items)

    def clear(self):
        self.queue = []
        self.pos = -1

    def next(self):
        self.pos += 1

        if self.pos >= len(self.queue):
            self.pos = 0

        return self.queue[self.pos]

    def current(self):
        if not self.queue:
            return
        return self.queue[self.pos]

    def shuffle(self):
        random.shuffle(self.queue)