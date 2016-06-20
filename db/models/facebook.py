#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from sqlalchemy import Column, String, Index, ForeignKey, func, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from db import Base, DB
from db.models import SCHEMA_DATA


def get_since(entry_cls, page):
    with DB().ctx() as session:
        (since_last,) = session.query(func.max(entry_cls.data['created_time'].astext)).filter(
            entry_cls.meta['page'].astext == page).first()
        return since_last


# todo make a proper meta table with constraints etc.
class FacebookPostEntry(Base):
    __tablename__ = "facebook_posts"
    id = Column(String, primary_key=True)
    data = Column(JSONB, nullable=False)
    meta = Column(JSONB, nullable=False, default={})
    crawl_ts = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    __table_args__ = (
        Index(__tablename__ + "_date_index", data['created_time']),
        Index(__tablename__ + "_page_index", meta['page']),
        Index(__tablename__ + "_lang_index", meta['lang']),
        Index(__tablename__ + "_tags_index", meta['tags'], postgresql_using='gin'),
        Index(__tablename__ + "_crawl_ts_index", crawl_ts),
        {'schema': SCHEMA_DATA}
    )

    def __repr__(self):
        return "<FacebookPostEntry(id='%s', data='%s', meta='%s)>" % (self.id, self.data, self.meta)


class FacebookCommentEntry(Base):
    __tablename__ = "facebook_comments"
    post_id = Column(String, ForeignKey(FacebookPostEntry.id, ondelete='CASCADE'), nullable=False)
    id = Column(String, primary_key=True)
    data = Column(JSONB, nullable=False)
    meta = Column(JSONB, nullable=False, default={})
    crawl_ts = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    __table_args__ = (
        Index(__tablename__ + "_date_index", data['created_time']),
        Index(__tablename__ + "_page_index", meta['page']),
        Index(__tablename__ + "_lang_index", meta['lang']),
        Index(__tablename__ + "_tags_index", meta['tags'], postgresql_using='gin'),
        Index(__tablename__ + "_crawl_ts_index", crawl_ts),
        {'schema': SCHEMA_DATA}
    )

    def __repr__(self):
        return "<FacebookCommentEntry(id='%s', data='%s', meta='%s)>" % (self.id, self.data, self.meta)


class FacebookReactionEntry(Base):
    __tablename__ = "facebook_reactions"
    post_id = Column(String, ForeignKey(FacebookPostEntry.id, ondelete='CASCADE'), nullable=False)
    id = Column(String, primary_key=True)
    data = Column(JSONB, nullable=False)
    meta = Column(JSONB, nullable=False, default={})
    crawl_ts = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    __table_args__ = (
        Index(__tablename__ + "_date_index", data['created_time']),
        Index(__tablename__ + "_page_index", meta['page']),
        Index(__tablename__ + "_crawl_ts_index", crawl_ts),
        {'schema': SCHEMA_DATA}
    )

    def __repr__(self):
        return "<FacebookReactionEntry(id='%s', data='%s', meta='%s)>" % (self.id, self.data, self.meta)
