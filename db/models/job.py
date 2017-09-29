#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name,too-few-public-methods
"""Job related ORM classes"""
import datetime

from sqlalchemy import Column, Integer, BigInteger, Boolean, DateTime, String, Index

from db import Base
from db.models.activities import SCHEMA


class Job(Base):
    """Represents a running Job in the database. Used mainly with the `job` module for exclusive runs."""
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
