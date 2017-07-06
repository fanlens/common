#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import uuid
from contextlib import contextmanager
from enum import Enum

from db import default_engine
from db.models.job import Job
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool


class Space(Enum):
    WORKER = 1
    BRAIN = 2
    WEB = 3
    CRAWLER = 4


_start_job_sql = text('''
INSERT INTO activity.job(owner, pid, oid, granted, timestamp)
SELECT CURRENT_USER, pg_backend_pid(), :oid, pg_try_advisory_lock(:oid), CASE WHEN :timestamp IS NULL THEN now() ELSE :timestamp END
RETURNING *
''')


def init_exclusive_run(oid: Space):
    run_id = uuid.uuid1()
    engine = default_engine(poolclass=NullPool)
    connection = engine.connect()
    session = Session(bind=connection, autocommit=False)
    return run_id, engine, connection, session


def start_exclusive_run(oid: Space, session: Session, timestamp: datetime.datetime = None, lenient=False):
    id, owner, pid, oid, granted, timestamp = session.execute(_start_job_sql,
                                                              params=dict(oid=oid.value,
                                                                          timestamp=timestamp)).fetchone()
    session.commit()
    job = Job(id=id, owner=owner, pid=pid, oid=oid, granted=granted, timestamp=timestamp)
    if not job.granted and not lenient:
        raise RuntimeError('couldn\'t grant job for oid: %d' % oid)
    return job


def close_exclusive_run(run):
    run_id, engine, connection, session = run
    session.close()
    connection.close()
    engine.dispose()


@contextmanager
def exclusive_run_ctx(oid: Space):
    run = init_exclusive_run(oid)
    run_id, engine, connection, session = run
    try:
        logging.debug('Starting exclusive job for oid: %d, run: %s' % (oid.value, run_id))
        start_exclusive_run(oid, session, lenient=False)  # throws exception if it can't start the job
        yield run
    except RuntimeError as err:
        logging.debug('Couldn\'t fetch lock for oid: %d, run: %s' % (oid.value, run_id))
    finally:
        close_exclusive_run(run)
        logging.debug('Done with exclusive job for oid: %d, run: %s' % (oid.value, run_id))


def run_exclusive_job(oid: Space, job: callable):
    try:
        with exclusive_run_ctx(oid):
            return job()
    except RuntimeError as err:
        pass


def runs_exclusive(oid: Space):
    def wrapper(fun: callable):
        def wrapped(*args, **kwargs):
            return run_exclusive_job(oid, fun)

        return wrapped

    return wrapper
