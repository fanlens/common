import enum
import datetime
from sqlalchemy import Column, Integer, String, UniqueConstraint, text, ForeignKey, DateTime, Table, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CrawlState(enum.Enum):
    START = 0
    DONE = 1
    FAIL = 2


class CrawlLog(Base):
    __tablename__ = "crawllog"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('activity.source.id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    state = Column(Enum(CrawlState, name='crawl_state', schema='activity'), nullable=False)

    __table_args__ = (
        {'schema': 'activity'}
    )


add_auto_crawl_field = text('''
ALTER TABLE activity.source ADD COLUMN IF NOT EXISTS auto_crawl BOOLEAN NOT NULL DEFAULT FALSE;
''')

remove_auto_crawl_field = text('''
ALTER TABLE activity.source DROP COLUMN IF EXISTS auto_crawl;
''')

grants = text('''
GRANT ALL ON TABLE activity.crawllog TO fanlens;
GRANT SELECT ON TABLE activity.crawllog TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE activity.crawllog TO "write.data";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA activity to "write.data";
''')


def upgrade(migrate_engine):
    Table('source', Base.metadata, schema='activity', autoload=True, autoload_with=migrate_engine)
    Base.metadata.create_all(migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(add_auto_crawl_field)
        transaction.execute(grants)


def downgrade(migrate_engine):
    CrawlLog.__table__.drop(bind=migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(remove_auto_crawl_field)
