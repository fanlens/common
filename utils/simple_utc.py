#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Conversion/Helper for UTC types and parsing"""
from typing import Optional
from datetime import tzinfo, timedelta, datetime


class SimpleUTC(tzinfo):
    """Class to be used to give naive UTC tzinfo for parsed timestamps"""

    def tzname(self, _: Optional[datetime]):
        return "UTC"

    def utcoffset(self, _: Optional[datetime]):
        return timedelta(0)

    def dst(self, _: Optional[datetime]):
        return 0


SIMPLE_UTC = SimpleUTC()
