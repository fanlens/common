import hashlib
from sqlalchemy import text

CREATE_ROLE = """
CREATE ROLE %(username)s LOGIN
  ENCRYPTED PASSWORD :password
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
"""

DROP_ROLE = """
DROP ROLE %(username)s;
"""

USERS = ('web', 'worker')


def upgrade(migrate_engine):
    with migrate_engine.begin() as transaction:
        for username in USERS:
            password_in = input('Password for user %s: ' % username).strip()
            assert password_in
            password = 'md5' + hashlib.md5((password_in + username).encode('utf-8')).hexdigest()
            transaction.execute(text(CREATE_ROLE % dict(username=username)), password=password)


def downgrade(migrate_engine):
    with migrate_engine.begin() as transaction:
        for username in USERS:
            transaction.execute(text(DROP_ROLE % dict(username=username)))
