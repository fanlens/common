#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

from db import Base


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean)
    confirmed_at = Column(DateTime)
    roles = relationship('Role', secondary='roles_users', backref=backref('users', lazy='dynamic'))


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    role_id = Column(Integer, ForeignKey(Role.id), primary_key=True)
