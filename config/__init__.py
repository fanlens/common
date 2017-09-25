#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import os
from configparser import ConfigParser
from functools import lru_cache

from pkg_resources import resource_string


class StrictEnvDefaultConfigParser(ConfigParser):
    def __init__(self, defaults=None):
        super(ConfigParser, self).__init__(defaults=defaults)

    def get(self, section, option, raw=False, vars=None, fallback=object()):
        vars = vars or dict((k, v) for k, v in os.environ.items() if k.startswith('FL_'))
        return super(ConfigParser, self).get(section, option, raw=raw, vars=vars, fallback=fallback)

    def items(self, section=None, raw=False, vars=None):
        if section:
            sections = [section]
        else:
            sections = self.sections()
        return [(option, self.get(section=section, option=option))
                for option in self.options(section)
                for section in sections]


@lru_cache()
def _get_config(module_name: str, config_file_name: str, max_depth: int = 0) -> StrictEnvDefaultConfigParser:
    parser = StrictEnvDefaultConfigParser()
    config_string = None
    read_err = None
    found = False
    while max_depth >= 0 and not found:
        try:
            config_string = str(resource_string(module_name, config_file_name), 'utf-8')
            found = True
        except FileNotFoundError as err:
            read_err = err
            config_file_name = '../' + config_file_name
            max_depth -= 1
    if not found:
        raise read_err or RuntimeError('Could not load config file')
    parser.read_string(config_string)
    return parser


def get_config(module_name: str = None,
               config_file_name: str = 'config.ini',
               max_depth=2) -> StrictEnvDefaultConfigParser:
    """
    :param module_name: optional, will use callers module parent directory name if not specified. allows for nicer config() call in default case
    :param config_file_name: name of the config file located in the callers package
    :param max_depth: how many directories to step up while searching for config.ini
    :return: the parsed config file using os.environ as defaults
    """
    if not module_name:
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        module_name = caller_module.__name__
    return _get_config(module_name, config_file_name, max_depth)
