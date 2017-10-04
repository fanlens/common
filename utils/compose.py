#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Function composing"""
import functools
from typing import TypeVar, Callable, Any, List  # pylint: disable=unused-import

_CT = TypeVar('_CT')
_CS = TypeVar('_CS')
_CR = TypeVar('_CR')


def _compose(func_f: Callable[[_CS], _CR], func_g: Callable[[_CT], _CS]) -> Callable[[_CT], _CR]:
    def _composed(x: _CT) -> _CR:
        return func_f(func_g(x))

    return _composed


T = TypeVar('T')
R = TypeVar('R')


def compose(func: Callable[[T], Any], *funcs: Callable[[Any], Any]) -> Callable[[T], R]:
    """convenience function to chain transformations"""
    function_list = [func]  # type: List[Callable[[Any], Any]]
    function_list.extend(funcs)
    composed = functools.reduce(_compose,
                                reversed(function_list),
                                lambda x: x)
    return composed
