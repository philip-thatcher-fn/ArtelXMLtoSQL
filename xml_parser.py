# This script processes Artel Data Manager XML files and pushes relevant data to a MySQL Database
import xmltodict
import mysql.connector
from dateutil.parser import parse
import os
import shutil
from util import log
import datetime
import time


# Opening file to read with binary encoding and parsing to dict
def xmlToDict(path):
    with open(path, 'rb') as f:
        doc = xmltodict.parse(f.read())
    return doc


# Reformats FileID to get time in format: YYMMDDSSHHMMSS
def getTime(data):
    header = data['Header3']
    time = f"{header['Date']} {header['Time']}"
    return parse(time)


def getFileData(doc):
    data = doc['Data']

    outputData = {}

    # Determine file type based on presence of 'Plate' key
    # Create 'groups' (a list) with each group dict as a separate element
    groups = None
    if 'Plate' in data:
        # Full Plate Format
        log('Parsing in Full Plate mode...')
        mode = 'plate'
        # There is only one plate dict so we need to wrap it in a list
        groups = [data['Plate']]
    elif 'Group' in data:
        # Partial Plate (Group) Format
        log('Parsing in Partial Plate (Group) mode...')
        mode = 'group'
        if type(data['Group']) == list:
            # There are multiple group dicts in a list
            groups = data['Group']
        else:
            # There is only one group dict so we need to wrap it in a list
            groups = [data['Group']]
    else:
        log('File Format Error!')

    # Pull group independent data
    outputData['snReader'] = data['Plate_Reader']['Serial_Number']
    outputData['dateTime'] = getTime(data)
    outputData['type'] = mode
    outputData['device'] = data['Header3']['Device_ID']
    outputData['idLayout'] = data['Header3']['Layout_ID']
    outputData['idFile'] = data['FileID']
    outputData['snReader'] = data['Plate_Reader']['Serial_Number']

    # Get Lot Numbers and format as comma-separated str
    lotNumbers = ''
    for i in range(len(data['Materials']['Item'])):
        lot = data['Materials']['Item'][i]['LSN']
        if i == 0:
            lotNumbers += lot
        else:
            lotNumbers += ', ' + lot

    outputData['lsn'] = lotNumbers

    # Get data that could be left blank
    if 'Operator' in data['Header3']:
        outputData['operator'] = data['Header3']['Operator']
    else:
        outputData['operator'] = ''

    if 'Setup_Notes' in data['Header3']:
        outputData['setupNotes'] = data['Header3']['Setup_Notes']
    else:
        outputData['setupNotes'] = ''

    # Get Target Volume if mode = 'plate'
    if mode == 'plate':
        target = data['Run_Statistics']['Target_Volume']

    # Loop through groups to pull out info
    wellGroup = []
    wellRow = []
    wellCol = []
    wellVol_ul = []
    wellVolTgt_ul = []
    wellData = {}
    for group in groups:

        # remove spaces from group name
        groupNameTmp = group['Name'].replace(' ', '')
        groupName = groupNameTmp.lower()

        # get target volume if mode = 'group'
        if mode == 'group':
            target = group['Group_Run_Statistics']['Target_Volume']

        rows = group['Well_Volumes']['Rows']

        colNames = [x['Name'] for x in group['Well_Volumes']['Columns']['Column']]

        for row in rows:
            for (well, colName) in zip(row['Column'], colNames):
                wellCol.append(colName)
                wellRow.append(row['Row'])
                wellGroup.append(groupName)
                wellVol_ul.append(well['Value'])
                wellVolTgt_ul.append(target)

    wellData['wellGroup'] = wellGroup
    wellData['wellRow'] = wellRow
    wellData['wellCol'] = wellCol
    wellData['wellVol_ul'] = wellVol_ul
    wellData['wellVolTgt_ul'] = wellVolTgt_ul

    outputData['wellData'] = wellData

    return outputData


def xmlToData(path):
    # Parsed XML file dict
    data = xmlToDict(path)
    # Extract well data
    wellData = getFileData(data)
    return wellData


def connectDB(dbHost, dbUser, dbPasswd, dbName):
    db = mysql.connector.connect(host=dbHost,
                                 user=dbUser,
                                 passwd=dbPasswd,
                                 database=dbName
                                 )

    cursor = db.cursor()

    return db, cursor


# Checks the database for FileID to be processed and returns True if unique
def checkDupFileID(fileID, cursor):
    unique = True
    cmd = "SELECT DISTINCT id_file FROM run_data"
    cursor.execute(cmd)
    rows = cursor.fetchall()
    for row in rows:
        if fileID == row[0]:
            unique = False
            break
    return unique


# Input dictionary must have the following keys:
def dataToDB(data, db, cursor):
    # Build epoch time for inserting data from fileID
    fileIDStr = data['idFile']
    monthStr = fileIDStr[0:2]
    dayStr = fileIDStr[2:4]
    yearStr = "20" + fileIDStr[4:6]
    hourStr = fileIDStr[6:8]
    minStr = fileIDStr[8:10]
    secStr = fileIDStr[10:12]
    dt = datetime.datetime(int(yearStr), int(monthStr), int(dayStr), int(hourStr), int(minStr), int(secStr))
    timeID = int(time.mktime(dt.timetuple()))

    # Split data in hamilton and hardware
    hardware = data['device'].split("_")
    deviceTested = str(hardware[0])
    hardwareTested = str(hardware[1])

    # Populate 'run_data' Table
    cmd = "INSERT INTO run_data (date_time, type, device, id_file, sn_reader, id_layout, operator, setup_notes, lot_numbers) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (data['dateTime'], data['type'], data['device'], data['idFile'], data['snReader'], data['idLayout'],
           data['operator'], data['setupNotes'], data['lsn'])

    cursor.execute(cmd, val)
    fkey = int(cursor.lastrowid)
    log(str(cursor.rowcount) + " row(s) inserted into run_data.")

    # Populate 'well_data' Table
    cmd = "INSERT INTO well_data (id_run, `group`, plate_row, plate_col, vol_ul, vol_tgt_ul, epoch_time, date_time, device_id, hardware_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = []
    for i in range(len(data['wellData']['wellGroup'])):
        val.append(
            [fkey, data['wellData']['wellGroup'][i], data['wellData']['wellRow'][i], data['wellData']['wellCol'][i],
             data['wellData']['wellVol_ul'][i], data['wellData']['wellVolTgt_ul'][i], timeID, data['dateTime'],
             deviceTested, hardwareTested])

    cursor.executemany(cmd, val)
    log(str(cursor.rowcount) + " row(s) inserted into well_data.")

    db.commit()


def moveFile(currFilePath, destFolder):
    fileName = os.path.basename(currFilePath)
    currFolderPath = os.path.dirname(currFilePath)
    newFilePath = currFolderPath + '/' + destFolder + '/' + fileName
    shutil.move(currFilePath, newFilePath)
    log('File moved to: ' + newFilePath)


def processFile(filePath, uniqueCheck):
    data = xmlToData(filePath)
    db, cursor = connectDB('localhost', 'python_user', '*f39SEXJlUG1', 'artel_data')

    if uniqueCheck == 1:
        unique = checkDupFileID(data['idFile'], cursor)
    else:
        unique = True

    if unique:
        dataToDB(data, db, cursor)
        moveFile(filePath, 'Processed')
        log('Processing completed successfully!')
    else:
        log('Duplicate FileID found in DB: ' + str(data['idFile']))
        moveFile(filePath, 'Not Processed')
        log('Data not pushed to DB! Processing completed unsuccessfully!')
