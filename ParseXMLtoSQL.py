# This script processes Artel Data Manager XML files and pushes relevant data to a MySQL Database
import xmltodict
import mysql.connector
from dateutil.parser import parse
import time


# Opening file to read with binary encoding and parsing to dict
def xmlToDict(path):
    with open(path, 'rb') as f:
        doc = xmltodict.parse(f.read())
    return doc


# Reformats FileID to get time in format: YYMMDDSSHHMISS
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
        print('Parsing in Full Plate mode...')
        mode = 'plate'
        groups = [data['Plate']]
    elif 'Group' in data:
        # Partial Plate (Group) Format
        print('Parsing in Partial Plate (Group) mode...')
        mode = 'group'
        groups = data['Group']
    else:
        print('File Format Error!')

    # Pull group independent data
    outputData['snReader'] = data['Plate_Reader']['Serial_Number']
    outputData['dateTime'] = getTime(data)
    outputData['type'] = mode
    outputData['device'] = data['Header3']['Device_ID']
    outputData['idLayout'] = data['Header3']['Layout_ID']
    outputData['idFile'] = data['FileID']
    outputData['snReader'] = data['Plate_Reader']['Serial_Number']

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

    print(outputData)
    return outputData


def xmlToData(path):
    # Parsed XML file dict
    data = xmlToDict(path)
    # Extract well data
    wellData = getFileData(data)
    return wellData


# Input dictionary must have the following keys:
def dataToDB(data, dbName):
    db = mysql.connector.connect(host='localhost',
                                 user='python_user',
                                 passwd='*f39SEXJlUG1',
                                 database=dbName
                                 )
    cursor = db.cursor()

    # Populate 'run_data' Table
    cmd = "INSERT INTO run_data (date_time, type, device, id_file, sn_reader, id_layout, operator, setup_notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (data['dateTime'], data['type'], data['device'], data['idFile'], data['snReader'], data['idLayout'], data['operator'], data['setupNotes'])
    cursor.execute(cmd, val)
    fkey = int(cursor.lastrowid)
    print(str(cursor.rowcount) + " row(s) inserted into run_data.")

    # Populate 'well_data' Table
    cmd = "INSERT INTO well_data (id_run, `group`, `row`, col, vol_ul, vol_tgt_ul) VALUES (%s, %s, %s, %s, %s, %s)"

    val = []
    for i in range(len(data['wellData']['wellGroup'])):
        val.append([fkey, data['wellData']['wellGroup'][i], data['wellData']['wellRow'][i], data['wellData']['wellCol'][i], data['wellData']['wellVol_ul'][i], data['wellData']['wellVolTgt_ul'][i]])
    cursor.executemany(cmd, val)
    print(str(cursor.rowcount) + " row(s) inserted into well_data.")

    db.commit()

pathC96 = '3uL 1_10.xml'
pathCHi = '3_10uL_CHi.xml'

data = xmlToData(pathCHi)

dataToDB(data, 'artel_data')
