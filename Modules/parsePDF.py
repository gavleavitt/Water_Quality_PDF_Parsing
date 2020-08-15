# open_pdf = PyPDF3.PdfFileReader(pdf_loc, 'rb')
# p1 = open_pdf.getPage(0)
# p1_text = p1.extractText()
import pandas as pd
import pdfplumber
import unicodedata
from datetime import datetime
import hashlib
from urllib.request import urlretrieve
import DB_Queries as DBQ
import os

beachList = ['Carpinteria State Beach', 'Summerland Beach', 'Hammond\'s', 'Butterfly Beach',
             'East Beach @ Sycamore Creek',
             'East Beach @ Mission Creek', 'Leadbetter Beach', 'Arroyo Burro Beach', 'Hope Ranch Beach', 'Goleta Beach',
             'Sands @ Coal Oil Point', 'El Capitan State Beach', 'Refugio State Beach', 'Guadalupe Dunes',
             'Jalama Beach',
             'Gaviota State Beach']
beachfk = {'Carpinteria State Beach': 1, 'Summerland Beach': 2, 'Hammond\'s': 3, 'Butterfly Beach': 4,
           'East Beach @ Sycamore Creek': 5, 'East Beach @ Mission Creek': 6, 'Leadbetter Beach': 7,
           'Arroyo Burro Beach': 8, 'Hope Ranch Beach': 9, 'Goleta Beach': 10,
           'Sands @ Coal Oil Point': 11, 'El Capitan State Beach': 12, 'Refugio State Beach': 13, 'Guadalupe Dunes': 14,
           'Jalama Beach': 15,
           'Gaviota State Beach': 16}
col = ['Total Coliform Results (MPN*)', 'Total Coliform State Health Standard (MPN*)',
       "Fecal Coliform Results (MPN*)", 'Fecal Coliform State Health Standard (MPN*)', 'Enterococcus Results (MPN*)',
       'Enterococcus State Health Standard (MPN*)', 'Exceeds FC:TC ratio standard **', 'Beach Status', 'fk']
resampdict = {}


def downloadPDF(url, pdfDest):
    """
    Downloads the water quality PDF with a new name, using the current date, and places it in a destionation folder.
    The source URL and PDF name do not change, they are updates with new content.
    :param url:
    :param pdfDest:
    :return:
    """
    urlretrieve(url, pdfDest)


def md5hash(text):
    """
    Generates a md5 hash of the text of the PDF, the text first has to be encoded. This will be used to see if
    the text within a PDF has been changed since the last time it was checked.
    :param text:
    :return:
    """
    return hashlib.md5(text.encode()).hexdigest()


# def handlehash(text, pdfDate, pdfName, pdfLoc, insDate, hashedtext):
#     if DBQ.checkmd5tab(hashedtext, pdfDate) is False:
#         print("Already processed this PDF, deleting and exiting!")
#         deletePDFQuit(pdfLoc)
#         quit()
#     elif DBQ.checkmd5tab(hashedtext, pdfDate) == "New":
#         res = DBQ.insmd5(hashedtext, pdfDate, pdfName, insDate)
#     else:
#         pass
#     return res

def deletePDFQuit(pdfLoc):
    """
    Deletes pdf and ends the script
    :param pdfLoc:
    :return:
    """
    os.remove(pdfLoc)
    quit()


def handlePDFStatus(pdfstatus, pdfLoc, hashedtext, pdfDict, pdfName, currentTime):
    if pdfstatus == "Exists":
        print("Already processed this pdf, removing pdf and quitting!")
        os.remove(pdfLoc)
        quit()
    elif pdfstatus == "Update":
        pass
    elif pdfstatus == "New":
        print("New PDF!")
        # Generate beach dictionary
        beachDict = genDict(pdfDict['pdfDate'])
        # Populate beach dictionary with results
        beachDict = populateDict(pdfDict['tab'], beachDict)
        # Get the md5 hash for the new pdf
        hashid = DBQ.insmd5(hashedtext, pdfDict['pdfDate'], pdfName, currentTime)
        # Insert records into postgres, using the beachDict
        DBQ.insertWaterQual(beachDict, hashid)
    else:
        print("Something wrong happened!")

def cleanText(textList):
    """
    Normalizes the unicode text within the provided list, this is needed since the PDF conversion to text leads to
    some unicode characters being a combination of two unicode points, where we want a single value for ease of use.
    Items that are None are also converted to "Null" since the conversion sets some values to None for some reason.
    :param textList:
    :return:
    """
    text = []
    for item in textList:
        if item is None:
            item = "Null"
        item = convertValue(item)
        text.append(unicodedata.normalize("NFKD", item).replace("\n", ""))
    return text


def genDict(pdfDate):
    """
    Generate a nested dictionary with beach names as keys at the upper level, and columns as keys at the
    nested level, values are set to '', except for the pdf date, so they can be filled in later.
    :param pdfDate:
    :return:
    """
    beachDict = {}
    for i in beachList:
        beachDict[i] = {}
        for c in col:
            beachDict[i][c] = ''
        beachDict[i]['Date'] = pdfDate
        beachDict[i]['fk'] = beachfk[i]
    return beachDict


def convertValue(record):
    """

    :param record:
    :return:
    """
    if record == "<10":
        return "0"
    else:
        return record


def handleReSample(recordlist, count, year, pdfDate):
    """

    :param recordlist:
    :param count:
    :param year:
    :param pdfDate:
    :return:
    """
    # Add blank entries to dict to hold values
    beachname = recordlist[0].split(" Re")[0]
    resampdict[beachname] = {}
    # Add original values to dictionary, before resampling
    resampdict[beachname][beachname + " initial"] = {}

    # Get resampled values and build dictionary with them
    for i in range(0, count):
        reSampDate = str(recordlist[0].split("sample ")[i + 1].split(" ")[i]) + year
        reSampID = (beachname + "ReSample " + reSampDate)
        resampdict[beachname][reSampID] = {}
        totColi = convertValue(recordlist[1].split(" ")[1])
        fecColi = convertValue(recordlist[3].split(" ")[1])
        entero = convertValue(recordlist[5].split(" ")[1])
        resampdict[beachname][reSampID]['totColi'] = totColi
        resampdict[beachname][reSampID]['fecColi'] = fecColi
        resampdict[beachname][reSampID]['entero'] = entero
        resampdict[beachname][reSampID]['Status'] = recordlist[8]
        resampdict[beachname][reSampID]['Date'] = reSampDate


def getPDFContents(pdfLoc):
    """

    :param pdfLoc:
    :return:
    """
    pdfDict = {}
    with pdfplumber.open(pdfLoc) as pdf:
        p1 = pdf.pages[0]
        pdfDict['text'] = p1.extract_text()
        pdfDict['tab'] = p1.extract_tables()[0]
    pdfDate = cleanText([pdfDict['text'].split("Sample Results for the Week of: ")[1].split(" \nOpen")[0]])[0]
    pdfDict['pdfDate'] = datetime.strptime(pdfDate, '%B %d, %Y')
    return pdfDict


def populateDict(tab, beachDict):
    """
    Table comes in as a list of lists.
    :param tab:
    :param pdfDate:
    :return:
    """

    # Skip list 1, which is column names, and use the index of row, nested list, being accessed
    for row in range(1, len(tab)):
        # Clean the text in the row, a single list of values
        list = cleanText(tab[row])
        # print(list)
        #
        for i in range(0, (len(tab[row]) - 1)):
            reSampleCount = list[0].count("sample")
            if reSampleCount > 0:
                print(f"Re-sampling Occurred! \nWith {reSampleCount} re-sample(s)!")
                beachDict[list[0]][col[i]] = list[i + 1]
            else:
                beachDict[list[0]][col[i]] = list[i + 1]
    return beachDict

currentTime = datetime.now()
pdfName = f"\\Ocean_Water_Quality_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
pdfLoc = pdfDest = r"G:\My Drive\Projects\Water_Quality\pdf" + pdfName
downloadURL = "https://countyofsb.org/uploadedFiles/phd/PROGRAMS/EHS/Ocean%20Water%20Weekly%20Results.pdf"

# Kick off script by downloading PDF
downloadPDF(downloadURL, pdfDest)
# Get pdf details
pdfDict = getPDFContents(pdfLoc)
# Hash text of pdf document
hashedtext = md5hash(pdfDict['text'])
# Check if md5 hash is already in postgres
pdfstatus = DBQ.checkmd5(hashedtext, pdfDict['pdfDate'], pdfLoc)
# Handle the results of the md5 hash check and control generation of dictionaries and interactions with postgres
handlePDFStatus(pdfstatus, pdfLoc, hashedtext, pdfDict, pdfName, currentTime)

# Get the md5 hash and check if its in postgres, get the hash id for use as fk
#

print("All Done!")

