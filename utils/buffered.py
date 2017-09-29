#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utilities to run buffered operations"""

from typing import Iterable, TypeVar, Generic, Callable, List

ET = TypeVar('ET')


class Buffered(Generic[ET]):
    # pylint: disable=too-few-public-methods
    """simple buffered execution workflow"""

    def __init__(self, iterator: Iterable[ET], handler: Callable[[List[ET]], None], max_size: int = 1) -> None:
        """
        create a new buffer for the provided `iterator` and execute `handler` in chunks of `max_size` elements
        :param iterator: the iterator values are drawn from
        :param handler: the handler executed on the buffer. a callable of the form (buffer: List[T]) -> None
        :param max_size: maximum size the buffer can grow to before invoking the handler function. must > 0.
        """
        assert max_size > 0, "buffer must have at least size 1"
        self._iterator = iterator
        self._handler = handler
        self._buffer = []  # type: List[ET]
        self._max_size = max_size

    def __call__(self) -> None:
        """exhaust the iterator and call the handler with chunks of `max_size`"""
        for element in self._iterator:
            self._buffer.append(element)
            if self.__len__() >= self.max_size:
                self._handler(self._buffer)
                self._buffer = []
        if self:
            self._handler(self._buffer)
            self._buffer = []

    @property
    def max_size(self) -> int:
        """get maximum buffer size"""
        return self._max_size

    def __len__(self) -> int:
        """get length of current buffer"""
        return len(self._buffer)
