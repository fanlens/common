#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Index
from sqlalchemy.dialects.postgresql import JSONB

from db import Base
from db.models import SCHEMA_DATA


class CrunchbaseEntry(Base):
    """crunchbase data model class"""
    __tablename__ = "crunchbase_people"

    id = Column(String, primary_key=True)
    properties = Column(JSONB, nullable=False)

    __table_args__ = (
        Index("gender_index", properties['gender']),
        Index("country_index", properties['country_code']),
        {'schema': SCHEMA_DATA}
    )

    def __repr__(self):
        return "<CrunchbaseEntry(id='%s', properties='%s')>" % (self.id, self.properties)
