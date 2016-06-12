#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""a db backed config"""

import typing

from config import ConfigBase
from db import DB
from db.models.config import DBSetting


class Config(ConfigBase):
    """
    database backed config module
    """

    def __init__(self, section=''):
        super().__init__(section=section)
        self._db = DB()

    def __len__(self):
        with self._db.ctx() as session:
            if self.section:
                return len(session
                           .query(DBSetting)
                           .filter(DBSetting.key == self._section)
                           .one().config)
            else:
                return session.query(DBSetting).count()

    def __getitem__(self, key) -> dict:
        with self._db.ctx() as session:
            if self.section:
                config = (session
                          .query(DBSetting)
                          .filter(DBSetting.key == self._section)
                          .one()
                          .config)
                return config[key]
            else:
                config = (session
                          .query(DBSetting)
                          .filter(DBSetting.key == key)
                          .one()
                          .config)
                return config

    def __iter__(self):
        with self._db.ctx() as session:
            if self.section:
                return iter(session.query(DBSetting)
                            .filter(DBSetting.key == self._section)
                            .one().config)
            else:
                return (tup[0] for tup in session.query(DBSetting.key).all())


def _set_value(key: str, param: str, value: typing.Any):
    """
    set a parameter for the config stored at key
    :param key: the top level key of this config
    :param param: the key of the field to set
    :param value: the value to set
    """
    with DB().ctx() as session:
        setting = session.query(DBSetting).get(key)
        setting.config[param] = value
        session.query(DBSetting).filter(DBSetting.key == key).update({DBSetting.config: setting.config})
        session.commit()


if __name__ == """__main__""":
    import argparse

    parser = argparse.ArgumentParser(description='provide name of facebook page')
    parser.add_argument('-k', '--key', type=str, help='the top level key', required=True)
    parser.add_argument('-p', '--param', type=str, help='the param to set', required=True)
    parser.add_argument('-v', '--value', type=str, help='the value to use, if not present return current value',
                        required=False)
    cli_args = vars(parser.parse_args())

    if cli_args['value'] is None:
        print(Config(cli_args['key'])[cli_args['param']])
    else:
        _set_value(**cli_args)