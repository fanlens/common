#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""buffer utilities"""


class Buffered(object):
    """simple buffered execution workflow"""

    def __init__(self, iterator, handler, max_size=1):
        """create a new buffer for the provided `iterator` and execute `handler` in chunks of `max_size` elements"""
        self._iterator = iterator
        self._handler = handler
        self._buffer = []
        self._max_size = max_size

    def __call__(self):
        """exhaust the iterator and call the handler with chunks of `max_size`"""
        for element in self._iterator:
            self._buffer.append(element)
            if len(self) >= self.max_size:
                self._handler(self._buffer)
                self._buffer = []
        if len(self) > 0:
            self._handler(self._buffer)
            self._buffer = []

    @property
    def max_size(self):
        """get maximum buffer size"""
        return self._max_size

    def __len__(self):
        """get length of current buffer"""
        return len(self._buffer)
