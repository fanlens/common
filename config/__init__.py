#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""the config module holds helpers to access file based and db based config files"""
from abc import ABCMeta
from collections import Mapping


class ConfigBase(Mapping, metaclass=ABCMeta):
    """base class for the different config classes"""

    def __init__(self, section: str = ''):
        self._section = section


    @property
    def section(self):
        """:return: the section name covered by this instance"""
        return self._section
