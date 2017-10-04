from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint, text, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
SCHEMA = 'activity'


class Feature(Base):
    __tablename__ = "feature"
    feature = Column(String, primary_key=True)

    __table_args__ = (
        {'schema': SCHEMA}
    )


class SourceFeature(Base):
    __tablename__ = "source_feature"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('%s.source.id' % SCHEMA, ondelete='CASCADE'), nullable=False)
    feature = Column(String, ForeignKey(Feature.feature, ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint(source_id, feature),
        {'schema': SCHEMA}
    )

auto_crawl_upgrade_sql = text('''
INSERT INTO activity.source_feature (source_id, feature)
SELECT id as source_id, 'auto_crawl' as feature
FROM activity.source
WHERE auto_crawl = true;

ALTER TABLE activity.source DROP COLUMN "auto_crawl";
''')


auto_crawl_downgrade_sql = text('''
ALTER TABLE activity.source ADD COLUMN "auto_crawl" boolean NOT NULL DEFAULT false;

UPDATE activity.source as source
SET auto_crawl = true
FROM activity.source_feature as source_feature
WHERE source_feature.source_id = source.id AND
      source_feature.feature = 'auto_crawl';
''')

grants = text('''
GRANT ALL ON TABLE activity.feature TO fanlens;
GRANT SELECT ON TABLE activity.feature TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE activity.feature TO "write.data";
GRANT ALL ON TABLE activity.source_feature TO fanlens;
GRANT SELECT ON TABLE activity.source_feature TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE activity.source_feature TO "write.data";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA activity to "write.data";
''')


def upgrade(migrate_engine):
    Table('source', Base.metadata, schema=SCHEMA, autoload=True, autoload_with=migrate_engine)
    Base.metadata.create_all(migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(grants)
        transaction.execute(Feature.__table__.insert(), feature='translate')
        transaction.execute(Feature.__table__.insert(), feature='auto_crawl')
        transaction.execute(auto_crawl_upgrade_sql)


def downgrade(migrate_engine):
    with migrate_engine.begin() as transaction:
        transaction.execute(auto_crawl_downgrade_sql)

    SourceFeature.__table__.drop(bind=migrate_engine)
    Feature.__table__.drop(bind=migrate_engine)
