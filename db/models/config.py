#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from db import Base


class DBSetting(Base):
    """
    model for the database setting entries
    """
    __tablename__ = "config"

    key = Column(String, primary_key=True)
    config = Column(JSONB, nullable=False)

    def __repr__(self):
        return "<DBSetting(key='%s', config='%s')>" % (self.key, self.config)