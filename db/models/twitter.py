#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Index
from sqlalchemy.dialects.postgresql import JSONB

from db import Base

from db.models import SCHEMA_DATA


class TwitterEntry(Base):
    """twitter data model class"""
    __tablename__ = "twitter"

    id = Column(String, primary_key=True)
    query = Column(String, nullable=False)
    tweet = Column(JSONB, nullable=False)

    __table_args__ = (
        Index("date_index", tweet['created_at']),
        Index("query_index", query),
        {'schema': SCHEMA_DATA}
    )

    def __repr__(self):
        return "<TwitterEntry(id='%s', query'%s', data='%s')>" % (self.id, self.query, self.tweet)
