#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, ForeignKey, String, Index
from sqlalchemy.dialects.postgres import JSONB

from db import Base
from db.models import SCHEMA_META
from db.models.tags import TagSet
from db.models.users import User


class Model(Base):
    __tablename__ = "models"
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)

    id = Column(String, primary_key=True)
    params = Column(JSONB, nullable=False)

    __table_args__ = (
        Index(__tablename__ + "_user_index", user_id),
        Index(__tablename__ + "_tagset_index", tagset_id),
        {'schema': SCHEMA_META}
    )

    def __repr__(self):
        return "<ModelEntry(id='%s', data='%s', meta='%s)>" % (self.id, self.data, self.meta)
