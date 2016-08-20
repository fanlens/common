#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Index
from sqlalchemy.dialects.postgres import JSONB

from db import Base
from db.models import SCHEMA_META
from db.models.tags import TagSet


class Model(Base):
    __tablename__ = "models"
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    id = Column(String, primary_key=True)
    params = Column(JSONB, nullable=False)
    score = Column(Float, nullable=False)
    trained_ts = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())

    __table_args__ = (
        Index(__tablename__ + "_user_index", user_id),
        Index(__tablename__ + "_tagset_index", tagset_id),
        {'schema': SCHEMA_META}
    )

    def __repr__(self):
        return "<Model(id='%s', tagset_id='%d', user_id='%d', score='%s', trained_ts='%s', params='%s')>" % (
            self.id, self.tagset_id, self.user_id, self.score, self.trained_ts, self.params)
