from sqlalchemy import Column, Integer, String, ForeignKey, Index, text, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

SCHEMA_META = 'meta'

Base = declarative_base()


class Model(Base):
    __tablename__ = "models"
    tagset_id = Column(Integer, ForeignKey('meta.tagset.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    id = Column(String, primary_key=True)
    params = Column(JSONB, nullable=False)

    __table_args__ = (
        Index(__tablename__ + "_user_index", user_id),
        Index(__tablename__ + "_tagset_index", tagset_id),
        {'schema': SCHEMA_META}
    )

    def __repr__(self):
        return "<ModelEntry(id='%s', data='%s', meta='%s)>" % (self.id, self.data, self.meta)


grants = text("""
GRANT ALL ON TABLE meta.models TO fanlens;
GRANT SELECT ON TABLE meta.models TO "read.meta";
GRANT UPDATE, INSERT, DELETE ON TABLE meta.models TO "write.meta";
""")


def upgrade(migrate_engine):
    Table('tagset', Base.metadata, schema=SCHEMA_META, autoload=True, autoload_with=migrate_engine)
    Table('user', Base.metadata, autoload=True, autoload_with=migrate_engine)
    Base.metadata.create_all(migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(grants)


def downgrade(migrate_engine):
    Base.metadata.drop_all(migrate_engine)
