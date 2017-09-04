#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import uuid

from db import Base
from db.models.activities import SCHEMA, Tag, TagSet, TagTagSet, Source, Data
from db.models.users import User
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, backref


class Model(Base):
    __tablename__ = "model"
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), nullable=False)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid1)
    params = Column(JSONB, nullable=False)
    score = Column(Float, nullable=False)
    trained_ts = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    created_by_user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    tagset = relationship(TagSet, backref=backref('models', lazy='dynamic'))
    tags = relationship(Tag,
                        secondary=TagTagSet.__table__,
                        primaryjoin=(tagset_id == TagTagSet.tagset_id),
                        lazy='dynamic')
    users = relationship(User,
                         secondary=SCHEMA + '.model_user',
                         backref=backref('models', lazy='dynamic'),
                         lazy='dynamic')
    sources = relationship(Source,
                           secondary=SCHEMA + '.source_model',
                           backref=backref('models', lazy='dynamic'),
                           lazy='dynamic')

    __table_args__ = (
        Index(__tablename__ + "_tagset_index", tagset_id),
        {'schema': SCHEMA}
    )


class ModelUser(Base):
    __tablename__ = "model_user"

    id = Column(Integer, primary_key=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey(Model.id, ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint(model_id, user_id),
        {'schema': SCHEMA}
    )


class ModelSources(Base):
    __tablename__ = 'source_model'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey(Source.id, ondelete='CASCADE'), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey(Model.id, ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint(source_id, model_id),
        {'schema': SCHEMA},
    )


class Prediction(Base):
    __tablename__ = "prediction"

    id = Column(Integer, primary_key=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey(Model.id, ondelete='CASCADE'), nullable=False)
    data_id = Column(Integer, ForeignKey(Data.id, ondelete='CASCADE'), nullable=False)

    prediction = Column(JSONB, nullable=False)

    data = relationship(Data, backref=backref('predictions', lazy='dynamic'))
    model = relationship(Model, backref=backref('predictions', lazy='dynamic'))

    __table_args__ = (
        UniqueConstraint(data_id, model_id),
        {'schema': SCHEMA}
    )
