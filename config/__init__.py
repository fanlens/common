#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration helpers. The config mechanism is intended to work in concert with a top level config.ini file
per module. This config.ini can define variables or use string interpolation to fill in fanlens level environment
variables following the pattern FL_*
"""
from typing import AnyStr, Any, Dict, Optional
from collections import ItemsView
import inspect
import os
from configparser import ConfigParser, _UNSET
from functools import lru_cache

from pkg_resources import resource_string


class StrictEnvDefaultConfigParser(ConfigParser):  # pylint: disable=too-many-ancestors
    """
    A stricter version of the default config parser that automatically pulls in environment variables starting with
    FL_ on access. The default behaviour leads to spurious elements.
    """

    def __init__(self, defaults: dict = None):
        super().__init__(defaults=defaults)

    def get(self, section: AnyStr, option: AnyStr,
            *, raw: bool = False, vars: Optional[Dict] = None, fallback: Optional[Any] = _UNSET) -> AnyStr:
        # pylint: disable=redefined-builtin
        # honor superclass signature (vars)
        _vars = vars or dict((k, v) for k, v in os.environ.items() if k.startswith('FL_'))
        return super().get(section, option, raw=raw, vars=_vars, fallback=fallback)

    def items(self, section: Optional[AnyStr] = None, raw: bool = False, vars: Optional[Dict] = None) -> ItemsView:
        # pylint: disable=redefined-builtin
        # honor superclass signature (vars)
        if section:
            sections = [section]
        else:
            sections = self.sections()
        return ItemsView(dict((option, self.get(section=section, option=option, raw=raw, vars=vars))
                              for option in self.options(section)
                              for section in sections))


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
