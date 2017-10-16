"""Conversion/Helper for UTC types and parsing"""
from datetime import tzinfo, timedelta, datetime
from typing import Optional


class SimpleUTC(tzinfo):
    """Class to be used to give naive UTC tzinfo for parsed timestamps"""

    def tzname(self, _: Optional[datetime]) -> str:
        return "UTC"

    def utcoffset(self, _: Optional[datetime]) -> timedelta:
        return timedelta(0)

    def dst(self, _: Optional[datetime]) -> Optional[timedelta]:
        return timedelta(0)
