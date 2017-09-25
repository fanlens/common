#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='postgres://uchqtxyh:uQHiVCDD8VCAsgTYgK24qWUbR_iFmyrh@packy.db.elephantsql.com:5432/uchqtxyh', repository='db/migration', debug='False')
