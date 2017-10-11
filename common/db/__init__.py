#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""the db module is responsible for managing the database connections it's based on sqlalchemy"""

import logging
from contextlib import contextmanager
from multiprocessing.util import register_after_fork
from typing import Set, Optional, Generator, Any

import sqlalchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Engine, ResultProxy
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, Query
from sqlalchemy.sql.compiler import SQLCompiler
from sqlalchemy.sql.expression import Insert

from ..config import get_config

ON_CONFLICT_DO_NOTHING = 'ON CONFLICT DO NOTHING'
ON_CONFLICT_DO_UPDATE = 'ON CONFLICT (%(column)s) DO UPDATE SET %(updates)s'


def _compiled_str(query: Query) -> str:
    return str(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def _get_model_dict(model: declarative_base) -> dict:
    """:return: dict version of the model"""
    return dict((column.name, getattr(model, column.name))
                for column in model.__table__.columns
                if getattr(model, column.name) is not None)


@compiles(Insert)
def _append_string(insert: Insert, compiler: SQLCompiler, **kwargs: Any) -> str:
    """append a string to insert"""
    append_string: str = compiler.visit_insert(insert, **kwargs)
    if insert.kwargs['postgresql_append_string']:
        if append_string.rfind("RETURNING") == -1:
            return "%s %s" % (append_string, insert.kwargs['postgresql_append_string'])
        return append_string.replace("RETURNING", " " + insert.kwargs['postgresql_append_string'] + " RETURNING ")
    return append_string


Insert.argument_for("postgresql", "append_string", None)


def insert_or_update(session: Session,
                     entry: declarative_base,
                     column: str,
                     update_fields: Optional[Set[str]] = None,
                     exclude_fields: Optional[Set[str]] = None,
                     flush: bool = False) -> ResultProxy:
    # pylint: disable=too-many-arguments
    """postgresql specific insert or update logic"""
    if exclude_fields is None:
        exclude_fields = set()

    model_dict = _get_model_dict(entry)
    if update_fields is None:
        update_fields = set(model_dict.keys())
    update_fields = set(update_fields).difference(set(exclude_fields))
    update_string = ', '.join(['{0} = %({0})s'.format(key) for key in update_fields])
    result = session.execute(entry.__table__.insert(
        postgresql_append_string=ON_CONFLICT_DO_UPDATE % dict(column=column, updates=update_string)), model_dict)
    if flush:
        session.flush()
    return result


def insert_or_ignore(session: Session,
                     entry: declarative_base,
                     flush: bool = False,
                     returning: Optional[str] = None) -> ResultProxy:
    """postgresql specific insert or ignore logic"""
    result = session.execute(
        entry.__table__.insert(postgresql_append_string=ON_CONFLICT_DO_NOTHING, returning=returning),
        _get_model_dict(entry))
    if flush:
        session.flush()
    return result


def create_engine(username: str, password: str, database: str, host: str = 'localhost', port: int = 5432,
                  **kwargs: Any) -> Engine:
    """
    Create a sqlalchemy engine.
    :param username: username used to connect to db
    :param password: password used to connect to db
    :param database: the db used
    :param host: the db host
    :param port: the db port
    :param kwargs: additional arguments for the engine creation
    :return: a new sqlalchemy engine
    """
    url = 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, database)
    return sqlalchemy.create_engine(url, client_encoding='utf8', **kwargs)


def default_engine(**kwargs: Any) -> Engine:
    """
    Create a new sqlalchemy engine based on default values provided via the config.ini
    :param kwargs: add/override additional engine arguments
    :return: sqlalchemy engine
    """
    config = get_config()
    parameters = dict(config.items('DB'))
    parameters.update(kwargs)
    return create_engine(**parameters)


Base: declarative_base = declarative_base()  # pylint: disable=invalid-name

ENGINE = default_engine()
_SESSIONMAKER = sessionmaker(bind=ENGINE, autocommit=False)

register_after_fork(ENGINE, Engine.dispose)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """:return: a sqlalchemy session for the configured database"""
    session = _SESSIONMAKER()

    try:
        yield session
    except Exception:  # pylint: disable=broad-except
        logging.exception('caught exception in db context, rolling back transaction')
        session.rollback()
    finally:
        session.close()
