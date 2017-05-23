#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import enum

from db import Base
from db.models.users import User
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship, backref

SCHEMA = 'activity'


class Type(enum.Enum):
    facebook = 'facebook'
    twitter = 'twitter'
    crunchbase = 'crunchbase'
    generic = 'generic'


class Source(Base):
    __tablename__ = 'source'

    id = Column(Integer, primary_key=True)

    type = Column(Enum(Type, name='type', schema=SCHEMA), nullable=False)
    uri = Column(String, nullable=False)
    slug = Column(String, nullable=False)

    # disabled typechecks to work on webuser
    user = relationship(User,
                        secondary=SCHEMA + '.source_user',
                        backref=backref('sources', lazy='dynamic', cascade='all, delete-orphan', single_parent=True),
                        uselist=False,
                        enable_typechecks=False)

    __table_args__ = (
        {'schema': SCHEMA},
    )


class SourceUser(Base):
    __tablename__ = 'source_user'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    source_id = Column(Integer, ForeignKey(Source.id, ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint(user_id, source_id),
        {'schema': SCHEMA},
    )


class Data(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True)

    object_id = Column(String, nullable=False)
    source_id = Column(Integer, ForeignKey(Source.id, ondelete='CASCADE'), nullable=False)

    data = Column(JSONB, nullable=False)

    source = relationship(Source, backref=backref('data', lazy='dynamic'), uselist=False)
    users = relationship(User,
                         primaryjoin=((SourceUser.source_id == source_id) & (SourceUser.user_id == User.id)),
                         secondary=SourceUser.__table__,
                         backref=backref('data', lazy='dynamic'))

    __table_args__ = (
        UniqueConstraint(object_id, source_id),
        {'schema': SCHEMA},
    )


class Text(Base):
    __tablename__ = 'text'

    id = Column(Integer, primary_key=True)
    data_id = Column(Integer, ForeignKey(Data.id, ondelete='CASCADE'), nullable=False, unique=True)
    text = Column(String, nullable=False)

    data = relationship(Data, backref=backref('text', lazy='select', uselist=False))

    __table_args__ = (
        UniqueConstraint(data_id),
        {'schema': SCHEMA},
    )


class Time(Base):
    __tablename__ = 'time'

    id = Column(Integer, primary_key=True)
    data_id = Column(Integer, ForeignKey(Data.id, ondelete='CASCADE'), nullable=False, unique=True)
    time = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

    data = relationship(Data, backref=backref('time', lazy='select', uselist=False))

    __table_args__ = (
        UniqueConstraint(data_id),
        {'schema': SCHEMA},
    )


class Fingerprint(Base):
    __tablename__ = 'fingerprint'

    id = Column(Integer, primary_key=True)
    data_id = Column(Integer, ForeignKey(Data.id, ondelete='CASCADE'), nullable=False, unique=True)
    fingerprint = Column(ARRAY(Integer), nullable=False)

    data = relationship(Data, backref=backref('fingerprint', lazy='select', uselist=False))

    __table_args__ = (
        UniqueConstraint(data_id),
        {'schema': SCHEMA},
    )


class TagSet(Base):
    __tablename__ = 'tagset'

    id = Column(Integer, primary_key=True)
    title = Column(String(length=256), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)

    # disabled typechecks to work on webuser
    user = relationship(User, backref=backref('tagsets', lazy='dynamic'), enable_typechecks=False)

    __table_args__ = (
        UniqueConstraint(user_id, title),
        {'schema': SCHEMA},
    )


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    tag = Column(String(length=64), nullable=False)

    data = relationship(Data, secondary=SCHEMA + '.tagging',
                        backref=backref('tags', lazy='select', collection_class=set, cascade='all'),
                        lazy='dynamic')
    user = relationship(User, backref=backref('tags', lazy='select', collection_class=set))
    tagsets = relationship(TagSet, secondary=SCHEMA + '.tag_tagset',
                           backref=backref('tags', lazy='select', collection_class=set))

    def __eq__(self, other):
        if isinstance(other, Tag):
            return ((self.tag == other.tag) and
                    (self.user_id == other.user_id))
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash("Tag(%s,%s)" % (self.user_id, self.tag))

    __table_args__ = (
        UniqueConstraint(user_id, tag),
        {'schema': SCHEMA},
    )


class Tagging(Base):
    __tablename__ = 'tagging'

    id = Column(Integer, primary_key=True)
    data_id = Column(Integer, ForeignKey(Data.id, ondelete='CASCADE'), nullable=False)
    tag_id = Column(Integer, ForeignKey(Tag.id, ondelete='CASCADE'), nullable=False)

    data = relationship(Data)
    tag = relationship(Tag, backref=backref('taggings', lazy='dynamic'))

    __table_args__ = (
        UniqueConstraint(data_id, tag_id),
        {'schema': SCHEMA},
    )


class TagTagSet(Base):
    __tablename__ = 'tag_tagset'

    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey(Tag.id, ondelete='CASCADE'), nullable=False)
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint(tag_id, tagset_id),
        {'schema': SCHEMA},
    )


# auto created from pycld2, python -mbrain.feature.language_detect
Lang = enum.Enum('Lang',
                 {'ee': 'EWE', 'xx-Phli': 'X_Inscriptional_Pahlavi', 'my': 'BURMESE', 'ko': 'Korean',
                  'xx-Cham': 'X_Cham',
                  'si': 'SINHALESE', 'mg': 'MALAGASY', 'gd': 'SCOTS_GAELIC', 'kri': 'KRIO', 'xx-Batk': 'X_Batak',
                  'xx-Buhd': 'X_Buhid', 'xx-Armn': 'X_Armenian', 'xx-Laoo': 'X_Lao', 'sv': 'SWEDISH',
                  'xx-Talu': 'X_New_Tai_Lue', 'xx-Grek': 'X_Greek', 'zze': 'X_ELMER_FUDD', 'xxx': 'Ignore',
                  'ak': 'AKAN',
                  'km': 'KHMER', 'luo': 'LUO_KENYA_AND_TANZANIA', 'ga': 'IRISH', 'bg': 'BULGARIAN', 'ml': 'MALAYALAM',
                  'xx-Kali': 'X_Kayah_Li', 'am': 'AMHARIC', 'rn': 'RUNDI', 'xx-Hano': 'X_Hanunoo', 'dv': 'DHIVEHI',
                  'tg': 'TAJIK', 'mfe': 'MAURITIAN_CREOLE', 'xx-Kthi': 'X_Kaithi', 'kl': 'GREENLANDIC', 'ba': 'BASHKIR',
                  'gu': 'GUJARATI', 'sr-ME': 'MONTENEGRIN', 'pl': 'POLISH', 'rm': 'RHAETO_ROMANCE',
                  'xx-Ethi': 'X_Ethiopic',
                  'lif': 'LIMBU', 'ne': 'NEPALI', 'xx-Khar': 'X_Kharoshthi', 'et': 'ESTONIAN', 'xx-Khmr': 'X_Khmer',
                  'fa': 'PERSIAN', 'ay': 'AYMARA', 'hr': 'CROATIAN', 'hi': 'HINDI', 'nn': 'NORWEGIAN_N',
                  'ab': 'ABKHAZIAN',
                  'xx-Egyp': 'X_Egyptian_Hieroglyphs', 'xx-Orkh': 'X_Old_Turkic', 'xx-Tavt': 'X_Tai_Viet',
                  'pa': 'PUNJABI',
                  'gaa': 'GA', 'ja': 'Japanese', 'lb': 'LUXEMBOURGISH', 'xx-Merc': 'X_Meroitic_Cursive',
                  'xx-Lydi': 'X_Lydian', 'or': 'ORIYA', 'tlh': 'X_KLINGON', 'pam': 'PAMPANGA', 'sa': 'SANSKRIT',
                  'xx-Lisu': 'X_Lisu', 'xx-Olck': 'X_Ol_Chiki', 'ku': 'KURDISH', 'xx-Saur': 'X_Saurashtra',
                  'sq': 'ALBANIAN',
                  'dz': 'DZONGKHA', 'ps': 'PASHTO', 'fj': 'FIJIAN', 'xx-Taml': 'X_Tamil', 'zu': 'ZULU',
                  'xx-Vaii': 'X_Vai',
                  'xx-Hebr': 'X_Hebrew', 'it': 'ITALIAN', 'xx-Linb': 'X_Linear_B', 'xx-Sylo': 'X_Syloti_Nagri',
                  'ka': 'GEORGIAN', 'vi': 'VIETNAMESE', 'ug': 'UIGHUR', 'un': 'UNKNOWN', 'el': 'GREEK', 'mt': 'MALTESE',
                  'xx-Ugar': 'X_Ugaritic', 'raj': 'RAJASTHANI', 'sn': 'SHONA', 'ceb': 'CEBUANO', 'xx-Osma': 'X_Osmanya',
                  'xx-Ital': 'X_Old_Italic', 'sl': 'SLOVENIAN', 'sw': 'SWAHILI', 'mr': 'MARATHI', 'ik': 'INUPIAK',
                  'xx-Lyci': 'X_Lycian', 'fo': 'FAROESE', 'xx-Plrd': 'X_Miao', 'xx-Phag': 'X_Phags_Pa', 'cs': 'CZECH',
                  'kn': 'KANNADA', 'za': 'ZHUANG', 'chr': 'CHEROKEE', 'xx-Shaw': 'X_Shavian', 'to': 'TONGA',
                  'xx-Avst': 'X_Avestan', 'xx-Cari': 'X_Carian', 'ha': 'HAUSA', 'fy': 'FRISIAN',
                  'xx-Sarb': 'X_Old_South_Arabian', 'eo': 'ESPERANTO', 'xx-Xsux': 'X_Cuneiform', 'mi': 'MAORI',
                  'xx-Qaai': 'X_Inherited', 'xx-Mlym': 'X_Malayalam', 'xx-Bali': 'X_Balinese', 'loz': 'LOZI',
                  'ta': 'TAMIL',
                  'is': 'ICELANDIC', 'xh': 'XHOSA', 'br': 'BRETON', 'uz': 'UZBEK', 've': 'VENDA', 'tn': 'TSWANA',
                  'xx-Brah': 'X_Brahmi', 'xx-Zyyy': 'X_Common', 'xx-Orya': 'X_Oriya', 'co': 'CORSICAN',
                  'uk': 'UKRAINIAN',
                  'xx-Sinh': 'X_Sinhala', 'na': 'NAURU', 'ru': 'RUSSIAN', 'xx-Deva': 'X_Devanagari', 'te': 'TELUGU',
                  'xx-Bugi': 'X_Buginese', 'xx-Sora': 'X_Sora_Sompeng', 'tl': 'TAGALOG', 'xx-Bopo': 'X_Bopomofo',
                  'bi': 'BISLAMA', 'wo': 'WOLOF', 'nl': 'DUTCH', 'fr': 'FRENCH', 'xx-Rjng': 'X_Rejang',
                  'os': 'OSSETIAN',
                  'kk': 'KAZAKH', 'iw': 'HEBREW', 'xx-Tglg': 'X_Tagalog', 'zzb': 'X_BORK_BORK_BORK',
                  'xx-Thaa': 'X_Thaana',
                  'bo': 'TIBETAN', 'xx-Lepc': 'X_Lepcha', 'zh-Hant': 'ChineseT', 'xx-Limb': 'X_Limbu',
                  'xx-Knda': 'X_Kannada', 'hy': 'ARMENIAN', 'xx-Cakm': 'X_Chakma', 'pt': 'PORTUGUESE',
                  'be': 'BELARUSIAN',
                  'lo': 'LAOTHIAN', 'tw': 'TWI', 'so': 'SOMALI', 'ie': 'INTERLINGUE', 'xx-Goth': 'X_Gothic',
                  'su': 'SUNDANESE', 'lv': 'LATVIAN', 'new': 'NEWARI', 'en': 'ENGLISH', 'bh': 'BIHARI', 'eu': 'BASQUE',
                  'ig': 'IGBO', 'ar': 'ARABIC', 'ti': 'TIGRINYA', 'xx-Tfng': 'X_Tifinagh', 'bs': 'BOSNIAN',
                  'xx-Armi': 'X_Imperial_Aramaic', 'oc': 'OCCITAN', 'sd': 'SINDHI', 'xx-Phnx': 'X_Phoenician',
                  'zzp': 'X_PIG_LATIN', 'xx-Syrc': 'X_Syriac', 'xx-Cans': 'X_Canadian_Aboriginal', 'aa': 'AFAR',
                  'crs': 'SESELWA', 'id': 'INDONESIAN', 'lt': 'LITHUANIAN', 'xx-Gujr': 'X_Gujarati',
                  'rw': 'KINYARWANDA',
                  'st': 'SESOTHO', 'kha': 'KHASI', 'ny': 'NYANJA', 'as': 'ASSAMESE', 'xx-Sund': 'X_Sundanese',
                  'xx-Java': 'X_Javanese', 'bn': 'BENGALI', 'xx-Mero': 'X_Meroitic_Hieroglyphs', 'haw': 'HAWAIIAN',
                  'yo': 'YORUBA', 'ht': 'HAITIAN_CREOLE', 'af': 'AFRIKAANS', 'xx-Thai': 'X_Thai', 'xx-Tale': 'X_Tai_Le',
                  'la': 'LATIN', 'vo': 'VOLAPUK', 'xx-Nkoo': 'X_Nko', 'mn': 'MONGOLIAN', 'ln': 'LINGALA', 'ms': 'MALAY',
                  'sg': 'SANGO', 'xx-Mong': 'X_Mongolian', 'hmn': 'HMONG', 'war': 'WARAY_PHILIPPINES',
                  'xx-Arab': 'X_Arabic',
                  'xx-Samr': 'X_Samaritan', 'xx-Shrd': 'X_Sharada', 'xx-Takr': 'X_Takri', 'syr': 'SYRIAC',
                  'xx-Lana': 'X_Tai_Tham', 'ky': 'KYRGYZ', 'xx-Prti': 'X_Inscriptional_Parthian', 'nr': 'NDEBELE',
                  'xx-Hang': 'X_Hangul', 'gn': 'GUARANI', 'zh': 'Chinese', 'sm': 'SAMOAN', 'xx-Brai': 'X_Braille',
                  'xx-Copt': 'X_Coptic', 'ks': 'KASHMIRI', 'az': 'AZERBAIJANI', 'nso': 'PEDI',
                  'xx-Mtei': 'X_Meetei_Mayek',
                  'fi': 'FINNISH', 'tr': 'TURKISH', 'xx-Beng': 'X_Bengali', 'xx-Dsrt': 'X_Deseret', 'qu': 'QUECHUA',
                  'xx-Kana': 'X_Katakana', 'sco': 'SCOTS', 'tum': 'TUMBUKA', 'ur': 'URDU', 'xx-Tagb': 'X_Tagbanwa',
                  'xx-Xpeo': 'X_Old_Persian', 'xx-Bamu': 'X_Bamum', 'da': 'DANISH', 'xx-Tibt': 'X_Tibetan',
                  'es': 'SPANISH',
                  'xx-Cyrl': 'X_Cyrillic', 'xx-Guru': 'X_Gurmukhi', 'xx-Hani': 'X_Han', 'ca': 'CATALAN',
                  'xx-Glag': 'X_Glagolitic', 'om': 'OROMO', 'xx-Yiii': 'X_Yi', 'iu': 'INUKTITUT', 'sk': 'SLOVAK',
                  'gl': 'GALICIAN', 'xx-Telu': 'X_Telugu', 'xx-Hira': 'X_Hiragana', 'mk': 'MACEDONIAN',
                  'xx-Geor': 'X_Georgian', 'tk': 'TURKMEN', 'ro': 'ROMANIAN', 'yi': 'YIDDISH', 'ss': 'SISWANT',
                  'th': 'THAI',
                  'ia': 'INTERLINGUA', 'xx-Ogam': 'X_Ogham', 'hu': 'HUNGARIAN', 'lua': 'LUBA_LULUA', 'tt': 'TATAR',
                  'ts': 'TSONGA', 'xx-Mymr': 'X_Myanmar', 'jw': 'JAVANESE', 'xx-Cprt': 'X_Cypriot',
                  'xx-Cher': 'X_Cherokee',
                  'zzh': 'X_HACKER', 'gv': 'MANX', 'cy': 'WELSH', 'no': 'NORWEGIAN', 'xx-Mand': 'X_Mandaic',
                  'sr': 'SERBIAN',
                  'xx-Runr': 'X_Runic', 'de': 'GERMAN', 'xx-Latn': 'X_Latin', 'lg': 'GANDA'})


class Language(Base):
    __tablename__ = 'language'

    id = Column(Integer, primary_key=True)
    data_id = Column(Integer, ForeignKey(Data.id, ondelete='CASCADE'), nullable=False, unique=True)
    language = Column(Enum(Lang, name='lang', schema=SCHEMA),
                      nullable=False)

    data = relationship(Data, backref=backref('language', lazy='select', uselist=False))

    __table_args__ = (
        UniqueConstraint(data_id),
        {'schema': SCHEMA},
    )


class Translation(Base):
    __tablename__ = 'translation'

    id = Column(Integer, primary_key=True)
    text_id = Column(Integer, ForeignKey(Text.id, ondelete='CASCADE'), nullable=False)
    translation = Column(String, nullable=False)
    target_language = Column(Enum(Lang, name='lang', schema=SCHEMA), nullable=False)

    text = relationship(Text, backref=backref('translations', lazy='dynamic'))

    __table_args__ = (
        UniqueConstraint(text_id, target_language),
        {'schema': SCHEMA},
    )


if __name__ == "__main__":
    from db import DB

    Base.metadata.create_all(DB().engine)
