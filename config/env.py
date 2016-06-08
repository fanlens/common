#!/usr/bin/env python
# -*- coding: utf-8 -*-

""".ini file backed settings"""

import os

from config import ConfigBase
from collections import defaultdict


class Environment(ConfigBase):
    """
    loads environment variables starting with 'FL_' for non database backed settings
    """
    _prefix = 'fl_'

    def __init__(self, section: str = ''):
        section = section.lower()
        super().__init__(section=section)
        if section:
            self._settings = dict(('_'.join(k.lower().split('_')[2:]), v) for k, v in os.environ.items() if
                                  k.lower().startswith(self._prefix + self.section))
        else:
            agg = defaultdict(dict)
            for k, (sk, v) in [(k.lower().split('_')[1], ('_'.join(k.lower().split('_')[2:]), v)) for k, v in
                               os.environ.items() if
                               k.lower().startswith(self._prefix + self.section)]:
                agg[k][sk] = v
            self._settings = dict(agg)

    def __len__(self):
        return len(self._settings)

    def __getitem__(self, key) -> dict:
        return self._settings[key.lower()]

    def __iter__(self):
        return iter(self._settings)
