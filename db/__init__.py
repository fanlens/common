#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""the db module is responsible for managing the database connections it's based on sqlalchemy"""

import typing
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

from config.env import Environment

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Insert

ON_CONFLICT_DO_NOTHING = 'ON CONFLICT DO NOTHING'
ON_CONFLICT_DO_UPDATE = 'ON CONFLICT (%(column)s) DO UPDATE SET %(updates)s'

def get_model_dict(model: declarative_base) -> dict:
    """:return: dict version of the model"""
    return dict((column.name, getattr(model, column.name))
                for column in model.__table__.columns
                if getattr(model, column.name) is not None)


@compiles(Insert)
def append_string(insert, compiler, **kw):
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
    model_dict = get_model_dict(entry)
    if update_fields is None:
        update_fields = set(model_dict.keys())
    update_fields = set(update_fields).difference(set(exclude_fields))
    update_string = ', '.join(['{0} = %({0})s'.format(key) for key in update_fields])
    session.execute(entry.__table__.insert(
        postgresql_append_string=ON_CONFLICT_DO_UPDATE % dict(column=column, updates=update_string)), model_dict)
    if flush:
        session.flush()


def insert_or_ignore(session: Session, entry: declarative_base, flush=False):
    """postgresql specific insert or ignore logic"""
    session.execute(entry.__table__.insert(postgresql_append_string=ON_CONFLICT_DO_NOTHING),
                    get_model_dict(entry))
    if flush:
        session.flush()


def connect(username, password, database, host='localhost', port=5432):
    """:return: a connection and a metadata object"""
    url = 'postgresql://{}:{}@{}:{}/{}'.format(username, password, host, port, database)
    engine = sqlalchemy.create_engine(url, client_encoding='utf8')
    return engine


_engine = connect(**Environment("DB"))
_Session = sessionmaker(bind=_engine, autoflush=True)
_AutoSession = sessionmaker(bind=_engine, autocommit=True, autoflush=True)
Base = declarative_base(bind=_engine)


class DB(object):
    """ central database manager """

    def __init__(self, create_all=True):
        if create_all:
            Base.metadata.create_all(checkfirst=True)

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        """:return: the engine"""
        return _engine

    @property
    def session(self) -> Session:
        """:return: a session"""
        return _Session()

    @property
    def auto_session(self) -> Session:
        """:return: an autocommit session"""
        return _AutoSession()

    @contextmanager
    def ctx(self) -> Session:
        """:return: a sqlalchemy session for the configured database"""
        session = self.session
        try:
            yield session
        except:
            session.rollback()
        finally:
            session.close()


T = typing.TypeVar('T', bound=Base)


class DBMapper(typing.Generic[T]):
    """helper class to apply function on all entries in db"""

    def __init__(self, entry_class: T):
        self._entry_class = entry_class
        self._filter = tuple()
        self._dry_run = False
        self._db = DB()

    @staticmethod
    def _error_handler(fun: typing.Callable[[T], T], session: Session):
        def _wrapped(entry):
            try:
                return fun(entry)
            except Exception as err:
                print("caught error during mapping, skipping", err)
                session.expunge(entry)

        return _wrapped

    def map(self, fun: typing.Callable[[T], T], tee=True) -> typing.Iterable[T]:
        """applies fun to each entry in db optionally yielding each result"""
        with self._db.ctx() as session:
            query = (session.query(self.entry_class)
                     .filter(*self._filter)
                     .yield_per(1000)
                     .enable_eagerloads(False))
            error_handling_fun = self._error_handler(fun, session)
            mapped_entries = (error_handling_fun(entry) for entry in query)
            for mapped_entry in mapped_entries:  # need to exhaust generator
                if tee:
                    yield mapped_entry
            # todo: lenience parameter for errors??
            session.commit()

    def each(self, fun: typing.Callable[[T], T]) -> None:
        """ simpler version of map without getting access to intermediary results """
        list(self.map(fun, tee=False))

    @property
    def entry_class(self) -> T:
        """:return: the class for the entries mapped"""
        return self._entry_class

    @property
    def filter(self):
        """:return: the current filter criteria"""
        return self._filter

    @filter.setter
    def filter(self, *criterion):
        """set the filter criteria"""
        self._filter = criterion


# todo: inefficient for non changing ops
def modifying(keys: typing.Iterable[str] = []):
    """add the sql_alchemy flag to the specified keys of this mapper"""

    def decorator(fun: typing.Callable[[Base], Base]):
        """the actual decorator for the mapper"""

        def wrapped(*args, **kwargs) -> Base:
            """set the flag_modified key"""
            mapped = fun(*args, **kwargs)
            for key in keys:
                flag_modified(mapped, key)
            return mapped

        return wrapped

    return decorator


def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count
