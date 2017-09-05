#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""the db module is responsible for managing the database connections it's based on sqlalchemy"""

import logging
import typing
import sqlalchemy
from contextlib import contextmanager

from config.env import Environment
from sqlalchemy import func
from sqlalchemy.engine import Engine, ResultProxy
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql.expression import Insert

ON_CONFLICT_DO_NOTHING = 'ON CONFLICT DO NOTHING'
ON_CONFLICT_DO_UPDATE = 'ON CONFLICT (%(column)s) DO UPDATE SET %(updates)s'


def _compiled_str(query):
    return str(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


def _get_model_dict(model: declarative_base) -> dict:
    """:return: dict version of the model"""
    return dict((column.name, getattr(model, column.name))
                for column in model.__table__.columns
                if getattr(model, column.name) is not None)


@compiles(Insert)
def _append_string(insert, compiler, **kw):
    """append a string to insert"""
    s = compiler.visit_insert(insert, **kw)
    if insert.kwargs['postgresql_append_string']:
        if s.rfind("RETURNING") == -1:
            return s + " " + insert.kwargs['postgresql_append_string']
        else:
            return s.replace("RETURNING", " " + insert.kwargs['postgresql_append_string'] + " RETURNING ")
    return s


Insert.argument_for("postgresql", "append_string", None)


def insert_or_update(session: Session, entry: declarative_base, column, update_fields: set = None, exclude_fields=set(),
                     flush=False):
    """postgresql specific insert or update logic"""
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


def insert_or_ignore(session: Session, entry: declarative_base, flush=False) -> ResultProxy:
    """postgresql specific insert or ignore logic"""
    result = session.execute(
        entry.__table__.insert(postgresql_append_string=ON_CONFLICT_DO_NOTHING), _get_model_dict(entry))
    if flush:
        session.flush()
    return result


def create_engine(username: str, password: str, database: str, host: str = 'localhost', port: int = 5432,
                  **kwargs) -> Engine:
    """:return: a connection and a metadata object"""
    url = 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, database)
    return sqlalchemy.create_engine(url, client_encoding='utf8', **kwargs)


def default_engine(**kwargs) -> Engine:
    return create_engine(**Environment("DB"))


Base = declarative_base()
engine = default_engine()
_sessionmaker = sessionmaker(bind=engine, autocommit=False)  # type: Session


@contextmanager
def get_session() -> typing.Generator[Session, None, None]:
    """:return: a sqlalchemy session for the configured database"""
    session = _sessionmaker()

    # noinspection PyBroadException
    try:
        yield session
    except Exception as err:
        logging.exception('caught exception in db context, rolling back transaction', err)
        session.rollback()
    finally:
        session.close()
