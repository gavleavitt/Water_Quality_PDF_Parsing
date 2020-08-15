from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import dbcon
from models import beaches, waterQualityMD5, stateStandards, waterQuality
import os

engine = create_engine(dbcon)
Session = sessionmaker(bind=engine)
session = Session()

def checkmd5tab(hash, pdfDate):
    query = session.query(waterQualityMD5).filter(waterQualityMD5.md5 == hash).all()
    if len(query) == 0:
        return False
    else:
        if query.pdfdate == pdfDate:
            return "Update"
        else:
            return "New"

def checkmd5(hash, pdfDate, pdfLoc):
    query = session.query(waterQualityMD5).filter(waterQualityMD5.md5 == hash).all()
    # Check if md5 hash is already in postgres, if so delete the downloaded pdf and quit the script
    if len(query) > 0:
        # Check if the pdfdate is already in postgres, if so this is an update, either containing resampling or filling
        # in missing data
        if query[0].pdfdate == pdfDate:
            return "Update"
        return "Exists"
    # This is a new record, the md5 is new and the pdfDate isn't in the table
    else:
        return "New"




def insmd5(MD5, pdfDate, pdfName, insDate):
    """
    Add water quality md5 and other information to postgres database. After committing, call on the primary key, id,
    to get the persisted, auto-incremented, id. The record must be committed before this value is assigned.
    :param MD5:
    :param pdfDate:
    :param pdfName:
    :param insDate:
    :return:
    """
    newrec = waterQualityMD5(md5=MD5, pdfdate=pdfDate, pdfName=pdfName, insdate=insDate)
    session.add(newrec)
    session.commit()
    newId = newrec.id
    print("Data added to MD5 table!")
    print(f"Water quality md5 hash id is {newrec.id}")
    return newId

def insertWaterQual(beachDict, md5_fk):
    inslist = []
    for key in beachDict.keys():
        inslist.append(waterQuality(Beach=beachDict[key]['fk'], TotColi=beachDict[key]['Total Coliform Results (MPN*)'],
                                    FecColi=beachDict[key]["Fecal Coliform Results (MPN*)"],
                                    Entero=beachDict[key]['Enterococcus Results (MPN*)'],
                                    ExceedsRatio=beachDict[key]['Exceeds FC:TC ratio standard **'],
                                    BeachStatus=beachDict[key]['Beach Status'], md5_id=int(md5_fk)))
    session.add_all(inslist)
    session.commit()
    session.close()
    print("Data added to water quality table!")