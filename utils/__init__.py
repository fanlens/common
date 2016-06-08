#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""different utility functions"""

import time


def now(millis=True) -> int:
    """:return: current epoch in milliseconds"""
    return int(time.time() * (1000 if millis else 1))
