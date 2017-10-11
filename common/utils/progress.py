#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Base class for progress callbacks"""
from abc import ABCMeta, abstractmethod
from typing import Any


class ProgressCallbackBase(metaclass=ABCMeta):
    # pylint: disable=too-few-public-methods
    """Simple Helper that stores the progress of the current task int the task meta"""

    @abstractmethod
    def __call__(self, *args: Any, **meta: Any) -> None:
        """
        :param args: additional args
        :param meta: metadata to store
        """
        pass
