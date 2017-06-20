#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from db import Base
from db.models.activities import SCHEMA
from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Boolean, DateTime, String, Index


class Job(Base):
    __tablename__ = "job"

    id = Column(Integer, primary_key=True)
    owner = Column(String, nullable=False)
    pid = Column(Integer, nullable=False)
    oid = Column(BigInteger, nullable=False)
    granted = Column(Boolean, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    comment = Column(String, nullable=True)

    __table_args__ = (
        Index(__tablename__ + "_date_index", timestamp),
        {'schema': SCHEMA}
    )
