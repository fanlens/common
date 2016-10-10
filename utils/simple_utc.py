#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import tzinfo, timedelta


class SimpleUTC(tzinfo):
    def tzname(self):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


simple_utc = SimpleUTC()
