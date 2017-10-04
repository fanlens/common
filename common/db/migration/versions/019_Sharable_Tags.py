from sqlalchemy import Column, ForeignKey, Integer, Table, UniqueConstraint, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
SCHEMA = 'activity'


class TagSetUser(Base):
    __tablename__ = "tagset_user"

    id = Column(Integer, primary_key=True)
    tagset_id = Column(Integer, ForeignKey('%s.tagset.id' % SCHEMA, ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint(tagset_id, user_id),
        {'schema': SCHEMA}
    )


upgrade_tagset_table = text('''
INSERT INTO activity.tagset_user (user_id, tagset_id) SELECT user_id, id FROM activity.tagset ON CONFLICT DO NOTHING;
ALTER TABLE activity.tagset RENAME COLUMN user_id TO created_by_user_id;
''')

downgrade_tagset_table = text('''
ALTER TABLE activity.tagset RENAME COLUMN created_by_user_id TO user_id;
DROP TABLE activity.tagset_user;
''')


class TagUser(Base):
    __tablename__ = "tag_user"

    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey('%s.tag.id' % SCHEMA, ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint(tag_id, user_id),
        {'schema': SCHEMA}
    )


upgrade_tag_table = text('''
INSERT INTO activity.tag_user (user_id, tag_id) SELECT user_id, id FROM activity.tag ON CONFLICT DO NOTHING;
ALTER TABLE activity.tag RENAME COLUMN user_id TO created_by_user_id;
''')

downgrade_tag_table = text('''
ALTER TABLE activity.tag RENAME COLUMN created_by_user_id TO user_id;
DROP TABLE activity.tag_user;
''')

grants = text('''
GRANT ALL ON TABLE activity.tag_user TO fanlens;
GRANT SELECT ON TABLE activity.tag_user TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE activity.tag_user TO "write.data";
GRANT ALL ON TABLE activity.tagset_user TO fanlens;
GRANT SELECT ON TABLE activity.tagset_user TO "read.data";
GRANT UPDATE, INSERT, DELETE ON TABLE activity.tagset_user TO "write.data";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA activity to "write.data";
''')


def upgrade(migrate_engine):
    Table('user', Base.metadata, autoload=True, autoload_with=migrate_engine)
    Table('tagset', Base.metadata, schema=SCHEMA, autoload=True, autoload_with=migrate_engine)
    Table('tag', Base.metadata, schema=SCHEMA, autoload=True, autoload_with=migrate_engine)
    Base.metadata.create_all(migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(upgrade_tagset_table)
        transaction.execute(upgrade_tag_table)
        transaction.execute(grants)


def downgrade(migrate_engine):
    with migrate_engine.begin() as transaction:
        transaction.execute(downgrade_tag_table)
        transaction.execute(downgrade_tagset_table)
