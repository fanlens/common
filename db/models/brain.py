#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index, LargeBinary
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSONB, UUID

from db import Base
from db.models.users import User
from db.models.activities import SCHEMA, Tag, TagSet, TagTagSet


class Model(Base):
    __tablename__ = "model"
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)

    id = Column(UUID, primary_key=True)
    params = Column(JSONB, nullable=False)
    score = Column(Float, nullable=False)
    trained_ts = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now())

    tags = relationship(Tag,
                        secondary=TagTagSet.__table__,
                        primaryjoin=(tagset_id == TagTagSet.tagset_id),
                        collection_class=set)
    user = relationship(User, backref=backref('models', lazy='dynamic'))

    __table_args__ = (
        Index(__tablename__ + "_user_index", user_id),
        Index(__tablename__ + "_tagset_index", tagset_id),
        {'schema': SCHEMA}
    )


class ModelFile(Base):
    __tablename__ = "modelfile"

    model_id = Column(UUID, ForeignKey(Model.id, ondelete='CASCADE'), nullable=False, primary_key=True)
    file = Column(LargeBinary, nullable=False)

    model = relationship(Model, backref=backref('file', lazy='select', uselist=False))

    __table_args__ = (
        {'schema': SCHEMA}
    )
