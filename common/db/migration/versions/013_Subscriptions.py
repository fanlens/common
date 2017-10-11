import datetime
from migrate import *
from sqlalchemy import Column, Integer, UniqueConstraint, String, CheckConstraint, text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    tag = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("email ~* '^[A-Za-z0-9._%-+]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'"),  # todo not a 100% correct with the plus i think
        UniqueConstraint(email, tag, timestamp),
    )


grants = text("""
GRANT ALL ON TABLE enquiries TO fanlens;
GRANT SELECT ON TABLE enquiries TO "read.users";
GRANT UPDATE, INSERT, DELETE ON TABLE enquiries TO "write.users";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to "write.users";
""")


def upgrade(migrate_engine):
    Base.metadata.create_all(migrate_engine)

    with migrate_engine.begin() as transaction:
        transaction.execute(grants)


def downgrade(migrate_engine):
    Enquiry.__table__.drop(bind=migrate_engine)
