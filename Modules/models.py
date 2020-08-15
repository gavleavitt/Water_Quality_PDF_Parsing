from sqlalchemy import Column, String, Integer, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class beaches(Base):
    __tablename__ = 'Beaches'

    id = Column(Integer, primary_key=True)
    BeachName = Column(String)

class waterQualityMD5(Base):
    __tablename__ = 'water_qual_md5'

    id = Column(Integer, primary_key=True)
    pdfdate = Column(Date)
    insdate = Column(Date)
    md5 = Column(String)
    pdfName = Column(String)

class stateStandards(Base):
    __tablename__ = "StateStandards"

    id = Column(Integer, primary_key=True)
    Name = Column(String)
    StandardMPN = Column(String)

class waterQuality(Base):
    __tablename__ = "Water_Quality"

    id = Column(Integer, primary_key=True)
    Beach = Column(Integer)
    TotColi = Column(Integer)
    FecColi = Column(Integer)
    Entero = Column(Integer)
    ExceedsRatio = Column(String)
    BeachStatus = Column(String)
    md5_id = Column(Integer)
    resample = Column(String)