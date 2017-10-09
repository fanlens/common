#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Tools for exclusive jobs backed by postgres advisory locks"""
import datetime
import logging
import uuid
from collections import namedtuple
from contextlib import contextmanager, suppress
from enum import Enum
from typing import Callable, Optional, Generator, TypeVar, Any
from functools import wraps

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from ..db import default_engine
from ..db.models.job import Job


class Space(Enum):
    """Specified spaces that can host exclusive run within postgres"""
    WORKER = 1
    BRAIN = 2
    WEB = 3
    CRAWLER = 4


_START_JOB_SQL = text('''
INSERT INTO activity.job(owner, pid, oid, granted, timestamp)
SELECT CURRENT_USER, pg_backend_pid(), :oid, pg_try_advisory_lock(:oid), CASE WHEN :timestamp IS NULL THEN now() ELSE :timestamp END
RETURNING *
''')

Run = namedtuple('Run', ['id', 'engine', 'connection', 'session'])


def _init_exclusive_run() -> Run:
    run_id = uuid.uuid1()
    engine = default_engine(poolclass=NullPool)
    connection = engine.connect()
    session = Session(bind=connection, autocommit=False)
    return Run(run_id, engine, connection, session)


def _start_exclusive_run(oid: Space,
                         session: Session,
                         timestamp: Optional[datetime.datetime] = None,
                         lenient: bool = False) -> Job:
    run_id, run_owner, run_pid, run_oid, run_granted, run_timestamp = session.execute(
        _START_JOB_SQL, params=dict(oid=oid.value, timestamp=timestamp)).fetchone()
    session.commit()
    job = Job(id=run_id, owner=run_owner, pid=run_pid, oid=run_oid, granted=run_granted, timestamp=run_timestamp)
    if not job.granted and not lenient:
        raise RuntimeError('couldn\'t grant job for oid: %d' % run_oid)
    return job


def _close_exclusive_run(run: Run) -> None:
    run.session.close()
    run.connection.close()
    run.engine.dispose()


@contextmanager
def exclusive_run_ctx(oid: Space) -> Generator[Run, None, None]:
    """
    exclusive context within the space specified
    :param oid: the space to run in
    """
    run = _init_exclusive_run()
    try:
        logging.debug('Starting exclusive job for oid: %d, run: %s', oid.value, run.id)
        _start_exclusive_run(oid, run.session, lenient=False)  # throws exception if it can't start the job
        yield run
    except RuntimeError:
        logging.debug('Couldn\'t fetch lock for oid: %d, run: %s', oid.value, run.id)
    finally:
        _close_exclusive_run(run)
        logging.debug('Done with exclusive job for oid: %d, run: %s', oid.value, run.id)


_RT = TypeVar('_RT')


def run_exclusive_job(oid: Space, job: Callable[..., _RT], *args: Any, **kwargs: Any) -> _RT:
    """
    run the given job inside an exclusive run within the space provided
    :param oid: the space to run in
    :param job: the callable job to be executed
    :param args: passed to job
    :param kwargs: passed to job
    """
    with suppress(RuntimeError), exclusive_run_ctx(oid):
        return job(*args, **kwargs)


def runs_exclusive(oid: Space) -> Callable[[Callable], Callable[..., _RT]]:
    """
    decorator to run a function insided an exclusive run within the space specified
    :param oid: the space to run in
    """

    def wrapper(fun: Callable[..., _RT]) -> Callable[..., _RT]:
        # pylint: disable=missing-docstring
        @wraps(fun)
        def wrapped(*args: Any, **kwargs: Any) -> _RT:
            return run_exclusive_job(oid, fun, *args, **kwargs)

        return wrapped

    return wrapper
