#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuration helpers. The config mechanism is intended to work in concert with a top level config.ini file
per module. This config.ini can define variables or use string interpolation to fill in fanlens level environment
variables following the pattern FL_*
"""
from typing import Dict, Optional, List
from collections import ItemsView
import inspect
import os
from configparser import ConfigParser
from functools import lru_cache

from pkg_resources import resource_string


class StrictEnvDefaultConfigParser(ConfigParser):  # pylint: disable=too-many-ancestors
    """
    A stricter version of the default config parser that automatically pulls in environment variables starting with
    FL_ on access. The default behaviour leads to spurious elements.
    """

    def __init__(self, defaults: Optional[Dict] = None) -> None:
        super().__init__(defaults=defaults)

    def get(self, section: str, option: str, *, raw: bool = False, vars: Optional[Dict] = None,  # type: ignore
            fallback: Optional[str] = None) -> str:
        # pylint: disable=redefined-builtin
        # honor superclass signature (vars)
        _vars = vars or dict((k, v) for k, v in os.environ.items() if k.startswith('FL_'))
        if fallback:
            return ConfigParser.get(self, section, option, raw=raw, vars=_vars, fallback=fallback)

        return ConfigParser.get(self, section, option, raw=raw, vars=_vars)

    def items(self, section: Optional[str] = None, raw: bool = False,  # type: ignore
              vars: Optional[Dict] = None) -> ItemsView:
        # pylint: disable=redefined-builtin
        # honor superclass signature (vars)
        sections = []  # type: List[str]
        if section:
            sections = [section]
        else:
            sections = self.sections()
            sections.append('DEFAULT')
        return dict((iter_option, self.get(section=iter_section, option=iter_option, raw=raw, vars=vars))
                    for iter_section in sections
                    for iter_option in self.options(iter_section)).items()


@lru_cache()
def _get_config(module_name: str, config_file_name: str, max_depth: int = 0) -> StrictEnvDefaultConfigParser:
    parser = StrictEnvDefaultConfigParser()
    config_string = ''
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


def get_config(module_name: Optional[str] = None,
               config_file_name: str = 'config.ini',
               max_depth: int = 3) -> StrictEnvDefaultConfigParser:
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
