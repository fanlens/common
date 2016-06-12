#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgres import ARRAY
from db import Base
from db.models import SCHEMA_META


class Tag(Base):
    """
    simple unique tags model
    """
    __tablename__ = "tags"

    tag = Column(String(length=64), primary_key=True)

    __table_args__ = (
        {'schema': SCHEMA_META}
    )

    def __repr__(self):
        return "<Tag(tag='%s')>" % self.tag


class TagSet(Base):
    """
    simple unique tags model
    """
    __tablename__ = "tagsets"

    id = Column(Integer, primary_key=True)
    title = Column(String(length=128), nullable=False)

    __table_args__ = (
        {'schema': SCHEMA_META}
    )

    def __repr__(self):
        return "<TagSet(id='%s', title='%s', tags='%s')>" % (self.id, self.title, self.tags)


class TagToTagSet(Base):
    __tablename__ = "tag_tagset"

    tag = Column(String, ForeignKey(Tag.tag, ondelete='CASCADE'), primary_key=True)
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), primary_key=True)

    __table_args__ = (
        {'schema': SCHEMA_META}
    )

    def __repr__(self):
        return "<TagToTagSet(tag='%s', tagset_id='%s')>" % (self.tag, self.tagset_id)
