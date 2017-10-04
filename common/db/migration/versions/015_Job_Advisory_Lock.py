import datetime

from sqlalchemy import Column, Integer, BigInteger, String, Table, text, DateTime, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base

SCHEMA = 'activity'

Base = declarative_base()


# example:
# ﻿insert into activity.job(user_id, pid, oid, granted, timestamp)
# select 5, pg_backend_pid(), 20, pg_try_advisory_lock(20), now()

class Job(Base):
    __tablename__ = "job"

    id = Column(Integer, primary_key=True)
    owner = Column(String, nullable=False)
    pid = Column(Integer, nullable=False)
    oid = Column(BigInteger, nullable=False)
    granted = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    __table_args__ = (
        Index(__tablename__ + "_date_index", timestamp),
        {'schema': SCHEMA}
    )


grants = text('''
GRANT ALL ON TABLE activity.job TO fanlens;
GRANT SELECT ON TABLE activity.job TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE activity.job TO "write.data";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA activity to "write.data";
''')

recreate_job_table_sql = text('''
DROP TABLE IF EXISTS activity.job CASCADE ;

CREATE TABLE activity.job
(
    id UUID NOT NULL,
    user_id INTEGER NOT NULL,
    started TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT job_pkey PRIMARY KEY (id),
    CONSTRAINT job_user_id_id_key UNIQUE (user_id, id),
    CONSTRAINT job_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES public."user" (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE activity.job
    OWNER TO fanlens;

GRANT ALL ON TABLE activity.job TO fanlens;

GRANT SELECT ON TABLE activity.job TO "read.data";

GRANT INSERT, UPDATE, DELETE ON TABLE activity.job TO "write.data";

CREATE INDEX job_user_id_idx
    ON activity.job USING BTREE
    (user_id)
    TABLESPACE pg_default;
''')


def upgrade(migrate_engine):
    Table('user', Base.metadata, autoload=True, autoload_with=migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(text('''DROP TABLE IF EXISTS activity.job'''))
    Base.metadata.create_all(migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(grants)


def downgrade(migrate_engine):
    with migrate_engine.begin() as transaction:
        transaction.execute(recreate_job_table_sql)
