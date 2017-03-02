#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import uuid

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index, LargeBinary, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import JSONB, UUID

from db import Base
from db.models.users import User
from db.models.activities import SCHEMA, Tag, TagSet, TagTagSet, Source, Data


class Model(Base):
    __tablename__ = "model"
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid1)
    params = Column(JSONB, nullable=False)
    score = Column(Float, nullable=False)
    trained_ts = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    tagset = relationship(TagSet, backref=backref('models', lazy='dynamic'))
    tags = relationship(Tag,
                        secondary=TagTagSet.__table__,
                        primaryjoin=(tagset_id == TagTagSet.tagset_id),
                        lazy='dynamic')
    user = relationship(User, backref=backref('models', lazy='dynamic'))
    sources = relationship(Source,
                           secondary=SCHEMA + '.source_model',
                           backref=backref('models', lazy='dynamic'),
                           lazy='dynamic')

    __table_args__ = (
        Index(__tablename__ + "_user_index", user_id),
        Index(__tablename__ + "_tagset_index", tagset_id),
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


class ModelFile(Base):
    __tablename__ = "modelfile"

    model_id = Column(UUID(as_uuid=True), ForeignKey(Model.id, ondelete='CASCADE'), nullable=False, primary_key=True)
    file = Column(LargeBinary, nullable=False)

    model = relationship(Model, backref=backref('file', lazy='select', uselist=False))

    __table_args__ = (
        {'schema': SCHEMA}
    )


class Job(Base):
    __tablename__ = "job"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid1)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    started = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)

    user = relationship(User, backref=backref('jobs', lazy='dynamic'), enable_typechecks=False)

    __table_args__ = (
        Index(__tablename__ + "_user_index", user_id),
        {'schema': SCHEMA}
    )


class Prediction(Base):
    __tablename__ = "prediction"

    id = Column(Integer, primary_key=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey(Model.id, ondelete='CASCADE'), nullable=False)
    data_id = Column(Integer, ForeignKey(Data.id, ondelete='CASCADE'), nullable=False)

    prediction = Column(JSONB, nullable=False)

    model = relationship(Model, backref=backref('prediction', lazy='dynamic'))
    data = relationship(Data, backref=backref('prediction', lazy='select', uselist=False, cascade='all, delete-orphan'))

    __table_args__ = (
        UniqueConstraint(data_id, model_id),
        {'schema': SCHEMA}
    )


if __name__ == "__main__":
    from db import DB

    Base.metadata.create_all(DB().engine)
