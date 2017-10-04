from sqlalchemy import Table, Column, BigInteger, Integer, String, ForeignKey, Enum, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)

    type = Column(Enum('facebook', 'twitter', 'crunchbase', name='source_type', schema='meta'), nullable=False)
    external_id = Column(BigInteger, nullable=False)
    slug = Column(String, nullable=True)
    title = Column(String, nullable=True)

    __table_args__ = (
        {'schema': 'meta'}
    )

    def __repr__(self):
        return "<Source(id='%s', external_id='%s', slug='%s', type='%s')>" % (
            self.id, self.external_id, self.slug, self.type)


class SourceToUser(Base):
    __tablename__ = "user_source"
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    source_id = Column(Integer, ForeignKey(Source.id, ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return "<SourceToUSer(user_id='%s', source_id='%s')>" % (self.user_id, self.source_id)


grants = text("""
GRANT ALL ON TABLE meta.sources TO fanlens;
GRANT SELECT ON TABLE meta.sources TO "read.meta";
GRANT UPDATE, INSERT, DELETE ON TABLE meta.sources TO "write.meta";

GRANT ALL ON TABLE user_source TO fanlens;
GRANT SELECT ON TABLE user_source TO "read.users";
GRANT UPDATE, INSERT, DELETE ON TABLE user_source TO "write.users";
""")


def upgrade(migrate_engine):
    Table('user', Base.metadata, autoload=True, autoload_with=migrate_engine)
    Base.metadata.create_all(migrate_engine)

    with migrate_engine.begin() as transaction:
        transaction.execute(grants)


def downgrade(migrate_engine):
    Table('user', Base.metadata, autoload=True, autoload_with=migrate_engine)
    SourceToUser.__table__.drop(bind=migrate_engine)
    Source.__table__.drop(bind=migrate_engine)
