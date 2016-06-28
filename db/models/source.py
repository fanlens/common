#!/usr/bin/env python
# -*- coding: utf-8 -*-


from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, Enum

from db import Base
from db.models import SCHEMA_META


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)

    type = Column(Enum('facebook', 'twitter', 'crunchbase', name='source_type', schema=SCHEMA_META), nullable=False)
    external_id = Column(BigInteger, nullable=False)
    slug = Column(String, nullable=True)
    title = Column(String, nullable=True)

    __table_args__ = (
        {'schema': SCHEMA_META}
    )

    def __repr__(self):
        return "<Source(id='%s', external_id='%s', slug='%s', type='%s')>" % (
            self.id, self.external_id, self.slug, self.type)


class SourceToUser(Base):
    __tablename__ = "user_source"
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    source_id = Column(Integer, ForeignKey(Source.id, ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return "<SourceToUSer(user_id='%s', source_id='%s')>" % (self.user_id, self.source_id)
