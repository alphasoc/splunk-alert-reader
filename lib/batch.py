class Batch(object):
    def __init__(self):
        self._items = []

    def __len__(self):
        return len(self._items)

    def is_empty(self):
        return self.__len__() == 0

    def get_list(self):
        return self._items

    def add(self, item):
        self._items.append(item)

    def clear(self):
        self._items = []
