#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from db.models import SCHEMA_META
from db.models.facebook import FacebookCommentEntry
from db.models.users import User


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
    collection of tags with a title
    """
    __tablename__ = "tagsets"

    id = Column(Integer, primary_key=True)
    title = Column(String(length=128), nullable=False)

    tags = relationship(Tag, secondary=SCHEMA_META + ".tag_tagset", collection_class=set)

    __table_args__ = (
        {'schema': SCHEMA_META}
    )

    def __repr__(self):
        return "<TagSet(id='%s', title='%s', tags='%s')>" % (self.id, self.title, self.tags)


class TagToTagSet(Base):
    """
    intermediary table to assign tags to tagsets
    """
    __tablename__ = "tag_tagset"

    tag = Column(String, ForeignKey(Tag.tag, ondelete='CASCADE'), primary_key=True)
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), primary_key=True)

    __table_args__ = (
        {'schema': SCHEMA_META}
    )

    def __repr__(self):
        return "<TagToTagSet(tag='%s', tagset_id='%s')>" % (self.tag, self.tagset_id)


class UserToTagSet(Base):
    __tablename__ = "user_tagset"

    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return "<UserToTagSet(user_id='%s', tagset_id='%s')>" % (self.user_id, self.tagset_id)


class UserToTagToComment(Base):
    __tablename__ = "user_tag_comment"
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    tag = Column(String, ForeignKey(Tag.tag, ondelete='CASCADE'), primary_key=True)
    comment_id = Column(String, ForeignKey(FacebookCommentEntry.id, ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return "<UserToTagToComment(user_id='%s', tag='%s', comment_id='%s')>" % (
            self.user_id, self.tag, self.comment_id)
