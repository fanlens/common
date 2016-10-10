#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""different utility functions"""

import time


def now(millis=True) -> int:
    """
    :deprecated:
    :return: current epoch in milliseconds"""
    from warnings import warn
    warn('now() is deprecated')
    return int(time.time() * (1000 if millis else 1))
