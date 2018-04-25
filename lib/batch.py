class Batch(object):
    def __init__(self, max_items=0):
        self._max_items = max_items if isinstance(max_items, int) else 0
        self._items = []

    def __len__(self):
        return len(self._items)

    def is_empty(self):
        return self.__len__() == 0

    def is_ready(self):
        if self._max_items <= 0:
            return False

        return self.__len__() >= self._max_items

    def get_list(self):
        return self._items

    def add(self, item):
        self._items.append(item)

    def clear(self):
        self._items = []
