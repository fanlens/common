#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from db import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, backref


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean)
    confirmed_at = Column(DateTime)


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    users = relationship(User, secondary='roles_users', backref=backref('roles', lazy='dynamic', collection_class=set))


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    role_id = Column(Integer, ForeignKey(Role.id), primary_key=True)


class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    tag = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

    __table_args__ = (
        # todo not a 100% correct with the plus i think
        CheckConstraint("email ~* '^[A-Za-z0-9._%-+]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'"),
        UniqueConstraint(email, tag, timestamp),
    )
