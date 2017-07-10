from sqlalchemy import Column, Integer, String, UniqueConstraint, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Shortener(Base):
    __tablename__ = "shortener"

    id = Column(Integer, primary_key=True)
    canonical = Column(String, nullable=True)
    orig_source = Column(String, nullable=True)
    type = Column(String, nullable=True)
    url = Column(String, nullable=True)
    locale = Column(String, nullable=True)
    site_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    card = Column(String, nullable=True)
    image = Column(String, nullable=True)
    title = Column(String, nullable=True)
    site = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint(canonical),
    )


grants = text('''
GRANT ALL ON TABLE shortener TO fanlens;
GRANT SELECT ON TABLE shortener TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE shortener TO "write.data";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to "write.data";
''')


def upgrade(migrate_engine):
    Base.metadata.create_all(migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(grants)


def downgrade(migrate_engine):
    Shortener.__table__.drop(bind=migrate_engine)
