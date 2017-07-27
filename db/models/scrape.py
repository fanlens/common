#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import enum

from db import Base
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint

from .activities import SCHEMA, Source


class Shortener(Base):
    __tablename__ = "shortener"

    id = Column(Integer, primary_key=True)
    canonical = Column(String, nullable=True)
    orig_source = Column(String, nullable=True)
    type = Column(String, nullable=True)
    url = Column(String, nullable=True)
    locale = Column(String, nullable=True)
    site_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    card = Column(String, nullable=True)
    image = Column(String, nullable=True)
    title = Column(String, nullable=True)
    site = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint(canonical),
    )


class CrawlState(enum.Enum):
    START = 0
    DONE = 1
    FAIL = 2


class CrawlLog(Base):
    __tablename__ = "crawllog"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey(Source.id, ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    state = Column(Enum(CrawlState, name='crawl_state', schema='activity'), nullable=False)

    __table_args__ = (
        {'schema': SCHEMA}
    )
