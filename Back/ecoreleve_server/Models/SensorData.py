from sqlalchemy import (
   Boolean,
   Column,
   DateTime,
   Float,
   Index,
   Integer,
   Numeric,
   Sequence,
   String,
   ForeignKey,
   func,
   UniqueConstraint,
   Table
 )

from ..Models import Base, dbConfig
from sqlalchemy.dialects.mssql.base import BIT,TINYINT,SMALLINT,FLOAT

sensor_schema = dbConfig['sensor_schema']
dialect = dbConfig['dialect']


class ArgosGps(Base):
    __tablename__ = 'T_argosgps'
    pk_id = Column('PK_id', Integer, primary_key=True)
    ptt = Column('FK_ptt', Integer, nullable = False)
    type_ = Column('type',String(3), nullable = False)
    date = Column('date', DateTime, nullable = False)
    lat = Column(Numeric(9, 5), nullable = False)
    lon = Column(Numeric(9, 5), nullable = False)
    ele = Column(Integer)
    speed = Column(Integer)
    course = Column(Integer)
    lc = Column('lc', String(1))
    iq = Column('iq', Integer)
    nbMsg = Column(Integer)
    nbMsg120 = Column(Integer)
    bestLvl = Column('bestLevel', Integer)
    passDuration = Column(Integer)
    nopc = Column('nopc', Integer)
    frequency = Column('freq', Float)
    checked = Column('checked', Boolean, nullable=False, default=False)
    imported = Column('imported', Boolean, nullable=False, default=False)
    if dialect.startswith('mssql'):
        __table_args__ = (
            Index(
                'idx_Targosgps_checked_with_pk_ptt_date',
                checked,
                ptt,
                mssql_include=[pk_id, date]
            ),
            {'schema': sensor_schema}
        )
    else:
        __table_args__ = (
            Index('idx_Targosgps_checked_ptt', checked, ptt),
            {'schema': sensor_schema}
        )

class Gsm(Base):
    __tablename__ = 'Tgsm'
    pk_id = Column('PK_id', Integer, primary_key=True)
    platform_ = Column('platform_', Integer, nullable = False)
    date = Column('DateTime', DateTime, nullable = False)
    lat = Column('Latitude_N',Numeric(9, 5), nullable = False)
    lon = Column('Longitude_E',Numeric(9, 5), nullable = False)
    ele = Column('Altitude_m',Integer)
    Speed = Column(Integer)
    Course = Column(Integer)
    checked = Column(Boolean, nullable=False, server_default='0')
    imported = Column(Boolean, nullable=False, server_default='0')
    SatelliteCount = Column(Integer)
    HDOP = Column(Integer)
    VDOP = Column(Integer)
    validated = Column(Boolean, nullable=False, server_default='0')

    if dialect.startswith('mssql'):
        __table_args__ = (
            Index('idx_Tgsm_checked_with_pk_ptt_date', checked, platform_,
                mssql_include=[pk_id, date]
            ),
            {'schema': sensor_schema}
        )
    else:
        __table_args__ = (
            Index('idx_Tgsm_checked_ptt', checked, platform_),
            {'schema': sensor_schema}
        )

class GsmEngineering (Base) :
    __tablename__ = 'Tengineering_gsm'
    PK_id = Column(Integer, Sequence('seq_Tengineering_gsm_id'), primary_key=True)
    platform_ = Column(Integer , nullable = False)
    date = Column('DateTime', DateTime, nullable = False)
    ActivityCount = Column(Integer, )
    Temperature_C = Column(Numeric)
    BatteryVoltage_V = Column(Numeric)
    file_date = Column(DateTime)

    __table_args__ = (
        Index('idx_Tengineering_gsm_pttDate_ptt', date, platform_),
        {'schema': sensor_schema}
    )
class ArgosEngineering(Base):
    __tablename__ = 'Tgps_engineering'
    pk_id = Column('PK_id', Integer, primary_key=True)
    fk_ptt = Column('FK_ptt', Integer, nullable = False)
    pttDate = Column('pttDate', DateTime, nullable = False)
    txDate = Column('txDate', DateTime, nullable = False)
    satId = Column(String(250))
    txCount = Column(Integer)
    temp = Column(Float)
    batt = Column(Float)
    fixTime = Column(Integer)
    satCount = Column(Integer)
    resetHours = Column(Integer)
    fixDays = Column(Integer)
    season = Column(Integer)
    shunt = Column(Boolean)
    mortalityGT = Column(Boolean)
    seasonalGT = Column(Boolean)
    latestLat = Column(Float)
    latestLon = Column(Float)

    __table_args__ = (
        Index('idx_Tgps_engineering_pttDate_ptt', pttDate, fk_ptt),
        {'schema': sensor_schema}
    )

class Rfid(Base):
    __tablename__ = 'T_rfid'
    ID = Column(Integer, Sequence('seq_rfid_pk_id'),primary_key=True)
    creator = Column(Integer)
    FK_Sensor = Column(Integer, nullable=False)
    chip_code = Column(String(15), nullable=False)
    date_ = Column(DateTime, nullable=False)
    creation_date = Column(DateTime, server_default=func.now())
    validated = Column('validated',Boolean, server_default='0')
    checked = Column('checked',Boolean, server_default='0')
    frequency = Column(Integer)
    __table_args__ = (
        Index('idx_Trfid_chipcode_date', chip_code, date_),
        UniqueConstraint(FK_Sensor, chip_code, date_),
        {'schema': sensor_schema}
    )

class CamTrap(Base):
    __tablename__ = 'TcameraTrap'
    pk_id = Column(Integer, Sequence('seq_camtrap_pk_id'), primary_key = True)
    path = Column(String(250) , nullable = False)
    name = Column(String(250) , nullable = False)
    extension = Column(String(250) , nullable = False)
    checked = Column(Boolean, server_default = '0')
    validated = Column(Boolean, server_default = '0')
    uploaded = Column(Boolean, server_default = '0')
    date_creation = Column(DateTime)
    date_uploaded = Column(DateTime, server_default = func.now())

    __table_args__ = (
        {'schema': sensor_schema}
    )
