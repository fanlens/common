import datetime
import enum

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, text, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TwitterAuth(Base):
    __tablename__ = "twitter_auth"

    id = Column(Integer, primary_key=True)
    oauth_token = Column(String, nullable=False)
    oauth_token_secret = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    __table_args__ = tuple(
        UniqueConstraint(oauth_token)
    )


class UserTwitterAuth(Base):
    __tablename__ = "user_twitter_auth"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    screen_name = Column(String, nullable=False)
    oauth_token = Column(String, ForeignKey(TwitterAuth.oauth_token, ondelete='SET NULL'), nullable=True)

    __table_args__ = (
        UniqueConstraint(user_id),
        UniqueConstraint(screen_name),
        UniqueConstraint(user_id, oauth_token)
    )


grants = text('''
GRANT ALL ON TABLE twitter_auth TO fanlens;
GRANT SELECT ON TABLE twitter_auth TO "read.users";
GRANT UPDATE, INSERT, DELETE ON TABLE twitter_auth TO "write.users";
GRANT ALL ON TABLE user_twitter_auth TO fanlens;
GRANT SELECT ON TABLE user_twitter_auth TO "read.users";
GRANT UPDATE, INSERT, DELETE ON TABLE user_twitter_auth TO "write.users";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to "write.users";
''')


def upgrade(migrate_engine):
    Table('user', Base.metadata, autoload=True, autoload_with=migrate_engine)
    Base.metadata.create_all(migrate_engine)
    with migrate_engine.begin() as transaction:
        transaction.execute(grants)


def downgrade(migrate_engine):
    UserTwitterAuth.__table__.drop(bind=migrate_engine)
    TwitterAuth.__table__.drop(bind=migrate_engine)
