from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint, text, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
SCHEMA = 'activity'


# class Model(Base):
#     __tablename__ = "model"
#     tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), nullable=False)
#     id = Column(UUID(as_uuid=True), primary_key=True)
#     params = Column(JSONB, nullable=False)
#     score = Column(Float, nullable=False)
#     trained_ts = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)


class ModelUser(Base):
    __tablename__ = "model_user"

    id = Column(Integer, primary_key=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey('%s.model.id' % SCHEMA, ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint(model_id, user_id),
        {'schema': SCHEMA}
    )


upgrade_model_table = text('''
INSERT INTO activity.model_user (user_id, model_id) SELECT user_id, id FROM activity.model;
ALTER TABLE activity.model DROP COLUMN IF EXISTS user_id
''')

downgrade_model_table = text('''
ALTER TABLE activity.model ADD COLUMN IF NOT EXISTS user_id INTEGER;
UPDATE activity.model SET (user_id) = (
  SELECT user_id
  FROM activity.model_user
  WHERE activity.model_user.model_id = activity.model.id
  LIMIT 1
);
ALTER TABLE activity.model ALTER COLUMN user_id SET NOT NULL;
ALTER TABLE activity.model ADD CONSTRAINT model_user_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) MATCH SIMPLE ON UPDATE NO ACTION ON DELETE CASCADE;
DROP TABLE activity.model_user;
''')

grants = text('''
GRANT ALL ON TABLE activity.model_user TO fanlens;
GRANT SELECT ON TABLE activity.model_user TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE activity.model_user TO "write.data";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA activity to "write.data";
''')


def upgrade(migrate_engine):
    Table('user', Base.metadata, autoload=True, autoload_with=migrate_engine)
    Table('model', Base.metadata, schema=SCHEMA, autoload=True, autoload_with=migrate_engine)
    Base.metadata.create_all(migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(upgrade_model_table)
        transaction.execute(grants)


def downgrade(migrate_engine):
    with migrate_engine.begin() as transaction:
        transaction.execute(downgrade_model_table)
